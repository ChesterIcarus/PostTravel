from util.db_util import DatabaseHandle
from util.print_util import Printer as pr

class MazSimDatabaseHandle(DatabaseHandle):
    def find_mazs(self, pt1, pt2):
        query = f'''
            SELECT
                mazs.maz_id
            FROM network.mazs
            WHERE ST_CONTAINS(ST_POLYGONFROMTEXT(
                "POLYGON((
                    {pt1[0]} {pt1[1]},
                    {pt1[0]} {pt2[1]},
                    {pt2[0]} {pt2[1]},
                    {pt2[2]} {pt1[1]},
                    {pt1[0]} {pt1[1]}))",
                2223),
            mazs.poly)
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_plans(self, mazs):
        query = f'''
            SELECT
                plans.agent_id,
                plans.size
            FROM plans
            INNER JOIN activities AS acts
            USING (agent_id)
            WHERE acts.maz IN {mazs}
            ORDER BY agent_id
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_routes(self, agents):
        query = f'''
            SELECT
                agent_id,
                route_index,
                src_maz,
                term_maz,
                dep_time,
                mode,
                dur_time
            FROM routes
            WHERE agent_id IN {agents}
            ORDER BY agent_id, route_index
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_activities(self, agents):
        query = f'''
            SELECT
                agent_id,
                act_index,
                start_time,
                end_time,
                act_type,
                x,
                y
            FROM activities
            WHERE agent_id IN {agents}
            ORDER BY agent_id, act_index
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    