class BrazilCFR:
    def __init__(self) -> None:
        self.const = -178.690701
        self.FAOPriceIndex_2 = 3.4993116
        self.FAOPriceIndex_3 = -3.121247675
        self.FAOPriceIndex_6 = 1.230804723
        self.USDEURO = -5.737761368
        self.FertProdQuad = -9.38E-16
        self.G20Inflation = 8.87621401
        self.dm3 = -0.459241726
        self.dm2 = 2.032841924
        self.dm4 = 13.88908466
        self.dm5 = 8.888008189
        self.dm6 = 19.01420226
        self.dm7 = 22.33183934
        self.dm8 = -0.340514025
        self.dm9 = 10.30597745
        self.dm10 = 12.00694986
        self.dm11 = 6.882082759
        self.dm12 = -1.537324367
        self.USGDP = 0.002946866
        self.BrazilCFR_1 = 0.916783965



class SEAsiaCFR:
    def __init__(self) -> None:
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
        self.SEAsia_1 = 0.9583022


class MineNetBack:
    def __init__(self) -> None:
        self.const = -18.33
        self.Q1Dummy = -7.16
        self.Q2Dummy = 1.25
        self.Q3Dummy = -1.81
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

        


