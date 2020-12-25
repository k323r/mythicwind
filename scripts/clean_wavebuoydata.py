#!/bin/python3

VERSION=0.1

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

    parser.add_argument("-v", "--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument('-if', '--input-files', nargs='+', help='input: single file or list of files')
    parser.add_argument("-i", "--input", help="input directory containing wave files", type=str)
    parser.add_argument("-o", "--output", help="name of output pickle file", type=str, required=True)
    parser.add_argument("-g", "--glob", help="glob pattern to select wave files, default is *.xls*", default='*.xls*')

    # parse arguments
    args = parser.parse_args()
    
    if args.verbose: print("* verbose: on")
    if args.verbose: print("* mythicwind v{}".format(VERSION))

    if not args.input:
        if args.verbose: print("* setting input directory to cwd")
        args.input=path.curdir

    if not args.output:
        raise Exception("please provide an output pickle name")

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

    try:
        waves.to_pickle(args.output)
    except Exception as e:
        print('*! failed to export pickle file {} -> {}'.format(args.output, e))


