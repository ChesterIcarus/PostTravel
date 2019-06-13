import json
from getpass import getpass

from xmlparsing.plans.plans_parser import PlansParser

CONFIG = 'WORKSTATION'

with open('./xmlparsing/plans/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

parser = PlansParser(params['database'], params['encoding'])

for table in params['database']['tables'].keys():
    parser.database.create_table(table, True)

parser.parse(params['source_path'], silent=False)