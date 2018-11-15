import xml.etree.ElementTree as etree
from collections import defaultdict
from typing import Dict, List

from network_agg import Network

# These activity types were throwing errors so I temporarily excluded them to get something working
EXCLUDED = ['experimentalPt1', 'pt interaction']


class OutputLinkFlow:
    ''' Turns MATsim output and MATsim network into flow over links'''

    def __init__(self):
        '''Default init method'''
        pass

    def flow(self, network, plans, name=''):
        ''' Mapping the total net flow across links, in hourly bins.
            network: str of filepath for xml MATsim network,
            plans: str of filepath for xml MATsim output,
            name: str for name of simulation, not required'''
        net_util = Network(network, name=name)
        for event, elem in etree.iterparse(plans, ['start']):
            if elem.tag == 'activity':
                if self.filter_type(elem):
                    activity_time = self.parse_time(elem, resolution='hour')
            if elem.tag == 'leg':
                links = self.parse_leg(elem)
                for link in links:
                    net_util.links[link].incr_flow(activity_time)
        return net_util

    def parse_time(self, element, resolution='hour'):
        ''' Parse the time of a given activity ending/starting.
            element: etree element representing an activity in MATsim xml output,
            resolution: DEFAULT=`hour`, options=(`second`).
                The resolution at which to report the time.'''
        act_atrb = element.attrib
        try:
            try:
                time_str = act_atrb['end_time']
            except KeyError:
                time_str = act_atrb['start_time']
        except KeyError:
            raise ValueError(element, print(
                '\nMissing end time for activity:', element.attrib))
        if resolution is 'hour':
            return int(time_str[0:2])
        if resolution is 'second':
            hr_int = int(time_str[0:2]) * 60 * 60
            min_int = int(time_str[3:5]) * 60
            sec_int = int(time_str[6:8])
            return (hr_int + min_int + sec_int)

    def parse_leg(self, element):
        ''' Parse the leg of a trip. If the leg has a route (> 2 links traversed),
            parse that as well. Return list of all link IDs used in leg.
            element: etree element representing a leg in MATsim xml output
        '''
        links_trav = list()
        try:
            route = list(element)[0]
            if not self.filter_type(route):
                return list()
        except IndexError:
            return list()

        r_atrb = route.attrib
        if route.text is None:
            links_trav = [r_atrb['start_link'], r_atrb['end_link']]
        else:
            links_trav = [_id.strip() for _id in route.text.split()]

        for index, value in enumerate(links_trav):
            try:
                links_trav[index] = int(value)
            except ValueError:
                pass
        return links_trav

    def filter_type(self, element):
        ''' Used to filter based on the excluded types defined in global scope.
            element: etree element of a leg/activity. Requires `type` to be
                in the dict returned from attrib, else KeyError will be raised.'''
        if element.attrib['type'] not in EXCLUDED:
            return True
        return False
