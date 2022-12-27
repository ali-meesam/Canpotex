from DataPipes.datapipeline import DataPipes

class DataFeed(DataPipes):
    def __init__(self, month=None, year=None) -> None:
        super().__init__(month, year)


    def gdp(self, std_window:int=48,lags:str='0'):
        """
        std_window: rolling standard deviation
        lags: multiple lags (comma separated i.e. 0,2,7 for no_lag, 2 months, 7 months)
        """
        # Adding Lags and Rolling Standard Deviation
        df = self.add_std_lags(self.get_gdp,std_window=std_window,lags=lags)
        return df

    def fertilizer_production(self, std_window:int=48,lags:str='0'):
        """
        std_window: rolling standard deviation
        lags: multiple lags (comma separated i.e. 0,2,7 for no_lag, 2 months, 7 months)
        """
        # Adding Lags and Rolling Standard Deviation
        df = self.add_std_lags(self.get_fertilizer_production,std_window=std_window,lags=lags)
        return df

    def natural_gas(self, std_window:int=48,lags:str='0'):
        """
        std_window: rolling standard deviation
        lags: multiple lags (comma separated i.e. 0,2,7 for no_lag, 2 months, 7 months)
        """
        # Adding Lags and Rolling Standard Deviation
        df = self.add_std_lags(self.get_naturalgas,std_window=std_window,lags=lags)
        return df

    def usdeur(self, std_window:int=48,lags:str='0'):
        """
        std_window: rolling standard deviation
        lags: multiple lags (comma separated i.e. 0,2,7 for no_lag, 2 months, 7 months)
        """
        # Adding Lags and Rolling Standard Deviation
        df = self.add_std_lags(self.get_usdeur,std_window=std_window,lags=lags)
        return df
    
    def fpi(self, std_window:int=48,lags:str='0'):
        """
        std_window: rolling standard deviation
        lags: multiple lags (comma separated i.e. 0,2,7 for no_lag, 2 months, 7 months)
        """
        # Adding Lags and Rolling Standard Deviation
        df = self.add_std_lags(self.get_fpi,std_window=std_window,lags=lags)
        return df
