from network.apn_cleaner import ApnCleaner
from util.db_util import DatabaseHandle
import geopandas as gpd
from getpass import getpass
import json


with open('PostTravel/src/config/test_exposure_config.json') as handle:
    config = json.load(handle)['sample']


cleaner = ApnCleaner()
# data = cleaner.to_centroids(config['parcels']['path'],
#                             config['parcels']['project_to'])
# data.to_file('centroid_projected_apns.gpkg', layer='parcels', driver='GPKG')
# data[0:100].to_file('centroid_projected_apns_sample.gpkg',
#                     layer='parcels', driver='GPKG')
# print(data.head())
db_param = config['database']
db_param['password'] = getpass(
    f'MySQL password for user {db_param["user"]}: ')
db = DatabaseHandle(params=db_param)
data = gpd.read_file('centroid_projected_apns.gpkg', layer='parcels')
cleaner.to_sql(data, db, 'apn')
