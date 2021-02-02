from scipy.signal import find_peaks
import vg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calc_deflection(x, y):
    """
    calculates the deflection (magnitude) of the vector v = (x,y)
    """
    return np.sqrt(np.power(x,2) + np.power(y,2))

def find_max_deflection(t, deflection):
    """
    identifies local maxima in the deflection signal

    return: max_i: list of indices at which the maxima occur
            max_t: the time at which the maxima occur
            max:   the acutal value of he maxima
    """
    max_i, _ = find_peaks(deflection)
    return ([max_i, t[max_i], deflection[max_i]])

def find_min_deflection(t, deflection):
    """
    identifies local minima in the deflection signal

    returns: min_i: list of indices at which the minima occur
             min_t: time at which the minima occur
             min:   the actual value of the minima
    """
    min_i, _ = find_peaks(-1*deflection)
    return ([min_i, t[min_i], deflection[min_i]])

def calc_max_deflection_angles(t, max_deflection_i, x, y, skip_odd=True, reference_axis=[0,1,0]):
    """
    calculates the angle between the maximum deflection vector and a reference axis (default [0,1,0])

    returns: angle_t: the time corresponding to the angle at max. displacement
             angle:   the actual angles (in degrees!)
    """
    
    if skip_odd:
        max_deflection_i = max_deflection_i[::2].copy()
    
    max_deflection_vector_list = np.array([x[max_deflection_i],
                                           y[max_deflection_i],
                                           np.zeros(len(max_deflection_i))
                                          ]).T
    reference_axis_vector_list = np.array(reference_axis*len(max_deflection_i)).reshape(len(max_deflection_i), 3)
    
    angles = vg.angle(max_deflection_vector_list, reference_axis_vector_list)
    
    return (t[max_deflection_i], angles)

def calc_axis_ratio(min_deflection_t, min_deflection, max_deflection_t, max_deflection):
    """
    calculates the ratio between maximum and minimum deflection, corresponding to the half-major
    and half-minor axis, if the orbit was an elipse

    returns: ratio_t: the time stamp coinciding with the ratio
             ratio:   the actual ratio
    """
    if min_deflection_t[0] < max_deflection_t[0]:
        print('min index comes first, removing')
        min_deflection_t = min_deflection_t[1:]
        min_deflection = min_deflection[1:]

    if len(min_deflection_t) > len(max_deflection_t):
        min_deflection_t = min_deflection_t[:-1]
        min_deflection = min_deflection[:-1]
    elif len(min_deflection_t) < len(max_deflection_t):
        max_deflection_t = max_deflection_t[:-1]
        max_deflection = max_deflection[:-1]
    
    eccentricity = np.sqrt(1 - np.power((min_deflection / max_deflection), 2))
    
    return (max_deflection_t, min_deflection/max_deflection, eccentricity)  


def calc_peak_convolution(data, peaks):
    
       
    peaks_rolled = np.roll(peaks, -1)
    
    data_even = -data[peaks_rolled[::2]] + data[peaks[::2]]
    data_odd  = -data[peaks_rolled[::2]] + data[peaks_rolled[1::2]]
    
    data_combined = np.stack((data_even, data_odd), axis = 1).flatten()
    
    return (data_combined)

def calc_p2p_vectors(x, y, peaks):
    
    x_combined = calc_peak_convolution(x, peaks)
    y_combined = calc_peak_convolution(y, peaks)

    return np.array((x_combined, y_combined))

def calc_p2p_angles(x, y, peaks, peaks_t, reference_axis = [0,1,0]):
    if len(peaks)%2:
        print('omitting last element')
        peaks = peaks[:-1]
        peaks_t = peaks_t[:-1]

    x_list, y_list = calc_p2p_vectors(x, y, peaks)
    vector_list = np.array([x_list, y_list, np.zeros(len(x_list))]).T
    reference_axis_vector_list = np.array(reference_axis*len(x_list)).reshape(len(x_list), 3)

    angles = vg.angle(vector_list, reference_axis_vector_list)

    return (peaks_t, angles)

def geometry_analysis(dataframe):
    t = dataframe.index.to_numpy()
    
    # calculate deflection
    deflection = calc_deflection(dataframe.pos_x.to_numpy(), dataframe.pos_z.to_numpy())
    """
    dataframe.insert(loc=len(dataframe.columns),
                     column='deflection',
                     value=deflection,
                    )
    """
    # find max an min deflection
    max_deflection_i, max_deflection_t, max_deflection = find_max_deflection(t, deflection)
    min_deflection_i, min_deflection_t, min_deflection = find_min_deflection(t, deflection)
    
    # calculate angles
    max_deflection_angles_t, max_deflection_angles = calc_max_deflection_angles(t, max_deflection_i, dataframe.pos_x, dataframe.pos_z, skip_odd=False)
    
    # calculate p2p angles
    p2p_t, p2p_angles = calc_p2p_angles(dataframe.pos_x.to_numpy(), 
                                        dataframe.pos_z.to_numpy(), 
                                        max_deflection_i, 
                                        max_deflection_t,
                                       )
    
    # calculate orbit shape parameters
    ratio_t, ratio, eccentricity = calc_axis_ratio(min_deflection_t, 
                                                   min_deflection, 
                                                   max_deflection_t, 
                                                   max_deflection)
    
    # build dataframes
    ratio_df = pd.DataFrame({'axis_ratio' : ratio, 
                             'eccentricity' : eccentricity}, 
                            index = ratio_t, 
                           )
    
    deflection_df = pd.DataFrame({'max_deflection' : max_deflection, 
                                  'max_deflection_index' : max_deflection_i,
                                 },
                                 index=max_deflection_t
                                )
    
    angle_df = pd.DataFrame({'axis_angle' : max_deflection_angles,
                            }, 
                            index = max_deflection_angles_t
                           )

    p2p_df = pd.DataFrame({'p2p_angle' : p2p_angles,
                          }, 
                          index = p2p_t
                         )
    
    # merge DataFrame and return
    geometry_df = pd.merge(ratio_df, deflection_df, left_index=True, right_index=True)
    geometry_df = pd.merge(geometry_df, angle_df, left_index=True, right_index=True)
    geometry_df = pd.merge(geometry_df, p2p_df, left_index=True, right_index=True)
    
    return(geometry_df)

def plot_geometry_analysis(orbit_df, geometry_df):

    _, (ax1, ax2, ax3, ax4) = plt.subplots(ncols=1, nrows=4, figsize=(9,12))
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