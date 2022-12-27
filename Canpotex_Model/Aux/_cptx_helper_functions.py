from datetime import datetime
import pandas as pd
import configparser
from statsmodels.tsa.seasonal import seasonal_decompose
import os
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('dark_background')


class CptxHelper:
    def __init__(self,month=None, year=None) -> None:
        self.year = datetime.now().year if not year else year
        self.month = datetime.now().month if not month else month
        
        self.quarter = (self.month-1)//3 + 1
        
        self.src_table = pd.read_excel(self.read_config('S3_LINKS','s3_data_src_table'),index_col=0)
        self.sources = list(set(self.src_table.SRC.to_list()))
        self.MainPipe = {} # Initialize for DataPipeline
        self.simulations = 20000


    def read_config(self,section,var):
        DATA_CONFIG_PATH = os.path.join(os.getenv("CPTX_MODEL_PATH"),'Aux','dataConfig.cfg')
        config = configparser.ConfigParser()
        # READ DATA CONFIG FILE
        config.read(DATA_CONFIG_PATH)
        try:
            return config[section][var]
        except:
            print(f"Not Found! {section}>>{var}")
            return None

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
            # ser = ser.append(pd.DataFrame(interpolate,columns =['Date','Prices']).set_index("Date")['Prices'])
            ser = pd.concat([ser,pd.DataFrame(interpolate,columns =['Date','Prices']).set_index("Date")['Prices']],axis=0, join='outer')

        return ser
    
    def get_s3_link(self,src_tag,type_tag):
        return self.src_table[(self.src_table.SRC==src_tag)&(self.src_table.TYPE==type_tag)]['S3 Location'].iloc[0]

    @staticmethod
    def kde_max_density(_df):
        """
        INPUT: DATAFRAME AND LIST OF COLUMNS TO RUN KDE ON
        OUTPUT: MAX KDE VALUE PER COLUMN IN A DICTIONARY
        """
        columns = _df.columns.tolist()
        max_density = {}
        for column_name in columns:
            # condition1 = column_name not in ['Close',f'delta_{_frame}', f'PercPer{_frame}']
            # condition2 = self.time_frame not in ['1D','1M','1W']
            # if condition1 and condition2:
            # try:
            ###################################################
            
            ax = pd.Series(_df[column_name]).plot.kde()
            plt.close()
            items = ax.get_children()
            l = [items.index(i) for i in items if 'Line2D' in str(i)][0]
            _x_ = ax.get_children()[l]._x
            _y_ = ax.get_children()[l]._y
            # FIND MAX Density Index
            maximum_density = _x_[_y_.argmax()]
            
            # maximum_density = float(_df[column_name].mean())
            ###################################################
            max_density[column_name] = maximum_density
            # except:
            #     print(f"!!!error KDE estimation:{column_name}",end='\r')
            #     print(" "*100,end='\r')
        return max_density

    def monthly_dummy(self,month:int=0):
        if month!=0:
            self.month = month
        dm1 = 1*self.dm1 if self.month == 1 else 0
        dm2 = 1*self.dm2 if self.month == 2 else 0
        dm3 = 1*self.dm3 if self.month == 3 else 0
        dm4 = 1*self.dm4 if self.month == 4 else 0
        dm5 = 1*self.dm5 if self.month == 5 else 0
        dm6 = 1*self.dm6 if self.month == 6 else 0
        dm7 = 1*self.dm7 if self.month == 7 else 0
        dm8 = 1*self.dm8 if self.month == 8 else 0
        dm9 = 1*self.dm9 if self.month == 9 else 0
        dm10 =1*self.dm10 if self.month == 10 else 0
        dm11 =1*self.dm11 if self.month == 11 else 0
        dm12 =1*self.dm12 if self.month == 12 else 0
        monthly_dummy = dm1 + dm2+dm3+dm4+dm5+dm6+dm7+dm8+dm9+dm10+dm11+dm12
        return monthly_dummy

    
    def quarterly_dummy(self,month:int=0):
        if month!=0:
            self.month = month
        # GET THE QUARTER
        self.quarter = (self.month-1)//3 + 1
        # FIND THE Q DUMMY IMPACT
        q1 = 1*self.Q1Dummy if self.quarter == 1 else 0
        q2 = 1*self.Q2Dummy if self.quarter == 2 else 0
        q3 = 1*self.Q3Dummy if self.quarter == 3 else 0
        q4 = 1*self.Q4Dummy if self.quarter == 4 else 0
        return q1+q2+q3+q4

    def tri_distribute(self,val, r):
        """val: mode >> middle value
            r: standard deviation / +/- number"""
        return np.random.triangular(val-r,val,val+r)


    def war_dummy(self):
        try:
            if self.month>=1 and self.year>2021:
                return 1*self.WarDummy
            else:
                return 0
        except:
            return 0

        
    @staticmethod
    def check_floats(x):
        try:
            return float(x)
        except:
            return None


    def add_std_lags(self,df,std_window:int,lags:str,colname='Value'):
        """
        df - timeseries dataframe Date Index | Value Column
        """
        _df = df.copy()
        # Get total lags
        lags = [int(x) for x in lags.split(',')]
        
        counter = 0
        for i,lag in enumerate(lags):
            # FOR ONE LAG ITEM ONLY
            if (len(lags) ==1 or 0 not in lags) and int(lag)!=0:
                _df[f'std'] = _df[colname].rolling(window=std_window).std()
            
            
            if int(lag)>0:
                # i = 1 if len(lags)==1 else i
                counter+=1
                _df[f'lag{counter}'] = _df.Value.shift(lag)
                _df[f"std{counter}"] = _df[f'lag{counter}'].rolling(window=std_window).std()
            else:
                _df[f'std'] = _df[colname].rolling(window=std_window).std()

        return _df
