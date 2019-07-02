
from datetime import datetime
from typing import Dict, List, Tuple

from xmlgeneration.link_flow.linkflow_db_util import LinkFlowDatabaseHandle


class LinkFlow:

    def __init__(self, database=None):
        self.database = LinkFlowDatabaseHandle(database)

    def write_xml(self, savepath, bin_count, silent=False):
        
        elems: List = []
        bins: List = []
        nodes: Tuple = ()
        links: Dict = {}

        if not silent:
            self.print(f'Beginning network link flow generation to {savepath}.')
        elems.append('<?xml version="1.0" encoding="UTF-8"?>')
        elems.append('<!DOCTYPE network SYSTEM "http://www.matsim.org/files/dtd/network_v2.dtd">')
        elems.append('<network>')

        if not silent:
            self.print('Fetching network node data.')
        elems.append('<nodes>')
        nodes = self.database.fetch_nodes()
        node_frmt = '<node id="%s" x="%s" y="%s"></node>'
        if not silent:
            self.print('Processing node data into formatted xml.')
        for node in nodes:
            elems.append(node_frmt % node)
        nodes = ()
        elems.append('</nodes>')

        if not silent:
            self.print('Writing node data to xml file.')
        with open(savepath, 'w') as outfile:
            outfile.write(''.join(elems))
        elems = []
        
        if not silent:
            self.print('Fetching link network layout data.')
        network = self.database.fetch_links()
        links = {link[0]: list(link) + [0]*bin_count for link in network}

        if not silent:
            self.print('Fetching leg binnning information.')
        tmin, tmax = self.database.fetch_bounds()
        bin_size = (tmax - tmin) / bin_count
        bins = [round(bin_size * i + tmin) for i in range(bin_count)]
        bins.append(tmax)

        for i in range(bin_count):
            if not silent:
                self.print(f'Fetching leg data form time {bins[i]} to {bins[i+1]}.')
            times = self.database.fetch_link_times(bins[i], bins[i+1])
            if not silent:
                self.print('Updating and merging dictionaries.')
            for time in times:
                links[time[0]][i+9] = time[1]

        if not silent:
            self.print('Processing link data into formatted xml.')
        elems.append('<links>')
        link_frmt = ('<link id="%d" from="%d" to="%d" length="%d" freespeed="%d" ' +
            'capacity="%d" permlanes="%d" oneway="%d" modes="%s"><attributes>' +
            ''.join(['<attribute name="tbin' + str(i) + 
            '" class="java.lang.Integer">%d</attribute>' for i in range(bin_count)]) +
            '</attributes></link>')

        if not silent:
            self.print('Formatting and writing link data to xml.')

        i = 0
        with open(savepath, 'a') as outfile:
            for key in links:
                elems.append(link_frmt % tuple(links[key]))
                i += 1
                if i >= 100000:
                    outfile.write(''.join(elems))
                    outfile.flush()
                    elems = []
                    i = 0
            elems.append('</links>')
            elems.append('</network>')
            outfile.write(''.join(elems))
            outfile.flush()
            elems = []
            links = {}

        if not silent:
            self.print('Network link flow data generation complete.')



    def print(self, string):
        time = datetime.now()
        print('[' + time.strftime('%H:%M:%S:') + 
            ('000' + str(time.microsecond // 1000))[-3:] + '] ' + string)
