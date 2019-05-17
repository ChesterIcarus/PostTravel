from exposure.daymet import Daymet
import dask
import pandas as pd
import dask.dataframe as dd

fetch = False
read = True
project = True
proj_str = ('+proj=tmerc +lat_0=31 +lon_0=-111.9166666666667 ' +
            '+k=0.9999 +x_0=213360 +y_0=0 +ellps=GRS80 ' +
            '+datum=NAD83 +to_meter=0.3048 +no_defs')

daymet = Daymet()

if fetch:
    base_url = 'https://thredds.daac.ornl.gov/thredds/fileServer/ornldaac/1328/tiles/2018/'
    # tiles = ['11194', '11195', '11014', '11015']
    tiles = ['11014', '11015']
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

    data = daymet.read(fetched)
    # data.to_csv('daymet_sample_small.csv', index_label='index')
    # with dask.config.set(scheduler='processes'):
    #     dd_proc = dd.read_csv('daymet_sample.csv',
    #                           blocksize=1000000)
    # data = dd_proc.compute()

    if project:

        data = daymet.project_from_sys(data, 'EPSG:4326', 'EPSG:2223')
        diff_ = data[['x_proj', 'y_proj', 'x_meter', 'y_meter']].diff()
        diff_.to_csv('diff_sample.csv', index_label='index')
        # data = daymet.project_from_str(data, proj_str, n_split=2)
        data.to_csv('proj_sample.csv', index_label='index')
        # daymet.bounding_calc(data)
