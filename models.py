from datapipeline import DataFeed
from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

plt.style.use('dark_background')


class SourceModel(DataFeed):
    def __init__(self) -> None:
        DataFeed.__init__(self)
        self.simulations = 20000
        self.month = datetime.now().month
        self.month = 7
        self.year = datetime.now().year
        self.quarter = (self.month-1)//3 + 1

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
            self.quarter = (self.month-1)//3 + 1
        q1 = 1*self.dq1 if self.quarter == 1 else 0
        q2 = 1*self.dq2 if self.quarter == 2 else 0
        q3 = 1*self.dq3 if self.quarter == 3 else 0
        q4 = 1*self.dq4 if self.quarter == 4 else 0
        return q1+q2+q3+q4



class BrazilCFR(SourceModel):
    def __init__(self) -> None:
        SourceModel.__init__(self)
        
        self.const = -178.690701
        ########################################
        self.FAOPriceIndex_2 = 3.4993116
        self.FAOPriceIndex_3 = -3.121247675
        self.FAOPriceIndex_6 = 1.230804723
        ########################################
        self.USDEURO = -5.737761368
        ########################################
        self.FertProdQuad = -9.38E-16
        ########################################
        self.G20Inflation = 8.87621401
        ########################################
        self.dm1 = 0
        self.dm2 = 2.032841924
        self.dm3 = -0.459241726
        self.dm4 = 13.88908466
        self.dm5 = 8.888008189
        self.dm6 = 19.01420226
        self.dm7 = 22.33183934
        self.dm8 = -0.340514025
        self.dm9 = 10.30597745
        self.dm10 = 12.00694986
        self.dm11 = 6.882082759
        self.dm12 = -1.537324367
        ########################################
        self.USGDP = 0.002946866
        ########################################
        self.BrazilCFR_1 = 0.916783965
    
    def predict(self):
        # get DATA
        fao = self.get_food_price_index
        eurusd = self.get_eurusd
        fertprod = self.get_total_fertilizer_production
        inflation = self.get_g20_cpi
        gdp = self.get_gdp
        brazil_cfr = self.get_BrazilCFR

        dm = self.monthly_dummy()
        const = self.const
        
        # LATEST ENTRY ONLY
        # FAO
        f = fao[(fao.index.month==self.month) & (fao.index.year==self.year)].iloc[-1]
        # EURUSD
        e = eurusd[(eurusd.index.month==self.month) & (eurusd.index.year==self.year)].iloc[-1]
        # FERTILIZER PRODUCTION
        fert = fertprod[(fertprod.index.month==self.month) & (fertprod.index.year==self.year)].iloc[-1]
        # INFLATION
        ig20 = inflation[(inflation.index.month==self.month) & (inflation.index.year==self.year)].iloc[-1]
        # GDP
        g = gdp[(gdp.index.month==self.month) & (gdp.index.year==self.year)].iloc[-1]
        # BRAZIL CFR
        b = brazil_cfr[(brazil_cfr.index.month==self.month) & (brazil_cfr.index.year==self.year)].iloc[-1]

        brazil_latest_cfr = []
        for _ in tqdm(range(self.simulations)):
            fao2m = np.random.triangular(f.fao_2m-f.std_2m_8,f.fao_2m,f.fao_2m+f.std_2m_8)
            fao3m = np.random.triangular(f.fao_3m-f.std_3m_6,f.fao_3m,f.fao_3m+f.std_3m_6)
            fao6m = np.random.triangular(f.fao_6m-f.std_6m_3,f.fao_6m,f.fao_6m+f.std_6m_3)
            e0m = np.random.triangular(e['Adj Close']-e.std_3,e['Adj Close'],e['Adj Close']+e.std_3)
            fert0m = np.random.triangular(fert.FertProdQuad-fert.std_quad_60,fert.FertProdQuad,fert.FertProdQuad+fert.std_quad_60)
            ig200m = np.random.triangular(ig20.G20CPI-ig20.std_6,ig20.G20CPI,ig20.G20CPI+ig20.std_6)
            g0m = np.random.triangular(g.GDPQXUS-g.std_48,g.GDPQXUS,g.GDPQXUS+g.std_48)
            b0m = np.random.triangular(b.BrazilCFR-b.std_12,b.BrazilCFR,b.BrazilCFR+b.std_12)

            brazil_latest_cfr.append(dm + const + self.FAOPriceIndex_2*fao2m + self.FAOPriceIndex_3*fao3m + self.FAOPriceIndex_6*fao6m + self.USDEURO*e0m + self.FertProdQuad*fert0m + self.G20Inflation*ig200m + self.USGDP*g0m + self.BrazilCFR_1*b0m)

        pred_df = pd.DataFrame(brazil_latest_cfr,columns=['Predictions'])
        print("*"*50)
        print(pred_df.describe())
        print("*"*50)
        pred_df.plot(kind='hist',bins=100,title=f'Brazil CFR - {self.simulations} Iterations');
        plt.show()
        prediction = round(self.kde_max_density(pred_df)['Predictions'],2)
        print(f"Max Density -->>> ${prediction}")
        return prediction


class SEAsiaCFR(SourceModel):
    def __init__(self) -> None:
        SourceModel.__init__(self)
        self.const = -225.2471554
        self.HHNaturalGasPrice = 12.94327564
        self.USGDP = 0.001833302
        self.USDEURO = 36.48494964
        self.TotalFertilizerProduction = 5.63E-07
        self.dm1 = -4.12408246
        self.dm2 = 3.134492968
        self.dm3 = 7.577126814
        self.dm4 = 8.469762281
        self.dm5 = 13.45954694
        self.dm6 = 6.819304955
        self.dm7 = 7.871255767
        self.dm8 = -2.483386348
        self.dm9 = 8.212417022
        self.dm10 = 6.969052856
        self.dm11 = 3.903027432
        self.dm12 = 0
        self.SEAsia_1 = 0.9583022

    
    def predict(self):
        # get DATA
        naturalgas = self.get_natural_gas
        gdp = self.get_gdp
        eurusd = self.get_eurusd
        fertprod = self.get_total_fertilizer_production
        seasia_cfr = self.get_SEAsiaCFR

        dm = self.monthly_dummy()
        const = self.const
        # LATEST ENTRY ONLY
        # Natural Gas
        n = naturalgas[(naturalgas.index.month==self.month) & (naturalgas.index.year==self.year)].iloc[-1]
        # GDP (based on current month)
        g = gdp[(gdp.index.month==self.month) & (gdp.index.year==self.year)].iloc[-1]
        # EURUSD
        e = eurusd[(eurusd.index.month==self.month) & (eurusd.index.year==self.year)].iloc[-1]
        # FERTILIZER PRODUCTION
        fert = fertprod[(fertprod.index.month==self.month) & (fertprod.index.year==self.year)].iloc[-1]
        # BRAZIL CFR
        s = seasia_cfr.iloc[-1]

        seasia_latest_cfr = []
        for i in tqdm(range(self.simulations)):
            ng0m = np.random.triangular(n.NGHHUUS-n.std_6,n.NGHHUUS,n.NGHHUUS+n.std_6)
            g0m = np.random.triangular(g.GDPQXUS-g.std_48,g.GDPQXUS,g.GDPQXUS+g.std_48)
            e0m = np.random.triangular(e['Adj Close']-e.std_3,e['Adj Close'],e['Adj Close']+e.std_3)
            fert0m = np.random.triangular(fert['Total Fertilizer Production']-fert.std_60,fert['Total Fertilizer Production'],fert['Total Fertilizer Production']+fert.std_60)
            s0m = np.random.triangular(s.SEAsia-s.std_12,s.SEAsia,s.SEAsia+s.std_12)
            result =dm + const + self.HHNaturalGasPrice* ng0m + self.USGDP*g0m + self.USDEURO*e0m + self.TotalFertilizerProduction*fert0m + self.SEAsia_1 *s0m
            seasia_latest_cfr.append(result)

        pred_df = pd.DataFrame(seasia_latest_cfr,columns=['Predictions'])

        print("*"*50)
        print(pred_df.describe())
        print("*"*50)
        pred_df.plot(kind='hist',bins=100,title=f'SEAsia CFR - {self.simulations} Iterations');
        plt.show()
        prediction = round(self.kde_max_density(pred_df)['Predictions'],2)
        print(f"Max Density -->>> ${prediction}")
        return prediction


class MineNetBack(SourceModel):
    def __init__(self) -> None:
        SourceModel.__init__(self)
        self.const = -18.33
        self.Q1Dummy = -7.16
        self.Q2Dummy = 1.25
        self.Q3Dummy = -1.81
        self.Q4Dummy = 0
        self.EIAE85 = 6.15
        self.FreightCost = -0.22
        self.SEAsia = 0.49
        self.BrazilCFR = 0.37

class ActualNetback:
    def __init__(self) -> None:
        self.MineNetback = 0.41
        self.MineNetback_1 = -0.14
        self.MineNetback_6 = -0.13
        self.WarDummy = 11.50
        self.Q1Dummy = 2.84
        self.Q2Dummy = 0.00
        self.Q3Dummy = -1.30
        self.Interim = 0.84

        

if __name__=='__main__':
    print("="*100)
    print("BRAZIL MODEL")
    m = BrazilCFR()
    m.predict()
    print("="*100)
    print("SE ASIA MODEL")
    m = SEAsiaCFR()
    m.predict()
    