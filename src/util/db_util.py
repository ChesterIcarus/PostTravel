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

        elif isinstance(params, dict):
            keys = ['user', 'password', 'db', 'host', 'unix_socket']
            login = {key:params[keys] for key in keys if key in params}
            try:
                self.connection = sql.connect(**login)
                self.cursor = self.connection.cursor()
                self.user = params['user']
                self.host = params['host']
                self.db = params['db']
            except Exception as ex:
                # Creating the database that didn't exist, if that was the error above
                connection: sql.connections.Connection
                connection = sql.connect(**login)
                cursor = connection.cursor()
                cursor.execute(f'CREATE DATABASE {params["db"]}')
                connection.commit()
                cursor.close()
                connection.close()
                self.connection = sql.connect(**login)
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
        sql_schema = (', ').join(table_data['schema'])
        exec_str = f'''DROP TABLE IF EXISTS {self.db}.{table}'''
        self.cursor.execute(exec_str)
        self.connection.commit()
        exec_str = f'''CREATE TABLE {self.db}.{table} ({sql_schema})'''
        print(exec_str)
        self.cursor.execute(exec_str)
        self.connection.commit()

    def create_index(self, table, name):
        columns = (', ').join(self.tables[table]['indexes'][name])
        exec_str = f'''CREATE INDEX
                            {name}
                        ON {self.db}.{table}
                            ({columns})'''
        self.cursor.execute(exec_str)
        self.connection.commit()

    def alter_add_composite_PK(self, table, name):
        formed_index_cols = (', ').join(self.tables[table]['comp_PK'])
        exec_str = f'''ALTER TABLE {self.db}.{table}
                        ADD PRIMARY KEY ({formed_index_cols})'''
        self.cursor.execute(exec_str)
        self.connection.commit()

    def write_rows(self, data, table):
        s_strs = f"({', '.join(['%s'] * len(self.tables[table]['schema']))})"

        exec_str = f''' INSERT INTO {self.db}.{table}
                        VALUES {s_strs} '''
        self.cursor.executemany(exec_str, data)
        self.connection.commit()

    def write_geom_rows(self, data, table):
        s_strs = f"""{', '.join(
            ['%s'] * (len(self.tables[table]['schema']) - 1))}"""
        s_strs += ', ST_GeomFromText(%s)'
        exec_str = f''' INSERT INTO {self.db}.{table}
                        VALUES ({s_strs}) '''
        self.cursor.executemany(exec_str, data)
        self.connection.commit()
