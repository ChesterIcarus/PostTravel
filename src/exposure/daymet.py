from typing import List, Dict, T
import os
import wget
from math import sqrt
import pandas as pd
import numpy as np

import geopandas as gpd
from pyproj import Proj, transform, Transformer
from math import pi, sin, floor
from shapely.strtree import STRtree
import dask
import dask.dataframe as dd
import xarray as xr



class Daymet:

    def __init__(self):
        pass

    def fetch(self, tiles: List[int], url: str, override=False,
              out_dir:str='data/post_processing/') -> List[str]:
        ''' Fetches given DAYmet tile IDs from a given url and returns
        the paths to any files that were fetched '''
        url_temps = ['_2018/tmax.nc', '_2018/tmax.nc']
        temps = ['tmin', 'tmax']
        paths = [f'{out_dir}{tile}_{t_}.nc' for tile in tiles for t_ in temps]
        urls = [f'{url}{tile}{t_}' for tile in tiles for t_ in url_temps]
        fetched = list()
        for tile in tiles:
            for temp in temps:
                path = f'{out_dir}{tile}_{t_}.nc'
                pass

        for i in range(len(paths)):
            if os.path.isfile(paths[i]) and not override:
                continue
            wget.download(urls[i], paths[i])
            if 'tmin' in paths[i]:
                fetched.append({paths[i]})
        return fetched


    def read(self, files: List[str], yearday: int=219, concat=True) -> pd.DataFrame:
        ''' Read a list of DAYmet files in netCDF and convert to pandas DF,
        with the option of merging the tiles into a single dataframe '''
        main_df = pd.DataFrame()
        df_list = list()
        for file_ in files:
            df = xr.open_dataset(file_).to_dataframe()
            df = df.dropna(subset=['tmax', 'yearday'], how='any')
            df = df.query(f'nv == 0 & yearday == {yearday}')
            df = df.reset_index()
            df[['x', 'y']] = df[['lon', 'lat']]
            df = df.drop(['nv', 'time_bnds', 'time',
                          'lat', 'lon',
                          'lambert_conformal_conic'], axis=1)
            if concat:
                main_df = pd.concat([main_df, df], ignore_index=True)
            else:
                df_list.append(df)
        if concat:
            return main_df
        return df_list

    def nearest_approx(self, data: pd.DataFrame, orig_crs, new_crs):
        ''' Used for approximating neareast points for
        temperature points from raster.  Final value used in
        query of STR-tree as buffer value '''
        tformer = Transformer.from_proj(Proj(orig_crs), Proj(new_crs))
        bottom_left = data[['x', 'y']].head(1).values.tolist()[0]
        top_right = data[['x', 'y']].tail(1).values.tolist()[0]
        bottom_left = tformer.transform(bottom_left[1],bottom_left[0])
        top_right = tformer.transform(top_right[1], top_right[0])
        y_delta = top_right[0] - bottom_left[0]
        x_delta = top_right[1] - bottom_left[1]
        n_axis = sqrt(data.shape[0])
        points_on_hyp = sqrt((n_axis ** 2) + (n_axis ** 2))
        hyp_length = sqrt((x_delta ** 2) + (y_delta ** 2))
        avg_dist = hyp_length / ((points_on_hyp - 1) / 2)
        return avg_dist

    def project_df(self, data: pd.DataFrame, orig_crs: str, new_crs: str):
        gdf = gpd.GeoDataFrame(
            data, geometry=gpd.points_from_xy(data['x'], data['y']))
        gdf.crs = {'init': orig_crs}
        gdf = gdf.to_crs({'init': new_crs})
        gdf['x'] = gdf.geometry.x
        gdf['y'] = gdf.geometry.y
        return gdf

    def temp_assignment(self, temp: gpd.GeoDataFrame,
                        apns: gpd.GeoDataFrame, buffer: int):
        tree = STRtree(temp.geometry)


    def closest(self, row):
        pass

    def to_steps(self, steps: int, seconds: int,
                 temp: pd.DataFrame) -> pd.DataFrame:
        ''' Convert raw DAYmet to n-step interpolation. Step length is
            given in seconds '''
        hours = float(seconds) / (60.0 * 60.0)
        step_t = hours / float(steps)
        time_max = floor(hours / step_t)
        rad_calc = lambda hour: (pi * (hour - 6)) / 12
        times = [rad_calc(step) for step in
                 range(stop=time_max, step=step_t)]

        temp = temp.loc[temp.index.repeat(steps).reset_index(drop=True)]
        temp['step'] = temp.groupby(['tile_id','tmax', 'tmin']).cumcount()
        temp['time'] = temp.apply(lambda row: row['step'] * step_t)
        temp['curr_temp'] = 0
        temp.apply(lambda row: self.diurnal_approx(row, times))
        temp.drop(['tmax', 'tmin'], inplace=True)
        return temp


    def diurnal_approx(self, row: pd.Series, times: List[float]) -> float:
        ''' Formulae for Diurnal temperature approximiation
        as per 1984 paper'''
        m_ = (row.at['tmax'] + row.at['tmin']) / 2
        w_ = (row.at['tmax'] - row.at['tmin']) / 2
        return m_ + (w_ * sin(times[row.at['step']]))
