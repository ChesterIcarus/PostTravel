
from util.db_util import DatabaseHandle

class EventsDatabaseHandle(DatabaseHandle):
    def update_legs(self, start, end):
        query = f'''
            UPDATE  {self.db}.legs
            SET     start_time = {'%s'}
            WHERE   agent_id = {'%s'}
            AND     start_time = NULL
            LIMIT 1
        '''
        self.cursor.executemany(query, start)
        self.connection.commit()

        query = f'''
            UPDATE  {self.db}.legs
            SET     end_time = {'%s'}
            WHERE   agent_id = {'%s'}
            AND     end_time = NULL
            LIMIT 1
        '''
        self.cursor.executemany(query, end)
        self.connection.commit()