import json
from getpass import getpass

from xmlgeneration.link_flow.link_flow import LinkFlow

CONFIG = 'WORKSTATION'

with open('./xmlgeneration/link_flow/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

generator = LinkFlow(params['database'])

generator.write_xml(params['bins'], params['save_path'], 
    params['coords'], params['time'])