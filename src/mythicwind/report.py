from collections import defaultdict
import pandas as pd
from pandas._libs.tslibs.timestamps import Timestamp
from os import path
from glob import glob
from IPython.display import display, Markdown, Latex
import matplotlib.pyplot as plt

from .csv_io import read_frame

def print_md(string):
    display(Markdown(string))

def print_ltx(string):
    display(Latex(string))

def find_blade_landing_data(data_dir: str, start: Timestamp, stop: Timestamp) -> list:
    data: defaultdict = defaultdict(list)
    for pos in ('helihoist-1', 'sbittip', 'sbitroot'):
        pos_dir = path.join(data_dir, pos)
        if path.isdir(pos_dir):
            print(f'\n\nprocessing {pos_dir}')
            pos_data = path.join(pos_dir, 'tom/acc-vel-pos')
            if path.isdir(pos_data):
                for tomfile in sorted(glob(path.join(pos_data, '*.csv'))):                
                    # parse the date of the file first
                    #t_start = tomfile.split('/')[-1].split('_')[4]
                    #t_stop = tomfile.split('/')[-1].split('_')[5].split('.')[0]

                    file_start = pd.to_datetime(tomfile.split('/')[-1].split('_')[4], format='%Y-%m-%d-%H-%M-%S', utc=True)
                    file_end = pd.to_datetime(tomfile.split('/')[-1].split('_')[5].split('.')[0], format='%Y-%m-%d-%H-%M-%S', utc=True)

                    if file_start > start:
                        if file_start < stop:
                            print(f'found file {tomfile}')
                            data[pos].append(read_frame(tomfile))

    helihoist = pd.concat(data['helihoist-1'])
    sbitroot = pd.concat(data['sbitroot'])
    sbittip = pd.concat(data['sbittip'])
    return([helihoist, sbitroot, sbittip])


        
def plot_blade_landing(helihoist, sbitroot, sbittip, first_contact, blade_landing, save_fig_path=None, ylim=(-0.1, 0.1)):

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, sharex=True, figsize=(16,9))

    ax1.plot(helihoist.deflection, label='helihoist')
    ax1.plot(sbitroot.deflection, label='sbitroot')
    ax1.plot(sbittip.deflection, label='sbittip')
    ax1.axvline(x=blade_landing, color='tab:red', label='blade landing')
    ax1.axvline(x=first_contact, color='tab:red', linestyle='--', label='first contact')
    ax1.legend(ncol=4, loc='lower right')
    ax1.set_ylabel('deflection (m)')

    ax2.set_ylim([-0.1, 0.1])
    ax2.plot(sbitroot.deflection - helihoist.deflection, label='sbitroot - helihoist', color='tab:orange')
    ax2.axvline(x=blade_landing, color='tab:red', label='blade landing')
    ax2.axvline(x=first_contact, color='tab:red', linestyle='--', label='first contact')
    ax2.axhline(y=0, color='k')
    ax2.legend(loc='upper right', ncol=2)
    ax2.set_ylabel('deflection diff (m)')

    ax3.set_ylim([-0.1, 0.1])
    ax3.plot(sbittip.deflection - helihoist.deflection, label='sbittip - helihoist', color='tab:green')
    ax3.axvline(x=blade_landing, color='tab:red', label='blade landing')
    ax3.axvline(x=first_contact, color='tab:red', linestyle='--', label='first contact')
    ax3.axhline(y=0, color='k')
    ax3.legend(loc='upper right', ncol=2)
    ax3.set_ylabel('deflection diff (m)')

    ax4.set_ylim([-0.1, 0.1])
    ax4.plot(sbitroot.deflection - sbittip.deflection, label='sbitroot - sbittip', color='lightblue')
    ax4.axvline(x=blade_landing, color='tab:red', label='blade landing')
    ax4.axvline(x=first_contact, color='tab:red', linestyle='--', label='first contact')
    ax4.axhline(y=0, color='k')
    ax4.legend(loc='upper right', ncol=2)
    ax4.set_ylabel('deflection diff (m)')
    ax4.set_xlabel('date / time')
    
    if save_fig_path:
        fig.savefig(save_fig_path, dpi=300)
    
def plot_blade_landing_geometry(helihoist, sbitroot, sbittip, first_contact, blade_landing, resample_window='50ms', rolling_window='1min', save_fig_path=None, ylim=(-0.1, 0.1)):

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, sharex=True, figsize=(16,9))

    ax1.plot(helihoist.max_deflection.resample(resample_window).mean().rolling(rolling_window).mean(), label='helihoist')
    ax1.plot(sbitroot.max_deflection.resample(resample_window).mean().rolling(rolling_window).mean(), label='sbitroot')
    ax1.plot(sbittip.max_deflection.resample(resample_window).mean().rolling(rolling_window).mean(), label='sbittip')
    ax1.axvline(x=blade_landing, color='tab:red', label='blade landing')
    ax1.axvline(x=first_contact, color='tab:red', linestyle='--', label='first contact')
    ax1.legend(ncol=4, loc='lower right')
    ax1.set_ylabel('deflection (m)')

    ax2.set_ylim([-0.1, 0.1])
    ax2.plot(sbitroot.max_deflection.resample(resample_window).mean().rolling(rolling_window).mean() - helihoist.max_deflection.resample(resample_window).mean().rolling(rolling_window).mean(), label='sbitroot - helihoist', color='tab:orange')
    ax2.axvline(x=blade_landing, color='tab:red', label='blade landing')
    ax2.axvline(x=first_contact, color='tab:red', linestyle='--', label='first contact')
    ax2.axhline(y=0, color='k')
    ax2.legend(loc='upper right', ncol=2)
    ax2.set_ylabel('deflection diff (m)')

    ax3.set_ylim([-0.1, 0.1])
    ax3.plot(sbittip.max_deflection.resample(resample_window).mean().rolling(rolling_window).mean() - helihoist.max_deflection.resample(resample_window).mean().rolling(rolling_window).mean(), label='sbittip - helihoist', color='tab:green')
    ax3.axvline(x=blade_landing, color='tab:red', label='blade landing')
    ax3.axvline(x=first_contact, color='tab:red', linestyle='--', label='first contact')
    ax3.axhline(y=0, color='k')
    ax3.legend(loc='upper right', ncol=2)
    ax3.set_ylabel('deflection diff (m)')

    ax4.set_ylim([-0.1, 0.1])
    ax4.plot(sbitroot.max_deflection.resample(resample_window).mean().rolling(rolling_window).mean() - sbittip.max_deflection.resample(resample_window).mean().rolling(rolling_window).mean(), label='sbitroot - sbittip', color='lightblue')
    ax4.axvline(x=blade_landing, color='tab:red', label='blade landing')
    ax4.axvline(x=first_contact, color='tab:red', linestyle='--', label='first contact')
    ax4.axhline(y=0, color='k')
    ax4.legend(loc='upper right', ncol=2)
    ax4.set_ylabel('deflection diff (m)')
    ax4.set_xlabel('date / time')
    
    if save_fig_path:
        fig.savefig(save_fig_path, dpi=300)