#!/bin/python3

import sys
from os import path

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from mythicwind.csv_io import read_frames_parallel, export_data_parallel, export_data
from mythicwind.postprocess import resample_filter_integrate_accelerations
import pandas as pd
from glob import glob

from multiprocessing import Pool

import argparse

from zipfile import ZipFile

def parse_commandline_arguments():
    parser = argparse.ArgumentParser()
    
    # I/O arguments
    parser.add_argument("--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("--input", help='input: directory cotaining data files')
    parser.add_argument("--input-file-pattern", help='pattern to select input files. Default: *.csv', type=str, default='*.csv')
    parser.add_argument("--output", help="output: directory for output files", type=str)
    parser.add_argument("--output-prefix", help="output file prefix. Default is acc-vel-pos", type=str, default='acc-vel-pos')
    parser.add_argument("--procs", help="number of processors to use", type=int)

    # processing 
    parser.add_argument("-m", "--substract-mean", help="substract mean values from acceleration", action="store_true")
    parser.add_argument("--integration-interval", help="saddle point to restart integration to ensure numerical stability, default is None (ignore)", default=None, type=str)
    parser.add_argument("--resample", help="resample flag, default is True", default=True)
    parser.add_argument("--resample-interval", help="resample frequency, default is 33ms", default="33ms", type=str)

    parser.add_argument("--filter-lower-frequency", help="lower cutoff filter frequency, default is 0.1 Hz", default=0.1, type=float)
    parser.add_argument("--filter-frequency", help="filter frequency, default is 30 Hz", default=30, type=float)
    parser.add_argument("--filter-order", help="filter order, dedfault is 3", default=3, type=int)
    parser.add_argument("--filter-pad-method", help="the padding method to be used when applying the filter", default="even", type=str)
    parser.add_argument("--filter-pad-length", help="number of elements to be padded to the signal prior to filtering", default=5000, type=int)

    # parse arguments
    return (parser.parse_args())   


def run_postprocessing(args):

    if args.verbose: print("* verbose: on")

    if not path.isdir(args.input):
        raise Exception("*! please provide a valid input data directory!")

    if not path.isdir(args.output):
        raise Exception("*! please provide an output data directory for data export")

    if args.output and args.verbose:
        print("* exporting data to: {}".format(args.output))
    
    if not args.procs:
        args.procs=4

    results = list()
    
    dataframes = read_frames_parallel(args.input, args.input_file_pattern, n_procs=args.procs)

    # if run with a single core
    if args.procs == 1:

        for df in dataframes:
            results.append(resample_filter_integrate_accelerations(df, args))
    
    # multicore
    else:
        pool = Pool(args.procs)
        if args.verbose: print("* iterating over files")
    
        # iterate over all data files and process each individually
        for df in dataframes:
            # process data files via pool of worker threads and append the output to the frames list
            results.append(
                pool.apply_async(
                    resample_filter_integrate_accelerations,
                    (df, args)
                )
            )
    
        # close the pool again
        pool.close()
        pool.join()

        # iterate over the results from the integration and reconstruct the single dataframes
        results = [result.get() for result in results]

    return (dataframes, results)

if __name__ == "__main__":
    args = parse_commandline_arguments()
    raw, data  = run_postprocessing(args)
    if args.procs == 1:
        export_data(data, args)
    elif args.procs > 1:
        export_data_parallel(data, args)

