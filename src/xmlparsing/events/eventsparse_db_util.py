
from util.db_util import DatabaseHandle

class EventsDatabaseHandle(DatabaseHandle):
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