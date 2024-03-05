import pandas as pd
import os
import warnings
from utils.utils import add_NDVI_feature, add_weather_info
warnings.filterwarnings('ignore')

#ADD NDVI
# data = pd.read_csv(os.path.join('data', 'StorkMigration.csv'))
# data['timestamp'] = pd.to_datetime(data['timestamp'])
# data = data[data['timestamp'] >= '2013-03-01']
# data = add_NDVI_feature(data)

data = pd.read_csv('StorkMigrationWithNDVI.csv')
data['timestamp'] = pd.to_datetime(data['timestamp'])
print(data.shape)
data = add_weather_info(data[211779:])
data.to_csv(os.path.join("data","StorkMigrationWithNDVIWeather-15.csv"))
print('Data to csv')