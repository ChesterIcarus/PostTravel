from util.db_util import DatabaseHandle

class MazDatabaseHandle(DatabaseHandle):

    def push_maz(self, mazs):
        cols = (', ').join([
            col.split(' ')[0] for col in self.tables['maz']['schema']])
        vals = '%s, %s, %s, ST_POLYGONFROMTEXT(%s)'
        query = f'''
            INSERT INTO {self.db}.maz ({cols})
            VALUES ({vals})
        '''
        self.cursor.executemany(query, mazs)
        self.connection.commit()