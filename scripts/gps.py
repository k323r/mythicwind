import vg
import numpy as np
import matplotlib.pyplot as plt



def calculate_sbit_mean_vector(sbitroot_gps, 
                               sbittip_gps, 
                               sbi_start, 
                               sbi_stop
                              ):
    
    sbittip_sbi_mean = (sbittip_gps[sbi_start:sbi_stop].longitude.mean(), 
                        sbittip_gps[sbi_start:sbi_stop].latitude.mean()
                       )
    
    sbitroot_sbi_mean = (sbitroot_gps[sbi_start:sbi_stop].longitude.mean(), 
                         sbitroot_gps[sbi_start:sbi_stop].latitude.mean()
                        )

    sbit_vector = (sbittip_sbi_mean[0] - sbitroot_sbi_mean[0],
                   sbittip_sbi_mean[1] - sbitroot_sbi_mean[1])
    
    return (sbitroot_sbi_mean, sbit_vector)

def estimate_nacelle_orientation(sbitroot_gps, 
                                 sbittip_gps, 
                                 sbi_start, 
                                 sbi_stop, 
                                 reference_axis=[0,1,0]
                                ):

    sbitroot_v, sbit_v = calculate_sbit_mean_vector(sbitroot_gps=sbitroot_gps, 
                                                               sbittip_gps=sbittip_gps, 
                                                               sbi_start=sbi_start, 
                                                               sbi_stop=sbi_stop
                                                              )

    abs_sbit_v = np.sqrt(np.power(sbit_v[0], 2) + np.power(sbit_v[1], 2))
    
    orientation_nacelle_v = np.array([0, abs_sbit_v, 0])
    reference_axis_v = np.array(reference_axis)
    
    # nacelle vector is orthogonal to the sbit vector:
    orientation_nacelle_v[0] = -1*((sbit_v[1]*orientation_nacelle_v[1])/sbit_v[0])
    
    # calculate orientation with respect to the reference axis
    orientation_nacelle_degree = vg.angle(orientation_nacelle_v, reference_axis_v)
    
    # make sure the angle goes from 0 - 360
    if orientation_nacelle_v[0] < 0:
        orientation_nacelle_degree = 360 - orientation_nacelle_degree
    
    print('nacelle orientation due north: {:1.0f}'.format(orientation_nacelle_degree))
    return (sbitroot_v, sbit_v, orientation_nacelle_v, orientation_nacelle_degree)


def plot_sbi(sbitroot_gps, 
             sbittip_gps, 
             helihoist_gps, 
             sbitroot_v,
             sbit_v,
             nacelle_v,
             start,
             stop,
             sbi_start,
             sbi_stop,
             turbine_name='turbine_01',
             blade_number=1,
             smooting_window='30min',
            ):
    smoothing_window='30min'

    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)

    fig.suptitle('{} - blade number {}'.format(turbine_name, blade_number))
    
    ax1.plot(sbittip_gps[start:stop].longitude.rolling(smoothing_window).mean(), 
            sbittip_gps[start:stop].latitude.rolling(smoothing_window).mean(), 
            alpha=0.5,
            color='tab:blue',
            )
    ax1.plot(sbitroot_gps[start:stop].longitude.rolling(smoothing_window).mean(), 
            sbitroot_gps[start:stop].latitude.rolling(smoothing_window).mean(), 
            alpha=0.5,
            color='tab:orange'
            )
    ax1.plot(helihoist_gps[start:stop].longitude.rolling(smoothing_window).mean(), 
            helihoist_gps[start:stop].latitude.rolling(smoothing_window).mean(), 
            alpha=0.5,
            color='grey',
            )

    ax1.plot(sbittip_gps[sbi_start:sbi_stop].longitude.rolling(smoothing_window).mean(), 
            sbittip_gps[sbi_start:sbi_stop].latitude.rolling(smoothing_window).mean(), 
            label='SBIT Tip',
            linewidth=2,
            color='tab:blue'
            )
    ax1.plot(sbitroot_gps[sbi_start:sbi_stop].longitude.rolling(smoothing_window).mean(), 
            sbitroot_gps[sbi_start:sbi_stop].latitude.rolling(smoothing_window).mean(), 
            label='SBIT Root',
            linewidth=2,
            color='tab:orange',
            )
    ax1.plot(helihoist_gps[sbi_start:sbi_stop].longitude.rolling(smoothing_window).mean(), 
            helihoist_gps[sbi_start:sbi_stop].latitude.rolling(smoothing_window).mean(), 
            label='HeliHoist',
            linewidth=2,
            color='grey',
            )

    ax1.plot([sbitroot_v[0], sbitroot_v[0]+sbit_v[0]],
            [sbitroot_v[1], sbitroot_v[1]+sbit_v[1]],
            label='orientation blade',
            linewidth=2,
            color='tab:red'
            )

    ax1.plot([sbitroot_v[0], sbitroot_v[0]+nacelle_v[0]],
            [sbitroot_v[1], sbitroot_v[1]+nacelle_v[1]],
            label='orientation nacelle',
            linewidth=2,
            color='tab:green'
            )

    ax1.set_xlabel('longitude')
    ax1.set_ylabel('latitude')
    ax1.axis('equal')
    ax1.grid()
    ax1.legend(ncol=2)

    ax2.plot(sbittip_gps[start:stop].elevation.rolling(smoothing_window).mean(), label='SBIT Tip', color='tab:blue')
    ax2.plot(sbitroot_gps[start:stop].elevation.rolling(smoothing_window).mean(), label='SBIT Root', color='tab:orange')
    ax2.plot(helihoist_gps[start:stop].elevation.rolling(smoothing_window).mean(), label='HeliHoist', color='grey')

    plt.axvspan(xmin=sbi_start, 
                xmax=sbi_stop,
                label='installation of blade 1',
                facecolor='w',
                edgecolor='grey',
                hatch='x'
            )

    ax2.legend(ncol=2)
    ax2.set_ylabel('elevation (m)')
    ax2.set_xlabel('date/time')

    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    plt.savefig('{}_sbi_{}.png'.format(turbine_name, blade_number), dpi=150)