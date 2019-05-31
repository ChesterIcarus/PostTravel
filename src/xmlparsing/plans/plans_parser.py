from typing import List, Dict, Tuple
from xml.etree.ElementTree import iterparse
from datetime import datetime
import numpy as np

from xmlparsing.plans.plansparse_db_util import PlansDatabaseHandle

class PlansParser:
    database: PlansDatabaseHandle = None
    encoding: Dict = None
    filepath: str = None

    def __init__(self, database=None, encoding=None):
        self.database = PlansDatabaseHandle(database)
        self.encoding = encoding

    def parse(self, filepath, bin_size=100000, silent=False):

        if not silent:
            self.print_time(f'Beginning XML agent plan parsing from {filepath}.')

        # XML parser
        parser = iterparse(filepath, events=('start', 'end'))
        parser = iter(parser)
        evt, root = next(parser)

        # bin counter (total legs processed)
        bin_count = 0

        # tabular data
        plans = []
        activities = []
        routes = []
        legs = []

        # indexes
        agent = 0
        route = 0
        activity = 0
        leg = 0

        # other important info
        distance = 0
        time = 0
        modes = set()

        # ireate over XML tags
        try:
            for evt, elem in parser:
                # tag openings
                if evt == 'start':
                    if elem.tag == 'person':
                        agent = int(elem.attrib['id'])
                # tag closings
                elif evt == 'end':
                    if elem.tag == 'person':
                        
                        plans.append([                  # PLANS
                            agent,                      # agent_id
                            route + activity,           # size
                            len(modes)                  # mode_count
                        ])

                        modes = set()
                        route = 0
                        activity = 0

                        if bin_count >= bin_size:
                            if not silent:
                                self.print_time(f'Pushing {bin_count} legs to SQL server.')

                            self.database.write_plans(plans)
                            self.database.write_activities(activities)
                            self.database.write_routes(routes)
                            self.database.write_legs(legs)
                            
                            if not silent:
                                self.print_time('Resuming XML agent plan parsing.')

                            root.clear()
                            plans = []
                            activities = []
                            routes = []
                            legs = []
                            bin_count = 0
                        
                    elif elem.tag == 'activity':
                        end_time = self.parse_time(elem.attrib['end_time'])
                        act_type = self.encoding['activity'][elem.attrib['type']]

                        activities.append([             # ACTIVITIES
                            agent,                      # agent_id
                            activity,                   # act_index
                            time,                       # start_time
                            end_time,                   # end_time
                            act_type                    # act_type
                        ])

                        time = end_time
                        activity += 1

                    elif elem.tag == 'leg':
                        mode = self.encoding['mode'][elem.attrib['mode']]
                        dtime = self.parse_time(elem.attrib['trav_time'])

                        modes.add(mode)

                        routes.append([                 # ROUTES
                            agent,                      # agent_id
                            leg,                        # size
                            route,                      # route_index
                            dtime,                      # time
                            distance,                   # distance
                            mode                        # mode
                        ])

                        time += dtime
                        distance = 0
                        leg = 0
                        route += 1

                    elif elem.tag == 'route':
                        distance += float(elem.attrib['distance'])
                        links = elem.text.split(" ")
                        leg = len(links)

                        legs.extend([[                  # LEGS
                            agent,                      # agent_id
                            link,                       # link_id
                            route,                      # route_index
                            leg,                        # leg_index
                            None,                       # start_time
                            None,                       # end_time
                        ] for link, leg in zip(links, range(0, leg))])

                        bin_count += leg
        except Exception as ex:
            pass
        
        if not silent:
            self.print_time(f'Pushing {bin_count} legs to SQL server.')

        self.database.write_plans(plans)
        self.database.write_activities(activities)
        self.database.write_routes(routes)
        self.database.write_legs(legs)
        
        if not silent:
            self.print_time('Completed XML agent plan parsing.')

        root.clear()
        plans = []
        activities = []
        routes = []
        legs = []
    
    def parse_time(self, clk):
        clk = clk.split(':')
        return int(clk[0]) * 3600 + int(clk[1]) * 60 + int(clk[2])


    def print_time(self, string):
        time = datetime.now()
        return print('[' + time.strftime('%H:%M:%S:') + 
            ('000' + str(time.microsecond // 1000))[-3:] +
            ']\t' + string)