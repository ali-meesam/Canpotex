import os 
import pandas as pd

class DataFeed:
    def __init__(self) -> None:
        self.src = "DataFeeds"
        

    @property
    def get_eurusd(self):
        file_name = 'EURUSD=X.csv'
        src_file = os.path.join(self.src,file_name)
        return pd.read_csv(src_file,index_col=0, parse_dates=True)

    @property
    def get_food_price_index(self):
        file_name = 'FoodPriceIndex_FAO.xlsx'
        src_file = os.path.join(self.src,file_name)
        return pd.read_excel(src_file,index_col=0, parse_dates=True)
