
from util.db_util import DatabaseHandle

class InputDatabaseHandle(DatabaseHandle):
    def write_plans(self, plans):
        cols = (', ').join([
            col.split(' ')[0] for col in self.tables['plans']['schema']])
        vals = (', ').join(['%s'] * len(self.tables['plans']['schema']))
        query = f'''
            INSERT INTO {self.db}.plans ({cols})
            VALUES ({vals})
        '''
        self.cursor.executemany(query, plans)
        self.connection.commit()

    def write_activities(self, activities):
        cols = (', ').join([
            col.split(' ')[0] for col in self.tables['activities']['schema']])
        vals = (', ').join(['%s'] * len(self.tables['activities']['schema']))
        query = f'''
            INSERT INTO {self.db}.activities ({cols})
            VALUES ({vals})
        '''
        self.cursor.executemany(query, activities)
        self.connection.commit()

    def write_routes(self, routes):
        cols = (', ').join([
            col.split(' ')[0] for col in self.tables['routes']['schema']])
        vals = (', ').join(['%s'] * len(self.tables['routes']['schema']))
        query = f'''
            INSERT INTO {self.db}.routes ({cols})
            VALUES ({vals})
        '''
        self.cursor.executemany(query, routes)
        self.connection.commit()
