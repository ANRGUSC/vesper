#!/usr/bin/env python
from __future__ import division

import argparse
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys
import numpy as np

sys.path.append('../')

import config as cfg

from log_parser import LogParser

colors = ['b', 'g', 'c', 'm', 'y']
markers = ['^', 'o', 's', 'd']

devices = ['car'] + [ 'rsu%d' % x for x in range(5) ]

# Empirical CDF
def ecdf(x, makespan):
    xs = np.sort(x)
    ys = np.arange(1, len(xs)+1)/float(len(xs))

    if xs[-1] < makespan:
        return np.append(xs, makespan), np.append(ys, 1.0)
    return xs, ys

if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser(
        description='Tool to generate plots for evaluating experiments'
    )

    parser.add_argument('folder', help='folder with logs')
    args = parser.parse_args()

    pipeline_accuracies = [x[2] for x in cfg.PIPELINES]

    metrics = {}
    T_o = None
    M_o = {}
    dev_ratio = []

    folders = os.listdir(args.folder)
    folders.sort()

    for algo in folders:
        # One folder for each algorithm
        log_list = os.listdir(os.path.join(args.folder, algo))

        successful_job_count = 0
        total_jobs = 0
        total_time_ms = 0.0

        pipeline_counts = np.zeros(len(cfg.PIPELINES), dtype=np.int)
        metrics[algo + '.makespans'] = []
        dev_counts = np.zeros(len(devices))

        for filename in log_list:
            filepath = os.path.join(args.folder, algo, filename)

            reader = LogParser(filepath)
            results = reader.extract()

            df = pd.DataFrame(data=results['job_pipelines'],
                              columns=['id','pipeline'])

            # Update count for each pipeline
            counts = df.pipeline.value_counts()
            keys = counts.keys()
            values = counts.values
            for i in range(len(keys)):
                pipeline_counts[keys[i]] += values[keys[i]]

            # Throughput constraint
            if T_o is None:
                T_o = results['T_o'][0][1]
            else:
                assert(T_o == results['T_o'][0][1])

            # Makespan constraint
            if not algo in M_o:
                M_o[algo] = results['M_o'][0][1]
            else:
                assert(M_o[algo] == results['M_o'][0][1])

            metrics[algo + '.makespans'].extend(results['makespans'])

            total_jobs += len(results['job_completed'])
            total_time_ms += results['job_completed'][-1] - results['job_created'][0]

            # Device assignments
            df_dev = pd.DataFrame(data=results['results'],
                              columns=['seconds', 'devices'])

            temp_counts = df_dev.devices.value_counts()
            for dev_idx, dev in zip(range(len(devices)), devices):
                if dev in temp_counts:
                    dev_counts[dev_idx] += temp_counts[dev]

        metrics[algo + '.throughput'] = total_jobs / (total_time_ms/1000)
        metrics[algo + '.accuracy'] = np.sum(pipeline_counts *
                                             pipeline_accuracies) / total_jobs

        dev_ratio.append(dev_counts / total_jobs)

    dev_ratio = np.array(dev_ratio)
    dev_existance = np.sum(dev_ratio, 0) > 0

    #print metrics

    if True:
        for i in range(len(cfg.PIPELINES)):
            # Plot pipeline accuracies
            acc = cfg.PIPELINES[i][2]
            label_text = cfg.PIPELINES[i][3]

            plt.axhline(y=acc, color=colors[i], linestyle='-', label=label_text)

        plt.axvline(x=T_o, color='r', linestyle='-', label='Throughput Constraint')

        for algo_idx in range(len(folders)):
            algo = folders[algo_idx]
            plt.scatter(x=metrics[algo + '.throughput'], y=metrics[algo + '.accuracy'],
                        marker=markers[algo_idx], label=algo)

            print 'Algorithm:', algo
            print 'Throughput', metrics[algo + '.throughput']
            print 'Accuracy:', metrics[algo + '.accuracy']
            print

        plt.legend(scatterpoints=1, loc=0)

        plt.gca().grid(alpha=0.7, linestyle='--')
        plt.gca().set_xlim(-0.1, T_o+0.5)
        plt.gca().set_xlabel('Throughput (frames processed per sec)')
        plt.gca().set_ylabel('Frame-Averaged mAP')
        plt.gca().set_title('mAP vs. Average Throughput')
        plt.show()

    if True:
        for algo_idx in range(len(folders)):
            algo = folders[algo_idx]
            ser_mk = pd.Series(data=metrics[algo + '.makespans'])
            x, y = ecdf(ser_mk, M_o[algo])
            plt.plot(x, y, label=algo)

        M_o_max = 0.0

        first = True
        for key, value in M_o.iteritems():
            if first:
                plt.axvline(x=value, color='r', linestyle='-', label='Makespan Constraint')
            else:
                plt.axvline(x=value, color='r', linestyle='-')

            first = False
            M_o_max = max(M_o_max, value)

        plt.gca().grid(alpha=0.7, linestyle='--')
        plt.gca().set_title('Empirical Makespan CDF')
        plt.gca().set_xlabel('Makespan (sec)')
        plt.gca().set_ylabel('Probability')
        plt.gca().legend(loc=0)
        plt.gca().set_ylim(0, 1.1)
        plt.gca().set_xlim(0, 1.1 * M_o_max)
        plt.show()

    if True:
        index = np.arange(len(folders))
        bar_width = 0.2
        opacity = 0.6

        for dev_idx, dev in zip(range(len(devices)), devices):
            if dev_existance[dev_idx]:
                plt.bar(index + dev_idx * bar_width, dev_ratio[:, dev_idx], bar_width,
                        alpha=opacity,
                        color=colors[dev_idx],
                        label=dev)

        plt.xlabel('Algorithms')
        plt.ylabel('Percentage')
        plt.title('Fraction of Jobs Using a Device')
        plt.xticks(index + bar_width, folders)
        plt.legend(loc=0)
        plt.gca().set_ylim(0, 1)
        plt.show()
