import vg
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from os import path
import sys


def estimate_sbi(helihoist,
                 sbitroot,
                 sbittip,
                 smoothing_window='20min',
                 resample_window='10min',
                 sbi_altitude_threshold=100,
                 min_sbi_length='30min'
                 ):
    """
    estimate_sbi - a function to approximate single blade installation duration based on 
    GNSS data.

    parameters:
    helihoist           pandas dataframe containing gnss data from the helihoist
    sbitroot            pandas dataframe containing gnss data from the sbit root
    sbittip             pandas dataframe containing gnss data from the sbit tip
    """

    # 1. smooth gnss data by applying a rolling mean and resample to 10 min intervals
    helihoist_smooth_resampled = helihoist.rolling(
        smoothing_window).mean().resample(resample_window).mean()
    sbitroot_smooth_resampled = sbitroot.rolling(
        smoothing_window).mean().resample(resample_window).mean()
    sbittip_smooth_resampled = sbittip.rolling(
        smoothing_window).mean().resample(resample_window).mean()

    # 2. select data where altitude > sbi_threshold
    helihoist_altitude_selected = helihoist_smooth_resampled.altitude[
        helihoist_smooth_resampled.altitude > sbi_altitude_threshold]
    sbitroot_altitude_selected = sbitroot_smooth_resampled.altitude[
        sbitroot_smooth_resampled.altitude > sbi_altitude_threshold]
    sbittip_altitude_selected = sbittip_smooth_resampled.altitude[
        sbittip_smooth_resampled.altitude > sbi_altitude_threshold]

    # 3. intersect indices to select indices only present in all three data sets
    sbitroot_sbittip_altitude_selected_i = sbitroot_altitude_selected.index.intersection(
        sbittip_altitude_selected.index)
    helihoist_sbitroot_sbittip_altitude_selected_i = sbitroot_sbittip_altitude_selected_i.intersection(
        helihoist_altitude_selected.index)

    if len(helihoist_sbitroot_sbittip_altitude_selected_i) == 0 and len(sbitroot_sbittip_altitude_selected_i) > 0:
        print(f'* no helihoist data available! proceed with caution')
        ret_index = sbitroot_sbittip_altitude_selected_i
    else:
        ret_index = helihoist_sbitroot_sbittip_altitude_selected_i

    return (helihoist_smooth_resampled,
            sbitroot_smooth_resampled,
            sbittip_smooth_resampled,
            ret_index[1:-1]
            )


def calculate_sbit_mean_vector(sbitroot_gps,
                               sbittip_gps,
                               sbi_time_index,
                               ):

    sbittip_sbi_mean = (sbittip_gps.loc[sbi_time_index].longitude.mean(),
                        sbittip_gps.loc[sbi_time_index].latitude.mean()
                        )

    sbitroot_sbi_mean = (sbitroot_gps.loc[sbi_time_index].longitude.mean(),
                         sbitroot_gps.loc[sbi_time_index].latitude.mean()
                         )

    sbit_vector = (sbittip_sbi_mean[0] - sbitroot_sbi_mean[0],
                   sbittip_sbi_mean[1] - sbitroot_sbi_mean[1])

    print(f'sbit vector: {sbit_vector}')

    return (sbitroot_sbi_mean, sbit_vector)


def estimate_nacelle_orientation(sbitroot_gps,
                                 sbittip_gps,
                                 sbi_time_index,
                                 reference_axis=[0, 1, 0]
                                 ):

    sbitroot_v, sbit_v = calculate_sbit_mean_vector(sbitroot_gps=sbitroot_gps,
                                                    sbittip_gps=sbittip_gps,
                                                    sbi_time_index=sbi_time_index
                                                    )

    abs_sbit_v = np.sqrt(np.power(sbit_v[0], 2) + np.power(sbit_v[1], 2))

    orientation_nacelle_v = np.array([0, abs_sbit_v, 0])
    reference_axis_v = np.array(reference_axis)

    # nacelle vector is orthogonal to the sbit vector:
    # as the nacelle can only ever be left of the sbit root side
    # the sign of the x-element of the blade orientation is used to make sure, 
    # the nacelle vector is calculated correctly
    if sbit_v[0] > 0:
        orientation_nacelle_v[0] = -1 * ((sbit_v[1]*orientation_nacelle_v[1])/sbit_v[0])
    else:
        orientation_nacelle_v[1] *= -1
        orientation_nacelle_v[0] = -1*((sbit_v[1]*orientation_nacelle_v[1])/sbit_v[0])

    # calculate orientation with respect to the reference axis
    orientation_nacelle_degree = vg.angle(
        orientation_nacelle_v, reference_axis_v)

    # make sure the angle goes from 0 - 360
    if orientation_nacelle_v[0] < 0:
        print('substracting 360 degrees')
        orientation_nacelle_degree = 360 - orientation_nacelle_degree

    print('nacelle orientation due north: {:1.0f}'.format(
        orientation_nacelle_degree))
    return (sbitroot_v, sbit_v, orientation_nacelle_v, orientation_nacelle_degree)


def plot_sbi(
    sbitroot_gps,
    sbittip_gps,
    helihoist_gps,
    sbitroot_v,
    sbit_v,
    nacelle_v,
    sbi_time_indices,
    nacelle_angle=None,
    turbine_name='turbine_01',
    output_dir='.',
):  

    if not nacelle_angle:
        print('please provide a nacelle orientation angle!')
        sys.exit()

    start = sbi_time_indices[0] - pd.to_timedelta(1, unit='h')
    stop = sbi_time_indices[-1] + pd.to_timedelta(1, unit='h')

    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)

    fig.suptitle(f'{turbine_name}')

    ax1.plot(sbittip_gps[start:stop].longitude,
             sbittip_gps[start:stop].latitude,
             alpha=0.5,
             color='tab:blue',
             )
    ax1.plot(sbitroot_gps[start:stop].longitude,
             sbitroot_gps[start:stop].latitude,
             alpha=0.5,
             color='tab:orange'
             )
    ax1.plot(helihoist_gps[start:stop].longitude,
             helihoist_gps[start:stop].latitude,
             alpha=0.5,
             color='grey',
             )

    ax1.plot(sbittip_gps.loc[sbi_time_indices].longitude,
             sbittip_gps.loc[sbi_time_indices].latitude,
             label='SBIT Tip',
             linewidth=2,
             color='tab:blue'
             )
    ax1.plot(sbitroot_gps.loc[sbi_time_indices].longitude,
             sbitroot_gps.loc[sbi_time_indices].latitude,
             label='SBIT Root',
             linewidth=2,
             color='tab:orange',
             )

    # edge case: sometime, only sbitroot and sbittip data is available so plotting
    # helihoist will yield an error -> check data is available for the given indices
    if sbi_time_indices[0] in helihoist_gps.index:
        ax1.plot(helihoist_gps.loc[sbi_time_indices].longitude,
                helihoist_gps.loc[sbi_time_indices].latitude,
                label='HeliHoist',
                linewidth=2,
                color='grey',
                )
    else:
        print("* no helihoist data available, skipping")

    ax1.plot([sbitroot_v[0], sbitroot_v[0]+sbit_v[0]],
             [sbitroot_v[1], sbitroot_v[1]+sbit_v[1]],
             label='orientation blade',
             linewidth=2,
             color='tab:red'
             )

    ax1.plot([sbitroot_v[0], sbitroot_v[0]+nacelle_v[0]],
             [sbitroot_v[1], sbitroot_v[1]+nacelle_v[1]],
             label=f'orientation nacelle: {nacelle_angle:.0f} due North',
             linewidth=2,
             color='tab:green'
             )

    ax1.set_xlabel('longitude')
    ax1.set_ylabel('latitude')
    ax1.axis('equal')
    ax1.grid()
    ax1.legend(ncol=2)

    ax2.plot(sbittip_gps[start:stop].altitude, label='SBIT Tip', color='tab:blue')
    ax2.plot(sbitroot_gps[start:stop].altitude, label='SBIT Root', color='tab:orange')
    ax2.plot(helihoist_gps[start:stop].altitude, label='HeliHoist', color='grey')

    plt.axvspan(xmin=sbi_time_indices[0],
                xmax=sbi_time_indices[-1],
                label='single blade installation',
                facecolor='w',
                edgecolor='grey',
                hatch='x'
                )

    ax2.legend(ncol=2)
    ax2.set_ylabel('altitude (m)')
    ax2.set_xlabel('date/time')

    plt.gcf().autofmt_xdate()
    #plt.tight_layout()

    plt.savefig(path.join(output_dir, f'{turbine_name}_sbi.png'), dpi=300)
