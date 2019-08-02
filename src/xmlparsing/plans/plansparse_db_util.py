
from util.db_util import DatabaseHandle

class PlansDatabaseHandle(DatabaseHandle):
    def count_plans(self):
        query = f'''
            SELECT COUNT(*)
            FROM icarus_presim.plans
        '''
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result[0][0]

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
        vals = '%s, %s, %s, %s, %s, ST_POINTFROMTEXT(%s, 2223), %s'
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
