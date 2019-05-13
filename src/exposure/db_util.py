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
    tables: Dict[str, Dict] = None

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

    def create_index(self, table, name):
        columns = (', ').join(
            self.tables[table]['indexes']['columns'])
        exec_str = f'''CREATE INDEX
                            {name}
                        ON {self.db}.{table}
                            ({columns})'''
        self.cursor.execute(exec_str)
        self.connection.commit()
