import os 
import pandas as pd
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose

class DataFeed:
    def __init__(self,month=None, year=None) -> None:

        self.year = datetime.now().year if not year else year
        self.month = datetime.now().month if not month else month
        
        self.quarter = (self.month-1)//3 + 1
        # GETTING LOCALLY STORED SRC TABLE FOR THE S3 LINKS
        self.src_table = pd.read_excel("DataSources.xlsx",index_col=0)
        self.sources = list(set(self.src_table.SRC.to_list()))
    
    @staticmethod
    def quarter_dates(x:str):
        """
        x: Format 'YYYY Q1'
        return: 'YYYY-mm-01'
        """
        year, qtr = x.rstrip().lstrip().split(' ')
        month = 1 if qtr=='Q1' else 4 if qtr=='Q2' else 7 if qtr=='Q3' else 10
        return datetime(int(year),month,1).strftime("%Y-%m-%d")

    @staticmethod
    def get_seasonality(ser, frequency_type):
        """
        frequency_type = 'm' or 'q'

        ***series must have datetime index***
        """
        if frequency_type=='m':
            periods_back = 60 # going 5 years back
            period = 12
        elif frequency_type=='q':
            periods_back = 20 # going 5 years back
            period = 4
        else:
            periods_back = int(input('Enter total periods back (default 30pts): ') or 30)
            period = int(input('Enter frequency (default 12): ') or 12)


        if len(ser)>periods_back:
            ser = ser[-periods_back:]
        
        model = seasonal_decompose(x=ser,extrapolate_trend='freq',period=period)
        seasonal = model.seasonal
        
        if period==4:
            # RESAMPLING FROM QUARTER TO MONTHLY DATA
            seasonal = seasonal.resample("M").first()
            # QUADRATIC SMOOTHING OVER INCREASED SAMPLED DATA
            seasonal = seasonal.interpolate(method='polynomial',order=2)

        seasonal = seasonal.loc[f'{ser.index[-1].year-1}']
        return {i.month:seasonal.loc[i] for i in seasonal.index}

    @staticmethod
    def yearly_average_interpolator(ser, seasonal:dict,averages:dict):
        """
        ser: timeseries data (1D timeseries)
        
        seasonal dict : 
        {1: 0.41134655049888985,
        2: 0.8480161224970932,
        3: 3.3452983943318477,
        4: 2.0956002897486163,
        5: 1.9889957092852701,
        6: -0.10832352344323615,
        7: -4.3017294260398655,
        8: -0.9741571538000056,
        9: -1.4775785707165492,
        10: -0.9313321811428561,
        11: -0.13003194835890602,
        12: -0.7661042628602994}
        
        averages = {
            2022:140,
            2023:135,
            2024:160
        }
        """
        
        years = list(averages.keys())
        years.sort()

        for year in years:
            # DEPARTURE POINT
            last = ser.index[-1]
            last_month = last.month if last.month <12 else 0
            last_price = ser[-1]
            # year = last.year
            interpolate = []
            prices = [] # DATE , PRICE

            for i in range(last_month+1,13):
                price = last_price+seasonal[i]
                prices.append(price)
                interpolate.append([datetime(year,i,1),price])
                last_price = price


            if max(ser.index).year>=year:
                A = sum(ser.loc[f'{year}'])
            else:
                A = 0

            c = (12*averages[year] - A)/(sum(prices))

            new_prices = [i*c for i in prices]

            # SANITY CHECK 
            # (sum(new_prices)+sum(ser.loc[f'{year}']))/12

            interpolate = [[interpolate[i][0],new_prices[i]] for i in range(len(interpolate))]

            # Add latest forecast to the series
            ser = ser.append(pd.DataFrame(interpolate,columns =['Date','Prices']).set_index("Date")['Prices'])

        return ser
    
    def get_s3_link(self,src_tag,type_tag):
        return self.src_table[(self.src_table.SRC==src_tag)&(self.src_table.TYPE==type_tag)]['S3 Location'].iloc[0]

    @property
    def get_gdp(self):
        source='GDP'
        a = self.src_table

        actual_s3_link = self.get_s3_link(source,'A')
        forecast_s3_link = self.get_s3_link(source,'F')

        # GET ACTUAL SERIES RAW
        actual = pd.read_parquet(actual_s3_link)
        # GET FORECAST SERIES RAW
        forecast = pd.read_parquet(forecast_s3_link)
        forecast['date'] = forecast['date'].apply(self.quarter_dates)
        # SAME COLUMN NAME AS THE ACTUAL SERIES
        forecast['US_GDP'] = forecast.nominalGDP
        # DROP USELESS COLUMNS
        forecast.drop(['realGDP', 'deflator', 'nominalGDP'],axis=1,inplace=True)

        # COMBINE BOTH DATAFRAMES
        gdp_consolidated = pd.concat([actual,forecast],ignore_index=True)
        # REMOVING DUPLICATES AND KEEPING THE ACTUAL FOR OLD FORECAST SERIES
        gdp_consolidated = gdp_consolidated[~gdp_consolidated['date'].duplicated(keep='first')]

        # SET DATE INDEX
        gdp_consolidated.set_index('date',inplace=True)
        # FORMAT TO DATETIME
        gdp_consolidated.index = pd.to_datetime(gdp_consolidated.index)

        # IF FRREQUENCY IS NOT MONTHLY
        if len([i for i in a[a.SRC==source]['INTERVAL'].tolist() if i!='M'])>0:
            gdp_consolidated = gdp_consolidated.resample("M").first().interpolate(mthod='polynomial',degree=2)
        return gdp_consolidated

    @property
    def get_fertilizer_production(self):
        source = "FERT"

        # a = self.src_table[self.src_table.SRC==source]

        actual_s3_link = self.get_s3_link(source,'A')
        forecast_s3_link = self.get_s3_link(source,'F')

        # READ DATA
        actual = pd.read_parquet(actual_s3_link)
        forecast = pd.read_parquet(forecast_s3_link)
        # Adjusting for 1000s of Tons
        forecast['TotalFertilizerForecast'] = forecast['TotalFertilizerForecast'].apply(lambda x:float(x)*1000)
        
        # FORMAT INDEX TO #S
        actual.reset_index(inplace=True)
        # RENAME FORECAST COLUMNS
        forecast.rename(columns={'year':'Year','TotalFertilizerForecast':'Production'},inplace=True)

        # COMBINE BOTH DATAFRAMES
        consolidated = pd.concat([actual,forecast],ignore_index=True)
        # FORMAT YEAR COLUMN TO DATE TIME
        consolidated.Year = pd.to_datetime(consolidated.Year.apply(lambda x:datetime(int(x),12,1)))
        # REMOVING DUPLICATES AND KEEPING THE ACTUAL FOR OLD FORECAST SERIES
        consolidated = consolidated[~consolidated['Year'].duplicated(keep='first')]
        # consolidated.set_index("Year",inplace=True)
        # consolidated = consolidated.resample('M',convention='start').last()
        # consolidated.bfill(inplace=True)

        # INCREASE SAMPLE TO YEARLY WITH ALL THE YEARLY VALUES THE SAME FOR EACH MONTH
        arr =[]
        for i in range(len(consolidated)):
            x = consolidated.iloc[i]
            [arr.append([x.Year.replace(month=m),x.Production]) for m in range(1,13)]
        df = pd.DataFrame(arr,columns=['Date','FERT'])
        df.set_index("Date",inplace=True)

        return df

    @property
    def get_naturalgas(self):
        source = "NG"

        a = self.src_table[self.src_table.SRC==source]

        # S3 LINKS
        actual_s3_link = self.get_s3_link(source,'A')
        forecast_s3_link = self.get_s3_link(source,'F')

        # READ DATA
        actual = pd.read_parquet(actual_s3_link)
        forecast = pd.read_parquet(forecast_s3_link)

        # COMBINE BOTH DATAFRAMES
        consolidated = pd.concat([actual,forecast],ignore_index=True)

        # FORMAT YEAR COLUMN TO DATE TIME
        consolidated.date = pd.to_datetime(consolidated.date)

        # REMOVING DUPLICATES AND KEEPING THE ACTUAL FOR OLD FORECAST SERIES
        consolidated = consolidated[~consolidated['date'].duplicated(keep='first')]

        # SET DATETIME INDEX
        consolidated.set_index("date",inplace=True)

        return consolidated

    @property
    def get_usdeur(self):
        source = "USDEUR"

        # a = self.src_table[self.src_table.SRC==source]

        # S3 LINKS
        actual_s3_link = self.get_s3_link(source,'A')
        forecast_s3_link = self.get_s3_link(source,'F')

        # READ DATA
        actual = pd.read_parquet(actual_s3_link)
        forecast = pd.read_parquet(forecast_s3_link)

        averages = {int(i[0]):i[1] for i in forecast[forecast.date>=self.year].values}

        actual.date = pd.to_datetime(actual.date)

        actual.set_index('date',inplace=True)

        seasonality = self.get_seasonality(actual['rate'],frequency_type='m')

        # INTERPOLATED SERIES WITH ACTUAL AND AVG YEARLY FORECAST DATA
        f_series = self.yearly_average_interpolator(actual['rate'],seasonal=seasonality,averages=averages)

        consolidated = pd.DataFrame()

        consolidated['USDEUR'] = f_series
        consolidated.index.name = 'Date'

        return consolidated


    @property
    def get_fpi(self):
        source = "FPI"
        COMMON_COL_NAME = 'FoodPriceIndex'

        a = self.src_table[self.src_table.SRC==source]

        # S3 LINKS
        actual_s3_link = self.get_s3_link(source,'A')
        forecast_s3_link = self.get_s3_link(source,'F')

        # READ DATA
        actual = pd.read_parquet(actual_s3_link)
        forecast = pd.read_parquet(forecast_s3_link)

        # REMOVING ALL rows with NaN Values
        actual.dropna(inplace=True)
        forecast.dropna(inplace=True)

        forecast.rename(columns={'year':'Date'},inplace=True)

        averages = {int(i[0]):i[1] for i in forecast[forecast.Date>=self.year].values}

        actual.date = pd.to_datetime(actual.Date)
        actual.set_index('Date',inplace=True)

        if not 'timestamp' in str(type(actual.index[0])).lower():
            actual.index = pd.to_datetime(actual.index)

        seasonality = self.get_seasonality(actual[COMMON_COL_NAME],frequency_type='m')

        # INTERPOLATED SERIES WITH ACTUAL AND AVG YEARLY FORECAST DATA
        f_series = self.yearly_average_interpolator(actual[COMMON_COL_NAME],seasonal=seasonality,averages=averages)

        consolidated = pd.DataFrame()

        consolidated[COMMON_COL_NAME] = f_series
        consolidated.index.name = 'Date'

        return consolidated

