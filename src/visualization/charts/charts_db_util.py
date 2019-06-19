from util.db_util import DatabaseHandle

class ChartsDatabseHandle(DatabaseHandle):
    def fetch_stats(self, db, table, column, group=[]):
        query = f'''
            SELECT
                COUNT(*) as `count`,
                SUM(`{column}`) as `sum`,
                MIN(`{column}`) as `min`,
                AVG(`{column}`) as `avg`,
                MAX(`{column}`) as `max`,
                STDDEV(`{column}`) as `stddev`
            FROM {db}.{table}
        '''
        self.cursor.execute(query)
        return list(self.cursor.fetchall()[0])


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
                    ROUND({col1}, {bin_size}) AS bin,
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

    def fetch_mat_act(self):
        query = f'''
            SELECT
                bin,
                SUM(freq)
            FROM(
                SELECT
                    ROUND(`time`, -2) AS `bin`,
                    COUNT(*) AS `freq`
                FROM icarus_postsim.vehicle_events
                WHERE enter = 1
                GROUP BY
                    bin
                UNION
                SELECT
                    ROUND(`time`, -2) AS `bin`,
                    COUNT(*) * -1 AS `freq`
                FROM icarus_postsim.vehicle_events
                WHERE enter = 0
                GROUP BY
                    bin
            ) AS temp
            GROUP BY bin
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_abm_act(self):
        query = f'''
            SELECT
                bin,
                SUM(freq)
            FROM(
                SELECT
                    ROUND(dep_time, -2) AS bin,
                    COUNT(*) AS freq
                FROM icarus_presim.routes
                GROUP BY bin
                UNION
                SELECT
                    ROUND(dep_time + dur_time, -2) AS bin,
                    COUNT(*) * -1 AS freq
                FROM icarus_presim.routes
                GROUP BY bin
            ) AS temp
            GROUP BY bin
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()