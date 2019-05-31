from typing import List, Dict, Tuple
import xml.etree.ElementTree as etree
from datetime import datetime
import numpy as np
import resource
import gc

from xmlparsing.events.eventsparse_db_util import EventsDatabaseHandle

class EventsParser:
    database: EventsDatabaseHandle = None

    def __init__(self, database=None):
        self.database = EventsDatabaseHandle(database)

    def parse(self, filepath, bin_size=100000, silent=False):
        
        if not silent:
            self.print(f'Beginning XML leg/vehicle event parsing from {filepath}.')

        parser = etree.iterparse(filepath, events=('end',))
        parser = iter(parser)
        evt, root = next(parser)

        leg_evts: List[Tuple[int, str, int, int]] = list()
        veh_evts: List[Tuple[int, int, int, int]] = list()
        bin_count: int = 0

        for evt, elem in parser:
            if elem.tag == 'event':
                etype = elem.attrib['type']
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
                elem.clear()
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
                    # leg_evts = []
                    # veh_evts = []

                    bin_count = 0
                    self.print(str(gc.get_stats()))
                    if not silent:
                        mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                        self.print(f'Peak process memory usage: {mem} kB.')
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
