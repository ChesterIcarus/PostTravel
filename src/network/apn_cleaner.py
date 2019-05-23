import shapely as shp
import geopandas as gpd

import pandas as pd
import numpy as np
from util.db_util import DatabaseHandle

class ApnCleaner:
    def __init__(self):
        pass

    def to_centroids(self, apn_file: str, proj_crs: str=None):
        gdf = gpd.read_file(apn_file)
        gdf = gdf.dropna()
        gdf['geometry'] = gdf.centroid
        if proj_crs is not None:
            gdf = gdf.to_crs({'init': proj_crs})
        gdf['wkt'] = gdf.geometry.apply(lambda row: row.wkt)
        gdf['x'] = gdf.geometry.x
        gdf['y'] = gdf.geometry.y
        return gdf

    def to_sql(self, gdf: gpd.GeoDataFrame,
               db_handle: DatabaseHandle, table: str):
        db_handle.create_table(table)
        schema = db_handle.tables[table]['schema']
        fields = [field.split()[0] for field in schema[0:-1]]
        fields.append('wkt')
        db_handle.write_geom_rows(
            [tuple(row) for row in gdf[fields].values.tolist()], table)
