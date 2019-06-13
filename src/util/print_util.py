
from datetime import datetime
from time import sleep

class ProgressBar:
    
    @staticmethod
    def tester():
        progbar = ProgressBar('Progress Bar Test ', 0, 100)
        for i in range(101):
            sleep(0.1)
            progbar.update(i)
        progbar.close()

    def __init__(self, string, start, end, bin=20):
        self.string = string
        self.start = start
        self.end = end
        self.bin = 20

    def update(self, value):
        prog = value * self.bin // (self.end - self.start)
        togo = self.bin - prog
        perc = str(min(value / self.end * 100, 100))[:3] + '%'
        bar = self.string + '[' + '=' * prog + ' ' * togo + '] ' + perc
        bar = '\b' * len(bar) + bar
        print(bar, end='', flush=True)
        if perc == '100%':
            self.close()

    def close(self):
        print()
    
class Timestamp:
    pass
