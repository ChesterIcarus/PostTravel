from typing import List, Dict, T
from math import pi, sin, floor
from timeit import timeit
import os
import wget
import xarray as xr
from pyproj import Proj, transform, itransform

import pandas as pd
import numpy as np


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
        for i in range(len(paths)):
            if os.path.isfile(paths[i]) and not override:
                continue
            wget.download(urls[i], paths[i])
            fetched.append(paths[i])
        return fetched


    def read(self, files: List[str], concat=True) -> pd.DataFrame:
        ''' Read a list of DAYmet files in netCDF and convert to pandas DF,
        with the option of merging the tiles into a single dataframe '''
        df_list = list()
        for file_ in files:
            df = xr.open_dataset(file_).to_dataframe()
            df = df.dropna(subset=['tmax', 'yearday'], how='any')
            df = df.query('nv == 0')
            df = df.reset_index()
            df = df.drop(['x', 'y', 'nv',
                          'lambert_conformal_conic',
                          'time_bnds', 'time'], axis=1)
            if concat:
                df_list.append(df)
        if concat:
            return pd.concat(df_list)
        return df_list

    def project(self, temp: pd.DataFrame,
                in_proj: str, out_proj: str) -> pd.DataFrame:
        ''' Project coordinates in given DF to desired projection.
            in_proj and out_proj should both be strings of EPSG codes '''
        self.in_p = Proj(init=in_proj)
        self.out_p = Proj(init=out_proj)
        temp[['lon', 'lat']] = temp.apply(self.trans_df, axis=1)
        return temp

    def trans_df(self, row):
        ''' Function to be mapped to a dataframe to project coords'''
        row[['lon', 'lat']] = transform(self.in_p, self.out_p,
                                        row['lon'], row['lat'])
        return row[['lon', 'lat']]

    def bounding_calc(self):
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
        m_ = (row.at['tmax'] + row.at['tmin']) / 2
        w_ = (row.at['tmax'] - row.at['tmin']) / 2
        return m_ + (w_ * sin(times[row.at['step']]))
