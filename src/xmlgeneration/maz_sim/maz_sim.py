from datetime import datetime
from typing import Dict, List, Tuple
from xml.etree.ElementTree import iterparse

import numpy as np

from xmlgeneration.maz_sim.mazsim_db_util import MazSimDatabaseHandle
from util.print_util import Printer as pr


class MazSim:
    def __init__(self, database):
        self.database = MazSimDatabaseHandle(database)

    def chunk(self, arr, n):
        for i in range(0, len(arr), n):
            yield arr[i: i+n]

    def time(self, secs):
        hours = secs // 3600
        secs -= hours * 3600
        mins = secs // 60
        secs -= mins * 60
        time = [hours, mins, secs]
        return ':'.join(str(t).format('02d') for t in time)

    def encode_route(self, act):
        return (self.time(act[4]), act[5], self.time(act[6]))

    def encode_act(self, route):
        return (self.time(route[3] - route[2]), self.time(route[3]),
            route[4], route[5], route[6])

    def generate(self, planpath, routepath, mazs):
        pr.print('Generating input plans on select MAZs.', time=True)
        pr.print('Finding agents on selected MAZs.', time=True)
        
        mazs = tuple(mazs)
        plans = self.database.get_plans(mazs)
        
        plan_frmt = '<person id="%s"><plan selected="yes">'
        route_frmt = '<leg dep_time="%s" mode="%s" trav_time="%s" />'
        act_frmt = '<act dur="%s" end_time="%s" type="%s" x="%s" y="%s" />'

        planfile = open(planpath, 'w')
        routefile = open(routepath, 'w')
        target = len(plans)

        pr.print(f'Iterating over {target} plans and building plans file.',
            time=True)

        n = 100000
        planfile.write('<?xml version="1.0" encoding="utf-8"?><!DOCTYPE '
            'plans SYSTEM "http://www.matsim.org/files/dtd/plans_v4.dtd">')
        routefile.write('agent_id,route_index,src_maz,term_maz,dep_time,'
            'mode,dur_time\n')
        for group in self.chunk(plans, n):
            agents = tuple(plan[0] for plan in group)
            routes = list(self.database.get_routes(agents))
            activities = list(self.database.get_activities(agents))
            routefile.write('\n'.join(','.join(str(attr)
                for attr in route) for route in routes))
            routefile.flush()
            for plan in group:
                planfile.write(plan_frmt % plan[0])
                for i in range(plan[1] // 2):
                    planfile.write(act_frmt % self.encode_act(activities.pop(0)))
                    planfile.write(route_frmt % self.encode_route(routes.pop(0)))
                planfile.write(act_frmt % self.encode_act(activities.pop(0)))
                planfile.write('</plan></person>')
            planfile.flush()
        planfile.close()
        routefile.close()

        pr.print('Plans generation for select MAZs complete.', time=True)
                    



