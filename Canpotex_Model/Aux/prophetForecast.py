from prophet import Prophet
import pandas as pd

# The dataframe must has only 'ds' and 'y' as columns

n_future = 24 # total number of future forecasts
