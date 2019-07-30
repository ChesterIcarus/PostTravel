
import shapefile

from xmlparsing.apn.apn_db_util import ParcelDatabseHandle
from util.print_util import Printer as pr

class ParcelParser:
    def __init__(self, database):
        self.database = ParcelDatabseHandle(database)

    def encode_poly(self, poly):
        if len(poly) == 0:
            return None
        if poly[0] != poly[-1]:
            poly.append(poly[0])
        return 'POLYGON((' + ','.join(str(pt[0]) + ' ' +
                str(pt[1]) for pt in poly) + '))'

    def parse(self, filepath, resume=False):
        progress = pr.printer(persist=True, frmt='bold', replace=True)

        pr.print('Beginning APN parcel data parsing.', time=True)
        progress('APNs parsed: 0', progress=0)
        parser = shapefile.Reader(filepath)
        target = len(parser)
        total = 0
        apns = []

        if resume:
            pr.print('Finding where parsing left off last.', time=True)
            offset = self.database.count_apn()
            pr.print(f'Skipping to APN {offset}.', time=True)

        n = 0
        for item in parser:
            if resume:
                n += 1
                if n >= offset:
                    total += n
                    n = 0
                    resume = False
                    pr.print('Resuming APN parcel parsing.', time=True)
                    progress(f'APNs parsed: {total}', progress = total/target)
                continue
            apns.append((
                item.record['APN'],
                item.record['ADDRESS'],
                item.record['FLOOR'],
                None,
                self.encode_poly(item.shape.points)))
            n += 1
            if n >= 100000:
                pr.print(f'Pushing {n} APNs to database.', time=True)
                self.database.push_apns(apns)
                apns = []
                total += n
                n = 0
                pr.print(f'Resuming APN parcel parsing.', time=True)
                progress(f'APNs parsed: {total}', progress = total/target)

        pr.print(f'Pushing {n} APNs to database.', time=True)
        self.database.push_apns(apns)
        pr.print('APN parcel data parsing complete.', time=True)
        progress(f'APNs parsed: {n + target}', progress = 1)
