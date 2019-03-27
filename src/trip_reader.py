import json
from getpass import getpass

from simple_trips.handler import SimpleTripHandler


CONFIG = 'TEST'

if __name__ == "__main__":
    with open('simple_trips/config.json', 'r') as handle:
        params = json.load(handle)

    params = params[CONFIG]
    params['database']['password'] = getpass(
        f'Password for {params["database"]["user"]}: ')

    handler = SimpleTripHandler(params['database'], encode=params['encoding'])

    handler.database.create_trip_table(params['database']['table'],
                                       params['database']['schema'])

    handler.parse_trips(params['trip_path'])

    for index in params['database']['indexes']:
        handler.database.create_index(index['name'],
                                      index['columns'])
