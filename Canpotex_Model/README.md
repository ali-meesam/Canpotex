Installation

Installing the environment and main packages

```
conda create -n cptx python=3.8

conda activate cptx

conda install -c anaconda jupyter

conda install -c anaconda scipy

conda install -c conda-forge statsmodels

conda install -c conda-forge pyarrow

conda install -c conda-forge fsspec

pip install -r requirements.txt
```

ADD TO PYTHON PATH FOR QUICK IMPORTS



AWS Setup / Access:
* https://nutrien.service-now.com/it?sys_kb_id=c98816361b6e7344c92dfc43cd4bcb01&id=kb_article_view&sysparm_rank=1&sysparm_tsqueryId=a921e8ad47bf9950526caf57746d4391
* From terminal
```
aws-azure-login

cat ~/.aws/credentials
```


AWS Roles:
* Insights-DataCitizen-Role
* Insights-DataCitizen-Restricted-Role


AWS S3 (buckets):
* insights-canpotex-datalake
* insights-canpotex-downloads-sandboxlz

Data Pipeline
* simple_data_pipeline (minimal transformation - no lag and standard deviation)
* trans_data_pipeline (full transformed data based on frequency, lags and rolling standard deviations)


Models
* Model versioning


Control Config
* Configuration file to pull model and corresponding data pipes for forecasting


Forecast Versioning
* Model result archiving for static dashboarding


Trigger Handlers
* Config file for thresholds

