#!/bin/python3

VERSION=0.1
LIBPATH='../yasb'

import sys
from os import getcwd as cwd
import os.path as path

sys.path.insert(0, "/home/san/data/Turmschwingungen/src/library")

from bikbox import *
from LIDAR import *

from glob import glob
from math import sqrt, log

import argparse
import gc

from datetime import timedelta

waves_times = list()
lidar_times = list()
tom_times = list()

t10 = list()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("-o", "--output", help="output pickle path", type=str)
    parser.add_argument("-w", "--waves", help="wave data pickle", type=str)
    parser.add_argument("-l", "--lidar", help="lidar data pickle", type=str)
    parser.add_argument("-t", "--tom", help="tom box data pickle", type=str)
    parser.add_argument("--auto-times", help='determine start and end time automatically', action="store_true")
    parser.add_argument("--start", help="start time", type=str) 
    parser.add_argument("--end", help="end time", type=str) 
    parser.add_argument("--timezone", help="time zone of the data", default="Europe/Berlin")
    parser.add_argument("--lidar-return-level", type=str, default="3")
    parser.add_argument("-r", "--resample-interval", help="resample interval used to unify waves, lidar and tom box data. default 33 ms", default='33 ms')
    parser.add_argument("-s", "--search-window", help="temporal search window to align data. Default 10 min", default='10 min')

    # parse arguments
    args = parser.parse_args()
    
    if args.verbose: print("* verbose: on")
    if args.verbose: print("* TOMTool v{}".format(VERSION))

    if not args.tom:
        raise Exception('*! please provide a tom pickle')

    if not args.waves:
        raise Exception('*! please provide a wave pickle file')

    if not args.lidar:
        raise Exception('*! please provide a lidar pickle file')

    if not args.output:
        raise Exception('*! please provide an output pickle file')

    if not args.start and not args.auto_times:
        raise Exception('*! please provide a start time')

    if not args.end and not args.auto_times:
        raise Exception('*! please provide a end time')

    try:
        tom = pd.read_pickle(args.tom)
    except Exception as e:
        print ('*! failed to read in tom pickle: {}'.format(e)) 

    if args.auto_times:
        if args.verbose: print("* using search window to determine start and end time")
        times = [tt[0] for tt in tom.resample(args.search_window)]
        start_time = times[1]
        end_time = times[-2]
        if args.verbose: print("* start time: {} -> end time: {}".format(start_time, end_time))
    else:
        try:
            start_time = pd.to_datetime(args.start).tz_localize(args.timezone)
        except Exception as e:
            print("*! failed to parse star time: {}".format(e))
        try:
            end_time = pd.to_datetime(args.end).tz_localize(args.timezone)
        except Exception as e:
            print("*! failed to parse star time: {}".format(e))

    try:
        waves = pd.read_pickle(args.waves)
    except Exception as e:
        print ('*! failed to read in tom pickle: {}'.format(e))
 
    try:
        lidar = pd.read_pickle(args.lidar)
    except Exception as e:
        print ('*! failed to read in tom pickle: {}'.format(e))

    # only keep neccessary value: pos_x, pos_y, pos_z, deflection, ws_3, dir_3, Hm0, Dirp, Tp, Tz
    
    wind_speed = "wind_speed_{}".format(args.lidar_return_level)
    wind_dir = "wind_dir_{}".format(args.lidar_return_level)
    wind_dir_corrected = "wind_dir_{}_corr".format(args.lidar_return_level)

    lidar = pd.DataFrame({'wind_speed' : lidar[wind_speed],
                          'wind_dir' : lidar[wind_dir],
                          'wind_dir_corr' : lidar[wind_dir_corrected],
                         })

    waves = pd.DataFrame({'Hs' : waves.Hm0,
                          'wave_dir' : waves.Dirp,
                          'wave_spread' : waves.Sprp,
                          'Tz' : waves.Tz,
                          'Tp' : waves.Tp,
                         })

    tom = pd.DataFrame({'acc_x' : tom.acc_xrf,
                        'acc_y' : tom.acc_yrf,
                        'acc_z' : tom.acc_zrf,
                        'vel_x' : tom.vel_x,
                        'vel_y' : tom.vel_y,
                        'vel_z' : tom.vel_z,
                        'pos_x' : tom.pos_x,
                        'pos_y' : tom.pos_y,
                        'pos_z' : tom.pos_z,
                        'deflection' : tom.deflection,
                       })
    # get available time intervals

    if args.verbose:
        print('* selecting times: {} -> {}'.format(start_time, end_time))
    
    # remove duplicate indices
    tom = tom.loc[~tom.index.duplicated(keep='first')]
    lidar = lidar.loc[~lidar.index.duplicated(keep='first')]
    waves = waves.loc[~waves.index.duplicated(keep='first')]

    tom = tom[start_time:end_time]
    lidar = lidar[start_time:end_time]
    waves = waves[start_time:end_time]
    
    # iterate over the given selection in 10 minute windows and only select windows with at 
    # least 100 data points. store time tuples where more than 100 data points are available
    # in a tuple

    for t, d in tom.resample('10min'):
        if len(d) > 100:
            tom_times.append((t, t + timedelta(minutes=10)))
            if args.verbose: print('* adding to selection: {}'.format(tom_times[-1]))

    if args.verbose: print('* start {} stop {}'.format(tom_times[0][0], tom_times[-1][1]))

    # resample waves! to match the search intervall
    waves = waves.resample('10min').ffill()

    # iterate over times and build start stop pairs
    for start, stop in tom_times:
        if args.verbose: print('* processing interval: {} {}'.format(start, stop))

        try:
            if not lidar[start:stop].empty:
                # TODO implement gradient detection!

                lidar_times.append((start, stop))
        except:
            if args.verbose: print ('*! no lidar data found {} {}'.format(start, stop))
            continue

        try:
            if not waves[start:stop].empty:
                waves_times.append((start, stop))
        except:
            if args.verbose: print ('*! no wave data found {} {}'.format(start, stop))
            continue

    # use python sets to extract all common time tuples
    if args.verbose: print('* creating index sets')
    # build sets of common time intervalls
    waves_times = set(waves_times)
    lidar_times = set(lidar_times)

    # use set intersections to select only the time tuples contained in all data sets
    if args.verbose: print('* select data based on set intersection ')
    tom_selection = pd.concat([tom[start:stop] for start, stop in lidar_times.intersection(waves_times)])
    lidar_selection = pd.concat([lidar[start:stop] for start, stop in lidar_times.intersection(waves_times)])
    waves_selection = pd.concat([waves[start:stop] for start, stop in lidar_times.intersection(waves_times)])

    del(tom)
    del(lidar)
    del(waves)
    gc.collect()

    # sort the dataframes again, as the time tuples from the set are not in order !
    if args.verbose: print('* sort dataframes')
    tom_selection.sort_index(inplace=True)
    lidar_selection.sort_index(inplace=True)
    waves_selection.sort_index(inplace=True)

    # remove duplicate indices
    if args.verbose: print('* remove duplicate indices')
    tom_selection = tom_selection.loc[~tom_selection.index.duplicated(keep='first')]
    lidar_selection = lidar_selection.loc[~lidar_selection.index.duplicated(keep='first')]
    waves_selection = waves_selection.loc[~waves_selection.index.duplicated(keep='first')]

    # resample data
    if args.verbose: print('* resampling data to {}'.format(args.resample_interval))
    tom_selection = tom_selection.resample(args.resample_interval).ffill()
    lidar_selection = lidar_selection.resample(args.resample_interval).ffill()
    waves_selection = waves_selection.resample(args.resample_interval).ffill()

    # merge data
    if args.verbose: print('* merging dataframes')
    mergedData = pd.merge(tom_selection, lidar_selection, how='inner', left_index=True, right_index=True)
    mergedData = pd.merge(mergedData, waves_selection, how='inner', left_index=True, right_index=True)

    del(waves_selection)
    del(tom_selection)
    del(lidar_selection)
    
    gc.collect()

    # remove all data sections, were the derivative of the deflection is 0
    mergedData.insert(column='deflection_gradient', value=np.gradient(mergedData.deflection), loc=10)
    # mergedData = mergedData.loc[mergedData.deflection_gradient > 0]

    if args.verbose: print('* exporting data')
    if args.output:
        if path.isfile(args.output):
            print("*! file already exists, skipping")
        else:
            try:
                mergedData.to_pickle(args.output)
            except Exception as e:
                print("*! failed to export pickle!")
                print("*! -> {}".format(e))

