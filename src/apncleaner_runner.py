from network.apn_cleaner import ApnCleaner


orig_crs = 'epsg:4326'
new_crs = 'epsg:2223'
parcel_path = 'data/mag_to_matsim_required_aux/Parcels_All/Parcels_All.shp'

cleaner = ApnCleaner()
data = cleaner.to_centroids(parcel_path, new_crs)
data.to_file('centroid_projected_apns.gpkg', layer='apn', driver='GPKG')
