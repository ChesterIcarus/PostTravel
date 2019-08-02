import json
from getpass import getpass

from util.print_util import Printer as pr
from xmlparsing.events.events_parser import EventsParser

CONFIG = 'WORKSTATION'

with open('./xmlparsing/events/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

parser = EventsParser(params['database'])

if not params['resume']:
    for table in params['database']['tables'].keys():
        parser.database.create_table(table, True)

pr.print('Beginning XML leg/vehicle event parsing '
         f'from {params["source_path"]}.', time=True)
parser.parse(params['source_path'], resume=params['resume'])
