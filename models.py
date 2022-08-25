from typing import SupportsRound
from datapipeline import DataFeed
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

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


class MineNetBack(SourceModel):
    def __init__(self) -> None:
        SourceModel.__init__(self)
        self.const = -18.33
        self.Q1Dummy = -7.16
        self.Q2Dummy = 1.25
        self.Q3Dummy = -1.81
        self.EIAE85 = 6.15
        self.FreightCost = -0.22
        self.SEAsia = 0.49
        self.BrazilCFR = 0.37

class ActualNetback_Coeff:
    def __init__(self) -> None:
        self.MineNetback = 0.41
        self.MineNetback_1 = -0.14
        self.MineNetback_6 = -0.13
        self.WarDummy = 11.50
        self.Q1Dummy = 2.84
        self.Q2Dummy = 0.00
        self.Q3Dummy = -1.30
        self.Interim = 0.84

        


