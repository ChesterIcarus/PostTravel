from util.db_util import DatabaseHandle

class StatsDatabseHandle(DatabaseHandle):
    def fetch_stats(self, db, table, column, group=[]):
        query = f'''
            select
                count(*) as `count`,
                sum(`{column}`) as `sum`,
                min(`{column}`) as `min`,
                avg(`{column}`) as `avg`,
                max(`{column}`) as `max`,
                stddev(`{column}`) as `stddev`
            from {db}.{table}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def fetch_bin(self, db, table, column, bin_count=20, bin_size=-3, bin_off=0):
        query = f'''
            select
                round({column}, {bin_size}) as `bin`,
                count(*) as `freq`
            from {db}.{table}
            group by `bin`
            limit {bin_off}, {bin_count}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_activity(self):
        query = f'''
            SELECT
                bin,
                SUM(freq)
            FROM(
                SELECT
                    ROUND(`time`, -3) AS `bin`,
                    COUNT(*) AS `freq`
                FROM icarus_postsim.vehicle_events
                WHERE enter = 1
                GROUP BY
                    bin,
                    enter
                UNION
                SELECT
                    ROUND(`time`, -3) AS `bin`,
                    COUNT(*) * -1 AS `freq`
                FROM icarus_postsim.vehicle_events
                WHERE enter = 0
                GROUP BY
                    bin,
                    enter
            ) AS temp
            GROUP BY bin
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
