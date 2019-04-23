import json
from getpass import getpass

from simple_trips.handler import SimpleTripHandler


CONFIG = 'TEST'

if __name__ == "__main__":
    with open('PostTravel/src/simple_trips/config.json', 'r') as handle:
        params = json.load(handle)

    params = params[CONFIG]
    params['database']['password'] = getpass(
        f'Password for {params["database"]["user"]}: ')

    handler = SimpleTripHandler(params['database'], encode=params['encoding'])

    for table in ['legs', 'activities']:
        handler.database.create_table(table)

    handler.parse_plans(params['source_path'])

    # for index in params['database']['indexes']:
    #    handler.database.create_index(index['name'],
    #                                  index['columns'])
