#!/usr/bin/python3

import pandas as pd
import argparse
from os import path
from glob import glob
import datetime

inputFiles = list()
dfs = list()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', nargs='+', help='input glob pattern or file')
    parser.add_argument('-o', '--output', help='input directory or file')
    parser.add_argument('-v', '--verbose', help='input directory or file', action='store_true')
    
    parser.add_argument('-pdt', '--print-time-delta', help='print the time delta of the selected time', action='store_true')
    parser.add_argument('-st', '--start-time', help='select values by time')
    parser.add_argument('-et', '--end-time', help='select values by time')
    parser.add_argument('-sa', '--select-by-altitude', help='select values by altitude')
    parser.add_argument('-sg', '--select-generic', help='select values by altitude')

    args = parser.parse_args()

    # check if the user provided input
    if not args.input:
        print('*! please provide an input file or glob pattern')
        exit()

    if args.start_time: print('* start time: {}'.format(args.start_time))
    if args.end_time: print('* end time: {}'.format(args.end_time))
    for f in args.input:
        if path.isfile(f):
            if args.verbose: print('* processing file {}'.format(f))
            inputFiles.append(f)
        else:
            print('*! skipping: {}'.format(f))

    for f in inputFiles:
        dfs.append(pd.read_pickle(f))

    data = pd.concat(dfs) 

    if args.start_time and args.end_time:
        start = pd.to_datetime(args.start_time)
        end = pd.to_datetime(args.end_time)
        data = data[start:end]
        if args.verbose: print('* slicing from: {} -> end time: {}'.format(data.index[0],
                                                                         data.index[-1]))
    elif args.start_time and not args.end_time:
        start = pd.to_datetime(args.start_time)
        data = data[start:]
        if args.verbose: print('* slicing from: {}'.format(data.index[0]))

    elif not args.start_time and args.end_time:
        end = pd.to_datetime(args.end_time)
        data = data[:end]
        if args.verbose: print('* slicing to: {}'.format(data.index[-1]))

    else:
        if args.verbose: print('* start time: {} -> end time: {}'.format(data.index[0],
                                                                         data.index[-1]))
    # time delta if needed
    if args.print_time_delta:
        print('* time delta: {} -> {}'.format(data.index[-1] - data.index[0],
                                              (data.index[-1] - data.index[0]).total_seconds()))

    if args.output:
        if args.verbose: print ('writing output to {}'.format(args.output))
        try:
            data.to_pickle(args.output)
        except Exception as e:
            print('*! failed to export data: {}'.format(e))


