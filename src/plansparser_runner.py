import json
from getpass import getpass

from xmlparsing.plans.plans_parser import PlansParser


CONFIG = 'TEST'

with open('PostTravel/src/xmlparsing/plans/config.json', 'r') as handle:
    params = json.load(handle)

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

parser = PlansParser(params['database'], params['encoding'])

for table in params['database']['tables'].keys():
    parser.database.create_table(table)

parser.parse(params['source_path'])

parser.database.alter_add_composite_PK('plans', 'agent_id')
