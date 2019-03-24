from typing import List, Dict, Tuple
from getpass import getpass
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
                cursor.commit()
                cursor.close()
                connection.close()
                self.connection = sql.connect(user=params['user'],
                                              password=params['password'],
                                              db=params['db'], host=params['host'])
                self.cursor = self.connection.cursor()
                self.user = params['user']
                self.host = params['host']
                self.db = params['db']
                self.table = None
                self.columns = None
        else:
            self.user = None
            self.host = None
            self.db = None
            self.cursor = None
            self.connection = None
            self.table = None
            self.columns = None
            warn('No valid database passed, DatabaseHandle initialized without connection')

    def create_trip_table(self, table, schema):
        self.table = table
        self.columns = [column.split(' ')[0] for column in schema]
        sql_schema = (', ').join(schema)
        exec_str = f'''DROP TABLE IF EXISTS {self.db}.{self.table}'''
        self.cursor.execute(exec_str)
        self.connection.commit()
        exec_str = f'''CREATE TABLE {self.db}.{self.table} ({sql_schema})'''
        self.cursor.execute(exec_str)
        self.connection.commit()

    def write_trips(self, trips):
        s_strs = (', ').join(['%s'] * len(self.columns))
        exec_str = f'''
                    INSERT INTO {self.db}.{self.table}
                        ({self.columns})
                    values ({s_strs})
                   '''
        self.cursor.executemany(exec_str, trips)
        self.connection.commit()

    def create_index(self, index_name, index_columns):
        formed_index_cols = (', ').join(index_columns)
        exec_str = f'''CREATE INDEX 
                            {index_name}
                        ON {self.db}.{self.table}
                            ({formed_index_cols})'''
        self.cursor.execute(exec_str)
        self.connection.commit()
