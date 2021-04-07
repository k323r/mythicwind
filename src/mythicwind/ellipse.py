from numpy.lib.histograms import _unsigned_subtract
from scipy.signal import find_peaks
import vg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calc_deflection(x, y):
    """
    calculates the deflection (magnitude) of the vector v = (x,y)
    """
    return np.sqrt(np.power(x, 2) + np.power(y, 2))

def find_minmax_deflection(data, distance=30, prominence=0.001):

    assert hasattr(data, 'deflection')

    drop_maxima = list()
    drop_minima = list()

    max_i, _ = find_peaks(data.deflection, distance=distance, prominence=prominence)
    min_i, _ = find_peaks(data.deflection*-1, distance=distance, prominence=prominence)

    max_df = pd.DataFrame({'max_deflection' : data.deflection[max_i],
                           'max_deflection_i' : max_i,
                          }, index=data.index[max_i])
    min_df = pd.DataFrame({'min_deflection' : data.deflection[min_i],
                           'min_deflection_i' : min_i,
                          }, index=data.index[min_i])

    if min_df.index[0] < max_df.index[0]:
        min_df = min_df[1:]

    for i in range(len(max_df) - 1):
    
        start = max_df.index[i]
        end = max_df.index[i+1]

        n_min = len(min_df[start:end].min_deflection)

        if n_min == 0:

            drop_maxima.append(end)

        elif n_min > 1:

            drop_minima.append((start, end))        

        else:
            pass

    for (start, end) in drop_minima:
        min_df.drop(min_df[start:end][min_df[start:end].min_deflection != min_df[start:end].min_deflection.min()].index, inplace=True)

    for index in drop_maxima:
        max_df.drop(index, inplace=True)

    if max_df.index[-1] > min_df.index[-1]:
        max_df = max_df.iloc[:-1]

    assert len(max_df.max_deflection) == len(min_df.min_deflection)

    if len(max_df.max_deflection) % 2:
        max_df = max_df.iloc[:-1]
        min_df = min_df.iloc[:-1]

    max_df.insert(loc=len(max_df.columns), column='ddt_max_deflection', value=calc_ddt(max_df.max_deflection))
    min_df.insert(loc=len(min_df.columns), column='ddt_min_deflection', value=calc_ddt(min_df.min_deflection))


    return (min_df, max_df)
    
def calc_max_deflection_angles(x, y, max_deflection_df, skip_odd=True, reference_axis=[0, 1, 0], view_axis=np.array([0, 0, 1])):
    """
    calculates the angle between the maximum deflection vector and a reference axis (default [0,1,0])

    returns: angle_t: the time corresponding to the angle at max. displacement
             angle:   the actual angles (in degrees!)
    """

    if skip_odd:
        max_deflection_df = max_deflection_df.iloc[::2]
        
    n_elem = len(max_deflection_df.max_deflection)

    max_deflection_vector_list = np.array([x[max_deflection_df.index],
                                           y[max_deflection_df.index],
                                           np.zeros(n_elem)
                                           ]).T
    reference_axis_vector_list = np.array(
        reference_axis*n_elem).reshape(n_elem, 3)

    unsigned_angles = vg.angle(
        max_deflection_vector_list, reference_axis_vector_list)

    signed_angles = vg.signed_angle(
        max_deflection_vector_list, reference_axis_vector_list, look=view_axis)
    
    axis_angles_df = pd.DataFrame({'axis_angle_signed' : signed_angles,
                                   'axis_angle_unsigned' : unsigned_angles,
                                  }, index=max_deflection_df.index)
    
    
    axis_angles_df.insert(loc=len(axis_angles_df.columns), column='axis_azimuth', value=axis_angles_df.axis_angle_signed.apply(correct_angle))
    axis_angles_df.insert(loc=len(axis_angles_df.columns), column='ddt_axis_angle_signed', value=calc_ddt(axis_angles_df.axis_angle_signed))
    axis_angles_df.insert(loc=len(axis_angles_df.columns), column='ddt_axis_angle_unsigned', value=calc_ddt(axis_angles_df.axis_angle_unsigned))


    return axis_angles_df

def calc_axis_ratio(min_deflection, max_deflection):
    """
    calculates the ratio between maximum and minimum deflection, corresponding to the half-major
    and half-minor axis, if the orbit was an elipse

    returns: ratio_t: the time stamp coinciding with the ratio
             ratio:   the actual ratio
    """

    # if min_deflection_t[0] < max_deflection_t[0]:
    if min_deflection.index[0] < max_deflection.index[0]:
        min_deflection = min_deflection[1:]

    if len(min_deflection) > len(max_deflection):
        min_deflection = min_deflection[:-1]
    elif len(min_deflection) < len(max_deflection):
        max_deflection = max_deflection[:-1]

    if not len(min_deflection) == len(max_deflection):
        raise Exception(
            'min_deflection and max_deflection are not of equal length!')

    eccentricity = np.sqrt(
        1 - np.power((min_deflection.to_numpy() / max_deflection.to_numpy()), 2))

    ratio_df = pd.DataFrame({'axis_ratio': min_deflection.to_numpy()/max_deflection.to_numpy(),
                         'eccentricity': eccentricity,
                         }, index=max_deflection.index)
    
    ratio_df.insert(loc=len(ratio_df.columns), column='ddt_axis_ratio', value=calc_ddt(ratio_df.axis_ratio))
    ratio_df.insert(loc=len(ratio_df.columns), column='ddt_eccentricity', value=calc_ddt(ratio_df.eccentricity))

    return ratio_df


def calc_peak_convolution(data, peaks):

    peaks_rolled = np.roll(peaks, -1)

    data_even = -data[peaks_rolled[::2]] + data[peaks[::2]]
    data_odd = -data[peaks_rolled[::2]] + data[peaks_rolled[1::2]]

    data_combined = np.stack((data_even, data_odd), axis=1).flatten()

    return (data_combined)


def calc_p2p_vectors(x, y, peaks):

    x_combined = calc_peak_convolution(x, peaks)
    y_combined = calc_peak_convolution(y, peaks)

    return np.array((x_combined, y_combined))


def calc_p2p_angles(x, y, max_deflection, reference_axis=[0, 1, 0], view_axis=np.array([0, 0, 1])):
    
    if len(max_deflection.max_deflection) % 2:
        max_deflection = max_deflection.iloc[:-1]

    x_list, y_list = calc_p2p_vectors(x.to_numpy(), y.to_numpy(), max_deflection.max_deflection_i.to_numpy())

    vector_list = np.array([x_list, y_list, np.zeros(len(x_list))]).T

    reference_axis_vector_list = np.array(
        reference_axis*len(x_list)).reshape(len(x_list), 3)

    unsigned_angles = vg.angle(vector_list, reference_axis_vector_list)

    signed_angles = vg.signed_angle(
        vector_list, reference_axis_vector_list, look=view_axis)
    
    p2p_angles_df = pd.DataFrame({'p2p_angle_unsigned' : unsigned_angles,
                                  'p2p_angle_signed' : signed_angles,
                                 }, index=max_deflection.index)

    p2p_angles_df.insert(loc=len(p2p_angles_df.columns), column='p2p_azimuth', value=p2p_angles_df.p2p_angle_signed.apply(correct_angle))
    p2p_angles_df.insert(loc=len(p2p_angles_df.columns), column='p2p_azimuth_unwrapped', value=np.rad2deg(np.unwrap(np.deg2rad(p2p_angles_df.p2p_azimuth))))
    p2p_angles_df.insert(loc=len(p2p_angles_df.columns), column='ddt_p2p_azimuth_unwrapped', value=calc_ddt(p2p_angles_df.p2p_azimuth_unwrapped))
    p2p_angles_df.insert(loc=len(p2p_angles_df.columns), column='ddt_p2p_azimuth', value=calc_ddt(p2p_angles_df.p2p_azimuth))
    p2p_angles_df.insert(loc=len(p2p_angles_df.columns), column='ddt_p2p_angle_unsigned', value=calc_ddt(p2p_angles_df.p2p_angle_unsigned))
    p2p_angles_df.insert(loc=len(p2p_angles_df.columns), column='ddt_p2p_angle_signed', value=calc_ddt(p2p_angles_df.p2p_angle_signed))
    
    return p2p_angles_df


def calc_ddt(timeseries):
    t = (timeseries.index.to_series().astype('int64')/1e9).to_numpy()
    x = timeseries.to_numpy()
    return (np.gradient(x, t))


def correct_angle(x):
    if x < 0:
        x += 360

    return x


def geometry_analysis(dataframe):


    min_df, max_df = find_minmax_deflection(dataframe)

    ratio_df = calc_axis_ratio(min_df.min_deflection, max_df.max_deflection)

    p2p_angles_df = calc_p2p_angles(dataframe.pos_z, dataframe.pos_x, max_df)

    axis_angles_df = calc_max_deflection_angles(dataframe.pos_z, dataframe.pos_x, max_df)

        # merge DataFrame and return
    geometry_df = pd.merge(max_df, ratio_df,
                           left_index=True, right_index=True)
    geometry_df = pd.merge(geometry_df, axis_angles_df,
                           left_index=True, right_index=True)
    geometry_df = pd.merge(geometry_df, p2p_angles_df,
                           left_index=True, right_index=True)

    return(geometry_df)


def plot_geometry_analysis(orbit_df, geometry_df):

    # TODO: move to fit_ellipse.py

    _, (ax1, ax2, ax3, ax4) = plt.subplots(ncols=1, nrows=4, figsize=(9, 12))
    ax1.plot(orbit_df.pos_x,
             orbit_df.pos_z,
             label='orbit')

    ax1.scatter(orbit_df.pos_x[geometry_df.max_deflection_index],
                orbit_df.pos_z[geometry_df.max_deflection_index],
                color='tab:red',
                label='maxima')

    ax1.axis('equal')
    ax1.legend(loc='upper right')

    ax2.plot(orbit_df.pos_x, label='pos x')
    ax2.plot(orbit_df.pos_z, label='pos z')
    ax2.plot(orbit_df.deflection, label='deflection')

    ax2.plot(geometry_df.max_deflection, color='grey', alpha=0.5)
    ax2.legend(loc='lower center', ncol=3)
    ax2.set_xticklabels([])
    ax2.get_shared_x_axes().join(ax2, ax3)

    ax3.plot(geometry_df.axis_angle, label='main axis angle')
    ax3.plot(geometry_df.p2p_angle, label='p2p angle')
    ax3.set_ylim([0, 180])
    ax3.legend(loc='lower center')
    ax3.set_xticklabels([])
    ax3.get_shared_x_axes().join(ax3, ax4)

    ax4.plot(geometry_df.axis_ratio, label='elipse axis ratio')
    ax4.plot(geometry_df.eccentricity, label='eccentricity')
    ax4.legend(loc='lower center', ncol=2)
