#!/usr/bin/env python
from __future__ import division

import argparse
import collections
#import matplotlib.pyplot as plt
#import pandas as pd


import sys
sys.path.append('../')

import config as cfg

class LogParser(object):
    """Parses a VESPER car log file."""
    def __init__(self, filename):
        self.filename = filename
        return

    def extract(self):
        data = collections.defaultdict(list)

        with open(self.filename, 'r') as f:
            start_time = 0.0

            for line in f:
                tokens = line.split('|')
                timestamp, level, classname, thread, message = tokens

                timestamp = float(timestamp)
                message = message.strip()

                if classname == 'boot_car':
                    data['start_time'] = timestamp
                    continue

                if thread == 'Monitor.callback':
                    if message.startswith('measurements:') or \
                       message.startswith('values:'):
                        _, values_str = message.split(' ', 1)
                        values_str = values_str.replace('~', '') # Remove ~'s

                        values = eval(values_str)
                        for key, value in values.iteritems():
                            data[key].append((timestamp, value))

                #print tokens

        return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plots data from VESPER car log file'
    )

    parser.add_argument('log', help='log file to load')
    args = parser.parse_args()

    reader = LogParser(args.log)
    data = reader.extract()

    #print data
