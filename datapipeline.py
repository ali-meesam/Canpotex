import os 
import pandas as pd
from datetime import datetime


class DataFeed:
    def __init__(self) -> None:
        self.src = "DataFeeds"

        self.year = datetime.now().year
        self.month = datetime.now().month
        # self.year = 2022
        # self.month = 7
        
        self.quarter = (self.month-1)//3 + 1
    
    @staticmethod
    def check_floats(x):
        try:
            return float(x)
        except:
            return None
        
    @property
    def get_BrazilCFR(self):
        # Adding volatility window
        brazilcfr_std_window = 12
        
        file_name = 'BrazilCFR.xlsx'
        src_file = os.path.join(self.src,file_name)
        b = pd.read_excel(src_file,index_col=0, parse_dates=True)
        b[f'std_1'] = b['BrazilCFR'].rolling(window=brazilcfr_std_window).std()
        return b

    @property
    def get_SEAsiaCFR(self):
        # Adding volatility window
        seasiacfr_std_window = 12  # x months

        file_name = 'SEAsiaCFR.xlsx'
        src_file = os.path.join(self.src,file_name)
        s = pd.read_excel(src_file,index_col=0, parse_dates=True)
        s[f'std_1'] = s['SEAsia'].rolling(window=seasiacfr_std_window).std()
        return s

    @property
    def get_food_price_index(self):
        """current model: lags>> 2m 3m 6m"""
        file_name = 'FoodPriceIndex_FAO.xlsx'
        src_file = os.path.join(self.src,file_name)
        f = pd.read_excel(src_file,index_col=0, parse_dates=True)
        # LAGS
        lag1 = 2 #months
        lag2 = 3 #months
        lag3 = 6 #months

        # Volatility Window
        std1 = 8 #corresponds to lag # 1
        std2 = 6 #corresponds to lag # 2
        std3 = 3 #corresponds to lag # 3


        # Adding lag
        f[f'lag1'] = f['Food Price Index'].shift(lag1).values
        f[f'lag2'] = f['Food Price Index'].shift(lag2).values
        f[f'lag3'] = f['Food Price Index'].shift(lag3).values

        # Adding volatility
        f[f'std1'] = f[f'lag1'].rolling(window=std1).std()
        f[f'std2'] = f[f'lag2'].rolling(window=std2).std()
        f[f'std3'] = f[f'lag3'].rolling(window=std3).std()
        return f

    # @property
    # def get_eurusd(self):
    #     eurusd_std_window = 3
    #     file_name = 'EURUSD=X.csv'
    #     src_file = os.path.join(self.src,file_name)
    #     e = pd.read_csv(src_file,index_col=0, parse_dates=True)
    #     e[f'std_1'] = e['Adj Close'].rolling(window=eurusd_std_window).std()
    #     return e

    @property
    def get_eurusd(self):
        # EUR USD
        eurusd_std_window = 3
        source = "OECD"

        if source == 'OECD':
            # EUR USD
            file_name = 'EURUS@propertyD-OECD.csv'
            src_file = os.path.join(self.src,file_name)
            e = pd.read_csv(src_file, parse_dates=True)
            e = e[['TIME','Value']]
            e['std_1'] = e['Value'].rolling(window=eurusd_std_window).std()
            e['TIME'] = pd.to_datetime(e['TIME'])
            e.set_index("TIME",inplace=True)
            e = e.resample('M').mean()
            e.ffill(inplace=True)
            e.rename(columns={"Value":"DEXUSEU"},inplace=True)
            return e
        elif source == 'FRED':
            file_name = 'DEXUSEU.csv'
            src_file = os.path.join(self.src,file_name)
            e = pd.read_csv(src_file,index_col=0, parse_dates=True)
            e.DEXUSEU = e.DEXUSEU.apply(self.check_floats)
            # DROP ALL NON FLOAT VALUES
            e.dropna(inplace=True)
            # Taking the mean for the month resample (instead of the last price)
            e = e.resample('1M').mean()
            e[f'std_1'] = e['DEXUSEU'].rolling(window=eurusd_std_window).std()
            return e


    @property
    def get_g20_cpi(self):
        inflation_std_window = 6
        file_name = 'G20CPI.xlsx'
        src_file = os.path.join(self.src,file_name)
        i = pd.read_excel(src_file,index_col=0, parse_dates=True)
        i[f'std_1'] = i['G20CPI'].rolling(window=inflation_std_window).std()
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
        df[f'std_1']=df['GDPQXUS'].rolling(window=gdp_std_window).std()
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
        df[f'std_1'] = df['NGHHUUS'].rolling(window=ng_std_window).std()
        return df

    @property
    def get_ethanol(self):
        # Ethanol >> Quarterly Data to Monthly
        eth_std_window = 12
        file_name = 'E85.xlsx'
        src_file = os.path.join(self.src,file_name)
        f = pd.read_excel(src_file,index_col=0, parse_dates=True)
        f[f'std_1'] = f.E85.rolling(window=eth_std_window).std()
        d = f.resample('M').last()
        d.ffill(inplace=True)

        x = d.iloc[-1]

        addition = []
        if x.name.year==self.year and x.name.month <self.month:
            m_delta = self.month - x.name.month
            month = x.name.month
            eth_price = x.E85
            eth_std = x.std_1
            for _i in range(m_delta):
                month += 1    
                addition.append([datetime(year=self.year,month=month,day=1), eth_price, eth_std])
        addition

        new_df = pd.DataFrame(addition,columns = ['Survey Start Date','E85'	,f'std_1'])

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
        f[f'std_quad'] = f['FertProdQuad'].rolling(window=fertprodquad_std_window).std()
        f[f'std_1'] = f['Total Fertilizer Production'].rolling(window=fertprod_std_window).std()
        return f
    
    @property
    def get_freightCost(self):
        std_total = 8
        file_name = 'FreightCost.xlsx'
        src_file = os.path.join(self.src,file_name)
        f = pd.read_excel(src_file,index_col=0, parse_dates=True)
        f['TotalCost'] = f.sum(axis=1)
        
        f[f'std_1'] = f.TotalCost.ewm(span=std_total,min_periods=std_total).std()
        return f

    @property
    def get_interimPricing(self):
        std_window = 12
        file_name = 'InterimPricing.xlsx'
        src_file = os.path.join(self.src,file_name)
        df = pd.read_excel(src_file,index_col=0, parse_dates=True)
        df[f'std_1'] = df.InterimPricing.rolling(window=std_window).std()
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