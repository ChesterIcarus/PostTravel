from util.db_util import DatabaseHandle

class StatsDatabseHandle(DatabaseHandle):
    def fetch_stats(self, table, column, group=[]):
        query = f'''
            select
                count(*) as `count`,
                sum(`{column}`) as `sum`,
                min(`{column}`) as `min`,
                avg(`{column}`) as `avg`,
                max(`{column}`) as `max`,
                stddev(`{column}`) as `stddev`
            from {self.db}.{table}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def fetch_bin(self, table, column, bin_count=20, bin_size=-4, bin_off=0):
        query = f'''
            select
                round({column}, {bin_size}) as `bin`,
                count(*) as `freq`
            from {self.db}.{table}
            group by `bin`
            limit {bin_off}, {bin_count}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
