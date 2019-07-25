import json
from getpass import getpass

from xmlparsing.maz.maz import MazParser

CONFIG = 'WORKSTATION'

with open('./xmlparsing/maz/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

parser = MazParser(params['database'])

for table in params['database']['tables'].keys():
    parser.database.create_table(table, silent=True)

parser.parse(params['source_path'])