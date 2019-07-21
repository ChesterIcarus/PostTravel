
import json
from getpass import getpass

from xmlgeneration.maz_sim.maz_sim import MazSim

CONFIG = 'WORKSTATION'

with open('./xmlgeneration/maz_sim/config.json', 'r') as handle:
    params = json.load(handle)

params = params[CONFIG]

params['database']['password'] = getpass(
    f'Password for {params["database"]["user"]}: ')

generator = MazSim(params['database'])

generator.generate(params['savepath'], params['maz'])
