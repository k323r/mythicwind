#!/bin/python3

### TODO

import sys
from os import path

import numpy as np
from multiprocessing import Pool
from glob import glob
from math import sqrt, log

import argparse
from zipfile import ZipFile

# from ..mythicwind.tom import process_data_set_parallel

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from mythicwind.tom import process_data_set_parallel
from mythicwind.csv_io import export_data, export_data_parallel



def parse_commandline_arguments():

    """
    parse_commandline_arguments

    : return    : parsed argparse object
    """

    parser = argparse.ArgumentParser()
    
    parser.add_argument("--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("--input", help="input directory containing TOMBox log files", type=str)
    parser.add_argument("--output", help="output target directory", type=str)
    parser.add_argument("--output-prefix", help="output file prefix. Default is m", type=str, default='m')
    parser.add_argument("--procs", help="number of processors to use", type=int, default=4)
    parser.add_argument("--substract-mean", help="substract mean values from acceleration", action="store_true", default=True)
    parser.add_argument("--no-gps", help="surpress gps data", action="store_true", default=False)
    parser.add_argument("--normalize-gps", help="surpress gps data", action="store_true", default=False)
    parser.add_argument('--substract-gps', help="tuple of lat and lon to be substracted from the gps data", type=str, default='54,6.5')

    return parser.parse_args()


def run_clean_data():
    pass

    args = parse_commandline_arguments()
    
    if args.verbose: print("* verbose: on")

    # check for empty input directory
    if len(glob(path.join(args.input, "*.txt"))) == 0:
        raise Exception("could not find any *.txt file in {} -> exit".format(args.input))

    if not path.isdir(args.output):
        raise Exception("please provide an output file name for data export")

    if args.output and args.verbose:
        print("* exporting pickle to: {}".format(args.output))
    
    if not args.procs:
        if args.verbose: print(f'setting number of processors to 4')
        args.procs=4

    if not path.isdir(args.input):
        raise Exception("Please provide a valid input directory")

    if args.verbose: print("* calling parallel processing function, using {} processors".format(args.procs))

    data = process_data_set_parallel(
        args.input,
        n_procs=args.procs,
        verbose=args.verbose,
        substract_mean=args.substract_mean,
    )

    # check for empty data frames
    data = [data[frame] for frame in data if not data[frame].empty]
    
    # insert unix epoch (for bartok!) 
    for frame in data:
        frame.insert(
            loc=0,
            column='epoch',
            value=frame.index.astype('int64')/1.0e9
        )

    if args.verbose: print(f'* dropping gpstime')
    for frame in data:
        if not hasattr(frame, 'gpstime'):
            print(f'no gpstime found, skipping')
            continue
        frame.drop(columns='gpstime', inplace=True)

    # parallelize?
    # substract mean for each acceleration component
    if args.substract_mean:
        if args.verbose: print("* substracting mean")
        for frame in data:
            for comp in ("acc_x", "acc_y", "acc_z"):
                try:
                    frame[comp] -= np.mean(frame[comp])
                except:
                    print("*! could not calculate mean, data cleaning needed!")
                    continue

   
    # data is a dictionary now!
    # iterate over dataframes in the data dict
    # normalize gps
    if args.normalize_gps:
        if args.verbose: print('* normalizing gps latitude and longitude')
        for frame in data:
            frame.latitude -= frame.latitude.mean()
            frame.longitude -= frame.longitude.mean()

    if args.substract_gps:
        if args.verbose: print(f'* substracting gps tuple from recorded data: {args.substract_gps}')
        try:
            lat, lon = args.substract_gps.split(',')
        except:
            raise Exception(f'failed to parse gps tuple {args.substract_gps}')

        try:
            lat = float(lat)
            lon = float(lon)
        except:
            print('failed to cast float from command line tuple')

        for frame in data:
            frame.latitude -= lat
            frame.longitude -= lon

    # remove gps
    if args.no_gps:
        if args.verbose: print('* removing gps latitude and longitude')
        for frame in data:
            frame.drop(['latitude', 'longitude'], axis=1, inplace=True)

    if args.procs == 1:
        export_data(data, args)
    elif args.procs > 1:
        export_data_parallel(data, args)

    return data

if __name__ == '__main__':

    data = run_clean_data()