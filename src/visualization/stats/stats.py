import math

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

from visualization.stats.stats_db_util import StatsDatabseHandle
from scipy.interpolate import make_interp_spline as mis


class StatsVisual:

    def __init__(self, database):
        self.database = StatsDatabseHandle(database)

    def distrib(self, silent=False):
        stat = self.database.fetch_stats('icarus_postsim', 'routes', 'time')
        stat = list(stat[0])
        avg = float(stat[3])
        stddev = float(stat[5])

        xaxis = np.arange(avg - 3*stddev, avg + 3*stddev, 100)
        pdf = stats.norm.cdf(xaxis, avg, stddev)
        plt.plot(xaxis, pdf)
        plt.tight_layout()
        plt.savefig('distrib.png', bbox_inches='tight')
        plt.clf()

    def activity(self, silent=False):
        evts = self.database.fetch_activity()
        evts = list(zip(*evts))
        bins = [int(x) for x in evts[0]]
        freq = [float(x) for x in evts[1]]
        sums = [sum(freq[:i]) for i in range(len(freq))]

        plt.plot(bins, sums)
        plt.xlabel('time (sec)')
        plt.ylabel('active vehicles')
        plt.tight_layout()
        plt.savefig('line.png', bbox_inches='tight')
        plt.clf()

    def histogram(self, silent=False):
        hist = self.database.fetch_bin('icarus_postsim', 'routes', 'time')
        hist = list(zip(*hist))
        bins = hist[0]
        freq = hist[1]
        
        pos = []
        ticks = []
        lbls = []
        for i in range(len(bins)):
            pos.append(i)
            if i % 4 == 0:
                ticks.append(i)
                lbls.append(bins[i])

        plt.bar(pos, freq, align='center', color='r')
        plt.xticks(ticks, lbls)
        plt.xlabel('route duration (sec)')
        plt.ylabel('frequency')
        plt.tight_layout()
        plt.savefig('histogram.png', bbox_inches='tight')
        plt.clf()