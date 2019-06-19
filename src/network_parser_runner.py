import json
from getpass import getpass

from xmlparsing.network.network_parser import NetworkParser

CONFIG = 'WORKSTATION'

with open('./xmlparsing/network/config.json') as handle:
    params = json.load(handle)

params = params[CONFIG]
params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

parser = NetworkParser(params['database'], params['encoding'])

for table in params['database']['tables'].keys():
    parser.database.create_table(table, True)

parser.parse(params['source_path'])
