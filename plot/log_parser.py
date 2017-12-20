#!/usr/bin/env python
from __future__ import division

import argparse
import collections
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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

        late_jobs = set()

        with open(self.filename, 'r') as f:
            for line in f:
                tokens = line.split('|')
                timestamp, level, classname, thread, message = tokens

                timestamp = float(timestamp)
                message = message.strip()

                if thread == 'Monitor.callback':
                    if message.startswith('measurements:') or \
                       message.startswith('values:'):
                        _, values_str = message.split(' ', 1)
                        values_str = values_str.replace('~', '') # Remove ~'s

                        values = eval(values_str)
                        for key, value in values.iteritems():
                            if (key == 'Frame Rate') or (key == 'pipeline'):
                                if data[key]:
                                    v = data[key][-1][1]
                                    if v != value:
                                        data[key].append((timestamp, v))

                            data[key].append((timestamp, value))

                if message.startswith('job') and ('completed' in message):
                    if not 'late' in message:
                        data['job_completed'].append(timestamp)
                        device = message.rsplit(' ', 1)[-1].replace("'", '')
                    else:
                        device = message.rsplit(' ', 2)[-2].replace("'", '')

                        job_id = int(message.split(' ', 2)[1])
                        late_jobs.add(job_id)

                    data['results'].append((timestamp, device))

                if thread == 'Controller':
                    if message.startswith('<Job') and (not 'Probe' in message):
                        data['job_created'].append(timestamp)

                if thread == 'MainThread':
                    if message.startswith('<Job') and (not 'Probe' in message):
                        spaces = message.split()
                        job_id = int(spaces[1][:-1])
                        pipeline = int(spaces[2][1:])

                        if job_id in late_jobs:
                            # Skip
                            continue

                        data['job_pipelines'].append((job_id, pipeline))

                if message.startswith('job') and ('makespan' in message):
                    makespan = float(message.rsplit(' ', 1)[-1])
                    data['makespans'].append(makespan)

                #print tokens

        return data


def get_axes():
    if nrows > 1:
        ax = axes[cur_row]
    else:
        ax = axes

    return ax

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plots data from VESPER car log file'
    )

    parser.add_argument('log', help='log file to load')
    parser.add_argument('-n', default=False, action='store_true',
                        help='disable plotting')
    args = parser.parse_args()

    reader = LogParser(args.log)
    results = reader.extract()

    #print data

    nrows = 6
    cur_row = 0

    min_time = sys.maxint
    max_time = 0.0

    fig, axes = plt.subplots(nrows=nrows, ncols=1, figsize=(15, 10), sharex=True)

    data_frames = {}
    for key, value in results.iteritems():
        if not type(value) == list:
            continue

        if type(value[0]) != tuple:
            continue

        #if key == 'job_pipelines':
        if not type(value[0][0]) == float:
            continue

        data_frames[key] = pd.DataFrame(data=value, columns=['seconds', 'y'])
        min_time = min(min_time, data_frames[key].seconds.min())
        max_time = max(max_time, data_frames[key].seconds.max())


    ax = get_axes()

    # Image Reception Rate
    data_frames['FPS'].plot(x='seconds', y='y',
                            ax=ax, ls='', color='b', marker='.')
    ax = data_frames['FPS.avg'].plot(x='seconds', y='y',
                           ax=ax, color='b')

    ax.set_ylim([0, data_frames['FPS'].y.max() * 1.05])
    ax.grid(alpha=0.7, linestyle='--')
    ax.legend(['Recv. Rate','Recv. Rate (EWMA)'], loc=0)
    ax.set_ylabel('FPS')
    ax.set_title('Image Reception Rate')

    cur_row += 1

    # Throughput
    ax = get_axes()
    data_frames['Throughput'].plot(x='seconds', y='y',
                                   ax=ax, color='g', marker='.')

    ax.set_ylim([0, data_frames['Throughput'].y.max() * 1.05])
    ax.grid(alpha=0.7, linestyle='--')
    ax.legend(['Throughput'], loc=0)
    ax.set_ylabel('FPS')
    ax.set_title('Image Completion Rate')

    cur_row += 1

    # Average Makespan
    ax = get_axes()
    data_frames['Makespan'].plot(x='seconds', y='y',
                                   ax=ax, color='r', marker='.')

    ax.set_ylim([0, data_frames['Makespan'].y.max() * 1.05])
    ax.grid(alpha=0.7, linestyle='--')
    ax.legend(['Avg. Makespan'], loc=0)
    ax.set_ylabel('Seconds')
    ax.set_title('Processing Makespan')

    cur_row += 1

    # Requested Frame Rate
    ax = get_axes()
    data_frames['Frame Rate'].plot(x='seconds', y='y', legend=None,
                                   ax=ax, color='g')

    ax.set_ylim([data_frames['Frame Rate'].y.min() * 0.95,
                 data_frames['Frame Rate'].y.max() * 1.05])
    ax.grid(alpha=0.7, linestyle='--')
    ax.set_ylabel('Frame Rate')
    ax.set_title('Requested Frame Rate')

    cur_row += 1

    # Pipeline Selection
    ax = get_axes()
    data_frames['pipeline'].plot(x='seconds', y='y', legend=None,
                                   ax=ax, color='b')

    ax.set_ylim([-0.5, data_frames['pipeline'].y.max() + 0.5])
    ax.grid(alpha=0.7, linestyle='--')
    ax.set_ylabel('Pipeline')
    ax.set_title('Pipeline Selection (top = best accuracy)')

    cur_row += 1

    # Completed Jobs by Device
    if 'results' in data_frames:
        ax = get_axes()

        sp = sns.stripplot(x='seconds', y='y', data=data_frames['results'], size=3)
        ax.grid(alpha=0.7, linestyle='--')
        ax.set_ylabel('Device')
        ax.set_title('Completed Images by Device')

        cur_row += 1

    ax.set_xlim([min_time, max_time])
    ax.set_xlabel('Time (ms)')

    if not args.n:
        plt.show()
