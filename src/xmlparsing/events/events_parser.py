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
        links: Dict[str: int] = {}

        leg_evts: List[Tuple[int, str, int, int]] = list()
        veh_evts: List[Tuple[int, int, int, int]] = list()
        leg_id: int = 0
        veh_id: int = 0
        bin_count: int = 0
        total_count: int = 0

        if not silent:
            self.print(f'Beginning XML leg/vehicle event parsing from {filepath}.')
            self.print('Fetching network link data.')
        links = dict(self.database.fetch_network())
        if not silent:
            self.print('Network link data fetch completed.')

        if update:
            if not silent:
                self.print('Finding where we left off parsing last.')
            leg_id = self.database.get_leg_count()
            veh_id = self.database.get_veh_count()
            offset = leg_id + veh_id
            if not silent:
                self.print(f'Skipping to event {offset} of XML file.')
                print(f'\033[1mTotal events parsed: {total_count}\033[0m', end='\r')
        elif not silent:
            self.print('Resuming XML leg/vehicle event parsing.')
            print(f'\033[1mTotal events parsed: {total_count}\033[0m', end='\r')

        for evt, elem in parser:
            if elem.tag == 'event' and evt == 'end':
                etype = elem.attrib['type']

                if update and etype in types:
                    bin_count += 1
                    total_count += 1
                    if bin_count >= bin_size:
                        root.clear()
                        bin_count = 0
                        if not silent:
                            self.print(f'Skipped to event {total_count}.')
                            print(f'\033[1mTotal events parsed: {total_count}\033[0m', end='\r')
                    if total_count == offset:
                        root.clear()
                        bin_count = 0
                        update = False
                        if not silent:
                            self.print(f'Skipped to event {total_count}.')
                            self.print('Event skipping complete.')
                            self.print('Resuming XML leg/vehicle event parsing.')
                            print(f'\033[1mTotal events parsed: {total_count}\033[0m', end='\r')
                    continue

                if etype == 'entered link':
                    leg_evts.append((
                        leg_id,
                        int(elem.attrib['vehicle']),
                        None,
                        links[elem.attrib['link']],
                        elem.attrib['link'],
                        int(float(elem.attrib['time'])),
                        1
                    ))
                    bin_count += 1
                    leg_id += 1
                elif etype == 'left link':
                    leg_evts.append((
                        leg_id,
                        int(elem.attrib['vehicle']),
                        None,
                        links[elem.attrib['link']],
                        elem.attrib['link'],
                        int(float(elem.attrib['time'])),
                        0
                    ))
                    bin_count += 1
                    leg_id += 1
                elif etype == 'PersonEntersVehicle':
                    veh_evts.append((
                        veh_id,
                        int(elem.attrib['vehicle']),
                        int(elem.attrib['person']),
                        int(float(elem.attrib['time'])),
                        1
                    ))
                    bin_count += 1
                    veh_id += 1
                elif etype == 'PersonLeavesVehicle':
                    veh_evts.append((
                        veh_id,
                        int(elem.attrib['vehicle']),
                        int(elem.attrib['person']),
                        int(float(elem.attrib['time'])),
                        0
                    ))
                    bin_count += 1
                    veh_id += 1

                if bin_count >= bin_size:
                    total_count += bin_size
                    if not silent:
                        self.print(f'Pushing {bin_count} events to SQL database.')
                        print(f'\033[1mTotal events parsed: {total_count}\033[0m', end='\r')
                    self.database.write_leg_evts(leg_evts)
                    self.database.write_veh_evts(veh_evts)
                    root.clear()
                    leg_evts = list()
                    veh_evts = list()
                    bin_count = 0
                    if not silent:
                        self.print(f'Resuming XML leg/vehicle event parsing.')
                        print(f'\033[1mTotal events parsed: {total_count}\033[0m', end='\r')

        total_count += bin_size
        if not silent:
            self.print(f'Pushing {bin_count} events to SQL database.')
        self.database.write_leg_evts(leg_evts)
        self.database.write_veh_evts(veh_evts)
        if not silent:
            self.print('XML leg/vehicle event parsing complete.')
            self.print(f'A total of {total_count} events were parsed.')

    def print(self, string):
        time = datetime.now()
        print('[' + time.strftime('%H:%M:%S:') + 
            ('000' + str(time.microsecond // 1000))[-3:] +
            ']  ' + string)
