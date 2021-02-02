#!/bin/python3

### TODO

from csv_io import read_frames_parallel, write_output_file
from postprocess import resample_acceleration, filter_acceleration, double_integration, g
import pandas as pd
from glob import glob

from multiprocessing import Pool

import argparse
from os import path
from zipfile import ZipFile

def parse_commandline_arguments():
    parser = argparse.ArgumentParser()
    
    # I/O arguments
    parser.add_argument('-v', "--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument('-i', '--input', help='input: directory cotaining data files')
    parser.add_argument('--input-file-pattern', help='pattern to select input files. Default: *.csv', type=str, default='*.csv')
    parser.add_argument("-o", "--output", help="output: directory for output files", type=str)
    parser.add_argument("--output-prefix", help="output file prefix. Default is acceleration-velocity-position", type=str, default='acceleration-velocity-position')
    parser.add_argument("-j", "--procs", help="number of processors to use", type=int)
    parser.add_argument("--dry-run", help="if true, simulates exection without acutal data", default=False, action="store_true")

    # processing 
    parser.add_argument("-m", "--substract-mean", help="substract mean values from acceleration", action="store_true")
    parser.add_argument("-s", "--select-by", help="selection of data based on PARAMETER OPERATOR VALUE, where OPERATOR can be '==', '>', '<', '<=', '>='", default=False, type=tuple)
    parser.add_argument("--integrate", help="integration flag, default is True", default=True)
    parser.add_argument("--integration-interval", help="saddle point to restart integration to ensure numerical stability, default is 10min", default="10min", type=str)
    parser.add_argument("--resample", help="resample flag, default is True", default=True)
    parser.add_argument("--resample-interval", help="resample frequency, default is 33ms", default="33ms", type=str)
    parser.add_argument("--filter", help="filter flag, default is True", default=True)
    parser.add_argument("--filter-type", help="the type of filter to apply", default='band')
    parser.add_argument("--filter-lower-frequency", help="lower cutoff filter frequency, default is 0.1 Hz", default=0.1, type=float)
    parser.add_argument("--filter-upper-frequency", help="upper cutoff filter frequency, default is 1 Hz", default=1, type=float)
    parser.add_argument("--filter-frequency", help="filter frequency, default is 30 Hz", default=30, type=float)
    parser.add_argument("--filter-order", help="filter order, dedfault is 3", default=3, type=int)
    parser.add_argument("--calculate-deflection", help="calculate acceleration magnitude, default is True", default=True)
    parser.add_argument("--calculate-direction", help="calculate direction of oscillation, default is False", action="store_true", default=False)
    parser.add_argument("--magnetic-correction", help="correction oscillation direction by using the magnetic field. EXPERIMENTAL!, default is False", action="store_true")
    parser.add_argument("--check-duplicate-indices", help="checks for duplicated indices", action="store_true")

    # parse arguments
    return (parser.parse_args())   

def export_data(data, args, ):
    pool = Pool(args.procs)
    
    for frame in data:
        # parse name
        frame_start_time = "{:04}-{:02}-{:02}-{:02}-{:02}-{:02}".format(
            frame.index[0].year,
            frame.index[0].month,
            frame.index[0].day,
            frame.index[0].hour,
            frame.index[0].minute,
            frame.index[0].second,
        ) 
        
        frame_end_time = "{:04}-{:02}-{:02}-{:02}-{:02}-{:02}".format(
            frame.index[-1].year,
            frame.index[-1].month,
            frame.index[-1].day,
            frame.index[-1].hour,
            frame.index[-1].minute,
            frame.index[-1].second,
        )

        out_file_name = "{}_{}_{}.csv".format(
            args.output_prefix,
            frame_start_time,
            frame_end_time,
        )
        
        out_file_path = path.join(args.output, out_file_name)
        if args.verbose: print('* exporting data file: {}'.format(out_file_path))

        pool.apply_async(write_output_file, (frame, out_file_path))

    pool.close()
    pool.join()

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

    if args.filter_type not in ('band', 'sos'):
        raise Exception('*! please specifiy either band or sos type filter')

    results = list()
    dataframes = read_frames_parallel(args.input, args.input_file_pattern, n_procs=4)

    if args.procs == 1:

        for df in dataframes:

            df = resample_acceleration(df,
                                       # resample_interval=args.resample_interval, 
                                       verbose=True,
                                      )

            df = filter_acceleration(df,
                                #filter_low_cut=args.filter_lower_frequency,
                                #filter_high_cut=args.filter_upper_frequency,
                                #filter_frequency=args.filter_frequency,
                                #filter_order=args.filter_order,
                                filter_type=args.filter_type, 
                                verbose=True,
                                )

            integrated_data = list()
            for _, d in df.resample(args.integration_interval):
                double_integration(d, verbose=True)
                integrated_data.append(d)
            
            results.append(pd.concat(integrated_data))
    
    else:
        print('* parallel postprocessing not implemented yet')

    return (dataframes, results)

if __name__ == "__main__":
    args = parse_commandline_arguments()
    raw, data  = run_postprocessing(args)
    export_data(data, args)

