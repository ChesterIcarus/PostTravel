from exposure.daymet import Daymet
import dask
import pandas as pd
import geopandas as gpd
import dask.dataframe as dd



fetch = False
read = True
project = True

base_url = 'https://thredds.daac.ornl.gov/thredds/' + \
    'fileServer/ornldaac/1328/tiles/2018/'
tiles = ['11014', '11015']
orig_crs = 'epsg:4326'
new_crs = 'epsg:2223'

daymet = Daymet()

if fetch:
    fetched = daymet.fetch(tiles, base_url)
    print(fetched)

else:
    fetched = None

if read:
    if fetched is None:
        fetched = ['data/post_processing/11014_tmin.nc']
                # 'data/post_processing/11014_tmax.nc',
                # 'data/post_processing/11015_tmin.nc',
                # 'data/post_processing/11015_tmax.nc']
    if project:
        data = daymet.read(fetched)
        data = daymet.project_df(data, orig_crs, new_crs)
        data.to_file('cleaned_tile_projected.gpkg', layer='tmin')
    else:
        data = gpd.read_file('cleaned_tile_projected.gpkg', layer='tmin')
    print(data.head())
    buffer = daymet.nearest_approx(data, orig_crs, new_crs)
