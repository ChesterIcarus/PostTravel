import json
from getpass import getpass

from xmlparsing.events.events_parser import EventsParser

CONFIG = 'WORKSTATION'

with open('./xmlparsing/events/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

parser = EventsParser(params['database'])

# for table in params['database']['tables'].keys():
#     parser.database.create_table(table, True)

parser.parse(params['source_path'], silent=False, update=True)