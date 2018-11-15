import xml.etree.ElementTree as etree
from typing import List, Dict, T
import csv


class LinkFlow:
    ''' Link object. Holds a bin for each time segment denoted. Used
        to store flow over a link throughout a simulation'''
    link_id: str = None
    time: List[int] = list()

    def __init__(self, link_id, time=24):
        self.link_id = link_id
        self.time = [0] * time

    def incr_flow(self, time):
        self.time[time] += 1


class Network:
    ''' Metadata object for a MATsim xml Network. Processes the links,
        writes to csv. Class methods to be expanded in the future.'''
    name: str = None
    simulation_hours: int = 24
    links: Dict[T, LinkFlow] = {}

    def __init__(self, filepath, name=''):
        ''' Reads a MATsim network, and creates LinkFlow objects for each link
            filepath: path to well-formed MATsim xml network'''
        self.name = name
        net = etree.parse(filepath)
        root = net.getroot()
        for link in root.iter('link'):
            try:
                _id = int(link.attrib['id'])
            except ValueError:
                _id = link.attrib['id']
            self.links[_id] = LinkFlow(_id, time=self.simulation_hours)

    def to_csv(self, filepath):
        ''' Writes the contents of links to a csv file.
            filepath: path to write csv file'''
        with open(filepath, 'w+') as handle:
            wr_ = csv.writer(handle)
            wr_.writerow(['link_id', 'time', 'flow', 'pct_of_total'])
            for _id, link in self.links.items():
                for step, flow in enumerate(link.time):
                    wr_.writerow([_id, step, flow, 0.0])
