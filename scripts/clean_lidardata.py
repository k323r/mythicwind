#!/bin/python3

VERSION=0.1

import sys
# sys.path.insert(0, "/home/san/data/Turmschwingungen/src/library")


from glob import glob
from math import sqrt, log

import pandas as pd
import numpy as np

from multiprocessing import Pool

import argparse
from os import path
from zipfile import ZipFile

inputfiles = list()


def generateKeys():
    """

    generates and returns a dictionary containing the original columns names from the
    LIDAR file as values and the currently used column names as corresponding keys

    wind_speed_1  : Speed Value.1
    wind_wind_dir_1 : Direction Value.1
    height_1   : Node RT01 Lidar Height

    """

    keys = {"wind_speed_0" : "Speed Value", "wind_dir_0" : "Direction Value", "height_0" : "Node RT00 Lidar Height"}
    for i in range(1, 11):
        keys.update({"wind_speed_{}".format(i) : "Speed Value.{}".format(i),
                     "wind_dir_{}".format(i) : "Direction Value.{}".format(i),
                     "height_{}".format(i) : "Node RT{:02d} Lidar Height".format(i+1),
                    })
    return keys

def generateDateTime(df):
    """

    combines date and time from the LIDAR file and returns a new datetime index

    """

    tempD = df.date.apply(lambda x: "-".join(reversed(x.split("/"))))
    return tempD + " " + df.time

def correctHeading(x, headingCorrection):

    """

    corrects a given column of directional data with the given headingCorrection

    """

    if x + headingCorrection > 360:
        return (x + headingCorrection) - 360
    else:
        return x + headingCorrection

def processLIDARFile(lidarFile, keys, verbose=False, lidarLevels=(0, 10)):

    """

    reads in a lidar file in csv format, parses out wind speed, wind direction
    and return point altitude

    returns a single dict with the datestring as key and the pandas dataframe as value

    lidarFile: Path to a valid LIDAR file
    keys: dictionary containing the columns from the lidarFile to be used
    verbose: switch to activate detailled output
    lidarLevels: range of lidar return levels to be processed

    """

    if verbose: print("*    reading in file...")
    try:
        rawData = pd.read_csv(lidarFile, low_memory=False)
    except Exception as e:
        print('*! failed to read in file, skipping {} -> {}'.format(lidarFile, e))
        return pd.DataFrame()

    if verbose: print("*    done")
    cleanData = pd.DataFrame()

    if verbose: print("*    iterating over lidar return levels:")

    for i in range(lidarLevels[0], lidarLevels[1]+1):
        if verbose: print("*    lidar level {}".format(i))
        # extract wind speed (ws), direction (dir) and the height of the lidar return point (h)
        cleanData.insert(column="wind_speed_{}".format(i),
                         value=rawData[keys["wind_speed_{}".format(i)]].copy(),
                         loc=len(cleanData.columns)
                        )
        cleanData.insert(column="wind_dir_{}".format(i),
                         value=rawData[keys["wind_dir_{}".format(i)]].copy(),
                         loc=len(cleanData.columns)
                        )
        cleanData.insert(column="wind_dir_{}_corr".format(i),
                         value=rawData[keys["wind_dir_{}".format(i)]].copy(),
                         loc=len(cleanData.columns)
                        )
        cleanData.insert(column="height_{}".format(i),
                         value=rawData[keys["height_{}".format(i)]].copy(),
                         loc=len(cleanData.columns)
                        )

    if verbose: print("*    adding heading")
    cleanData.insert(column="heading",
                     value=rawData["Ships Gyro 1 Value"],
                     loc=len(cleanData.columns)
                    )

    if verbose: print("*    adding time/date")
    cleanData.insert(column="time",
                     value=rawData.Time,
                     loc=0
                    )
    cleanData.insert(column="date",
                     value=rawData.Date,
                     loc=0
                    )

    dateString = "-".join(reversed(cleanData.date[2].split("/")))

    return {dateString : cleanData}

def cleanLIDARData(data, verbose=False, timezone='Europe/Berlin'):

    """
    
    takes a pandas dataframe as input and performs various numerical operations on it:
    - dropping non numeric data lines
    - creating a time zone aware index
    - setting the time zone to Europe/Berlin
    - converting to numeric data
    - cleaning of NaNs

    """

    if verbose: print("* processing: {}".format('-'.join(reversed(data.date[2].split('/')))))

    if verbose: print("*    dropping non-parsable lines")
    # mitigate weird error: in some files, the header appears randomly
    data.drop(data.loc[data.date == "Date"].index, inplace=True)

    if verbose: print("*    creating new UTC time index")
    # create a new date time index with the format YYYY-MM-DD HH:MM:SS
    try:
        data.insert(column="datetime",
                       value=pd.to_datetime(generateDateTime(data), utc=True),
                       loc=0
                      )
    except Exception as e:
        print('*! failed to generate datetime index, skipping')
        return pd.DataFrame()

    data.set_index("datetime", inplace=True)

    if verbose: print("*    setting time zone to {}".format(timezone))
    data.index = data.index.tz_convert(timezone)

    # remove old columns
    if verbose: print("*    dropping old columns")
    data.drop(columns=["date", "time"], inplace=True)

    # convert all remaining columns to numeric data
    if verbose: print("*    converting to numeric data")
    for c in data.columns:
        try:
            data[c] = pd.to_numeric(data[c])
        except Exception as e:
            print('*! failed to generate numeric value for {} at {}.. skipping'.format(c,data.index[0]))
            continue

    # convert non-physical values (999.9, -60.0) to NaNs
    if verbose: print("*    replacing NaNs")
    data.replace(999.9, np.NaN, inplace=True)
    data.replace(-60.0, np.NaN, inplace=True)

    # replace NaNs
    data.fillna(method="pad", inplace=True)

    if verbose: print("\n")

    return data


def cleanLIDARDays(days, verbose=False, timezone='Europe/Berlin'):

    """

    iterates over a dict of days and performs various cleaning and cleansing
    tasks on the data:
    - dropping non numeric data lines
    - creating a time zone aware index
    - setting the time zone to Europe/Berlin
    - converting to numeric data
    - cleaning of NaNs

    """

    for k in sorted(days):
        try:
            cleanLIDARData(days[k], verbose=verbose, timezone=timezone)
        except Exception as e:
            print('*! failed to clean LIDAR data for day {} -> {} -> skipping'.format(k, e))
            continue

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-if', '--input-files', nargs='+', help='input: single file or list of files')
    parser.add_argument("-v", "--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("-o", "--output-dir", help="name of output directory", type=str)
    parser.add_argument("-og", "--output-global", help="used to export the global data frame", type=str)
    parser.add_argument("-i", "--input-dir", help="name of input directory", type=str)
    parser.add_argument("-j", "--procs", help="number of processor to use", type=int, default=8)
    parser.add_argument("-p", "--lidar-pattern", help="glob pattern to select the files containing lidar data. If not provided, genLIDARPickle defaults to *.csv", type=str, default="*.csv")

    # parse arguments
    args = parser.parse_args()
    
    if args.verbose: print("* verbose: on")
    if args.verbose: print("* genLIDARPickle.py v{}".format(VERSION))

    """
    if not args.input_dir and not args.input_files:
        print("* setting input directory to cwd")
        args.input_dir=path.curdir
    """

    if not args.output_dir:
        raise Exception("*! please provide an output directory name")

    if not path.isdir(args.output_dir):
        raise Exception("*! not a directory: {}".format(args.output_dir))
    
    if not args.input_dir and not args.input_files:
        raise Exception("*! Please provide a valid input directory or a list of files to process")

    if args.input_files:
        for f in args.input_files:
            if path.isfile(f):
                inputfiles.append(f)
    else:
        inputfiles = glob(path.join(args.input_dir, args.lidar_pattern))
        inputfiles = [f for f in inputfiles if path.isfile(f)]

    ### main logic
    
    pool = Pool(args.procs)
    frames = list()
    days = dict()

    keys = generateKeys()


    for lidarFile in inputfiles:
        frames.append(
                pool.apply_async(
                    processLIDARFile, (lidarFile, keys, args.verbose)))

    for lidardict in [d.get() for d in frames]:
        days.update(lidardict)
   
    # ckeck for empty dataframes:
    for day in days:
        if days[day].empty:
            if args.verbose:
                print('* found empty data frame: {}, deleting'.format(day))
            del(days[day])

    frames = list() 

    for day in sorted(days):
        frames.append(
                pool.apply_async(
                    cleanLIDARData, (days[day], args.verbose)))

    frames = pd.concat([d.get() for d in frames])

    for i in range(0, 11):
        key = "wind_dir_{}_corr".format(i)
        if args.verbose: print("*       correcting for vessel heading for each lidar level {}".format(i))
        ### list comprehension faster? -> yes
        frames[key] = [correctHeading(x, y) for x, y in zip(frames[key], frames["heading"])]

    # delete duplicate indices
    if args.verbose: print('* deleting duplicated indices')
    frames = frames.loc[~frames.index.duplicated(keep='first')]

    # resample to 1 s for datetime selection
    if args.verbose: print('* resampling to 1 s')
    frames = frames.asfreq('1s', fill_value=np.nan)

    # drop nans
    if args.verbose: print('* dropping NaNs')
    frames.dropna(inplace=True)

    if args.verbose: print("* saving pickles")
    for day, data in frames.groupby(pd.Grouper(freq='D')):
        if not len(data) > 600:         # 10 min
            if args.verbose: print('* skipping day: {}'.format(day))
            continue
        datestring = '{:04d}-{:02d}-{:02d}'.format(day.year, day.month, day.day)
        exportPickle = path.join(args.output_dir, "{}_LIDAR.pickle".format(datestring))
        if args.verbose: print("*   exporting {}".format(exportPickle))
        try:
            data.to_pickle(exportPickle)
        except:
            print("*! failed to export data as pickles")

    if args.output_global:
        if args.verbose: print('* saving global pickle')
        try:
            frames.to_pickle(args.output_global)
        except Exception as e:
            print('*! failed to export global frame {}'.format(e))

