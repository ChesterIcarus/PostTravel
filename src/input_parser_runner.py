import json
from getpass import getpass

from xmlparsing.input.input_parser import InputParser

CONFIG = 'WORKSTATION'

with open('./xmlparsing/input/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

parser = InputParser(params['database'], params['encoding'])

for table in params['database']['tables'].keys():
    parser.database.create_table(table, True)

parser.parse(params['source_path'], silent=False)