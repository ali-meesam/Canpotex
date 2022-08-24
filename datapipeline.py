import os 
import pandas as pd

class DataFeed:
    def __init__(self) -> None:
        self.src = "DataFeeds"
    
    @property
    def get_BrazilCFR(self):
        file_name = 'BrazilCFR.xlsx'
        src_file = os.path.join(self.src,file_name)
        return pd.read_excel(src_file,index_col=0, parse_dates=True)

    @property
    def get_SEAsiaCFR(self):
        file_name = 'SEAsiaCFR.xlsx'
        src_file = os.path.join(self.src,file_name)
        return pd.read_excel(src_file,index_col=0, parse_dates=True)


    @property
    def get_eurusd(self):
        file_name = 'EURUSD=X.csv'
        src_file = os.path.join(self.src,file_name)
        return pd.read_csv(src_file,index_col=0, parse_dates=True)

    @property
    def get_food_price_index(self):
        file_name = 'FoodPriceIndex_FAO.xlsx'
        src_file = os.path.join(self.src,file_name)
        return pd.read_excel(src_file,index_col=0, parse_dates=True)

    @property
    def get_g20_cpi(self):
        file_name = 'G20CPI.xlsx'
        src_file = os.path.join(self.src,file_name)
        return pd.read_excel(src_file,index_col=0, parse_dates=True)

    @property
    def get_gdp(self):
        file_name = 'GDP_Steo.xlsx'
        src_file = os.path.join(self.src,file_name)
        df = pd.read_excel(src_file)
        df['Date'] = pd.to_datetime(df.Month+"-"+df.Year.apply(lambda x:str(x)))
        df = df[['Date','GDPQXUS']]
        df.set_index('Date',inplace=True)
        return df

    @property
    def get_historical_netback(self):
        file_name = 'Historical_Actual_Netback.xlsx'
        src_file = os.path.join(self.src,file_name)
        df = pd.read_excel(src_file,index_col=0,parse_dates=True)
        return df

    @property
    def get_natural_gas(self):
        file_name = 'Natural_Gas_Steo.xlsx'
        src_file = os.path.join(self.src,file_name)
        df = pd.read_excel(src_file)
        df['Date'] = pd.to_datetime(df.Month+"-"+df.Year.apply(lambda x:str(x)))
        df = df[['Date','NGHHUUS']]
        df.set_index('Date',inplace=True)
        return df

    @property
    def get_total_fertilizer_production(self):
        file_name = 'TotalFertilizerProduction.xlsx'
        src_file = os.path.join(self.src,file_name)
        return pd.read_excel(src_file,index_col=0, parse_dates=True)

    @property
    def get_POT_price(self):
        file_name = 'POT_Stock_Price.csv'
        src_file = os.path.join(self.src,file_name)
        return pd.read_csv(src_file,index_col=0, parse_dates=True)

    @property
    def get_AGU_price(self):
        file_name = 'AGU_Stock_Price.csv'
        src_file = os.path.join(self.src,file_name)
        return pd.read_csv(src_file,index_col=0, parse_dates=True)

    @property
    def get_NTR_price(self):
        file_name = 'NTR_Stock_Price.csv'
        src_file = os.path.join(self.src,file_name)
        return pd.read_csv(src_file,index_col=0, parse_dates=True)