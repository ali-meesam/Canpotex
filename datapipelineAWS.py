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
    
    def get_s3_link(self,tag_name):
        return self.src_table[self.src_table.SRC==tag_name]['S3 Location'].iloc[0]

    @property
    def get_gdp_actual(self):
        tag='gdp_actual'
        s3_link = self.get_s3_link(tag_name=tag)
        # GET ACTUAL SERIES RAW
        return pd.read_parquet(s3_link)


    @property
    def get_gdp_consolidated(self):
        source='GDP'
        a_src = self.src_table[self.src_table.SRC==source]

        actual_s3_link = a_src[a_src.TYPE=='A']['S3 Location'].iloc[0]
        forecast_s3_link = a_src[a_src.TYPE=='F']['S3 Location'].iloc[0]

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
        return gdp_consolidated