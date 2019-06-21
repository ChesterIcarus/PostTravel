
from util.db_util import DatabaseHandle

class EventsDatabaseHandle(DatabaseHandle):
    def get_leg_count(self):
        query = f'''
            SELECT 
                COUNT(*) as `count`
            FROM
                xml_events_leg_events
        '''
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result[0][0]

    def get_veh_count(self):
        query = f'''
            SELECT 
                COUNT(*) as `count`
            FROM
                vehicle_events
        '''
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result[0][0]

    def write_leg_evts(self, leg_evts):
        cols = (', ').join([ col.split(' ')[0] for col in 
            self.tables['xml_events_leg_events']['schema']])
        vals = (', ').join(['%s'] * 
            len(self.tables['xml_events_leg_events']['schema']))
        query = f'''
            INSERT INTO {self.db}.xml_events_leg_events ({cols})
            VALUES ({vals})
        '''
        self.cursor.executemany(query, leg_evts)
        self.connection.commit()

    def write_veh_evts(self, veh_evts):
        cols = (', ').join([ col.split(' ')[0] for col in 
            self.tables['vehicle_events']['schema']])
        vals = (', ').join(['%s'] * 
            len(self.tables['vehicle_events']['schema']))
        query = f'''
            INSERT INTO {self.db}.vehicle_events ({cols})
            VALUES ({vals})
        '''
        self.cursor.executemany(query, veh_evts)
        self.connection.commit()
    
    def create_leg_events(self):
        query = f'''
            CREATE TABLE leg_events
            AS SELECT
                xele.vehicle_id AS vehicle_id,
                links.link_id AS link_id,
                COUNT(*) - 1 AS leg_index,
                xele.time AS time,
                xele.enter AS enter
            FROM xml_events_leg_events AS xele
            LEFT JOIN network_links AS links
            ON xele.link_str = links.link_str
            LEFT JOIN xml_events_leg_events AS xele1
            ON xele.vehicle_id = xele1.vehicle_id
                AND xele.time >= xele1.time
            GROUP BY
                xele.vehicle_id
            ORDER BY
                xele.vehicle_id,
                xele.leg_index
        '''
        self.cursor.execute(query)
        self.cursor.commit()