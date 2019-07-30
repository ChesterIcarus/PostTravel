
from getpass import getpass
from xmlparsing.apn.apn import ParcelParser
import json

CONFIG = 'WORKSTATION'

with open('./xmlparsing/apn/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

parser = ParcelParser(params['database'])

if not params['resume']:
    for table in params['database']['tables'].keys():
        parser.database.create_table(table, True)

parser.parse(params['source_path'], resume=params['resume'])
