import numpy as np
import pandas as pd
from scipy import integrate
from scipy.signal import butter, lfilter, sosfiltfilt

g = 9.80665

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """
    applies a butter bandpass filter to the given dataDir
    """ 

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

def butter_bandpass_filter_sos(data, lowcut, highcut, fs, order=5):
    """
    applies a symmetric filter (no phase offset)
    """

    nyq = fs*0.5
    low = lowcut/nyq
    high = highcut/nyq

    sos = butter(order, [low, high], btype='band', output='sos')
    y = sosfiltfilt(sos, data)

    return y

def resample_acceleration(acc_df, 
                          resample_interval='30ms', 
                          verbose=False, 
                          components=('x', 'y', 'z'),
                         ):

    """
    resamples the accelerations provided in acc_df and return a new data frame with the resampled data
    """

    # resample data
    if verbose: print(f'* resampling data to {resample_interval}. Start time: {acc_df.index[0]}')

    # empty dataframe to store the resampled values in
    data = pd.DataFrame()
 
    # resample data!
    for comp in components:
        data.insert(column=f'acc_{comp}r',
                    value=acc_df[f'acc_{comp}'].resample(resample_interval).bfill()*g,
                    loc=len(data.columns)
                   )
    return data

def filter_acceleration(acc_df, 
                        filter_low_cut=0.1, 
                        filter_high_cut=1, 
                        filter_frequency=33.333, 
                        filter_order=3, 
                        filter_type='band',
                        verbose=False, 
                        components=('x', 'y', 'z'),
                       ):
    """
    applies a butterworth bandpass filter to the specified acceleration components
    """

    if filter_type == 'band':
        filter_f = butter_bandpass_filter
    elif filter_type == 'sos':
        filter_f = butter_bandpass_filter_sos

    for comp in components:
        acc_df.insert(column="acc_{}rf".format(comp),
                      value=filter_f(acc_df[f'acc_{comp}r'],
                            filter_low_cut,
                            filter_high_cut,
                            filter_frequency,
                            order=filter_order,
                      ),
                      loc=len(acc_df.columns),
                     )
    return acc_df

def double_integration(data,
                       verbose=False,
                       components = ("x", "y", "z"),
                      ):

    """
    integrates the given acceleration twice to yield velocity, position and deflection
    """

    t = data.index.astype(np.int64)/10**9

    if verbose: print('* converting to SI units')

    if verbose: print('* removing mean')
    for comp in components:
        data[f'acc_{comp}rf'] = data[f'acc_{comp}rf'] -  data[f'acc_{comp}rf'].mean()

    if verbose: print("*    integrating acceleration")
    for comp in components:
        if verbose: print(f'* acceleration {comp}')

        # integrate filtered acceleration
        data.insert(column=f'vel_{comp}',
                    value=integrate.cumtrapz(data[f'acc_{comp}rf'], t, initial=0),
                    loc=len(data.columns)
                   )



    if verbose: print("*    integrating velocity")
    for comp in components:

        data[f'vel_{comp}'] -= data[f'vel_{comp}'].mean()

        if verbose: print(f'* velocity {comp}')
        # integrate velocity to yield position
        data.insert(column=f'pos_{comp}',
                    value=integrate.cumtrapz(data[f'vel_{comp}'], t, initial=0),
                    loc=len(data.columns)
                   )
    if verbose: print("*    calculating deflection")
    data.insert(column = "deflection",
                value = np.sqrt(np.power(data.pos_z, 2) + np.power(data.pos_x, 2)),
                loc = len(data.columns),
               )
