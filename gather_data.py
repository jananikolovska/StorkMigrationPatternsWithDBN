'''
Script to add NDVI and METEO information to original dataset

Since the dataset we use is ~1035000 records,
and the weather API has an HOURLY and DAILY limits
this script was run multiple times in batches in order to process the whole dataset
'''
import pandas as pd
import os
import warnings
from utils.utils import add_NDVI_feature, add_weather_info
warnings.filterwarnings('ignore')

#ADD NDVI
data = pd.read_csv(os.path.join('data', 'StorkMigration.csv'))
data['timestamp'] = pd.to_datetime(data['timestamp'])
data = data[data['timestamp'] >= '2013-03-01']
data = add_NDVI_feature(data)

#ADD METEO DATA
#data = pd.read_csv('StorkMigrationWithNDVI.csv')
data['timestamp'] = pd.to_datetime(data['timestamp'])
print(data.shape)
data = add_weather_info(data[875671:])
#data.to_csv(os.path.join("data","FILENAME.csv"))
data.to_csv(os.path.join("data","StorkMigrationWithNDVIWeather-52.csv"))
print('Data to csv')
