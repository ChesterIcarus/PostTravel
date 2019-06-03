from typing import List, Dict, Tuple
import xml.etree.ElementTree as etree
from datetime import datetime
import numpy as np

from xmlparsing.events.eventsparse_db_util import EventsDatabaseHandle

class EventsParser:
    database: EventsDatabaseHandle = None

    def __init__(self, database=None):
        self.database = EventsDatabaseHandle(database)

    def parse(self, filepath, bin_size=1000000, silent=False, update=False):

        parser = etree.iterparse(filepath, events=('end','start'))
        parser = iter(parser)
        evt, root = next(parser)

        types: Tuple[str] = ('entered link', 'left link', 
            'PersonEntersVehicle', 'PersonLeavesVehicle')

        leg_evts: List[Tuple[int, str, int, int]] = list()
        veh_evts: List[Tuple[int, int, int, int]] = list()
        bin_count: int = 0
        total_count: int = 0

        if not silent:
            self.print(f'Beginning XML leg/vehicle event parsing from {filepath}.')

        if update:
            if not silent:
                self.print('Finding where we left off parsing last.')
            offset = self.database.get_leg_count()
            offset += self.database.get_veh_count()
            if not silent:
                self.print(f'Skipping to event {offset} of XML file.')

        for evt, elem in parser:
            if elem.tag == 'event' and evt == 'end':
                etype = elem.attrib['type']
                if update and etype in types:
                    bin_count += 1
                    total_count += 1
                    if bin_count >= bin_size:
                        root.clear()
                        bin_count = 0
                    if total_count == offset:
                        root.clear()
                        bin_count = 0
                        update = False
                        if not silent:
                            self.print('Event skipping complete.')
                            self.print('Resuming XML leg/vehicle event parsing')
                    continue

                if etype == 'entered link':
                    leg_evts.append((
                        int(elem.attrib['vehicle']),
                        elem.attrib['link'],
                        int(float(elem.attrib['time'])),
                        1
                    ))
                    bin_count += 1
                elif etype == 'left link':
                    leg_evts.append((
                        int(elem.attrib['vehicle']),
                        elem.attrib['link'],
                        int(float(elem.attrib['time'])),
                        0
                    ))
                    bin_count += 1
                elif etype == 'PersonEntersVehicle':
                    veh_evts.append((
                        int(elem.attrib['vehicle']),
                        int(elem.attrib['person']),
                        int(float(elem.attrib['time'])),
                        1
                    ))
                    bin_count += 1
                elif etype == 'PersonLeavesVehicle':
                    veh_evts.append((
                        int(elem.attrib['vehicle']),
                        int(elem.attrib['person']),
                        int(float(elem.attrib['time'])),
                        0
                    ))
                    bin_count += 1
                if bin_count >= bin_size:
                    if not silent:
                        self.print(f'Pushing {bin_count} events to SQL database.')
                    self.database.write_leg_evts(leg_evts)
                    self.database.write_veh_evts(veh_evts)
                    root.clear()
                    del leg_evts[:]
                    del veh_evts[:]
                    leg_evts = list()
                    veh_evts = list()
                    bin_count = 0
                    if not silent:
                        self.print(f'Resuming XML leg/vehicle event parsing.')

        if not silent:
            self.print(f'Pushing {bin_count} events to SQL database.')
        self.database.write_leg_evts(leg_evts)
        self.database.write_veh_evts(veh_evts)
        if not silent:
            self.print('XML leg/vehicle event parsing complete.')

    def print(self, string):
        time = datetime.now()
        return print('[' + time.strftime('%H:%M:%S:') + 
            ('000' + str(time.microsecond // 1000))[-3:] +
            ']\t' + string)
