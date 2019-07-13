
from util.db_util import DatabaseHandle

class NeighborhoodDatabaseHandle(DatabaseHandle):
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

    def find_events(self, links, tmin=0, tmax=86400):
        query = f'''
            SELECT
                time,
                enter,
                vehicle_id,
                link_id
            FROM {self.db}.leg_events
            WHERE link_id IN {links}
            AND time >= {tmin}
            AND time <= {tmax}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()