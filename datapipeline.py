import os 
import pandas as pd

class DataFeed:
    def __init__(self) -> None:
        self.src = "DataFeeds"
        
    @property
    def get_BrazilCFR(self):
        # Adding volatility window
        brazilcfr_std_window = 12
        
        file_name = 'BrazilCFR.xlsx'
        src_file = os.path.join(self.src,file_name)
        b = pd.read_excel(src_file,index_col=0, parse_dates=True)
        b[f'std_{brazilcfr_std_window}'] = b['BrazilCFR'].rolling(window=brazilcfr_std_window).std()
        return b

    @property
    def get_SEAsiaCFR(self):
        # Adding volatility window
        seasiacfr_std_window = 12  # x months

        file_name = 'SEAsiaCFR.xlsx'
        src_file = os.path.join(self.src,file_name)
        s = pd.read_excel(src_file,index_col=0, parse_dates=True)
        s[f'std_{seasiacfr_std_window}'] = s['SEAsia'].rolling(window=seasiacfr_std_window).std()
        return s

    @property
    def get_food_price_index(self):
        """current model: lags>> 2m 3m 6m"""
        file_name = 'FoodPriceIndex_FAO.xlsx'
        src_file = os.path.join(self.src,file_name)
        f = pd.read_excel(src_file,index_col=0, parse_dates=True)
        # LAGS
        foa_lag1 = 2 #months
        fao_lag2 = 3 #months
        fao_lag3 = 6 #months

        # Volatility Window
        fao_std_window1 = 8 #corresponds to lag # 1
        fao_std_window2 = 6 #corresponds to lag # 2
        fao_std_window3 = 3 #corresponds to lag # 3


        # Adding lag
        f[f'fao_{foa_lag1}m'] = f['Food Price Index'].shift(foa_lag1).values
        f[f'fao_{fao_lag2}m'] = f['Food Price Index'].shift(fao_lag2).values
        f[f'fao_{fao_lag3}m'] = f['Food Price Index'].shift(fao_lag3).values

        # Adding volatility
        f[f'std_{foa_lag1}m_{fao_std_window1}'] = f[f'fao_{foa_lag1}m'].rolling(window=fao_std_window1).std()
        f[f'std_{fao_lag2}m_{fao_std_window2}'] = f[f'fao_{fao_lag2}m'].rolling(window=fao_std_window2).std()
        f[f'std_{fao_lag3}m_{fao_std_window3}'] = f[f'fao_{fao_lag3}m'].rolling(window=fao_std_window3).std()
        return f

    @property
    def get_eurusd(self):
        eurusd_std_window = 3
        file_name = 'EURUSD=X.csv'
        src_file = os.path.join(self.src,file_name)
        e = pd.read_csv(src_file,index_col=0, parse_dates=True)
        e[f'std_{eurusd_std_window}'] = e['Adj Close'].rolling(window=eurusd_std_window).std()
        return e


    @property
    def get_g20_cpi(self):
        inflation_std_window = 6
        file_name = 'G20CPI.xlsx'
        src_file = os.path.join(self.src,file_name)
        i = pd.read_excel(src_file,index_col=0, parse_dates=True)
        i[f'std_{inflation_std_window}'] = i['G20CPI'].rolling(window=inflation_std_window).std()
        return i

    @property
    def get_gdp(self):
        gdp_std_window=48

        file_name = 'GDP_Steo.xlsx'
        src_file = os.path.join(self.src,file_name)
        df = pd.read_excel(src_file)
        df['Date'] = pd.to_datetime(df.Month+"-"+df.Year.apply(lambda x:str(x)))
        df = df[['Date','GDPQXUS']]
        df.set_index('Date',inplace=True)
        df[f'std_{gdp_std_window}']=df['GDPQXUS'].rolling(window=gdp_std_window).std()
        return df


    @property
    def get_historical_netback(self):
        file_name = 'Historical_Actual_Netback.xlsx'
        src_file = os.path.join(self.src,file_name)
        df = pd.read_excel(src_file,index_col=0,parse_dates=True)
        return df

    @property
    def get_natural_gas(self):
        ng_std_window = 6
        file_name = 'Natural_Gas_Steo.xlsx'
        src_file = os.path.join(self.src,file_name)
        df = pd.read_excel(src_file)
        df['Date'] = pd.to_datetime(df.Month+"-"+df.Year.apply(lambda x:str(x)))
        df = df[['Date','NGHHUUS']]
        df.set_index('Date',inplace=True)
        df[f'std_{ng_std_window}'] = df['NGHHUUS'].rolling(window=ng_std_window).std()
        return df

    @property
    def get_total_fertilizer_production(self):
        fertprodquad_std_window = 60
        fertprod_std_window = 60
        file_name = 'TotalFertilizerProduction.xlsx'
        src_file = os.path.join(self.src,file_name)
        f = pd.read_excel(src_file,index_col=0, parse_dates=True)
        f['FertProdQuad'] = f['Total Fertilizer Production']**2
        f[f'std_quad_{fertprodquad_std_window}'] = f['FertProdQuad'].rolling(window=fertprodquad_std_window).std()
        f[f'std_{fertprod_std_window}'] = f['Total Fertilizer Production'].rolling(window=fertprod_std_window).std()
        return f

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