import json
from getpass import getpass

from visualization.simple import SimpleVisualization

CONFIG = 'TEST'

if __name__ == "__main__":
    with open('simple_trips/config.json', 'r') as handle:
        params = json.load(handle)

    params = params[CONFIG]
    params['database']['password'] = getpass(
        f'Password for {params["database"]["user"]}: ')

    visual = SimpleVisualization(params['database'])

    data = visual.output_data(final_time=109200)
    visual.graph(data)
