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
            self.print(f'Beginning XML agent plan parsing from {filepath}.')

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
        plan_acts = []
        plan_routes = []

        # indexes
        agent = 0
        route = 0
        activity = 0
        leg = 0

        # other important info
        selected = False
        distance = 0
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

                    plan_acts.sort(key=lambda l:l[3])
                    plan_routes.sort(key=lambda l:l[0])

                    for i in range(len(plan_acts)):
                        plan_acts[i][1] = i
                    for i in range(len(plan_routes)):
                        del plan_routes[i][0]
                        plan_routes[i][1] = i

                    activities.extend(plan_acts)
                    routes.extend(plan_routes)

                    plan_acts = []
                    plan_routes = []
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
                            self.print('Resuming XML agent plan parsing.')

                        root.clear()
                        plans = []
                        activities = []
                        routes = []
                        bin_count = 0
                    
                elif elem.tag == 'activity':
                    end_time = self.parse_time(elem.attrib['end_time'])
                    act_type = self.encoding['activity'][elem.attrib['type']]

                    plan_acts.append([              # ACTIVITIES
                        agent,                      # agent_id
                        None,                       # act_index
                        None,                       # start_time
                        end_time,                   # end_time
                        act_type                    # act_type
                    ])
                    activity += 1

                elif elem.tag == 'leg':
                    stime = self.parse_time(elem.attrib['dep_time'])
                    dtime = self.parse_time(elem.attrib['trav_time'])
                    mode = self.encoding['mode'][elem.attrib['mode']]
                    modes.add(mode)

                    plan_routes.append([            # ROUTES
                        stime,                      # start_time - TEMP
                        agent,                      # agent_id
                        None,                       # route_index
                        leg,                        # size
                        dtime,                      # time
                        distance,                   # distance
                        mode                        # mode
                    ])

                    route += 1

                elif elem.tag == 'route':
                    distance = float(elem.attrib['distance'])
                    leg = len(elem.text.split(" "))
        
        if not silent:
            self.print(f'Pushing {bin_count} plans to SQL server.')

        self.database.write_plans(plans)
        self.database.write_activities(activities)
        self.database.write_routes(routes)
        
        if not silent:
            self.print('Completed XML agent plan parsing.')

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