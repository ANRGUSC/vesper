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

    folders = os.listdir(args.folder)
    folders.sort()

    for algo in folders:
        # One folder for each algorithm
        log_list = os.listdir(os.path.join(args.folder, algo))

        successful_job_count = 0
        total_jobs = 0
        total_time_ms = 0.0

        pipeline_counts = np.zeros(len(cfg.PIPELINES), dtype=np.int)

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

            if T_o is None:
                T_o = results['T_o'][0][1]
            else:
                assert(T_o == results['T_o'][0][1])

            total_jobs += len(results['job_completed'])
            total_time_ms += results['job_completed'][-1] - results['job_created'][0]

        metrics[algo + '.throughput'] = total_jobs / (total_time_ms/1000)
        metrics[algo + '.accuracy'] = np.sum(pipeline_counts *
                                             pipeline_accuracies) / total_jobs

    #print metrics

    for i in range(len(cfg.PIPELINES)):
        # Plot pipeline accuracies
        acc = cfg.PIPELINES[i][2]
        label_text = cfg.PIPELINES[i][3]

        plt.axhline(y=acc, color=colors[i], linestyle='-', label=label_text)

    plt.axvline(x=T_o, color='r', linestyle='-', label="Throughput Constraint")

    for algo_idx in range(len(folders)):
        algo = folders[algo_idx]
        plt.scatter(x=metrics[algo+".throughput"], y=metrics[algo+".accuracy"],
                    marker=markers[algo_idx], label=algo)

        print "Algorithm:", algo
        print "Throughput", metrics[algo+".throughput"]
        print "Accuracy:", metrics[algo+'.accuracy']
        print

    plt.legend(scatterpoints=1, loc=0)

    plt.gca().grid(alpha=0.7, linestyle='--')
    plt.gca().set_xlim(-0.1, T_o+0.5)
    plt.gca().set_xlabel("Throughput (frames processed per sec)")
    plt.gca().set_ylabel("Frame-Averaged mAP")
    plt.gca().set_title("mAP vs. Average Throughput")
    plt.show()


