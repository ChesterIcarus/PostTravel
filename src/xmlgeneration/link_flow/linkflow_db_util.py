from util.db_util import DatabaseHandle

class LinkFlowDatabaseHandle(DatabaseHandle):
    def fetch_nodes(self):
        query = f'''
            SELECT *
            FROM {self.db}.network_nodes
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def fetch_bounds(self):
        query = f'''
            SELECT
                MIN(min_time),
                MAX(max_time)
            FROM (
                SELECT
                    link_id,
                    MIN(time) AS min_time,
                    MAX(time) AS max_time
                FROM {self.db}.leg_events
                GROUP BY link_id
            ) AS temp
        '''
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result[0][0], result[0][1]

    def fetch_links(self):
        query = f'''
            SELECT
                link_id,
                source_node,
                terminal_node,
                length,
                freespeed,
                capacity,
                permlanes,
                oneway,
                modes
            FROM {self.db}.network_links
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_link_times(self, tmin, tmax):
        query = f'''
            SELECT
                link_id,
                COUNT(*)
            FROM {self.db}.leg_events
            WHERE time > {tmin}
            AND time <= {tmax}
            GROUP BY link_id
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

