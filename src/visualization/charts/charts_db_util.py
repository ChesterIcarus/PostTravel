from util.db_util import DatabaseHandle

class ChartsDatabseHandle(DatabaseHandle):
    def fetch_stats(self, db, tbl, col, group=[]):
        query = f'''
            SELECT
                COUNT(*) as `count`,
                SUM(`{col}`) as `sum`,
                MIN(`{col}`) as `min`,
                AVG(`{col}`) as `avg`,
                MAX(`{col}`) as `max`,
                STDDEV(`{col}`) as `stddev`
            FROM {db}.{tbl}
        '''
        self.cursor.execute(query)
        return list(self.cursor.fetchall()[0])

    def fetch_count(self, db, tbl):
        query = f'''
            SELECT
                COUNT(*)
            FROM {db}.{tbl}
        '''
        self.cursor.execute(query)
        return int(self.cursor.fetchall()[0][0])

    def fetch_bin(self, db, tbl, col, 
                  bin_size=-3, bin_offset=0, bin_count=100):
        query = f'''
            SELECT
                ROUND({col}, {bin_size}) AS bin,
                COUNT(*) AS freq
            FROM {db}.{tbl}
            GROUP BY bin
            LIMIT {bin_offset}, {bin_offset + bin_count}
        '''
        self.cursor.execute(query)
        rslt = self.cursor.fetchall()
        rslt = list(zip(*rslt))
        return [int(x) for x in rslt[0]], [int(x) for x in rslt[1]]
    
    def fetch_bin_dif(self, db, tbl, col1, col2, 
                      bin_size=-3, bin_offset=0, bin_count=100):
        query = f'''
            SELECT
                bin,
                SUM(freq)
            FROM (
                SELECT
                    ROUND({col1}, {bin_size}) AS bin,
                    COUNT(*) AS freq
                FROM {db}.{tbl}
                GROUP BY bin
                UNION
                SELECT
                    ROUND({col2}, {bin_size}) AS bin,
                    COUNT(*) * -1 AS freq
                FROM {db}.{tbl}
                GROUP BY bin
            ) AS temp
            GROUP BY bin
            LIMIT {bin_offset}, {bin_offset + bin_count}
        '''
        self.cursor.execute(query)
        rslt = self.cursor.fetchall()
        rslt = list(zip(*rslt))
        return [int(x) for x in rslt[0]], [int(x) for x in rslt[1]]