from typing import List, Dict, Tuple, T
import xml.etree.ElementTree as etree
import numpy as np

from simple_trips.trip_db_util import DatabaseHandle
from simple_trips import encoding


class SimpleTripHandler:
    ''' Trip handler but does NOT track agents routes'''
    filepath = None
    database: DatabaseHandle = None
    encode: Dict[str, int] = None

    def __init__(self, database=None, encode=None):
        self.database = DatabaseHandle(database)
        if isinstance(encode, dict):
            self.encode = encode
        elif encode is None:
            self.encode = encoding

    def time_to_sec(self, time_):
        ''' time_ is a string of the format HH:MM:SS '''
        time_ = time_.split(':')
        return ((int(time_[0]) * 60 * 60) +
                (int(time_[1]) * 60) +
                int(time_[2]))

    def parse_plans(self, filepath, bin_sz=100000):
        ''' Read trips from XML and put them into DB by AID and time of day'''
        # departures = np.zeros(bin_sz)
        # arrivals = np.zeros(bin_sz)

        # Departures and arrivals should fill up to len ~= bin_sz then be written
        # Depart_ct and arrive_ct keep track so no repeated call to `len`
        # Activity_ct and leg_ct are counters for acts and legs per person
        # person_id is set when we start and element w/ tag = `person`
        plan_selected = False
        legs: List[Tuple[int, int, int, int, int]] = list()
        acts: List[Tuple[int, int, int, int]] = list()
        person_id: str = ''
        plan_ct = 0
        act_ct = 0
        leg_ct = 0
        trav_time = 0
        mode = 0
        distance = 0
        # Allow us to iteratively parse the XML document
        context = etree.iterparse(filepath, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)
        elem: etree.Element

        for event, elem in context:
            if event == 'start':
                if elem.tag == 'person':
                    person_id = int(elem.attrib['id'])
                if elem.tag == 'plan':
                    if elem.attrib['selected'] != 'yes':
                        plan_selected = False
                    else:
                        plan_selected = True

            elif event == 'end':
                if plan_selected:
                    if elem.tag == 'plan':
                        act_ct = 0
                        leg_ct = 0
                        if plan_ct > bin_sz:
                            self.database.write_legs(legs)
                            self.database.write_acts(acts)
                            root.clear()
                            legs = []
                            acts = []

                    if elem.tag == 'leg':
                        trav_time = self.time_to_sec(elem.attrib['trav_time'])
                        mode = self.encode['mode'][elem.attrib['mode']]

                    if elem.tag == 'route':
                        distance = float(elem.attrib['distance'])
                        legs.append((person_id, leg_ct, trav_time,
                                     distance, mode))
                        leg_ct += 1

                    if elem.tag == 'activity':
                        end_time = self.time_to_sec(elem.attrib['trav_time'])
                        act_type = self.encode['activity'][elem.attrib['type']]
                        acts.append(person_id, act_ct, end_time, act_type)
                        act_ct += 1
        self.database.write_legs(legs)
        self.database.write_acts(acts)

    # def parse_leg(self, elem: etree.Element):
    #     ''' Parse the departure and arrival time from a leg
    #     Return both as the integer-second repr of that value
    #     '''
    #     depart = elem.attrib['dep_time'].split(':')

    #     dep_sec = ((int(depart[0]) * 60 * 60) +
    #                (int(depart[1]) * 60) +
    #                int(depart[2]))
    #     arrive = elem.attrib['trav_time'].split(':')
    #     arr_sec = ((int(arrive[0]) * 60 * 60) +
    #                (int(arrive[1]) * 60) +
    #                int(arrive[2]))
    #     return (dep_sec, (arr_sec + dep_sec))
