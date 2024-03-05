import ee
import pandas as pd
import os
import calendar
from geopy.distance import geodesic
import numpy as np
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def connect_googleengine():
    # Authenticate to the Earth Engine servers.
    ee.Authenticate()

    # Initialize the Earth Engine library.
    ee.Initialize()


def get_date_range(date):
    first_day = f"{date.year}-{date.month:02d}-01"
    last_day = f"{date.year}-{date.month:02d}-{calendar.monthrange(date.year, date.month)[1]}"
    return first_day, last_day


# Define a function to calculate NDVI
def meanNDVICollection(img):
    nir = img.select('B5')
    red = img.select('B4')
    ndviImage = nir.subtract(red).divide(nir.add(red)).rename('NDVI')

    # Compute the mean of NDVI over the region
    ndviValue = ndviImage.reduceRegion(**{
        'geometry': point,
        'reducer': ee.Reducer.mean(),
        'scale': 30  # Set the scale according to the resolution of Landsat data
    }).get('NDVI')

    newFeature = ee.Feature(None, {
        'NDVI': ndviValue
    }).copyProperties(img, [
        'system:time_start',
        'SUN_ELEVATION'
    ])

    return newFeature


def add_NDVI_feature(data):
    ndvis = []
    cache_ndvi = dict()
    for ind, row in data.iterrows():
        print(f'Now calculating for row {ind}')

        # Define a region of interest (ROI) as a point
        point = ee.Geometry.Point(
            [row['location-long'], row['location-lat']])  # Example coordinates (longitude, latitude)

        # Load Landsat data
        print(row['timestamp'])
        time_range = get_date_range(row['timestamp'])
        print(time_range[0])
        print(time_range[1])
        if not time_range[0] in cache_ndvi:
            landsat = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
                .filterBounds(point) \
                .filterDate(time_range[0], time_range[1]) \
                .first()

            # Calculate NDVI for the Landsat image
            result = meanNDVICollection(landsat)
            cache_ndvi[time_range[0]] = round(result.getInfo()['properties']['NDVI'], 4)
        ndvis.append(cache_ndvi[time_range[0]])
    print('Full data itterated. New feature -NDVI- added.')
    data['NDVI'] = ndvis
    return data


def add_weather_info(data):
    entries = []
    cache = dict()
    count_requests = 0
    for ind, row in data.iterrows():
        print(f'Now calculating for row {ind}')
        # Truncate the timestamp to hours
        timestamp_utc_truncated = row['timestamp'].tz_localize('UTC').tz_convert('UTC').floor('H')
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": row['location-long'],
            "longitude": row['location-lat'],
            "start_date": row['timestamp'].strftime('%Y-%m-%d'),
            "end_date": row['timestamp'].strftime('%Y-%m-%d'),
            "hourly": ["temperature_2m", "relative_humidity_2m", "rain", "surface_pressure", "cloud_cover",
                       "wind_speed_100m"]
        }
        cache_key = f"{round(row['location-long'],2)} {round(row['location-lat'],2)} {row['timestamp'].strftime('%Y-%m-%d')}"
        print(cache_key)
        try:
            if cache_key in cache:
                response = cache[cache_key]
            else:
                responses = openmeteo.weather_api(url, params=params)
                print('-----Request for API')
                count_requests +=1
                response = responses[0]
                cache[cache_key] =  response

            # Process hourly data. The order of variables needs to be the same as requested.
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
            hourly_rain = hourly.Variables(2).ValuesAsNumpy()
            hourly_surface_pressure = hourly.Variables(3).ValuesAsNumpy()
            hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
            hourly_wind_speed_100m = hourly.Variables(5).ValuesAsNumpy()

            hourly_data = {"date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )}
            hourly_data["temperature_2m"] = hourly_temperature_2m
            hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
            hourly_data["rain"] = hourly_rain
            hourly_data["surface_pressure"] = hourly_surface_pressure
            hourly_data["cloud_cover"] = hourly_cloud_cover
            hourly_data["wind_speed_100m"] = hourly_wind_speed_100m

            hourly_dataframe = pd.DataFrame(data=hourly_data)
            selected_dataframe = hourly_dataframe[hourly_dataframe['date'] == timestamp_utc_truncated]
            selected_dataframe = selected_dataframe.drop(['date'], axis=1)

            # Append the selected_dataframe to the new_row
            new_row = pd.concat([row, selected_dataframe.iloc[0]], axis=0)

            # Update the row in the DataFrame
            entries.append(new_row)
        except Exception as e:
            print(e)
            print(f'Last index processed {ind}')
            break

    new_data = pd.DataFrame.from_records(entries)
    new_data = new_data.drop(["Unnamed: 0.1", "Unnamed: 0"], axis=1)

    print(f'Number of requests to Open-Meteo API {count_requests}')
    return new_data

def calculate_distance(row, data):
    if row.name == 0:
        # If it's the first row, return NaN or skip the computation
        return np.nan  # For example, return NaN as distance
    else:
        prev_row = data.iloc[row.name - 1]
        prev_location = (prev_row['location-lat'], prev_row['location-long'])
        curr_location = (row['location-lat'], row['location-long'])
        return geodesic(prev_location, curr_location).kilometers

def last_location(values):
    return values.iloc[-1]

def group_weekly(data):
    concatenated_df = pd.DataFrame()
    print(len(list(set(data['tag-local-identifier']))))
    for selected_id in list(set(data['tag-local-identifier'])):
        print(selected_id)
        selected_data = data[data['tag-local-identifier'] == selected_id].reset_index(drop=True)
        print(selected_data.shape)

        # Order DataFrame by 'timestamp'
        selected_data.sort_values(by='timestamp', inplace=True)

        selected_data['distance-flown'] = selected_data.apply(lambda row: calculate_distance(row, selected_data),
                                                                 axis=1)

        selected_data = selected_data.dropna()
        result = (selected_data.groupby(['tag-local-identifier', pd.Grouper(key='timestamp', freq='W-MON')])
                  .agg({'NDVI': 'mean', 'temperature_2m': 'mean',
                        'relative_humidity_2m': 'mean', 'rain': 'mean',
                        'surface_pressure': 'mean', 'cloud_cover': 'mean',
                        'wind_speed_100m': 'mean', 'distance-flown': 'sum',
                        'location-lat': last_location,
                        'location-long': last_location})
                  .reset_index())
        result['distance-traveled'] = result.apply(lambda row: calculate_distance(row, result),
                                                              axis=1)
        concatenated_df = pd.concat([concatenated_df, result])
    #concatenated_df['distance_traveled_discretized'] = pd.cut(concatenated_df['distance-traveled'], bins=3,
    #                                                          labels=[0, 1, 2])
    print(concatenated_df.shape)
    return concatenated_df

