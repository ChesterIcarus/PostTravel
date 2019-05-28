from typing import List, Dict, Tuple
from xml.etree.ElementTree import iterparse
import numpy as np

from xmlparsing.events.eventsparse_db_util import EventsDatabaseHandle

class EventParser:
    database: EventsDatabaseHandle = None
    filepath: str = None

    def __init__(self, database=None):
        self.database = EventsDatabaseHandle(database)

    def parse(self, filepath, bin_size=100000):
        
        start = []
        end = []

        bin_count = 0

        for evt, elem in iterparse(filepath, events=('end',)):
            if elem.tag == 'event':
                etype = elem.attrib['type']
                if etype == 'entered link':
                    start.append([
                        int(elem.attrib['time']),       # start_time
                        int(elem.attrib['person'])      # agent_id
                    ])
                    bin_count += 1
                elif etype == 'left link':
                    end.append([
                        int(elem.attrib['time']),       # end_time
                        int(elem.attrib['person'])      # agent_id
                    ])
                    bin_count += 1

                if bin_count >= bin_size:
                    self.database.update_legs(start, end)
                    start = []
                    end = []