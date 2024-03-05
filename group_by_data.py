import pandas as pd
import os
import glob
import numpy as np
from utils.utils import group_weekly
import warnings
warnings.filterwarnings('ignore')

"""
For example, a threshold of 500 kilometers within a week 
might capture significant migratory movements while accommodating 
variations in individual behavior and environmental conditions
"""

concatenated_df = pd.DataFrame()

# Iterate over files in the folder
for file_path in glob.glob(os.path.join('data', 'StorkMigrationWithNDVIWeather*.csv')):
    data = pd.read_csv(file_path)
    if 'Unnamed: 0' in data.columns:
        data = data.drop(['Unnamed: 0'],axis=1)
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    result_data = group_weekly(data)
    concatenated_df = pd.concat([concatenated_df, result_data])

print(concatenated_df.shape)
concatenated_df.to_csv(os.path.join('data','GrouppedByData.csv'))

