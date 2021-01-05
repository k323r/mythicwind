#!/bin/python3

### TODO

from tom import *

from glob import glob
from math import sqrt, log

import argparse
from os import path
from zipfile import ZipFile

def parse_commandline_arguments():

    """
    parse_commandline_arguments

    : return    : parsed argparse object
    """

    parser = argparse.ArgumentParser()
    
    parser.add_argument("--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("--input-dir", help="input directory containing TOMBox log files", type=str)
    parser.add_argument("--output-dir", help="output target directory", type=str)
    parser.add_argument("--output-prefix", help="output file prefix. Default is m", type=str, default='m')
    parser.add_argument("--procs", help="number of processors to use", type=int, default=4)
    parser.add_argument("--substract-mean", help="substract mean values from acceleration", action="store_true", default=True)
    parser.add_argument("--no-gps", help="surpress gps data", action="store_true", default=False)
    parser.add_argument("--normalize-gps", help="surpress gps data", action="store_true", default=False)

    return parser.parse_args()


def run_clean_data():
    pass

    args = parse_commandline_arguments()
    
    if args.verbose: print("* verbose: on")

    # check for empty input directory
    if len(glob(path.join(args.input_dir, "*.txt"))) == 0:
        raise Exception("could not find any *.txt file in {} -> exit".format(args.input_dir))

    if not path.isdir(args.output_dir):
        raise Exception("please provide an output file name for data export")

    if args.output_dir and args.verbose:
        print("* exporting pickle to: {}".format(args.output_dir))
    
    if not args.procs:
        args.procs=4

    if not path.isdir(args.input_dir):
        raise Exception("Please provide a valid input directory")

    if args.verbose: print("* calling parallel processing function, using {} processors".format(args.procs))

    data = process_data_set_parallel(
        args.input_dir,
        n_procs=args.procs,
        verbose=args.verbose,
        substract_mean=args.substract_mean,
    )
    
    # insert unix epoch (for christian!) 
    for frame in data:
        data[frame].insert(
            loc=0,
            column='epoch',
            value=data[frame].index.astype('int64')//1e9
        )
    # parallelize?
    # substract mean for each acceleration component
    if args.substract_mean:
        if args.verbose: print("* substracting mean")
        for dname in data:
            print('processing: {}'.format(dname))
            for comp in ("acc_x", "acc_y", "acc_z"):
                try:
                    data[dname][comp] -= np.mean(data[dname][comp])
                except:
                    print("*! could not calculate mean, data cleaning needed!")
                    continue

   
    # data is a dictionary now!
    # iterate over dataframes in the data dict
    # normalize gps
    if args.normalize_gps:
        if args.verbose: print('* normalizing gps latitude and longitude')
        for frame in data:
            data[frame].latitude -= data[frame].latitude.mean()
            data[frame].longitude -= data[frame].longitude.mean()

    # remove gps
    if args.no_gps:
        if args.verbose: print('* removing gps latitude and longitude')
        for frame in data:
            data[frame].drop(['latitude', 'longitude'], axis=1, inplace=True)

    # output data

    for frame in data:
        # parse name
        old_file_name = frame.split('/')[-1].split('.')[0].split('_')[-1]
        out_file_name = "{}_{}.csv".format(args.output_prefix,  old_file_name)
        out_file_path = path.join(args.output_dir, out_file_name)
        if args.verbose: print('exporting data file: {}'.format(out_file_path))
        try:
            data[frame].to_csv(out_file_path)
        except:
            print('failed to export data - skippig file')
            continue

    return data

if __name__ == '__main__':

    data = run_clean_data()