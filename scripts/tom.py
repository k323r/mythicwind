import sys
import numpy as np
import pandas as pd
from os import listdir as ls
from IPython.display import display, Markdown, Latex
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.pyplot import cm
from multiprocessing import Pool
from glob import glob
from os import path
import scipy
from scipy import integrate
from scipy.signal import butter, lfilter

# Definition of constants
# matplotlib
PLOTWIDTH = 16
PLOTHEIGHT = 9
DEBUG = False

# deprecated file format format for Data coming from Boxes with old firmware -> depends on number of columns
columns = [
    "time",
    "latitude",
    "longitude",
    "elevation",
    "rot_x",
    "rot_y",
    "rot_z",
    "acc_x",
    "acc_y",
    "acc_z",
    "mag_x",
    "mag_y",
    "mag_z",
    "roll",
    "pitch",
    "yaw",
]

columns2 = [
    "time",
    "runtime",
    "gpstime",
    "latitude",
    "longitude",
    "elevation",
    "rot_x",
    "rot_y",
    "rot_z",
    "acc_x",
    "acc_y",
    "acc_z",
    "mag_x",
    "mag_y",
    "mag_z",
    "roll",
    "pitch",
    "yaw",
]

### Data aggregation and cleaning

def process_data_set_parallel(
    data_set,
    pickle_name = None, 
    pattern = "log_0???.txt", 
    n_procs = 32, 
    verbose=False, 
    substract_mean=True
):

    """
    process_data_set_parallel


    """

    if not path.isdir(data_set):
        print("*! invalid input directory!")
        sys.exit()
    
    if verbose: print("* processing: {}".format(data_set))
   
    cols = check_log_file_version(data_set, [columns, columns2])

    if verbose: print("* file version checked: {}".format(cols))
    
    pool = Pool(n_procs)
    frames = dict()
   
    if verbose: print("* iterating over files")
    
    # iterate over all data files and process each individually
    for dfile in sorted(glob(path.join(data_set, pattern))):
        # process data files via pool of worker threads and append the output to the frames list
        frames[dfile] = pool.apply_async(process_data_file,(dfile, cols, verbose))
    
    # close the pool again
    pool.close()
    pool.join()
    
    if not len(frames) > 0:
        print("*! no files found")
        sys.exit()

    # remove None entries! 

    final_frames = dict()

    for fname in frames:
        try:
            reconstructed_frame= frames[fname].get()
        except:
            print('skipping frame: {}'.format(fname))
            continue
        final_frames[fname] = reconstructed_frame
    
    return final_frames




def check_log_file_version(log_file_dir, cols, verbose=False):
    """

    checks the row length of log_0000.txt in a given directory to parse the log file version
    Two log file versions are available:
    - Version 1: normal log file format
    - Version 2: log including GPS timestamp

    return: the correct columns to use

    """

    # find a suitable log file
    log_file_path = glob(path.join(log_file_dir, "log_????.txt"))[0]

    if path.isfile(log_file_path):
        with open(log_file_path) as log_file:
            for i, line in enumerate(log_file):
                if i == 3:  # first line = header, second line = overflow from last file -> hence third line used to check for file version
                    if len(line.split(",")) == 18:
                        if verbose: print("* tom file version 2")
                        return cols[1]
                    elif len(line.split(",")) == 16:
                        if verbose: print("* tom file version 1")
                        return cols[0]
                    else:
                        print("wrong number of columns in file {}".format(log_file_path))
                    break
    else:
        raise Exception("no such file or directory: {}".format(log_file_path))



def process_data_file(data_file, cols=columns2, verbose=False):
    """
    process_data_file


    """    
    
    
    if not path.isfile(data_file):
        print("not a file: {}, skipping".format(data_file))
        return pd.DataFrame()
    
    temp_data = read_log_file(data_file, verbose=verbose, columns=cols)
    
    if temp_data.empty:
        print("skipping corrupt file: {}".format(data_file))
        return pd.DataFrame()
    
    temp_data = clean_data_frame(temp_data, verbose=verbose)        # clean it -> generate index, etc.

    if not temp_data.empty:                     # append the dataframes to the global dataframe
        return temp_data
    else:
        return pd.DataFrame()



def read_log_file(
    log_file_path,
    columns=columns,
    skip_header=3,
    verbose=False,
    low_memory=True,
    error_on_bad_line=False,
    engine="python",
):
    """
    readlog_file(log_file_path, columns=columns, skipheader=2, skipfooter=1):

    opens the given path, tries to read in the data, convert it to a dataframe
    and append it.

    returns a dataframe containing the data from a given csv file
    """

    if verbose: print("processing file: {}".format(log_file_path))

    if not path.isfile(log_file_path):
        print("no such file: {} -> skipping".format(log_file_path))
        return pd.DataFrame()

    try:
        temp_data_frame = pd.read_csv(
            log_file_path,
            skiprows=skip_header,
            names=columns,
            low_memory=low_memory,
            error_bad_lines=error_on_bad_line,
            skipfooter=1,
            engine=engine,
            )

    except:
        print("could not process file: {}, skipping".format(log_file_path))
        return pd.DataFrame()

    if verbose: print(temp_data_frame.info())
    
    return temp_data_frame





def clean_data_frame(
    df,
    verbose=False,
    time_zone="Europe/Berlin",
):

    """
    clean_data_frame
    """

    if df.empty:
        print("empty dataframe, skipping!")
        return pd.DataFrame()

    # convert relevant columns to strings

    if verbose: print("cleaning NaNs")
    df.fillna(method="ffill", inplace=True)

    if verbose: print("converting timestamps")
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)

    if verbose: print("converting timestamps to index")
    df.set_index("time", inplace=True)

    if verbose: print("correcting time stamp via GPS")
    if len(df.columns) == 17: # only log file version to is egligible to gps time correction
        if not GPS_date_time_correction(df, verbose=verbose):
            return None   # returning an empty data frame will cause failure somewhere else..

    if time_zone:
        if verbose: print("converting time zone to: {}".format(time_zone))
        try:
            df.index = df.index.tz_convert(time_zone)
        except:
            print("could not convert time zone to {}".format(time_zone))

    if verbose: print("dropping duplicate indices")
    df = df.loc[~df.index.duplicated(keep='first')]   

    return df

### new parallel processing of log_files


def GPS_date_time_correction(df, verbose=False):

    """
    this function extracts the last valid time stamp and the corresponding run time of the box
    and corrects the time index of the given data frame
    """

    try:

        """
        this method has a know edge case: if the last available time stamp has a time lock, 
        but no date lock, the time stamp might look something like this: 
        
        2000-00-00-12-13-14

        which fails later in the programm when trying to generate a valid datetime object from
        the time stamp (line 482). This is currently caught via an exception, however, this is far from ideal.
        As there is currently no easy fix, the whole concept should be re-evaluated
        """

        last_unique_GPS_time_stamp = pd.unique(             # multiple instance of a time stamp may be avaiable
            df.loc[                                         # get the time stamp values
                (df.gpstime != "0000-00-00-00-00-00") &     # where the time stamp is not 0000-00-00-00-00-00
                (df.gpstime != "2000-00-00-00-00-00")       # and where the time stamp is not 2000-00-00-00-00-00
                ].gpstime)[-1]                              # get the last entry
    except:
        print("no GPS time stamp available, skipping")
        return False

    # get the first line where the last unique time stamp is present
    run_time_at_last_GPS_time_stamp = df.loc[df.gpstime == last_unique_GPS_time_stamp].runtime[0] / 1000.0  # convert to seconds!
    
    # get the very first value of the run time and convert to seconds
    run_time_zero = df.runtime[0]/1000.0

    # calculate seconds since device was turned on
    delta_run_time = run_time_at_last_GPS_time_stamp - run_time_zero

    if verbose: print("found time stamp: {} runtime: {}, run time since beginning: {}".format(last_unique_GPS_time_stamp, 
                                                                                              run_time_at_last_GPS_time_stamp, 
                                                                                              (run_time_at_last_GPS_time_stamp - run_time_zero)))
    date = last_unique_GPS_time_stamp.split("-")[:3]
    time = last_unique_GPS_time_stamp.split("-")[3:]
    
    # try to convert the time stamp into a unix epoch
    try:
        gps_date_time_epoch = pd.to_datetime("{} {}".format("-".join(date), ":".join(time)), utc=True).value / 10**9
    except Exception as e:
        print("failed to generate gpsDateTime for {} : {}: {}".format(date, time, e))
        print("skipping dataframe")
        return False
    
    if verbose: print("correcting time")

    # apply time correction
    if correct_time(df, delta_run_time=delta_run_time, gps_time_stamp_epoch=gps_date_time_epoch):
        return True
    else:
        print("failed to apply GPS time correction, skipping file")
        return False



def correct_time(df, delta_run_time, gps_time_stamp_epoch, verbose=False):

    # calculate the approximate time stamp at which the device was turned on
    power_on_time_unix = gps_time_stamp_epoch - delta_run_time

    # convert it to a date time object
    power_on_time = pd.to_datetime(power_on_time_unix, unit="s", utc=True)

    if verbose: print("power on time: {}".format(power_on_time))

    # substract the current first time stamp from the complete time series
    # and add the estimated power-on time:
    corrected_time = (df.index - df.index[0]) + power_on_time

    if verbose: print("corrected power on time series: {}".format(corrected_time))
    if verbose: print("inserting as new index.. ")

    df.reset_index()
    df.insert(loc=0, column="truetime", value=corrected_time)
    try:
        df.set_index("truetime", inplace=True)
    except:
        print('failed to set index')
        return False

    if verbose: print(df.head())
    if verbose: print("done")
    return True
