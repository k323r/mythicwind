#!/bin/python3

### TODO

VERSION=0.1


from bikbox import *

from glob import glob

import argparse
from os import path
from zipfile import ZipFile

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

        # I/O arguments
    parser.add_argument("-v", "--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument('-i', '--input', nargs='+', help='input: single file or list of files')
    parser.add_argument("-o", "--output", help="name of output pickle file", type=str)
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
    parser.add_argument("--filter-lower-frequency", help="lower cutoff filter frequency, default is 0.1 Hz", default=0.1, type=float)
    parser.add_argument("--filter-upper-frequency", help="upper cutoff filter frequency, default is 1 Hz", default=1, type=float)
    parser.add_argument("--filter-frequency", help="filter frequency, default is 30 Hz", default=30, type=float)
    parser.add_argument("--filter-order", help="filter order, dedfault is 3", default=3, type=int)
    parser.add_argument("--calculate-deflection", help="calculate acceleration magnitude, default is True", default=True)
    parser.add_argument("--calculate-direction", help="calculate direction of oscillation, default is False", action="store_true", default=False)
    parser.add_argument("--magnetic-correction", help="correction oscillation direction by using the magnetic field. EXPERIMENTAL!, default is False", action="store_true")
    parser.add_argument("--check-duplicate-indices", help="checks for duplicated indices", action="store_true")

    # parse arguments
    args = parser.parse_args()
    
    if args.verbose: print("* verbose: on")
    if args.verbose: print("* TOMTool v{}".format(VERSION))

    if not args.input:
        raise Exception("*! please provide input data!")

    if not args.output:
        raise Exception("*! please provide an output file name for data export")

    if args.output and args.verbose:
        print("* exporting pickle to: {}".format(args.output))
    
    if not args.procs:
        args.procs=4

    input_files = list()
    
    for f in args.input:
        if path.isfile(f):
            input_files.append(f)

    try:
        data = pd.concat([pd.read_pickle(tt) for tt in sorted(input_files)])
        # data = pd.read_pickle(args.input)
    except Exception as e:
        print("*! could not read data")
        print("*! -> {}".format(e))
        exit()

    if args.check_duplicate_indices:
        if args.verbose: print("* checking for duplicate indices")
        data = data.loc[~data.index.duplicated(keep="first")]

    if args.verbose: print("* calling parallel processing function, using {} processors".format(args.procs))
    # apply resampling, filtering and integration

    if args.procs > 1:
        integral = applyIntegration_parallel(data,
                                             verbose=args.verbose,
                                             integrationInterval=args.integration_interval,
                                             nProcs=args.procs,
                                             resampleInterval=args.resample_interval,
                                             filterLowCut=args.filter_lower_frequency,
                                             filterHighCut=args.filter_upper_frequency,
                                             filterFrequency=args.filter_frequency,
                                             filterOrder=args.filter_order,
                                             calculateDeflection=args.calculate_deflection,
                                            )
    else:
        integral = applyIntegration(data,
                                    verbose=args.verbose,
                                    integrationInterval=args.integration_interval,
                                    resampleInterval=args.resample_interval,
                                    filterLowCut=args.filter_lower_frequency,
                                    filterHighCut=args.filter_upper_frequency,
                                    filterFrequency=args.filter_frequency,
                                    filterOrder=args.filter_order,
                                    calculateDeflection=args.calculate_deflection,
                                   )


    try:
        if args.verbose: print("* exporting pickle: {}".format(args.output))
        integral.to_pickle(args.output)
    except Exception as e:
        print("* could not export data as pickle")
        print("*! -> {}".format(e))


