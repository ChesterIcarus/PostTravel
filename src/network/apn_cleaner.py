import shapely as shp
import geopandas as gpd

import pandas as pd
import numpy as np

class ApnCleaner:
    def __init__(self):
        pass

    def to_centroids(self, apn_file: str, proj_crs: str=None):
        gdf = gpd.read_file(apn_file)
        gdf = gdf.dropna()
        cents = gdf.centroid
        if proj_crs is not None:
            cents = cents.to_crs({'init': proj_crs})
        return cents

