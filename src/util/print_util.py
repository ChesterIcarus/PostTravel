
import math
import os
import time
from datetime import datetime


class Printer:
    persist_str = ''
    persist_rows = 0

    @staticmethod
    def test():
        Printer.print('Beginning printer test.')
        time.sleep(1)
        Printer.print(Printer.time('This should have a timestamp.'))
        time.sleep(1)
        Printer.print('I will stay at the bottom.', persist='True')
        time.sleep(1)
        Printer.print('Even when something else is added.')
        time.sleep(1)
        Printer.print('But it can be updated.')
        Printer.print('As seen here.', persist=True, replace=True)
    
    @staticmethod
    def progress(prog, target=1, string = ''):
        perc = 100 * prog / target
        bar = ( string + ' [' + 
                '=' * int(perc // 5) + 
                ' ' * int(20 - perc // 5) + 
                '] ' + str(round(perc, 1)) + '%')
        print(bar, end='\r', flush=True)
        if perc >= 100:
            print()

    @staticmethod
    def clear(rows=None):
        if rows is None:
            rows, cols = os.popen('stty size', 'r').read().split()
            rows = int(rows)
        print('\n'*(rows-1) + '\033[F'*rows, end='\r')

    @staticmethod
    def delete(rows=None):
        pass

    @staticmethod
    def print(string, persist=False, replace=False):
        rows, cols = os.popen('stty size', 'r').read().split()
        rows = int(rows)
        cols = int(cols)
        print(('\033[F'+' '*cols)*Printer.persist_rows, end='\r')
        if persist:
            if not replace and Printer.persist_rows:
                string = Printer.persist_str + '\n' + string
            print(string, end='')
            Printer.persist_rows = sum([math.ceil(len(row) / cols) 
                for row in string.split('\n')])
            Printer.persist_str = string
        else:
            print(string)
            if Printer.persist_rows:
                print(Printer.persist_str, end='')        
    
    @staticmethod
    def time(string):
        date = datetime.now()
        return ('[' + date.strftime('%H:%M:%S:') + 
            str(date.microsecond // 1000).zfill(3) +
            '] ' + string)
