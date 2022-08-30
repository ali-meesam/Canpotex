import os 
import pandas as pd
from datetime import datetime


class DataFeed:
    def __init__(self) -> None:
        self.src = "DataFeeds"
        self.year = datetime.now().year
        self.year = 2022

        self.month = datetime.now().month
        self.month = 7
        
        self.quarter = (self.month-1)//3 + 1
        
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
    def get_historical_mineNetback(self):
        file_name = 'Historical_MineNetback.xlsx'
        src_file = os.path.join(self.src,file_name)
        df = pd.read_excel(src_file,index_col=0,parse_dates=True)

        lag1 = 0
        lag2 = 1
        lag3 = 6

        std_window1 = 12
        std_window2 = 12
        std_window3 = 12

        df['lag1'] = df.MineNetback.shift(lag1)
        df['lag2'] = df.MineNetback.shift(lag2)
        df['lag3'] = df.MineNetback.shift(lag3)

        df['std1'] = df.lag1.rolling(window=std_window1).std()
        df['std2'] = df.lag2.rolling(window=std_window2).std()
        df['std3'] = df.lag3.rolling(window=std_window3).std()

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
    def get_ethanol(self):
        # Ethanol >> Quarterly Data to Monthly
        eth_std_window = 12
        file_name = 'E85.xlsx'
        src_file = os.path.join(self.src,file_name)
        f = pd.read_excel(src_file,index_col=0, parse_dates=True)
        f[f'std_{eth_std_window}'] = f.E85.rolling(window=eth_std_window).std()
        d = f.resample('M').last()
        d.ffill(inplace=True)

        x = d.iloc[-1]

        addition = []
        if x.name.year==self.year and x.name.month <self.month:
            m_delta = self.month - x.name.month
            month = x.name.month
            eth_price = x.E85
            eth_std = x.std_12
            for _i in range(m_delta):
                month += 1    
                addition.append([datetime(year=self.year,month=month,day=1), eth_price, eth_std])
        addition

        new_df = pd.DataFrame(addition,columns = ['Survey Start Date','E85'	,f'std_{eth_std_window}'])

        new_df.set_index('Survey Start Date',inplace=True)

        df = pd.concat([d,new_df])

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
    def get_freightCost(self):
        std_total = 8
        file_name = 'FreightCost.xlsx'
        src_file = os.path.join(self.src,file_name)
        f = pd.read_excel(src_file,index_col=0, parse_dates=True)
        f['TotalCost'] = f.sum(axis=1)
        
        f[f'std_{std_total}'] = f.TotalCost.ewm(span=std_total,min_periods=std_total).std()
        return f

    @property
    def get_interimPricing(self):
        std_window = 12
        file_name = 'InterimPricing.xlsx'
        src_file = os.path.join(self.src,file_name)
        df = pd.read_excel(src_file,index_col=0, parse_dates=True)
        df[f'std_{std_window}'] = df.InterimPricing.rolling(window=std_window).std()
        return df

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