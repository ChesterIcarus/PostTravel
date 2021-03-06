import json
from getpass import getpass

from visualization.charts.charts import ChartsVisualization

CONFIG = 'WORKSTATION'

with open('./visualization/charts/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

visualizer = ChartsVisualization(params['database'])

visualizer.graph(params['graphs'], params['savepath'])