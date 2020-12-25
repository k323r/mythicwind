#!/usr/bin/python3

import pandas as pd
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="xlsx sheet containing the time tracks of the installation")
    parser.add_argument("-o", "--output", help="output file path")
    parser.add_argument("-v", "--verbose", help="verbose flag", action='store_true')

    args = parser.parse_args()

    if not args.input:
        print("*! please provide an input file")
        exit()

    if not args.output:
        print("*! please provide an output file")
        exit()

    if args.verbose: print('* reading in time tracking sheet: {}'.format(args.input))

    try:
        data = pd.read_excel(args.input,
                             converters = {
                                 'Tower Installation Start' : pd.to_datetime,
                                 'Tower Installation End' : pd.to_datetime,
                                 'Nacelle Installation Start' : pd.to_datetime,
                                 'Nacelle Installation End' : pd.to_datetime,
                                 'Blade Installation Start' : pd.to_datetime,
                                 'Blade Installation End' : pd.to_datetime,
                                 },
                            )
    except Exception as e:
        print("*! failed to read in ecxcel file: {}".format(e))
        exit()

    if args.verbose: print('* input file: {}'.format(args.input))

    installationTimes = data[~data['Tower Installation End'].isnull()]
    installationTimes.reset_index(inplace=True)
    # installationTimes['Blade Installation Start'].apply(lambda dt: pd.to_datetime(dt))
    installationTimes.insert(loc=len(installationTimes.columns),
                             column='deltaT TNH Configuration',
                             value=installationTimes['Blade Installation Start'] - installationTimes['Nacelle Installation End'],
                            )

    selectionTNH = pd.DataFrame({'OWEC' : installationTimes['OWEC'],
                                 'Nacelle Installation End' : installationTimes['Nacelle Installation End'],
                                 'Blade Installation Start' : installationTimes['Blade Installation Start'],
                                 'deltaT TNH Configuration' : installationTimes['deltaT TNH Configuration'],
                                })
    try:
        selectionTNH.to_pickle(args.output)
    except Exception as e:
        print('*! failed to export time selection pickle: {}'.format(e))


