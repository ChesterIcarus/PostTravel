from collections import namedtuple, defaultdict
import xml.etree.ElementTree as etree
from typing import List
from math import floor
import csv

Node = namedtuple('Node', ['id', 'x', 'y'])
Link = namedtuple('Link', ['id', 'node1', 'node2', 'length'])
Network = namedtuple('Network', ['name', 'coordsys', 'nodes', 'links'])
LinkFlow = namedtuple('LinkFlow', ['id', 'bins'])
Flow = namedtuple('Flow', ['bins', 'link_flow'])

class ChrisFlow:
    simulation_seconds = None
    sec_per_bin = None
    def __init__(self, simulation_seconds=60*60*24):
        self.simulation_seconds = simulation_seconds
        self.sec_per_bin = None

    def read_network(self, filepath,
                     name=None, coordsys=None, iter_size=250000) -> Network:
        network = Network(filepath if name is None else name,
                          coordsys, dict(), dict())
        iter_ct = 0
        context = etree.iterparse(filepath, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)
        elem: etree.Element

        for event, elem in context:
            if event == 'start':
                if elem.tag == 'link':
                    id_ = elem.attrib['id']
                    network.links[id_] = Link(id_,
                                              elem.attrib['from'],
                                              elem.attrib['to'],
                                              elem.attrib['length'])
                if elem.tag == 'node':
                    id_ = elem.attrib['id']
                    network.nodes[id_] = Node(id_, elem.attrib['x'],
                                              elem.attrib['y'])
                if iter_ct > iter_size:
                    root.clear()
                    iter_ct = 0
                iter_ct += 1
        return network

    def network_to_sql(self, network: Network):
        pass


    def events_to_flow(self, filepath, links: List[str],
                       bins=24,iter_size=250000, drop_unused=True):
        ''' Read MATsim event XML file output and calculate flow '''
        bins = int(bins)
        self.sec_per_bin = floor(self.simulation_seconds / bins)
        flow = Flow(bins, {link: LinkFlow(link, [0]*bins) for link in links})
        if drop_unused:
            untouched_links = set(links)
        iter_ct = 0
        # Allow us to iteratively parse the XML document
        context = etree.iterparse(filepath, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)
        elem: etree.Element

        for event, elem in context:
            if event == 'start' and elem.tag == 'event':
                iter_ct += 1
                if elem.attrib['type'] == 'entered link':
                    id_ = elem.attrib['link']
                    if drop_unused:
                        untouched_links.discard(id_)
                    bin_ = self.time_bin_index(elem.attrib['time'])
                    flow.link_flow[id_].bins[bin_] += 1
                if iter_ct > iter_size:
                    root.clear()
                    iter_ct = 0
        if drop_unused:
            for link in untouched_links:
                flow.link_flow.pop(link)
        return flow

    def time_bin_index(self, time_str) -> int:
        return int(floor(float(time_str) / self.sec_per_bin))


    def flow_to_csv(self, flow: Flow, dest: str):
        header = f'''link_id,{
            (",").join([f"hour_{x}" for x in range(flow.bins)])}'''
        with open(dest, 'w+') as handle:
            f_writer = csv.writer(handle)
            for link in list(flow.link_flow.values()):
                f_writer.writerow((link.id, *link.bins,))
