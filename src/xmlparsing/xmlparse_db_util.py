from util.db_util import DatabaseHandle

class XMLDatabaseHandle(DatabaseHandle):
    def write_events(self, events):
        cols = (', ').join([
            column.split(' ')[0] for column in self.tables['legs']["schema"]])
        values = (', ').join(['%s'] * len(self.tables['legs']['schema']))
        query = f'''
            INSERT INTO {self.db}.events ({cols})
            VALUES ({values})
        '''
        self.cursor.executemany(query, events)
        self.connection.commit()