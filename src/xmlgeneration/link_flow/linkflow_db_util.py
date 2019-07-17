from util.db_util import DatabaseHandle

class LinkFlowDatabaseHandle(DatabaseHandle):
    def fetch_nodes(self, ids):
        query = f'''
            SELECT
                node_id,
                x_coord,
                y_coord
            FROM {self.db}.network_nodes
            WHERE node_id IN {ids}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def find_nodes(self, xmin, ymin, xmax, ymax):
        query = f'''
            SELECT
                node_id,
                x_coord,
                y_coord
            FROM {self.db}.network_nodes
            WHERE x_coord >= {xmin}
            AND x_coord <= {xmax}
            AND y_coord >= {ymin}
            AND y_coord <= {ymax}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def find_links(self, nodes):
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
            WHERE source_node IN {nodes}
            OR terminal_node IN {nodes}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_link_times(self, tmin, tmax, links):
        query = f'''
            SELECT
                link_id,
                COUNT(*)
            FROM {self.db}.leg_events
            WHERE time > {tmin}
            AND time <= {tmax}
            AND link_id IN {links}
            GROUP BY link_id
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

