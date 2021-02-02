from scipy.signal import find_peaks
import vg
import numpy as np

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

