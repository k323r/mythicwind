#!/bin/python3

### TODO


VERSION=0.1

import sys
sys.path.insert(0, "/home/san/data/Turmschwingungen/src/library")

from bikbox import *
from LIDAR import *

from glob import glob
from math import sqrt, log

import argparse
from os import path
from zipfile import ZipFile

if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("-i", "--input", help="input pickle file containing measurement data", type=str)
    parser.add_argument("-o", "--output", help="name of output csv file", type=str)

    # parse arguments
    args = parser.parse_args()
    
    if args.verbose: print("* verbose: on")
    if args.verbose: print("* TOMTool v{}".format(VERSION))

    if not isfile(args.input):
        raise Exception("please provide an input pickle file")

    if not args.output:
        raise Exception("please provide an output file name for data export")

    if args.output and args.verbose:
        print("* exporting csv to: {}".format(args.output))

    data = pd.read_pickle(args.input)

    # keep only accelerations
    data = data.loc[:, 'acc_x' : 'acc_z']

    if args.output:
        if path.isfile(args.output):
            print("*! file already exists, done")
            exit()
        else:
            try:
                data.to_csv(args.output)
            except Exception as e:
                print("*! failed to export pickle!")
                print("*! -> {}".format(e))

