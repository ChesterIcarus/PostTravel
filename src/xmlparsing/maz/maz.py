
import shapefile
from util.print_util import Printer as pr
from xmlparsing.maz.maz_db_util import MazDatabaseHandle


class MazParser:
    def __init__(self, database):
        self.database = MazDatabaseHandle(database)

    def encode_poly(self, poly):
        return 'POLYGON((' + ','.join(str(pt[0]) + ' ' +
                str(pt[1]) for pt in poly) + '))'

    def parse(self, filepath):
        pr.print('Beginning MAZ spatial data parsing.', time=True)

        parser = shapefile.Reader(filepath)
        mazs = []

        n = 0
        for item in parser:
            if item.record.County == 'MC':
                mazs.append((
                    item.record.MAZ_ID_10,
                    item.record.TAZ_2015,
                    item.record.Sq_miles,
                    self.encode_poly(item.shape.points)))
                n += 1
            if n >= 10000:
                pr.print(f'Pushing {n} MAZs to database.', time=True)
                self.database.push_maz(mazs)
                mazs = []
                n = 0
                pr.print('Resuming MAZ parsing.', time=True)
        pr.print(f'Pushing {n} MAZs to database.', time=True)
        self.database.push_maz(mazs)
        pr.print('MAZ spatial data parsing complete.', time=True)