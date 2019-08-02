from datetime import datetime
from typing import Dict, List, Tuple
from xml.etree.ElementTree import iterparse

import numpy as np

from util.print_util import Printer as pr
from xmlparsing.events.eventsparse_db_util import EventsDatabaseHandle


class EventsParser:
    database: EventsDatabaseHandle = None

    def __init__(self, database=None):
        self.database = EventsDatabaseHandle(database)

    def parse(self, filepath, bin_size=1000000, resume=False):

        parser = iterparse(filepath, events=('end','start'))
        evt, root = next(parser)

        types: Tuple[str] = ('entered link', 'left link',
            'PersonEntersVehicle', 'PersonLeavesVehicle')
        links: Dict[str: int] = {}

        leg_evts: List[Tuple[int, str, int, int]] = list()
        veh_evts: List[Tuple[int, int, int, int]] = list()
        leg_id: int = 0
        veh_id: int = 0
        time: int = 0
        bin_count: int = 0
        total_count: int = 0

        pr.print('Fetching network link data.', time=True)
        links = dict(self.database.fetch_network())
        pr.print('Network link data fetch completed.', time=True)

        if resume:
            pr.print('Finding where we left off parsing last.', time=True)
            leg_id = self.database.get_leg_count()
            veh_id = self.database.get_veh_count()
            offset = leg_id + veh_id
            pr.print(f'Skipping to event {offset} of XML file.',)
        else:
            pr.print('Resuming XML leg/vehicle event parsing.', time=True)

        pr.print(f'Event Parsing Progress', progress=0, persist=True, 
            replace=True, frmt='bold')

        for evt, elem in parser:
            if elem.tag == 'event' and evt == 'end':
                etype = elem.attrib['type']
                if resume and etype in types:
                    bin_count += 1
                    total_count += 1
                    if bin_count >= bin_size:
                        time = int(float(elem.attrib['time']))
                        root.clear()
                        bin_count = 0
                        pr.print(f'Skipped to event {total_count}.')
                        pr.print(f'Event Parsing Progress', progress=time/86400, 
                            persist=True, replace=True, frmt='bold')
                    if total_count == offset:
                        time = int(float(elem.attrib['time']))
                        root.clear()
                        bin_count = 0
                        resume = False
                        pr.print(f'Skipped to event {total_count}.', time=True)
                        pr.print('Event skipping complete.', time=True)
                        pr.print('Resuming XML leg/vehicle event parsing.', time=True)
                        pr.print(f'Event Parsing Progress', progress=time/86400,
                            persist=True, replace=True, frmt='bold')
                    continue

                if etype == 'entered link':
                    time = int(float(elem.attrib['time']))
                    leg_evts.append((
                        leg_id,
                        int(elem.attrib['vehicle']),
                        None,
                        links[elem.attrib['link']],
                        time,
                        1))
                    bin_count += 1
                    leg_id += 1
                elif etype == 'left link':
                    time = int(float(elem.attrib['time']))
                    leg_evts.append((
                        leg_id,
                        int(elem.attrib['vehicle']),
                        None,
                        links[elem.attrib['link']],
                        time,
                        0))
                    bin_count += 1
                    leg_id += 1
                elif etype == 'PersonEntersVehicle':
                    time = int(float(elem.attrib['time']))
                    veh_evts.append((
                        veh_id,
                        int(elem.attrib['vehicle']),
                        int(elem.attrib['person']),
                        time,
                        1))
                    bin_count += 1
                    veh_id += 1
                elif etype == 'PersonLeavesVehicle':
                    time = int(float(elem.attrib['time']))
                    veh_evts.append((
                        veh_id,
                        int(elem.attrib['vehicle']),
                        int(elem.attrib['person']),
                        time,
                        0))
                    bin_count += 1
                    veh_id += 1

                if bin_count >= bin_size:
                    total_count += bin_size
                    pr.print(f'Pushing {bin_count} events to SQL database.', time=True)
                    self.database.write_leg_evts(leg_evts)
                    self.database.write_veh_evts(veh_evts)
                    root.clear()
                    leg_evts = []
                    veh_evts = []
                    bin_count = 0
                    pr.print(f'Resuming XML leg/vehicle event parsing.', time=True)
                    pr.print(f'Event Parsing Progress', progress=time/86400,
                            persist=True, replace=True, frmt='bold')

        total_count += bin_size
        pr.print(f'Pushing {bin_count} events to SQL database.', time=True)
        self.database.write_leg_evts(leg_evts)
        self.database.write_veh_evts(veh_evts)
        pr.print(f'Event Parsing Progress', progress=1, persist=True,
            replace=True, frmt='bold')
        pr.push()
        pr.print('XML leg/vehicle event parsing complete.', time=True)
        pr.print(f'A total of {total_count} events were parsed.', time=True)
        