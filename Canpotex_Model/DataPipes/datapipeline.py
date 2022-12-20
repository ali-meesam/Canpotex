"""
This file will contain all the data directly and indirecttly associated to Netbacck pricing Model
""";

from _helper_functions import CptxHelper
import pandas as pd
from datetime import datetime


class DataPipes(CptxHelper):
    def __init__(self, month=None, year=None) -> None:
        CptxHelper.__init__(self,month,year)

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









