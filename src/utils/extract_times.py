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