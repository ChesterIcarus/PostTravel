from typing import List, Dict, Tuple
from xml.etree.ElementTree import iterparse
from collections import namedtuple
import numpy as np

from xmlparsing.network.networkparse_db_util import NetworkDatabaseHandle

Link = namedtuple('Link', ['id_',
                           'source_node',
                           'terminal_node',
                           'length',
                           'freespeed',
                           'capacity',
                           'permenant_lanes',
                           'oneway',
                           'modes'])

Node = namedtuple('Node', ['id_',
                           'x_coord',
                           'y_coord'])

class NetworkParser:
    def __init__(self, database=None, encoding=None):
        self.database = NetworkDatabaseHandle(database)
        self.encoding = encoding

    def parse(self, filepath, coordsys=None, iter_size=250000):
        iter_ct = 0
        context = etree.iterparse(filepath, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)
        elem: etree.Element
        links = list()
        nodes = list()
        scope = None

        for event, elem in context:
            if event == 'start':
                if elem.tag == 'nodes':
                    scope = 'nodes'

                if elem.tag == 'links':
                    scope = 'links'

                if elem.tag == 'link':
                    links.append(
                        Link(int(elem.attrib['id']),
                             int(elem.attrib['from']),
                             int(elem.attrib['to']),
                             float(elem.attrib['length']),
                             float(elem.attrib['freespeed']),
                             float(elem.attrib['capacity']),
                             float(elemt.attrib['permenant_lanes']),
                             bool(int(elem.attrib['oneway'])),
                             str(elem.attrib['modes'])))

                if elem.tag == 'node':
                    nodes.append(
                        Node(int(elem.attrib['id']),
                             float(elem.attrib['x']),
                             float(elem.attrib['y'])))

                if iter_ct > iter_size:
                    if scope == 'nodes':
                        self.database.write_rows(nodes, 'network_nodes')
                        nodes = []

                    if scope == 'links':
                        self.database.write_rows(links, 'network_links')
                        links = []

                    root.clear()
                    iter_ct = 0

                iter_ct += 1

            if event == 'end':
                if elem.tag == 'nodes':
                    self.database.write_rows(nodes, 'network_nodes')
                    nodes = []
                    root.clear()

                if elem.tag == 'links':
                    self.database.write_rows(links, 'network_links')
                    links = []
                    root.clear()
