import ee
import pandas as pd
import os
import calendar


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

