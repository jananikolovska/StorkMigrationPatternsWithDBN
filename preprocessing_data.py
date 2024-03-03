import ee
import pandas as pd
import os
import calendar
from utils.utils import add_NDVI_feature

#ADD NDVI
data = pd.read_csv(os.path.join('data', 'StorkMigration.csv'))
data['timestamp'] = pd.to_datetime(data['timestamp'])
data = data[data['timestamp'] >= '2013-03-01']
data = add_NDVI_feature(data)





