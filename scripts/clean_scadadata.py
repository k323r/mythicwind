#!/bin/python3

VERSION=0.1

from glob import glob

import argparse
from os import path
from zipfile import ZipFile

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("-i", "--input", help="input scada file", type=str)
    parser.add_argument("-o", "--output", help="name of output pickle file", type=str)

    # parse arguments
    args = parser.parse_args()
    
    if args.verbose: print("* verbose: on")
    if args.verbose: print("* TOMTool v{}".format(VERSION))

    if not args.input:
        raise Exception("please provide an input scada file")

    if not args.output:
        raise Exception("please provide an output pickle name")
    
    if not path.isfile(args.input):
        raise Exception("Please provide a valid input directory")

    try:
        data = pd.read_excel(args.input)
    except:
        print('failed to parse excel file')

