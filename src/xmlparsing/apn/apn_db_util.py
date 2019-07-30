
from util.db_util import DatabaseHandle

class ParcelDatabseHandle(DatabaseHandle):
    def count_apn(self):
        query = f'''
            SELECT COUNT(*)
            FROM {self.db}.apn
        '''
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result[0][0]
        
    def push_apns(self, apns):
        cols = (', ').join([
            col.split(' ')[0] for col in self.tables['apn']['schema']])
        vals = '%s, %s, %s, %s, ST_POLYFROMTEXT(%s, 2223)'
        query = f'''
            INSERT INTO {self.db}.apn ({cols})
            VALUES ({vals})
        '''
        self.cursor.executemany(query, apns)
        self.connection.commit()