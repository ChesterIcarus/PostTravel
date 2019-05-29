from typing import List, Dict, Tuple
from xml.etree.ElementTree import iterparse
from datetime import datetime
import numpy as np

from xmlparsing.events.eventsparse_db_util import EventsDatabaseHandle

class EventParser:
    database: EventsDatabaseHandle = None
    filepath: str = None

    def __init__(self, database=None):
        self.database = EventsDatabaseHandle(database)

    def parse(self, filepath, bin_size=100000, silent=False):
        
        if not silent:
            self.print_time(f'Beginning XML leg event parsing from {filepath}.')

        start = []
        end = []

        bin_count = 0

        for evt, elem in iterparse(filepath, events=('end',)):
            if elem.tag == 'event':
                etype = elem.attrib['type']
                if etype == 'entered link':
                    start.append([                      # LEGS (UPDATE)
                        int(elem.attrib['time']),       # start_time
                        int(elem.attrib['person'])      # agent_id
                    ])
                    bin_count += 1
                elif etype == 'left link':
                    end.append([                        # LEGS (UPDATE)
                        int(elem.attrib['time']),       # end_time
                        int(elem.attrib['person'])      # agent_id
                    ])
                    bin_count += 1

                if bin_count >= bin_size:

                    if not silent:
                        self.print_time(f'Pushing {bin_count} legs to SQL server.')

                    self.database.update_legs(start, end)
                    start = []
                    end = []

                    if not silent:
                        self.print_time('Resuming XML leg event parsing.')

        if not silent:
            self.print_time(f'Pushing {bin_count} legs to SQL server.')
            
        self.database.update_legs(start, end)

        if not silent:
            self.print_time('Completed XML leg event parsing.')

        start = []
        end = []

    def print_time(self, string):
        time = datetime.now()
        return print('[' + time.strftime('%H:%M:%S:') + 
            ('000' + str(time.microsecond // 1000))[-3:] +
            ']\t' + string)