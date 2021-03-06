import math
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from scipy.interpolate import make_interp_spline as mis

from visualization.charts.charts_db_util import ChartsDatabseHandle


class ChartsVisualization:
    def __init__(self, database):
        self.database = ChartsDatabseHandle(database)

    def graph(self, graphs, savepath, silent=False):
        if not silent:
            self.print('Beginning data visualization.')

        for graph, run in graphs.items():
            if run and hasattr(self, graph):
                getattr(self, graph)(savepath, silent=silent)
        
        if not silent:
            self.print('Data visualization complete.')

    def print(self, string):
        time = datetime.now()
        return print('[' + time.strftime('%H:%M:%S:') + 
            ('000' + str(time.microsecond // 1000))[-3:] +
            '] ' + string)

    def align_bins(self, bin1, bin2, val1, val2):
        bins = list(set(bin1 + bin2))
        val1 = [0] * bins.index(bin1[0]) + val1
        val1 = val1 + [0] * (len(bins) - len(val1))
        val2 = [0] * bins.index(bin2[0]) + val2
        val2 = val2 + [0] * (len(bins) - len(val2))
        return bins, val1, val2

    def center_vals(self, vals, n):
        if n >= len(vals):
            return 0, len(vals)
        vals = vals[:]
        mins = vals[:]
        low = vals.index(max(mins))
        high = low + 1
        mins.pop(low)
        while True:
            val = max(mins)
            pos = vals.index(val)
            if pos < low:
                low = max(pos, high - n)
            elif pos >= high:
                high = min(pos + 1, low + n)
            if high - low == n:
                break
            mins.pop(mins.index(val))
        return low, high

    def route_differential(self, savepath, silent=False):
        if not silent:
            self.print('Fetching route differenetial data.')
        
        bins, freqs = self.database.fetch_route_dif(bin_size=-2)

        if not silent:
            self.print('Graphing route differential data.')

        low, high = self.center_vals(freqs, 40)
        bins = bins[low:high]
        freqs = freqs[low:high] 
        
        total = sum(freqs)
        freqs = [100 * freq / total for freq in freqs]
        pos = np.arange(len(bins))
        tick = len(freqs) // 9

        plt.bar(pos, freqs, width=1   , color='b')
        plt.xticks(pos[0::tick], bins[0::tick])
        plt.xlabel('percent error')
        plt.ylabel('occurance (%)')
        plt.tight_layout()

        if not silent:
            self.print('Saving route differential graph.')

        plt.savefig(savepath + 'route_differential.png', dpi=1200, bbox_inches='tight')
        plt.clf()


    def route_duration(self, savepath, silent=False):
        if not silent:
            self.print('Fetching route duration data.')

        mag_bin, mag_freq = self.database.fetch_bin(
            'icarus_presim', 'routes', 'dur_time', bin_size=-3, bin_count=15)
        mat_bin, mat_freq = self.database.fetch_bin(
            'icarus_postsim', 'routes', 'dur_time', bin_size=-3, bin_count=15)
        mag_tot = self.database.fetch_count('icarus_presim', 'routes')
        mat_tot = self.database.fetch_count('icarus_postsim', 'routes')

        if not silent:
            self.print('Graphing route duration data.')

        bins, mag_freq, mat_freq = self.align_bins(mag_bin, mat_bin, mag_freq, mat_freq)
        pos = np.arange(len(bins))
        mag_freq = [100 * x / mag_tot for x in mag_freq]
        mat_freq = [100 * x / mat_tot for x in mat_freq]
        width = 0.45

        plt.bar(pos + width / 2, mag_freq, width=width, color='b', label='MAG ABM')
        plt.bar(pos - width / 2, mat_freq, width=width, color='r', label='MATsim')
        plt.xticks(pos[0::4], bins[0::4])
        plt.xlabel('route duration (sec)')
        plt.ylabel('occurance (%)')
        plt.legend()
        plt.tight_layout()

        if not silent:
            self.print('Saving route duration graph.')

        plt.savefig(savepath + 'route_duration.png', dpi=1200, bbox_inches='tight')
        plt.clf()

    def agents_traveling(self, savepath, silent=False):
        if not silent:
            self.print('Fetching agent traveling data.')
            
        mag_bin, mag_freq = self.database.fetch_bin_dif(
            'icarus_presim', 'routes', 'dep_time', 
            'icarus_presim', 'routes', 'dep_time + dur_time',
            bin_size=-2, bin_count=1000)
        mat_bin, mat_freq = self.database.fetch_bin_dif(
            'icarus_postsim', 'routes', 'dep_time', 
            'icarus_postsim', 'routes', 'dep_time + dur_time',
            bin_size=-2, bin_count=1000)
        mag_tot = self.database.fetch_count('icarus_presim', 'plans')
        mat_tot = self.database.fetch_count('icarus_postsim', 'plans')

        if not silent:
            self.print('Graphing agent traveling data.')

        mag_cum = [100 * sum(mag_freq[:i]) / mag_tot for i in range(1, len(mag_freq)+1)]
        mat_cum = [100 * sum(mat_freq[:i]) / mat_tot for i in range(1, len(mat_freq)+1)]

        plt.plot(mag_bin, mag_cum, alpha=0.75, color='b', label='MAG ABM')
        plt.plot(mat_bin, mat_cum, alpha=0.75, color='r', label='MATsim')
        plt.xlabel('time of day (sec)')
        plt.ylabel('agents traveling (%)')
        plt.legend()
        plt.tight_layout()

        if not silent:
            self.print('Saving agent traveling graph.')

        plt.savefig(savepath + 'agents_traveling.png', dpi=1200, bbox_inches='tight')
        plt.clf()

    def activity_events(self, savepath, act_type=[], attr='', savename='', silent=False):
        pass

    def work_start(self, savepath, silent=False):
        if not silent:
            self.print('Fetching agent work start data.')

        mag_bin, mag_freq = self.database.fetch_bin_cond(
            'icarus_presim', 'activities', 'start_time', 'act_type', (1,),
            bin_size=-4, bin_count=10)
        mat_bin, mat_freq = self.database.fetch_bin_cond(
            'icarus_postsim', 'activities', 'start_time', 'act_type', (1,),
            bin_size=-4, bin_count=10)
        mag_tot = self.database.fetch_count_cond(
            'icarus_presim', 'activities', 'act_type', (1,))
        mat_tot = self.database.fetch_count_cond(
            'icarus_postsim', 'activities', 'act_type', (1,))

        if not silent:
            self.print('Graphing agent work start data.')

        bins, mag_freq, mat_freq = self.align_bins(mag_bin, mat_bin, mag_freq, mat_freq)
        pos = np.arange(len(bins))
        mag_freq = [100 * x / mag_tot for x in mag_freq]
        mat_freq = [100 * x / mat_tot for x in mat_freq]
        width = 0.45

        plt.bar(pos + width / 2, mag_freq, width=width, color='b', label='MAG ABM')
        plt.bar(pos - width / 2, mat_freq, width=width, color='r', label='MATsim')
        plt.xticks(pos[0::2], bins[0::2])
        plt.xlabel('agent work start time (sec)')
        plt.ylabel('occurance (%)')
        plt.legend()
        plt.tight_layout()

        if not silent:
            self.print('Saving agent work start graph.')

        plt.savefig(savepath + 'work_start.png', dpi=1200, bbox_inches='tight')
        plt.clf()

    def work_end(self, savepath, silent=False):
        if not silent:
            self.print('Fetching agent work end data.')

        mag_bin, mag_freq = self.database.fetch_bin_cond(
            'icarus_presim', 'activities', 'end_time', 'act_type', (1,),
            bin_size=-4, bin_count=15)
        mat_bin, mat_freq = self.database.fetch_bin_cond(
            'icarus_postsim', 'activities', 'end_time', 'act_type', (1,),
            bin_size=-4, bin_count=15)
        mag_tot = self.database.fetch_count_cond(
            'icarus_presim', 'activities', 'act_type', (1,))
        mat_tot = self.database.fetch_count_cond(
            'icarus_postsim', 'activities', 'act_type', (1,))

        if not silent:
            self.print('Graphing agent work start data.')

        bins, mag_freq, mat_freq = self.align_bins(mag_bin, mat_bin, mag_freq, mat_freq)
        pos = np.arange(len(bins))
        mag_freq = [100 * x / mag_tot for x in mag_freq]
        mat_freq = [100 * x / mat_tot for x in mat_freq]
        width = 0.45

        plt.bar(pos + width / 2, mag_freq, width=width, color='b', label='MAG ABM')
        plt.bar(pos - width / 2, mat_freq, width=width, color='r', label='MATsim')
        plt.xticks(pos[0::2], bins[0::2])
        plt.xlabel('agent work end time (sec)')
        plt.ylabel('occurance (%)')
        plt.legend()
        plt.tight_layout()

        if not silent:
            self.print('Saving agent work end graph.')

        plt.savefig(savepath + 'work_end.png', dpi=1200, bbox_inches='tight')
        plt.clf()

    def link_flow(self, savepath, silent=False):
        pass