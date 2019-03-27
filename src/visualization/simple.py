from simple_trips.trip_db_util import DatabaseHandle

import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns


class SimpleVisualization:
    database: DatabaseHandle = None

    def __init__(self, database=None):
        plt.style.use('classic')
        sns.set()
        self.database = DatabaseHandle(database)

    def mag_plans(self, timestep=300, final_time=172800):
        steps = int(math.ceil(final_time / timestep))
        data = pd.DataFrame(np.zeros(shape=(steps, 2)),
                            index=[int(timestep * i) for i in range(steps)],
                            columns=['depart',
                                     'arrive'])
        time = 0
        row = 0
        while time < final_time:
            step_dep = self.database.get_trips(time,
                                               (time + timestep), 0)
            step_arr = self.database.get_trips(time,
                                               (time + timestep), 1)
            data.iloc[row, :] = [step_dep, step_arr]
            time += timestep
            row += 1
        return data

    def output_data(self, timestep=300, final_time=172800):
        steps = int(math.ceil(final_time / timestep))
        data = pd.DataFrame(np.zeros(shape=(steps, 2)),
                            index=[int(timestep * i) for i in range(steps)],
                            columns=['depart',
                                     'arrive'])
        time = 0
        row = 0
        while time < final_time:
            step_dep = self.database.get_trips(time,
                                               (time + timestep), 0)
            step_arr = self.database.get_trips(time,
                                               (time + timestep), 1)
            data.iloc[row, :] = [step_dep, step_arr]
            time += timestep
            row += 1
        return data

    def graph(self, data):
        sns.lineplot(data=data)
        # sns.relplot(x="time", y="arrive", data=data, kind='line')
        plt.show()
