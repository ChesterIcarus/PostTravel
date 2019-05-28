
from util.db_util import DatabaseHandle

class EventsDatabaseHandle(DatabaseHandle):
    def update_legs(self, start, end):
        query = f'''
            UPDATE TOP(1) 
                {self.db}.legs
            SET     start_time = {'%s'}
            WHERE   agent_id = {'%s'}
            AND     start_time = NULL
        '''
        self.cursor.executemany(query, start)
        self.connection.commit()

        query = f'''
            UPDATE TOP(1) 
                {self.db}.legs
            SET     end_time = {'%s'}
            WHERE   agent_id = {'%s'}
            AND     end_time = NULL
        '''
        self.cursor.executemany(query, end)
        self.connection.commit()