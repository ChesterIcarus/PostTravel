from typing import List, Dict, Tuple
from warnings import warn
import MySQLdb as sql
import MySQLdb.connections as connections


class DatabaseHandle:
    connection = connections.Connection
    cursor = connections.cursors.Cursor
    user: str = None
    host: str = None
    db: str = None
    table: str = None
    columns: List[str] = None

    def __init__(self, params: Dict[str, str] = None, handle=None):
        if type(handle) is DatabaseHandle:
            self = handle

        if isinstance(params, dict):
            try:
                self.connection = sql.connect(user=params['user'],
                                              password=params['password'],
                                              db=params['db'], host=params['host'])
                self.cursor = self.connection.cursor()
                self.user = params['user']
                self.host = params['host']
                self.db = params['db']
            except sql._exceptions.DatabaseError:
                # Creating the database that didn't exist, if that was the error above
                connection: sql.connections.Connection
                connection = sql.connect(user=params['user'],
                                         password=params['password'],
                                         db='mysql', host=params['host'])
                cursor = connection.cursor()
                cursor.execute(f'CREATE DATABASE {params["db"]}')
                connection.commit()
                cursor.close()
                connection.close()
                self.connection = sql.connect(user=params['user'],
                                              password=params['password'],
                                              db=params['db'], host=params['host'])
                self.cursor = self.connection.cursor()
                self.user = params['user']
                self.host = params['host']
                self.db = params['db']

        else:
            self.user = None
            self.host = None
            self.db = None
            self.cursor = None
            self.connection = None
            warn('No valid database passed, DatabaseHandle initialized without connection')
        if 'tables' in params:
            self.tables = params['tables']
        else:
            self.tables = None

    def create_table(self, table):
        table_data = self.tables[table]
        print(table_data)
        # columns = [column.split(' ')[0] for column in table_data["schema"]]

        sql_schema = (', ').join(table_data['schema'])
        exec_str = f'''DROP TABLE IF EXISTS {self.db}.{table}'''
        self.cursor.execute(exec_str)
        self.connection.commit()
        exec_str = f'''CREATE TABLE {self.db}.{table} ({sql_schema})'''
        print(exec_str)
        self.cursor.execute(exec_str)
        self.connection.commit()


    def write_legs(self, legs):
        s_strs = (', ').join(['%s'] * len(self.tables['legs']['schema']))
        col_str = (', ').join([
            column.split(' ')[0] for column in self.tables['legs']["schema"]])
        exec_str = f'''
                    INSERT INTO {self.db}.legs
                        ({col_str})
                    values ({s_strs})
                   '''
        self.cursor.executemany(exec_str, legs)
        self.connection.commit()

    def write_acts(self, acts):
        s_strs = (', ').join(['%s'] * len(self.tables['activities']['schema']))
        col_str = (', ').join([
            column.split(' ')[0] for column in self.tables['activities']['schema']])
        exec_str = f'''
                    INSERT INTO {self.db}.activities
                        ({col_str})
                    values ({s_strs})
                   '''
        self.cursor.executemany(exec_str, acts)
        self.connection.commit()

    def create_index(self, table, name):
        columns = (', ').join(
            self.tables[table]['indexes']['columns'])
        exec_str = f'''CREATE INDEX
                            {name}
                        ON {self.db}.{table}
                            ({columns})'''
        self.cursor.execute(exec_str)
        self.connection.commit()

    # def get_legs(self, time_start, time_end, direction):
    #     exec_str = f''' SELECT
    #                         COUNT(*)
    #                     from
    #                         {self.db}.{self.table}
    #                     WHERE
    #                         time_sec > {time_start}
    #                     and
    #                         time_sec < {time_end}
    #                     and
    #                         direction = {direction}'''
    #     self.cursor.execute(exec_str)
    #     return self.cursor.fetchall()[0][0]
