import json
from getpass import getpass

from xmlparsing.plans.plans_parser import PlansParser
from util.print_util import Printer as pr

CONFIG = 'WORKSTATION'

with open('./xmlparsing/plans/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]
database = params['database']

database['password'] = getpass(
    f'Password for {database["user"]}: ')

parser = PlansParser(database, params['encoding'])

pr.print('Resetting tables for parsing.', time=True)
for table in database['tables'].keys():
    parser.database.create_table(table, True)

pr.print(f'Beginning XML agent plan parsing from {params["source_path"]}.', time=True)
parser.parse(params['source_path'])

pr.print('Starting index creation.', time=True)
for name, table in database['tables'].items():
    if hasattr(table, 'comp_PK'):
        pr.print(f'Creating primary key on table "{name}".', time=True)
        parser.database.alter_add_composite_PK(name)
    if hasattr(table, 'idx'):
        for idx in table['idx']:
            pr.print(f'Creating index on table "{name}".', time=True)
            
    if hasattr(table, 'spatial_idx'):
        for idx in table['spatial_idx'].keys():
            pr.print(f'Creating spatial index on table "{name}".', time=True)
            parser.database.create_spatial_index(name, idx)