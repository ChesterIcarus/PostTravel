import json
from getpass import getpass

from visualization.stats.stats import StatsVisual

CONFIG = 'WORKSTATION'

with open('./visualization/stats/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

visualizer = StatsVisual(params['database'])
visualizer.activity(silent=False)