import numpy as np
import pandas as pd
from os.path import join as joinPaths
from os.path import isdir
from os.path import isfile
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

def readLogFile(
    logFilePath,
    columns=columns,
    skipheader=3,
    verbose=False,
    lowMemory=True,
    errorOnBadLine=False,
    engine="python",
):
    """
    readLogFile(logFilePath, columns=columns, skipheader=2, skipfooter=1):

    opens the given path, tries to read in the data, convert it to a dataframe
    and append it.

    returns a dataframe containing the data from a given csv file
    """

    if verbose: print("processing file: {}".format(logFilePath))

    if not isfile(logFilePath):
        print("no such file: {} -> skipping".format(logFile))
        return None

    try:
        tempDataFrame = pd.read_csv(
            logFilePath,
            skiprows=skipheader,
            names=columns,
            low_memory=lowMemory,
            error_bad_lines=errorOnBadLine,
            skipfooter=1,
            engine=engine,
            )
        if verbose: print(tempDataFrame.info())

    except:
        print("could not process file: {}, skipping".format(logFilePath))
        return None

    return tempDataFrame

def cleanDataFrame(
    df,
    verbose=False,
    timeZone="Europe/Berlin",
):

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
        if not GPSDateTimeCorrection(df, verbose=False):
            return pd.DataFrame()   # returning an empty data frame will cause failure somewhere else..

    if timeZone:
        try:
            if verbose: print("converting time zone to: {}".format(timeZone))
            df.index = df.index.tz_convert(timeZone)
        except:
            print("could not convert time zone to {}".format(timeZone))

    if verbose: print("dropping duplicate indices")
    df = df.loc[~df.index.duplicated(keep='first')]   

    return df

### new parallel processing of logfiles

def processDataFile(dataFile, cols=columns2, verbose=False):
    
    tempData = pd.DataFrame()
    
    if not isfile(dataFile):
        print("not a file: {}, skipping".format(dataFile))
        return tempData
    
    tempData = readLogFile(dataFile, verbose=verbose, columns=cols)
    
    if tempData.empty:
        print("skipping corrupt file: {}".format(dataFile))
        return pd.DataFrame()
    
    tempData = cleanDataFrame(tempData, verbose=verbose)        # clean it -> generate index, etc.

    if not tempData.empty:                     # append the dataframes to the global dataframe
        return tempData
    
def processDataSet_parallel(dataSet, pickleName=None, pattern = "log_0???.txt", nProcs = 32, verbose=False, substractMean=True):

    if not isdir(dataSet):
        print("*! not a directory, skipping")
        return pd.DataFrame()
    
    if verbose: print("* processing: {}".format(dataSet))
   
    cols = checkLogFileVersion(dataSet, [columns, columns2])

    if verbose: print("* file version checked: {}".format(cols))
    
    pool = Pool(nProcs)
    frames = list()
   
    if verbose: print("* iterating over files")
    for dfile in sorted(glob(path.join(dataSet, pattern))):
          frameData = pool.apply_async(processDataFile,(dfile, cols, verbose))
          frames.append(frameData)

    pool.close()
    pool.join()
    
    if not len(frames) > 0:
        print("*! no files found")
        return pd.DataFrame()

    data = pd.concat([d.get() for d in frames])
  
    if substractMean:
        if verbose: print("* substracting mean")
        for comp in ("acc_x", "acc_y", "acc_z"):
            try:
                data[comp] -= np.mean(data[comp])
            except:
                print("*! could not calculate mean, data cleaning needed!")
                continue

    if pickleName:
        if verbose: print("* exporting pickle {}".format(pickleName))
        try:
            data.to_pickle(path.join(dataSet, "{}".format(pickleName)))
        except:
            print("*! failed to export pickle!")
    
    return data


### Functions for analysis

def fftTimeSeries(data, newFigure=True, label=None):
    """
    performs a fft on the given data and plots it.

    returns peak frequency
    """

    if newFigure:
        plt.figure()
    deltaT = data.index.to_series().diff()
    deltaTMean = np.mean(deltaT) / np.timedelta64(1, 's')
    print(np.mean(deltaT) / np.timedelta64(1, 's'))
    FFT = scipy.fftpack.fft(data)
    PSD = np.abs(FFT) ** 2
    Frequency = scipy.fftpack.fftfreq(len(data), deltaTMean)
    Frequency_i = Frequency > 0

    if label:
        plt.plot(Frequency[Frequency_i], PSD[Frequency_i], label=label)
    else:
        plt.plot(Frequency[Frequency_i], PSD[Frequency_i])

    plt.xlabel("Frequency"); plt.ylabel("Power Spectrum Density")
    return Frequency[np.argmax(PSD)]

def butter_bandpass(lowcut, highcut, fs, order=5):
    """
    generates a butter bandpass filter object
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """
    appliess a butter bandpass filter to the given dataDir
    """
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def integrateVelocityAcceleration(df,
                                  verbose=False,
                                  resampleInterval="30ms",
                                  filterLowCut=0.1,
                                  filterHighCut=1,
                                  filterFrequency=33.333,
                                  filterOrder=3,
                                  calculateDeflection=True,
                                  components = ("x", "y", "z"),
                                  applyG=True,
                                 ):
    g = 9.80665
    
    data = pd.DataFrame()

    """
    1. resample
    2. filter
    3. integrate

    if applyG:
        if verbose: print("> applying g")
        for comp in components:
            df["acc_{}".format(comp)] = df["acc_{}".format(comp)]*g
    
    # add raw components to data frame
    for comp in components:
        data.insert(column="acc_{}".format(comp),
                    value=df["acc_{}".format(comp)],
                    loc=len(data.columns)
                   )
    """
    # resample data
    if verbose: print("*    resampling data to {}. Start time: {}".format(resampleInterval, df.index[0]))
    # resample data and multiply with g!
    for comp in components:
        data.insert(column="acc_{}r".format(comp),
                    value=df["acc_{}".format(comp)].resample(resampleInterval).bfill()*g,
                    loc=len(data.columns)
                   )

    # time ins seconds, resampled -> used for integration
    t = data.index.astype(np.int64)/10**9

     
    if verbose: print("*    applying filter with order = {} frequency = {} lowcut = {} highcut = {}".format(filterOrder,
                                                                                                           filterFrequency,
                                                                                                           filterLowCut,
                                                                                                           filterHighCut,
                                                                                                          ))
    for comp in components:
        data.insert(column="acc_{}rf".format(comp),
                    value=butter_bandpass_filter(data["acc_{}r".format(comp)],
                                                 filterLowCut,
                                                 filterHighCut,
                                                 filterFrequency,
                                                 order=filterOrder),
                    loc=len(data.columns)
                   )


    if verbose: print("*    integrating acceleration")
    for comp in components:
        if verbose: print("*        acceleration {}".format(comp.upper()))
        # integrate filtered acceleration
        data.insert(column="vel_{}".format(comp),
                    value=integrate.cumtrapz(data["acc_{}rf".format(comp)], t, initial=0),
                    loc=len(data.columns)
                   )
    if verbose: print("*    integrating velocity")
    for comp in components:
        if verbose: print("*        velocity {}".format(comp.upper()))
        # integrate velocity to yield position
        data.insert(column="pos_{}".format(comp),
                    value=integrate.cumtrapz(data["vel_{}".format(comp)], t, initial=0),
                    loc=len(data.columns)
                   )
        
    if calculateDeflection:
        if verbose: print("*    calculating deflection")
        data.insert(column = "deflection",
                    value = np.sqrt(np.power(data.pos_z, 2) + np.power(data.pos_x, 2)),
                    loc = len(data.columns),
                   )

    return data

def applyIntegration_parallel(dataset, 
                              verbose=False,
                              nProcs=32,
                              integrationInterval="10min",
                              resampleInterval="30ms",
                              filterLowCut=0.1,
                              filterHighCut=1,
                              filterFrequency=30,
                              filterOrder=3,
                              calculateDeflection=True, 
                              components = ("x", "y", "z"),
                              applyG=True,
                             ):

    # create a pool of workers
    pool = Pool(nProcs)
    frames = list()

    if verbose: print("* integration interval set to {}. Starting integration with {} threads".format(integrationInterval, nProcs))
    ## iterate over the sample intervalls and enable parallel integration
    for t, dataSample in dataset.resample(integrationInterval):

        if verbose: print("* integration start: {}".format(t))

        if dataSample.empty:
            print("* empty integration interval, skipping..")
            continue
        
        frames.append(
            pool.apply_async(
                integrateVelocityAcceleration, (dataSample,
                                                verbose,
                                                resampleInterval,
                                                filterLowCut,
                                                filterHighCut,
                                                filterFrequency,
                                                filterOrder,
                                                calculateDeflection,
                                                components
                                                )))

    pool.close()
    pool.join()

    frames = pd.concat([d.get() for d in frames])
    
    return frames

def applyIntegration(dataset, 
                     verbose=False,
                     integrationInterval="10min",
                     resampleInterval="30ms",
                     filterLowCut=0.1,
                     filterHighCut=1,
                     filterFrequency=30,
                     filterOrder=3,
                     calculateDeflection=True, 
                     components = ("x", "y", "z"),
                     applyG=True,
                    ):
   
    frames = list()

    if verbose: print("* integration interval set to {}".format(integrationInterval))
    ## iterate over the sample intervalls and enable parallel integration
    for t, dataSample in dataset.resample(integrationInterval):
        if verbose: print("* integration start: {}".format(t))
        
        frames.append(integrateVelocityAcceleration(dataSample,
                                                    verbose,
                                                    resampleInterval,
                                                    filterLowCut,
                                                    filterHighCut,
                                                    filterFrequency,
                                                    filterOrder,
                                                    calculateDeflection,
                                                    components
                                                   ))

    frames = pd.concat(frames)
    
    return frames



def correctTime(df, runTime, gpsTimeStamp, verbose=False):

    powerOnTimeUnix = gpsTimeStamp - runTime
    powerOnTime = pd.to_datetime(powerOnTimeUnix, unit="s", utc=True)

    if verbose: print("power on time: {}".format(powerOnTime))

    correctedTime = (df.index - df.index[0]) + powerOnTime

    if verbose: print("corrected power on time series: {}".format(correctedTime))
    if verbose: print("inserting as new index.. ")

    df.reset_index()
    df.insert(loc=0, column="truetime", value=correctedTime)
    df.set_index("truetime", inplace=True)

    if verbose: print(df.head())

    if verbose: print("done")

def GPSDateTimeCorrection(df, verbose=False):

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

        lastUniqueGPSTimeStamp = pd.unique(
                df.loc[(df.gpstime != "0000-00-00-00-00-00") & 
                       (df.gpstime != "2000-00-00-00-00-00")
                      ].gpstime)[-1]
    except:
        print("no GPS time stamp available, skipping")
        return False

    runTime = df.loc[df.gpstime == lastUniqueGPSTimeStamp].runtime[0] / 1000.0  # convert to seconds!
    runTimeZero = df.runtime[0]/1000.0

    deltaRunTime = runTime - runTimeZero

    gpsTime = df.loc[df.gpstime == lastUniqueGPSTimeStamp].gpstime[0]
    if verbose: print("found time stamp: {} runtime: {}, run time since beginning: {}".format(gpsTime, runTime, (runTime - runTimeZero)))
    date = gpsTime.split("-")[:3]
    time = gpsTime.split("-")[3:]
    try:
        gpsDateTime = pd.to_datetime("{} {}".format("-".join(date), ":".join(time)), utc=True).value / 10**9
    except Exception as e:
        print("failed to generate gpsDateTime for {} : {}".format(date, time))
        print("skipping dataframe")
        return False
    if verbose: print("correcting time")
    correctTime(df, runTime=deltaRunTime, gpsTimeStamp=gpsDateTime)
    return True


def checkLogFileVersion(logFileDir, cols, verbose=False):
    """

    checks the row length of log_0000.txt in a given directory to parse the log file version
    Two log file versions are available:
    - Version 1: normal log file format
    - Version 2: log including GPS timestamp

    return: the correct columns to use

    """

    # find a suitable log file
    logFilePath = glob(path.join(logFileDir, "log_????.txt"))[0]

    if path.isfile(logFilePath):
        with open(logFilePath) as logFile:
            for i, line in enumerate(logFile):
                if i == 3:  # first line = header, second line = overflow from last file -> hence third line used to check for file version
                    if len(line.split(",")) == 18:
                        if verbose: print("file version 2")
                        return cols[1]
                    elif len(line.split(",")) == 16:
                        if verbose: print("file version 1")
                        return cols[0]
                    else:
                        print("wrong number of columns in file {}".format(logFilePath))
                    break
    else:
        raise Exception("no such file or directory: {}".format(logFilePath))
