import numpy as np
import pandas as pd
from numba import njit
from scipy import integrate
from scipy.signal import butter, lfilter, sosfiltfilt, filtfilt

g = 9.80665

def butter_bandpass_lfilter(data, lowcut, highcut, fs, pad=None, padlen=100, order=3):
    """
    applies a butter bandpass filter to the given dataDir
    """ 

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

def butter_bandpass_filtfilt(data, lowcut, highcut, fs, pad=None, padlen=31, order=3):
    """
    applies a symmetric filter (no phase offset)
    """

    if pad not in ('even', 'odd', 'constant', None):
        raise Exception ('please provide a valid padding')


    nyq = fs*0.5
    low = lowcut/nyq
    high = highcut/nyq

    b, a = butter(order, [low, high], btype='band',)
    y = filtfilt(b,a, data, padtype=pad, padlen=padlen)

    return y

def butter_bandpass_sosfiltfilt(data, lowcut, highcut, fs, pad=None, padlen=31, order=3):
    """
    applies a symmetric filter (no phase offset)
    """

    if pad not in ('even', 'odd', 'constant', None):
        raise Exception ('please provide a valid padding')

    nyq = fs*0.5
    low = lowcut/nyq
    high = highcut/nyq

    sos = butter(order, [low, high], btype='band', output='sos')
    y = sosfiltfilt(sos, data, padtype=pad,padlen=padlen)

    return y

def butter_highpass_sosfiltfilt(data, lowcut, fs, pad='even', padlen=5000, order=3):
    """
    applies a symmetric filter (no phase offset)
    """

    if pad not in ('even', 'odd', 'constant', None):
        raise Exception ('please provide a valid padding')

    # check if len(data > padlen)
    if len(data) < padlen:
        print(f'padlen exceeds the number of available data points. Setting padlen to {len(data)}')
        padlen=len(data) - 1

    nyq = fs*0.5
    low = lowcut/nyq

    sos = butter(order, low, btype='highpass', output='sos')
    y = sosfiltfilt(sos, data, padtype=pad, padlen=padlen)

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
        data.insert(column=f'acc_{comp}',
                    value=acc_df[f'acc_{comp}'].resample(resample_interval).bfill()*g,   ## here we transform data into m/s^2
                    loc=len(data.columns)
                   )
    return data



def filter_integrate(acc_df,
                     filter_order=3, 
                     filter_lowcut=0.1,
                     filter_frequency=33.3333,
                     pad='even',
                     padlen=5000,
                     verbose=False,
                     components=('x', 'y', 'z'),
                    ):
    
    """
    filter_integrate
    
    filters and integrates accelerations
    """
    
    data = pd.DataFrame()
    data.insert(loc=0,
                column='epoch',
                value=acc_df.index
               )
    data.set_index('epoch', inplace=True)

    t = data.index.astype('int64')/1e9

    # filter and insert acceleration data from source data frame
    for component in components:
        data.insert(loc=len(data.columns),
                    value=butter_highpass_sosfiltfilt(acc_df[f'acc_{component}'],
                                                      lowcut=filter_lowcut,
                                                      fs=filter_frequency,
                                                      pad=pad,
                                                      padlen=padlen,
                                                      order=filter_order                                                        
                                                     ),
                    column=f'acc_{component}'
                   )
    
    # integrate accelerations
    for component in components:
        data.insert(loc=len(data.columns),
                    value=integrate.cumtrapz(data[f'acc_{component}'], t, initial=0),
                    column=f'vel_{component}',
                   )
    
    # filter the velocity again to remove any low freqency components
    for component in components:
        data[f'vel_{component}'] = butter_highpass_sosfiltfilt(data[f'vel_{component}'],
                                                               lowcut=filter_lowcut,
                                                               fs=filter_frequency,
                                                               pad=pad,
                                                               padlen=padlen,
                                                               order=filter_order                                                        
                                                              )

    # integrate velocites
    for component in components:
        data.insert(loc=len(data.columns),
                    value=integrate.cumtrapz(data[f'vel_{component}'], t, initial=0),
                    column=f'pos_{component}',
                   )

    # apply highpassfilter to the position again
    for component in components:
        data[f'pos_{component}'] = butter_highpass_sosfiltfilt(data[f'pos_{component}'],
                                                               lowcut=filter_lowcut,
                                                               fs=filter_frequency,
                                                               pad=pad,
                                                               padlen=padlen,
                                                               order=filter_order                                                        
                                                              )

    #calculate deflection
    data.insert(loc=len(data.columns),
                value=np.sqrt(np.power(data.pos_x, 2) + np.power(data.pos_z, 2)),
                column='deflection'
               )
    return data


def resample_filter_integrate_accelerations(df, args):

    df = resample_acceleration(df,
                               resample_interval=args.resample_interval, 
                               verbose=args.verbose,
                              )

    if args.integration_interval:

        integrated_data = list()
        
        if args.verbose: print(f'* using a integration interval of {args.integration_interval} minutes')
        
        for _, d in df.resample(args.integration_interval):
            if args.verbose: print(f'* start: {d.index[0]} -> end: {d.index[-1]}')
            integrated_data.append(
                filter_integrate(
                    d,
                    filter_order=args.filter_order,
                    filter_lowcut=args.filter_lower_frequency,
                    filter_frequency=args.filter_frequency,
                    pad=args.filter_pad_method,
                    padlen=args.filter_pad_length,
                    verbose=True,
                )
            )
        
        return (pd.concat(integrated_data))
    
    else:

        if args.verbose: print(f'* integrating accelerations')

        return(
            filter_integrate(
                df,
                filter_order=args.filter_order,
                filter_lowcut=args.filter_lower_frequency,
                filter_frequency=args.filter_frequency,
                pad=args.filter_pad_method,
                padlen=args.filter_pad_length,
                verbose=True,
            )
        )



