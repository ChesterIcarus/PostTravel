import json

from events.handler import *

CONFIG = 'sample'

if __name__ == "__main__":
    with open('PostTravel/src/config/event_config.json', 'r') as handle:
        params = json.load(handle)

    params = params[CONFIG]
    example = ChrisFlow(simulation_seconds=60*60*24)

    # This will give us a pythonic representation of a MATsim network
    network = example.read_network(params['network_src'])

    # This wili write the network to a defined database
    # example.network_to_sql(network)

    flow = example.events_to_flow(params['event_src'], list(network.links),
                                  bins=params['flow_bins'], iter_size=250000)

    example.flow_to_csv(flow, params['flow_dest'])
