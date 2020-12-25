#!/bin/python3

### TODO


VERSION=0.1


from bikbox import *

from glob import glob
from math import sqrt, log

import argparse
from os import path
from zipfile import ZipFile

if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("-i", "--input", help="input directory containing TOMBox log files", type=str)
    parser.add_argument("-o", "--output", help="name of output pickle file", type=str)
    parser.add_argument("-j", "--procs", help="number of processors to use", type=int)
    parser.add_argument("-m", "--substract-mean", help="substract mean values from acceleration", action="store_true")
    parser.add_argument("--no-gps", help="surpress gps data", action="store_true")


    # parse arguments
    args = parser.parse_args()
    
    if args.verbose: print("* verbose: on")
    if args.verbose: print("* TOMTool v{}".format(VERSION))

    if not args.input:
        if args.verbose: print("* setting input directory to cwd")
        args.input=path.curdir

    # check for empty input directory
    if len(glob(path.join(args.input, "*.txt"))) == 0:
        raise Exception("could not find any *.txt file in {} -> exit".format(args.input))

    if not args.output:
        raise Exception("please provide an output file name for data export")


    if args.output and args.verbose:
        print("* exporting pickle to: {}".format(args.output))
    
    if not args.procs:
        args.procs=4

    if not path.isdir(args.input):
        raise Exception("Please provide a valid input directory")

    if args.verbose: print("* calling parallel processing function, using {} processors".format(args.procs))

    data = processDataSet_parallel(
            args.input,
            nProcs=args.procs,
            verbose=args.verbose,
            substractMean=args.substract_mean,
            )

    # remove duplicate indices
    if args.verbose:
        print('* removing duplicate indices')
    data = data.loc[~data.index.duplicated(keep='first')]

    if args.no_gps:
        if args.verbose: print('* removing gps latitude and longitude')
        data.drop(['latitude', 'longitude'], axis=1, inplace=True)

    if args.output:
        if path.isfile(args.output):
            print("*! file already exists, done")
            exit()
        else:
            try:
                data.to_pickle(args.output)
            except Exception as e:
                print("*! failed to export pickle!")
                print("*! -> {}".format(e))

