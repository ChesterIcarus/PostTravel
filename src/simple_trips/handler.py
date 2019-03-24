from typing import List, Dict, Tuple, T
import xml.etree.ElementTree as etree
import numpy as np

from simple_trips.encoding import Encoder
from simple_trips.trip_db_util import DatabaseHandle


class SimpleTripHandler:
    ''' Trip handler but does NOT track agents routes'''
    filepath = None
    database: DatabaseHandle = None

    def __init__(self, database=None):
        self.database = DatabaseHandle(database)

    def parse_trips(self, filepath, bin_sz=10000):
        ''' Read trips from XML and put them into DB by AID and time of day'''
        # departures = np.zeros(bin_sz)
        # arrivals = np.zeros(bin_sz)

        # Departures and arrivals should fill up to len ~= bin_sz then be written
        # Depart_ct and arrive_ct keep track so no repeated call to `len`
        # Activity_ct and leg_ct are counters for acts and legs per person
        # person_id is set when we start and element w/ tag = `person`
        trips: List[Tuple[str, int, int, int, int]] = list()
        trip_ct = 0
        person_id: str = ''
        trip_id = 0
        plan_selected = False
        # Allow us to iteratively parse the XML document
        context = etree.iterparse(filepath, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)
        elem: etree.Element

        for event, elem in context:
            if event == 'start':
                if elem.tag == 'person':
                    person_id = elem.attrib['id']
                if elem.tag == 'plan':
                    if elem.attrib['selected'] != 'yes':
                        plan_selected = False
                    else:
                        plan_selected = True
                        trip_id = 0

            elif event == 'end':
                if plan_selected:
                    if elem.tag == 'plan':
                        if trip_ct > bin_sz:
                            # We need to write the current departures && arrivals to DB on intervals
                            self.database.write_trips(trips)
                            root.clear()
                            trip_ct = 0
                            trips = []

                    if elem.tag == 'leg':
                        depart, arrive = self.parse_leg(elem)
                        mode = Encoder.mode[elem.attrib['mode']]
                        trips.extend([
                            (person_id, trip_id, depart, 0, mode),
                            (person_id, trip_id, arrive, 1, mode)
                        ])
                        trip_id += 1
                        trip_ct += 2

    def parse_leg(self, elem: etree.Element):
        ''' Parse the departure and arrival time from a leg
        Return both as the integer-second repr of that value
        '''
        depart = elem.attrib['dep_time']
        dep_sec = ((int(depart[0:2]) * 60 * 60) +
                   (int(depart[3:5]) * 60) +
                   int(depart[6:8]))
        arrive = elem.attrib['trav_time']
        arr_sec = ((int(arrive[0:2]) * 60 * 60) +
                   (int(arrive[3:5]) * 60) +
                   int(arrive[6:8]))

        return (dep_sec, (arr_sec + dep_sec))
