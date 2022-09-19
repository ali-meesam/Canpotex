from datapipeline import DataFeed
import os
import pandas as pd
from datetime import datetime
from models import ActualNetback
import matplotlib.pyplot as plt
plt.style.use('dark_background')

ben_comp = pd.read_excel("DataFeeds/Ben_Predictions.xlsx",index_col=0,parse_dates=True)

self = DataFeed()
brazil = self.get_BrazilCFR
seasia = self.get_SEAsiaCFR
foodpriceindex = self.get_food_price_index
eurusd = self.get_eurusd
cpi = self.get_g20_cpi
gdp = self.get_gdp
netback = self.get_historical_netback
minenetback = self.get_historical_mineNetback
naturalgas = self.get_natural_gas
ethanol = self.get_ethanol
fertilizerprod = self.get_total_fertilizer_production
freightcost = self.get_freightCost
interim = self.get_interimPricing

brazil.dropna(inplace=True)
seasia.dropna(inplace=True)
foodpriceindex.dropna(inplace=True)
eurusd.dropna(inplace=True)
cpi.dropna(inplace=True)
gdp.dropna(inplace=True)
netback.dropna(inplace=True)
minenetback.dropna(inplace=True)
naturalgas.dropna(inplace=True)
ethanol.dropna(inplace=True)
fertilizerprod.dropna(inplace=True)
freightcost.dropna(inplace=True)
interim.dropna(inplace=True)

_vars = [brazil,seasia,foodpriceindex,eurusd,cpi,gdp,netback,minenetback,naturalgas,ethanol,fertilizerprod,freightcost,interim]

counts = [v.iloc[0].name for v in _vars]

# GET THE SMALLEST DATA SET
times = _vars[counts.index(max(counts))].index.tolist()



curr_month = 7
curr_year = 2022

m = ActualNetback()

predictions = []
for t in times:
    month = t.month
    year = t.year
    if year==curr_year:
        if month<=curr_month:
            predictions.append([year,month,m.predict(month,year)])
    else:
        predictions.append([year,month,m.predict(month,year)])

netback_comparison = pd.DataFrame(predictions,columns=['Year','Month','Prediction'])
netback_comparison['Interim']= interim[-len(netback_comparison):].InterimPricing.values

# No need to shift since actual is realized by month end
# netback_comparison['Prediction'] = netback_comparison.Prediction.shift(1)

netback_comparison['Actual'] = netback[-len(netback_comparison):]['Netback ($/tonne)'].values

netback_comparison['BenPrediction'] = ben_comp.iloc[-len(netback_comparison):].values

netback_comparison[['Prediction','Actual','Interim','BenPrediction']].plot()

netback_comparison['Err-Prediction-Actual'] = (netback_comparison['Actual']/netback_comparison['Prediction']-1)*100
netback_comparison['Err-Interim-Actual'] = (netback_comparison['Actual']/netback_comparison['Interim']-1)*100
netback_comparison['Err-Ben-Actual'] = (netback_comparison['Actual']/netback_comparison['BenPrediction']-1)*100

print(netback_comparison)

abs(netback_comparison[['Err-Prediction-Actual','Err-Interim-Actual','Err-Ben-Actual']]).plot(kind='bar',title='Error Comparison')
plt.show()
abs(netback_comparison[['Err-Prediction-Actual','Err-Interim-Actual','Err-Ben-Actual']]).plot(kind='kde',title='Error Comparison')
plt.show()
