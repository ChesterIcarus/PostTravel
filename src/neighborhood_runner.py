
import json
from getpass import getpass

from xmlgeneration.neighborhood.neighborhood import Neighborhood

CONFIG = 'WORKSTATION'

with open('./xmlgeneration/neighborhood/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

generator = Neighborhood(params['database'])

generator.generate_neighborhood(params['network_path'],
    params['events_path'], params['coords'], params['time'])
