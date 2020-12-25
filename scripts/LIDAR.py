import pandas as pd
import numpy as np

# the following dict maps the columns header in the raw LIDAR files to the desired new column names
def generateKeys():
    """

    generates and returns a dictionary containing the original columns names from the
    LIDAR file as values and the currently used column names as corresponding keys

    ws_1  : Speed Value.1
    dir_1 : Direction Value.1
    h_1   : Node RT01 Lidar Height

    """

    keys = {"ws_0" : "Speed Value", "dir_0" : "Direction Value", "h_0" : "Node RT00 Lidar Height"}
    for i in range(1, 11):
        keys.update({"ws_{}".format(i) : "Speed Value.{}".format(i),
                     "dir_{}".format(i) : "Direction Value.{}".format(i),
                     "h_{}".format(i) : "Node RT{:02d} Lidar Height".format(i+1),
                    })
    return keys



# function to generate a new time index
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
        cleanData.insert(column="ws_{}".format(i),
                         value=rawData[keys["ws_{}".format(i)]].copy(),
                         loc=len(cleanData.columns)
                        )
        cleanData.insert(column="dir_{}".format(i),
                         value=rawData[keys["dir_{}".format(i)]].copy(),
                         loc=len(cleanData.columns)
                        )
        cleanData.insert(column="dir_{}_corr".format(i),
                         value=rawData[keys["dir_{}".format(i)]].copy(),
                         loc=len(cleanData.columns)
                        )
        cleanData.insert(column="h_{}".format(i),
                         value=rawData[keys["h_{}".format(i)]].copy(),
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
