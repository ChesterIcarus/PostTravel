from typing import List, Dict, T
import os
import wget
import pandas as pd
import numpy as np

from pyproj import Proj, transform, Transformer
from math import pi, sin, floor
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
            df[['x_meter', 'y_meter']] = df[['x', 'y']]
            df['x_meter'] = pd.to_numeric(df['x_meter'], downcast='signed')
            df['y_meter'] = pd.to_numeric(df['y_meter'], downcast='signed')
            df[['x_proj', 'y_proj']] = df[['lat', 'lon']]
            df = df.drop(['nv', 'time_bnds', 'time',
                          'x', 'y', 'lat', 'lon',
                          'lambert_conformal_conic'], axis=1)
            if concat:
                df_list.append(df)
        if concat:
            return pd.concat(df_list)
        return df_list

    def project_from_sys(self, temp: pd.DataFrame,
                in_proj: str, out_proj: str) -> pd.DataFrame:
        ''' Project coordinates in given DF to desired projection.
            in_proj and out_proj should both be strings of EPSG codes '''
        in_p = Proj(init=in_proj)
        out_p = Proj(init=out_proj)
        tformer = Transformer.from_proj(in_p, out_p)
        points_proj = temp.apply(lambda row: tformer.transform(row['y_proj'],
                                                               row['x_proj']),
                                 axis=1)
        points_proj = pd.DataFrame(points_proj.values.tolist(),
                                   index=points_proj.index)
        temp['y_proj'] = points_proj[0]
        temp['x_proj'] = points_proj[1]
        return temp

    # def project_from_str(self, temp: pd.DataFrame, proj_str: str, n_split=8):
    #     proj = Proj(proj_str)
    #     with dask.config.set(scheduler='processes'):
    #         dd_temp = dd.from_pandas(temp, n_split)
    #         dd_proc = dd_temp.apply(lambda row:
    #                                 proj(row['y_proj'], row['x_proj']),
    #                                 axis=1, meta={'x': 'f8', 'y': 'f8'})
    #         points_proj = dd_proc.compute()
    #         points_proj = pd.DataFrame(points_proj.values.tolist(),
    #                                 index=points_proj.index)
    #         temp['y_proj'] = points_proj[0]
    #         temp['x_proj'] = points_proj[1]
    #         return temp

    def temp_by_bounds(self, temp: pd.DataFrame):
        diffs = {'x_proj': None, 'y_proj': None}
        for diff_ in diffs:
            values = temp[diff_].unique()
            values = pd.DataFrame(np.sort(values), columns=[diff_])
            diffs[diff_] = values.diff()

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
