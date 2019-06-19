import math

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

from visualization.charts.charts_db_util import ChartsDatabseHandle
from scipy.interpolate import make_interp_spline as mis


class ChartsVisualization:

    def __init__(self, database):
        self.database = ChartsDatabseHandle(database)

    def graph(self, graphs, savepath, silent=False):
        for graph, run in graphs.items():
            if run and hasattr(self, graph):
                getattr(self, graph)(savepath, silent=silent)

    def route_duration(self, savepath, silent=False):
        mag_bin, mag_freq = self.database.fetch_bin(
            'icarus_presim', 'routes', 'dur_time', bin_size=-3, bin_count=15)
        mat_bin, mat_freq = self.database.fetch_bin(
            'icarus_postsim', 'routes', 'dur_time', bin_size=-3, bin_count=15)

        bins = mag_bin if len(mag_bin) > len(mat_bin) else mat_bin
        pos = np.arange(bins)
        mag_freq += [0]*(len(bins) - len(mag_bin))
        mat_freq += [0]*(len(bins) - len(mat_bin))
        width = 0.45

        plt.bar(pos + width / 2, mag_freq, width=width, color='b', label='MAG ABM')
        plt.bar(pos - width / 2, mat_freq, width=width, color='r', label='MATsim')
        plt.xticks(pos[0::4], bins[0::4])
        plt.xlabel('route duration (sec)')
        plt.ylabel('frequency')
        plt.legend()
        plt.tight_layout()
        plt.savefig(savepath + 'route_duration.png', dpi=1200, bbox_inches='tight')
        plt.clf()

    def agents_traveling(self, savepath, silent=False):
        mag_bin, mag_freq = self.database.fetch_bin_dif(
            'icarus_presim', 'routes', 'dep_time', 'dep_time + dur_time',
            bin_size=-2, bin_count=1000)
        mat_bin, mat_freq = self.database.fetch_bin_dif(
            'icarus_postsim', 'routes', 'dep_time', 'dep_time + dur_time',
            bin_size=-2, bin_count=1000)

        mag_cum = [sum(mag_freq[:i]) for i in range(1, len(mag_freq)+1)]
        mat_cum = [sum(mat_freq[:i]) for i in range(1, len(mat_freq)+1)]

        plt.plot(mag_bin, mag_cum, alpha=0.75, color='b', label='MAG ABM')
        plt.plot(mat_bin, mat_cum, alpha=0.75, color='b', label='MATsim')
        plt.xlabel('time of day (sec)')
        plt.ylabel('agents traveling')
        plt.legend()
        plt.tight_layout()
        plt.savefig(savepath + 'agents_traveling.png', dpi=1200, bbox_inches='tight')
        plt.clf()

    def route_arrivals(self, savepath, silent=False):
        pass
    
    def route_departures(self, savepath, silent=False):
        pass

            

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
        evts1 = self.database.fetch_mat_act()
        evts1 = list(zip(*evts1))
        bins1 = [int(x) for x in evts1[0]]
        freq1 = [float(x) for x in evts1[1]]
        sums1 = [sum(freq1[:i]) for i in range(1, len(freq1)+1)]


        evts2 = self.database.fetch_abm_act()
        evts2 = list(zip(*evts2))
        bins2 = [int(x) for x in evts2[0]]
        freq2 = [float(x) for x in evts2[1]]
        sums2 = [sum(freq2[:i]) for i in range(1, len(freq2)+1)]

        plt.plot(bins2, sums2, color='b', label='MAG ABM')
        plt.plot(bins1, sums1, color='r', label='MATsim')
        plt.xlabel('time (sec)')
        plt.ylabel('agents traveling')
        plt.legend()
        plt.tight_layout()
        plt.savefig('line.png', dpi=1200, bbox_inches='tight')
        plt.clf()

    def histogram(self, silent=False):
        hist1 = self.database.fetch_bin('icarus_postsim', 'routes', 'time')
        hist1 = list(zip(*hist1))
        hist2 = self.database.fetch_bin('icarus_presim', 'routes', 'dur_time')
        hist2 = list(zip(*hist2))
        bins = list(hist1[0])
        mat = list(hist1[1])
        abm = list(hist2[1])
        size = max(len(mat), len(abm))
        abm += [0]*(size - len(abm))
        
        width = 0.45
        pos = np.arange(len(bins))

        plt.bar(pos - width / 2, mat, width=width, color='r', label='MATsim')
        plt.bar(pos + width / 2, abm, width=width, color='b', label='MAG ABM')
        plt.xticks(pos[0::4], bins[0::4])
        plt.xlabel('route duration (sec)')
        plt.ylabel('frequency')
        plt.legend()
        plt.tight_layout()
        plt.savefig('histogram.png', dpi=1200, bbox_inches='tight')
        plt.clf()