"""
This file will contain all the data directly and indirecttly associated to Netbacck pricing Model
""";

from _cptx_helper_functions import CptxHelper
import pandas as pd
from datetime import datetime


class DataPipes(CptxHelper):
    def __init__(self, month=None, year=None) -> None:
        """Monthly DataFeeds Actuals and Forecast Merged to create full data stream for the model feed
        All Feeds Have Date - Index and Value - Column
        """
        CptxHelper.__init__(self,month,year)
        
        self.MainPipe = self.get_all_feeds

    @property
    def get_all_feeds(self):
        try:
            data = {
                "gdp": self.get_gdp,
                "ng" : self.get_naturalgas,
                "fertprod": self.get_fertilizer_production,
                "usdeur": self.get_usdeur,
                'fpi': self.get_fpi
                }

            return data
        except:
            print("Error Encountered: Pulling All Data Pipes {DataPipes -> get_all_feeds}")
            return {}
    @property
    def get_latest_dates(self):
        latest_dates = {k: v.index[-1] for (k,v) in self.MainPipe.items()}
        return latest_dates

    @property
    def get_gdp(self):
        # UPDATE IF THE DATA HASNT BEEN PULLED DURING CLASS INITIALZIATION
        if 'gdp' not in self.MainPipe:
            print("*"*100+"\n"+"Downloading: GDP"+"\n"+"*"*100)
            ######################################################
            # GET RAW DATA FROM S3 BUCKET
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
            ####################
            # RENAMING COLUMN
            gdp_consolidated.rename(columns={'US_GDP':'Value'},inplace=True)
            ######################################################
            return gdp_consolidated
        else:
            return self.MainPipe['gdp']

    @property
    def get_fertilizer_production(self):
        # UPDATE IF THE DATA HASNT BEEN PULLED DURING CLASS INITIALZIATION
        if 'fertprod' not in self.MainPipe:
            print("*"*100+"\n"+"Downloading: Fertilizer Production"+"\n"+"*"*100)
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
            # RENAMING COLUMN TO VALUE
            df.rename(columns={'FERT':'Value'},inplace=True)
            return df
        else:
            return self.MainPipe['fertprod']

    @property
    def get_naturalgas(self):
        # UPDATE IF THE DATA HASNT BEEN PULLED DURING CLASS INITIALZIATION
        if 'ng' not in self.MainPipe:
            source = "NG"
            print("*"*100+"\n"+"Downloading: HenryHub Natural Gas"+"\n"+"*"*100)
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

            # RENAMING COLUMN TO VALUE
            consolidated.rename(columns={'rate':'Value'},inplace=True)
            
            return consolidated
        else:
            return self.MainPipe['ng']

    @property
    def get_usdeur(self):
        # UPDATE IF THE DATA HASNT BEEN PULLED DURING CLASS INITIALZIATION
        if 'usdeur' not in self.MainPipe:
            source = "USDEUR"
            print("*"*100+"\n"+"Downloading: ExchangeRate USD/EUR"+"\n"+"*"*100)
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
            # RENAMING COLUMN TO VALUE
            consolidated.rename(columns={'USDEUR':'Value'},inplace=True)
            
            return consolidated
        else:
            return self.MainPipe['usdeur']
    
    @property
    def get_fpi(self):
        # UPDATE IF THE DATA HASNT BEEN PULLED DURING CLASS INITIALZIATION
        if 'fpi' not in self.MainPipe:
            print("*"*100+"\n"+"Downloading: Food Price Index"+"\n"+"*"*100)
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

            actual.Date = pd.to_datetime(actual.Date)
            actual.set_index('Date',inplace=True)

            if not 'timestamp' in str(type(actual.index[0])).lower():
                actual.index = pd.to_datetime(actual.index)

            seasonality = self.get_seasonality(actual[COMMON_COL_NAME],frequency_type='m')

            # INTERPOLATED SERIES WITH ACTUAL AND AVG YEARLY FORECAST DATA
            f_series = self.yearly_average_interpolator(actual[COMMON_COL_NAME],seasonal=seasonality,averages=averages)

            consolidated = pd.DataFrame()

            consolidated[COMMON_COL_NAME] = f_series
            consolidated.index.name = 'Date'
            # RENAMING COLUMN TO VALUE
            consolidated.rename(columns={'FoodPriceIndex':'Value'},inplace=True)
            
            return consolidated
        else:
            return self.MainPipe['fpi']




if __name__=="__main__":
    self = DataPipes()
    print(self.get_naturalgas)




