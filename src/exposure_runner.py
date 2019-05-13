from exposure.daymet import Daymet

fetch = False
read = True
project = True

daymet = Daymet()

if fetch:
    base_url = 'https://thredds.daac.ornl.gov/thredds/fileServer/ornldaac/1328/tiles/2018/'
    tiles = ['11194', '11195', '11014', '11015']
    fetched = daymet.fetch(tiles, base_url)
    print(fetched)

if read:
    files = ['data/post_processing/11014_tmin.nc']
             # 'data/post_processing/11014_tmax.nc',
             # 'data/post_processing/11015_tmin.nc',
             # 'data/post_processing/11015_tmax.nc']

    data = daymet.read(files)
    # data.to_csv('daymet_sample.csv')

    if project:
        data = daymet.project(data, 'EPSG:4326', 'EPSG:2223')
        data.to_csv('proj_sample.csv')
