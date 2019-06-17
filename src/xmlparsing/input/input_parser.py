from typing import List, Dict, Tuple
from xml.etree.ElementTree import iterparse
from datetime import datetime
import numpy as np

from xmlparsing.input.inputparse_db_util import InputDatabaseHandle

class InputParser:
    database: InputDatabaseHandle = None
    encoding: Dict = None
    filepath: str = None

    def __init__(self, database=None, encoding=None):
        self.database = InputDatabaseHandle(database)
        self.encoding = encoding

    def parse(self, filepath, bin_size=100000, silent=False):

        if not silent:
            self.print(f'Beginning XML input plan parsing from {filepath}.')

        # XML parser
        parser = iterparse(filepath, events=('start', 'end'))
        parser = iter(parser)
        evt, root = next(parser)

        # bin counter (total plans processed)
        bin_count = 0

        # tabular data
        plans = []
        activities = []
        routes = []

        # indexes
        agent = 0
        route = 0
        activity = 0

        # other important info
        modes = set()

        # ireate over XML tags
        for evt, elem in parser:
            if evt == 'start':
                if elem.tag == 'person':
                    agent = int(elem.attrib['id'])
                if elem.tag == 'plan':
                    if elem.attrib['selected'] != 'yes':
                        selected = False
                    else:
                        selected = True
            elif evt == 'end' and selected:
                if elem.tag == 'plan':
                    plans.append([                  # PLANS
                        agent,                      # agent_id
                        route + activity,           # size
                        len(modes)                  # mode_count
                    ])
                    
                    modes = set()
                    route = 0
                    activity = 0
                    bin_count += 1

                    if bin_count >= bin_size:
                        if not silent:
                            self.print(f'Pushing {bin_count} plans to SQL server.')

                        self.database.write_plans(plans)
                        self.database.write_activities(activities)
                        self.database.write_routes(routes)
                        
                        if not silent:
                            self.print('Resuming XML input plan parsing.')

                        root.clear()
                        plans = []
                        activities = []
                        routes = []
                        bin_count = 0
                    
                elif elem.tag == 'act':
                    end_time = self.parse_time(elem.attrib['end_time'])
                    dur_time = end_time if 'dur' not in elem.attrib else self.parse_time(elem.attrib['dur'])
                    act_type = self.encoding['activity'][elem.attrib['type']]

                    activities.append([             # ACTIVITIES
                        agent,                      # agent_id
                        activity,                   # act_index
                        end_time - dur_time,        # start_time
                        end_time,                   # end_time
                        act_type                    # act_type
                    ])
                    activity += 1

                elif elem.tag == 'leg':
                    dep_time = self.parse_time(elem.attrib['dep_time'])
                    dur_time = self.parse_time(elem.attrib['trav_time'])
                    mode = self.encoding['mode'][elem.attrib['mode']]
                    modes.add(mode)

                    routes.append([                 # ROUTES
                        agent,                      # agent_id
                        route,                      # route_index
                        dep_time,                   # dep_time
                        dur_time,                   # dur_time
                        mode                        # mode
                    ])
                    route += 1
        
        if not silent:
            self.print(f'Pushing {bin_count} plans to SQL server.')

        self.database.write_plans(plans)
        self.database.write_activities(activities)
        self.database.write_routes(routes)
        
        if not silent:
            self.print('Completed XML input plan parsing.')

        root.clear()
        plans = []
        activities = []
        routes = []
    
    def parse_time(self, clk):
        clk = clk.split(':')
        return int(clk[0]) * 3600 + int(clk[1]) * 60 + int(clk[2])


    def print(self, string):
        time = datetime.now()
        return print('[' + time.strftime('%H:%M:%S:') + 
            ('000' + str(time.microsecond // 1000))[-3:] +
            ']\t' + string)