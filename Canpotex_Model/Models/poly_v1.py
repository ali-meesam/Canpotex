from DataPipes.model_datapipeline import DataFeed
import tqdm
import pandas as pd
import numpy as np


class BrazilCFR(DataFeed):
    
    def __init__(self, month, year) -> None:
        DataFeed.__init__(self,month=month,year=year)
        
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


