#!/bin/python3

from glob import glob
from math import sqrt, log

import argparse
from os import path

import pandas as pd

import sys

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from mythicwind.csv_io import write_frame

if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("-i", "--input", help="path to MSR log file", type=str)
    parser.add_argument("-o", "--output", help="name of output csv file", type=str)
    parser.add_argument("-m", "--substract-mean", help="substract mean values from acceleration", action="store_true")
    parser.add_argument("-t", "--time-zone", help="time zone of time series", type=str, default='Europe/Berlin')


    # parse arguments
    args = parser.parse_args()
    
    if args.verbose: print("* verbose: on")

    if not path.isfile(args.input):
        raise Exception('please provide an input file')

    if not args.output:
        raise Exception("please provide an output file name for data export")

    if args.output and args.verbose:
        print("* exporting pickle to: {}".format(args.output))

    data = pd.read_csv(args.input,
                       skiprows=43,
                       delimiter=';',
                       header=0,
                       names=('acc_x', 'acc_y', 'acc_z', 'bat')
                      )

    data.drop(columns=['bat'], inplace=True)

    data.index = pd.to_datetime(data.index).tz_localize(args.time_zone)

    # remove duplicate indices
    if args.verbose:
        print('* removing duplicate indices')
    data = data.loc[~data.index.duplicated(keep='first')]

    if args.output:
        try:
            if args.verbose: print(f'* writing out data to {args.output}')
            write_frame(data, args.output, precision='%1.3f')
        except Exception as e:
            print("*! failed to export csv!")
            print("*! -> {}".format(e))

