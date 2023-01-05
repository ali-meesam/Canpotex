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
    
    def predict(self,month:int=None,year:int=None):
        if month:
            self.month=month
        if year:
            self.year = year
        
        print(f"Predicting Brazil >> {self.month} / {self.year}...")
        # get DATA
        fao = self.get_food_price_index
        eurusd = self.get_eurusd
        fertprod = self.get_total_fertilizer_production
        inflation = self.get_g20_cpi
        gdp = self.get_gdp
        brazil_cfr = self.get_BrazilCFR

        dm = self.monthly_dummy(month)
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
            fao2m = self.tri_distribute(f.lag1,f.std1)
            fao3m = self.tri_distribute(f.lag2,f.std2)
            fao6m = self.tri_distribute(f.lag3,f.std3)
            e0m = self.tri_distribute(e['DEXUSEU'],e.std_1)
            fert0m = self.tri_distribute(fert.FertProdQuad,fert.std_quad)
            ig200m = self.tri_distribute(ig20.G20CPI,ig20.std_1)
            g0m = self.tri_distribute(g.GDPQXUS,g.std_1)
            b0m = self.tri_distribute(b.BrazilCFR,b.std_1)
            brazil_latest_cfr.append(dm + const + self.FAOPriceIndex_2*fao2m + self.FAOPriceIndex_3*fao3m + self.FAOPriceIndex_6*fao6m + self.USDEURO*e0m + self.FertProdQuad*fert0m + self.G20Inflation*ig200m + self.USGDP*g0m + self.BrazilCFR_1*b0m)

        pred_df = pd.DataFrame(brazil_latest_cfr,columns=['Predictions'])
        print("*"*50)
        print(pred_df.describe())
        print("*"*50)
        pred_df.plot(kind='hist',bins=100,title=f'Brazil CFR - {self.simulations} Iterations');
        # plt.show()
        prediction = round(self.kde_max_density(pred_df)['Predictions'],2)
        print(f"Brazil EV -->>> {self.year} {self.month} ${prediction}")
        
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

    
    def predict(self,month:int=None,year:int=None):
        if month:
            self.month = month
        if year:
            self.year = year

        print(f"Predicting SE Asia >> {self.month} / {self.year}...")
        # get DATA
        naturalgas = self.get_natural_gas
        gdp = self.get_gdp
        eurusd = self.get_eurusd
        fertprod = self.get_total_fertilizer_production
        seasia_cfr = self.get_SEAsiaCFR

        dm = self.monthly_dummy(month)
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
        # SEAsia CFR
        s = seasia_cfr[(seasia_cfr.index.month==self.month) & (seasia_cfr.index.year==self.year)].iloc[-1]

        seasia_latest_cfr = []
        for i in tqdm(range(self.simulations)):
            ng0m = self.tri_distribute(n.NGHHUUS,n.std_1)
            g0m = self.tri_distribute(g.GDPQXUS,g.std_1)
            e0m = self.tri_distribute(e['DEXUSEU'],e.std_1)
            fert0m = self.tri_distribute(fert['Total Fertilizer Production'],fert.std_1)
            s0m = self.tri_distribute(s.SEAsia,s.std_1)
            result =dm + const + self.HHNaturalGasPrice* ng0m + self.USGDP*g0m + self.USDEURO*e0m + self.TotalFertilizerProduction*fert0m + self.SEAsia_1 *s0m
            seasia_latest_cfr.append(result)

        pred_df = pd.DataFrame(seasia_latest_cfr,columns=['Predictions'])

        print("*"*50)
        print(pred_df.describe())
        print("*"*50)
        pred_df.plot(kind='hist',bins=100,title=f'SEAsia CFR - {self.simulations} Iterations');
        # plt.show()
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

    def predict(self,month:int=None, year:int=None):
        if month:
            self.month=month
        if year:
            self.year = year
        print(f"Predicting MineNetback >> {self.month} / {self.year}...")
        # SE ASIA
        seasia_predict = SEAsiaCFR().predict(month=month,year=year)
        seasia_cfr = self.get_SEAsiaCFR
        seasia_std = seasia_cfr[(seasia_cfr.index.month==self.month) & (seasia_cfr.index.year==self.year)].std_1.iloc[-1]
        
        # BRAZIL
        brazil_predict = BrazilCFR().predict(month=month,year=year)
        brazil_cfr = self.get_BrazilCFR 
        brazil_std = brazil_cfr[(brazil_cfr.index.month==self.month) & (brazil_cfr.index.year==self.year)].std_1.iloc[-1]
        
        # ETHANOL
        ethanol = self.get_ethanol
        ethanol = ethanol[(ethanol.index.month==self.month) & (ethanol.index.year==self.year)].iloc[-1]
        
        # FREIGHT COST
        freightCost = self.get_freightCost
        freightCost = freightCost[(freightCost.index.month==self.month) & (freightCost.index.year==self.year)].iloc[-1]
        
        # CONST
        const = self.const
        # Quarter DUMMY
        quarterdummy = self.quarterly_dummy(self.month)

        mine_netbacks = []
        for i in tqdm(range(self.simulations)):
            seasia0m = self.tri_distribute(seasia_predict,seasia_std)
            brazil0m = self.tri_distribute(brazil_predict,brazil_std)
            ethanol0m = self.tri_distribute(ethanol.E85,ethanol.std_1)
            freightCost0m = self.tri_distribute(freightCost.TotalCost,freightCost.std_1)
            mine_netbacks.append(const + quarterdummy + ethanol0m*self.EIAE85 + freightCost0m*self.FreightCost + seasia0m*self.SEAsia + brazil0m*self.BrazilCFR)

        pred_df = pd.DataFrame(mine_netbacks,columns=['Predictions'])
        print("*"*50)
        print(pred_df.describe())
        print("*"*50)
        pred_df.plot(kind='hist',bins=100,title=f'Mine Netback - {self.simulations} Iterations');
        # plt.show()
        prediction = round(self.kde_max_density(pred_df)['Predictions'],2)
        print(f"Max Density -->>> ${prediction}")
        return prediction

class ActualNetback(SourceModel):
    def __init__(self) -> None:
        SourceModel.__init__(self)
        self.MineNetback = 0.41
        self.MineNetback_1 = -0.14
        self.MineNetback_6 = -0.13
        self.WarDummy = 11.50
        self.Q1Dummy = 2.84
        self.Q2Dummy = 0.00
        self.Q3Dummy = -1.30
        self.Q4Dummy = 0
        self.Interim = 0.84
        
    def predict(self,month:int=None, year:int=None):
        if month:
            self.month=month
        if year:
            self.year = year
        print(f"Predicting Actual Netback >> {self.month} / {self.year}...")
        # WAR DUMMY
        warDummy = self.war_dummy()
        # Q DUMMY
        qDummy = self.quarterly_dummy(month=month)
        # MINE NETBACK
        mineNetback_predict = MineNetBack().predict(month=month,year=year)
        mine_netbacks = self.get_historical_mineNetback
        mine_netbacks = mine_netbacks[(mine_netbacks.index.month==self.month) & (mine_netbacks.index.year==self.year)].iloc[-1]
        # INTERIM PRICING
        interim = self.get_interimPricing
        interim = interim[(interim.index.month==self.month) & (interim.index.year==self.year)].iloc[-1]

        actuals = []
        for i in tqdm(range(self.simulations)):
            interim0m = self.tri_distribute(interim.InterimPricing,interim.std_1)
            mine0m = self.tri_distribute(mineNetback_predict,mine_netbacks.std1)
            mine1m = self.tri_distribute(mine_netbacks.lag2,mine_netbacks.std2)
            mine6m = self.tri_distribute(mine_netbacks.lag3,mine_netbacks.std3)
            actuals.append(interim0m*self.Interim + mine0m*self.MineNetback + mine1m*self.MineNetback_1 + mine6m*self.MineNetback_6 + warDummy *  qDummy)
        pred_df = pd.DataFrame(actuals,columns=['Predictions'])
        print("*"*50)
        print(pred_df.describe())
        print("*"*50)
        pred_df.plot(kind='hist',bins=100,title=f'Actual Netback - {self.simulations} Iterations');
        prediction = round(self.kde_max_density(pred_df)['Predictions'],2)
        print(f"Max Density -->>> ${prediction}")
        plt.show()
        return prediction
        

if __name__=='__main__':
    # print("="*100)
    # print("BRAZIL MODEL")
    # m = BrazilCFR()
    # m.predict()
    # print("="*100)
    # print("SE ASIA MODEL")
    # m = SEAsiaCFR()
    # m.predict()
    _month = int(input("Enter a month: "))
    _year = int(input("Enter a year: "))

    m = ActualNetback()
    m.predict(_month,_year)
