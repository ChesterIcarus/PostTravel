from exposure.daymet import Daymet
import dask
import json
import pandas as pd
import geopandas as gpd
import dask.dataframe as dd



fetch = False
read = True
project = True

with open('PostTravel/src/config/test_exposure_config.json') as handle:
    config = json.load(handle)


daymet = Daymet()

if fetch:
    fetched = daymet.fetch(tiles, base_url)
    print(fetched)

else:
    fetched = None

if read:
    if fetched is None:
        fetched = ['data/post_processing/11014_tmin.nc']

    if project:
        data = daymet.read(fetched)
        data = daymet.project_df(data, orig_crs, new_crs)
        data.to_file('cleaned_tile_projected.gpkg', layer='tmin')
    else:
        data = gpd.read_file('cleaned_tile_projected.gpkg', layer='tmin')
    print(data.head())
    buffer = daymet.nearest_approx(data, orig_crs, new_crs)
