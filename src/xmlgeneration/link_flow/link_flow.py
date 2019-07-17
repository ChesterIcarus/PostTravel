
from datetime import datetime
from typing import Dict, List, Tuple

from util.print_util import Printer as pr
from xmlgeneration.link_flow.linkflow_db_util import LinkFlowDatabaseHandle


class LinkFlow:

    def __init__(self, database=None):
        self.database = LinkFlowDatabaseHandle(database)

    def write_xml(self, bin_count, savepath, coords, time, silent=False):
        
        if not silent:
            pr.print('Beginning network link flow sampling.', time=True)
            pr.print(f'Finding nodes from ({coords[0]}, {coords[1]}) to '
                f'({coords[2]}, {coords[3]}).', time=True)

        nodes = self.database.find_nodes(*coords)

        if not silent:
            pr.print(f'Finding links from ({coords[0]}, {coords[1]}) to ' 
                f'({coords[2]}, {coords[3]}).', time=True)

        node_ids = tuple(node[0] for node in nodes)
        links = {link[0]: list(link) for link in self.database.find_links(node_ids)}

        if not silent:
            pr.print('Fetching extraneous nodes from link sample.', time=True)  

        node_ids = tuple(node for link in links for node in link[1:3])
        nodes = self.database.fetch_nodes(node_ids)

        bin_size = (time[1] - time[0]) / bin_count
        bins = [round(bin_size * i + time[0]) for i in range(bin_count)]
        bins.append(time[1])

        for i in range(bin_count):
            if not silent:
                pr.print(f'Fetching leg data from time {bins[i]} to {bins[i+1]}.',
                    time=True)
            legs = self.database.fetch_link_times(bins[i], bins[i+1], links.keys())
            for leg in legs:
                links[leg[0]][i+9] = leg[i]
            legs = []

        node_frmt = '<node id="%s" x="%s" y="%s"></node>'
        link_frmt = (
            '<link id="%s" from="%s" to="%s" length="%s" freespeed="%s" '
            'capacity="%s" permlanes="%s" oneway="%s" modes="%s"><attributes>' +
            ''.join([f'<attribute name="tbin{i}" class="java.lang.Integer">' 
                '%s</attribute>' for i in range(bin_count)]) +
            '</attributes></link>')

        if not silent:
            pr.print(f'Writing network sample at {savepath}.', time=True)

        n = 100000
        with open(savepath, 'w') as network:
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
            pr.print('Network link flow sampling complete.', time=True)
