#!/bin/python3

# import sys
# sys.path.insert(0, "/home/san/data/Turmschwingungen/src/library")

from glob import glob
from math import sqrt, log

import argparse
from os import path

import pandas as pd

inputfiles = list()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("--input-files", nargs='+', help='input: single file or list of files')
    parser.add_argument("--input", help="input directory containing wave files", type=str)
    parser.add_argument("--output-dir", help="name of output directory for csv files", type=str, required=True)
    parser.add_argument("--output-prefix", help="output prefix string prepended to the output files", type=str, default='wavebuoy')
    parser.add_argument("--global-output", help="name of global output csv file", type=str)
    parser.add_argument("--glob", help="glob pattern to select wave files, default is *.xls*", default='*.xls*')

    # parse arguments
    args = parser.parse_args()
    
    if args.verbose: print("* verbose: on")

    if not args.input:
        if args.verbose: print("* setting input directory to cwd")
        args.input=path.curdir

    if not path.isdir(args.output_dir):
        raise Exception("please provide an output directory")

    if not path.isdir(args.input) and not args.input_files:
        raise Exception("Please provide a valid input directory or input files")

    if args.input_files:
        for f in args.input_files:
            if path.isfile(f):
                inputfiles.append(f)
    else:
        inputfiles = glob(path.join(args.input, args.glob))
        inputfiles = [f for f in inputfiles if path.isfile(f)]

    frames = list()
    # iterate over the input dir and read in wave files
    for f in inputfiles:
        if args.verbose: print('* reading in file {}'.format(f))
        try:
            frames.append(pd.read_excel(f))
        except Exception as e:
            print('*! failed to read file {} -> {}'.format(f,e))
            continue

    waves = pd.concat(frames)
    waves.insert(column="time", value=pd.to_datetime(waves["Zeitpunkt gerundet"]), loc=0)
    waves.set_index("time", inplace=True)
    waves.index = waves.index.tz_localize("Europe/Berlin")

    # Sort by index
    waves.sort_index(inplace=True)

    # remove NaNs
    waves.fillna(method='ffill', inplace=True)

    # remove duplicates
    waves = waves[~waves.duplicated(keep='first')]

    # convert significant wave height from cm -> m
    waves.Hm0 = waves.Hm0.apply(lambda x: x/100.0)
    waves['H(1/10)'] = waves['H(1/10)'].apply(lambda x: x/100.0)
    waves['H(1/3)'] = waves['H(1/3)'].apply(lambda x: x/100.0)
    waves.Hmax = waves.Hmax.apply(lambda x: x/100.0)

    # insert an epoch timestamp 
    waves.insert(loc=0,
                 column='epoch',
                 value=waves.index.astype('int64')/1e9
                )

    for day, data in waves.groupby(pd.Grouper(freq='D')):
        if not len(data) > 2:         # 1 hour
            if args.verbose: print('* skipping day: {}'.format(day))
            continue
        datestring = '{:04d}-{:02d}-{:02d}'.format(day.year, day.month, day.day)

        export_csv_path = path.join(args.output_dir, f'{args.output_prefix}_{datestring}.csv')

        if args.verbose: print("* exporting {}".format(export_csv_path))

        try:
            data.to_csv(export_csv_path)
        except:
            print("*! failed to export data as csv")

    if args.global_output:
        if args.verbose: print(f'* saving global csv {args.global_output}')
        export_csv_path_global = path.join(args.output_dir, args.global_output)
        try:
            waves.to_csv(export_csv_path_global)
        except Exception as e:
            print('*! failed to export global frame {}'.format(args.output_global))
