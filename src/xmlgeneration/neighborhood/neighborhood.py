
from typing import List, Tuple, Dict

from util.print_util import Printer as pr
from xmlgeneration.neighborhood.neighborhood_db_util import NeighborhoodDatabaseHandle


class Neighborhood:
    def __init__(self, database):
        self.database = NeighborhoodDatabaseHandle(database)

    def generate_neighborhood(self, network_path, events_path, 
        coords, time, silent=False):

        if not silent:
            pr.print('Beginning neighborhood simulation sampling.', time=True)
            pr.print(f'Finding nodes from ({coords[0]}, {coords[1]}) to '
                f'({coords[2]}, {coords[3]}).', time=True)

        nodes = self.database.find_nodes(*coords)

        if not silent:
            pr.print(f'Finding links from ({coords[0]}, {coords[1]}) to ' 
                f'({coords[2]}, {coords[3]}).', time=True)

        links = self.database.find_links(tuple(node[0] for node in nodes))

        if not silent:
            pr.print(f'Writing nodes and links to network file at ' 
                f'{network_path}.', time=True)

        node_frmt = '<node id="%d" x="%d" y="%d"></node>'
        link_frmt = ('<link id="%d" from="%d" to="%d" length="%d" freespeed="%d"'
            ' capacity="%d" permlanes="%d" oneway="%d" modes="%s"></link>')
        n = 100000
        with open(network_path, 'w') as network:
            network.write(
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<!DOCTYPE network SYSTEM "http://www.matsim.org/files/dtd/'
                'network_v2.dtd"><network><nodes>')
            for i in range(0, len(nodes), n):
                network.write(''.join([node_frmt % node for node in nodes[i:i+n]]))
                network.flush()
            network.write('</nodes><links>')
            for i in range(0, len(links), n):
                network.write(''.join([link_frmt % link for link in links[i:i+n]]))
                network.flush()
            network.write('</links></network>')

        if not silent:
            pr.print(f'Finding events occuring on network from {time[0]}'
                f' to {time[1]}.', time=True)

        legs = self.database.find_events(tuple(link[0] for link in links), * time)

        if not silent:
            pr.print(f'Writing leg events to events file at {events_path}.', time=True)

        leg_frmt = '<event time="%d" type="%s" vehicle="%d" link="%d"></event>'
        n = 100000
        with open(events_path, 'w') as events:
            events.write(
                '<?xml version="1.0" encoding="utf-8"?>'
                '<events version="1.0">')
            for i in range(0, len(legs), n):
                events.write(''.join([leg_frmt % (leg[0], 'entered link' if leg[1] 
                    else 'left_link', leg[2], leg[3]) for leg in legs[i:i+n]]))
                events.flush()
            events.write('</events>')

        if not silent:
            pr.print(f'Neighborhood sample generationg complete.', time=True)
