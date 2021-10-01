#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 12:34:53 2021

@author: lenastroer
"""
# %% IMPORTS


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import math 
import pylab 

from matplotlib.dates import DateFormatter
from glob import glob
from os import path
from collections import defaultdict


import sys
sys.path.insert(0, path.abspath(path.join(path.curdir, '../src')))

#%matplotlib notebook

# %% WIND DATA

wind_data = pd.read_csv('/Volumes/MASTERTHESE/MasterThese/wind_data_resampled1s_UTC.csv')
wind_data.set_index('datetime', inplace=True)
#wind_data.index= wind_data.index.tz_convert('UTC')
wind_data.index= pd.DatetimeIndex(wind_data.index)
print(type(wind_data.index[-1]))
print(wind_data.index[-1])


# %% BLADE LANDINGS BAS

blade_landings= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/blade_landing_helihoist_sbitroot.txt')

# make epoch index of dataframe and convert epoch into readable dates
blade_landings.epoch_land= blade_landings.epoch_land.apply(lambda x: pd.to_datetime(x, unit= 's', utc=True))

# convert blade landings of turbine 8 into readable dates
#blade_landing1= pd.to_datetime(1.571127e+09, unit='s', utc=True)
#blade_landing2= pd.to_datetime(1.571154e+09, unit='s', utc=True)
#blade_landing3= pd.to_datetime(1.571188e+09, unit='s', utc=True)
#landings = (blade_landing1, blade_landing2, blade_landing3)

landings_tb4 = (pd.to_datetime(blade_landings.epoch_land[0]))
landings_tb5 = (pd.to_datetime(blade_landings.epoch_land[1]), pd.to_datetime(blade_landings.epoch_land[2]), pd.to_datetime(blade_landings.epoch_land[3]))
landings_tb6 = (pd.to_datetime(blade_landings.epoch_land[4]), pd.to_datetime(blade_landings.epoch_land[5]))
landings_tb7 = (pd.to_datetime(blade_landings.epoch_land[6]), pd.to_datetime(blade_landings.epoch_land[7]), pd.to_datetime(blade_landings.epoch_land[8]))
landings_tb8 = (pd.to_datetime(blade_landings.epoch_land[9]), pd.to_datetime(blade_landings.epoch_land[10]), pd.to_datetime(blade_landings.epoch_land[11]))
landings_tb10 = (pd.to_datetime(blade_landings.epoch_land[12]))
landings_tb11 = (pd.to_datetime(blade_landings.epoch_land[13]), pd.to_datetime(blade_landings.epoch_land[14]))
landings_tb12 = (pd.to_datetime(blade_landings.epoch_land[15]), pd.to_datetime(blade_landings.epoch_land[16]))
landings_tb13 = (pd.to_datetime(blade_landings.epoch_land[17]), pd.to_datetime(blade_landings.epoch_land[18]))
landings_tb14 = (pd.to_datetime(blade_landings.epoch_land[19]), pd.to_datetime(blade_landings.epoch_land[20]), pd.to_datetime(blade_landings.epoch_land[21]))


# %% GPS DATA

# READ CSV files of GPS Data: turbine 4

# sbitroot
gps_sbitroot_tb4= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-04_sbitroot_tom_gps.csv')
gps_sbitroot_tb4.epoch= pd.to_datetime(gps_sbitroot_tb4.epoch, unit= 's', utc=True)
gps_sbitroot_tb4.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb4= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-04_sbittip_tom_gps.csv')
gps_sbittip_tb4.epoch= pd.to_datetime(gps_sbittip_tb4.epoch, unit= 's', utc=True)
gps_sbittip_tb4.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb4= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-04_helihoist-1_tom_gps.csv')
gps_helih_tb4.epoch= pd.to_datetime(gps_helih_tb4.epoch, unit= 's', utc=True)
gps_helih_tb4.set_index('epoch', inplace=True)


# READ CSV files of GPS Data: turbine 5

# sbitroot
gps_sbitroot_tb5= pd.read_csv('/Volumes/MASTERTHESE//MasterThese/GPS/turbine-05_sbitroot_tom_gps.csv')
gps_sbitroot_tb5.epoch= pd.to_datetime(gps_sbitroot_tb5.epoch, unit= 's', utc=True)
gps_sbitroot_tb5.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb5= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-05_sbittip_tom_gps.csv')
gps_sbittip_tb5.epoch= pd.to_datetime(gps_sbittip_tb5.epoch, unit= 's', utc=True)
gps_sbittip_tb5.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb5= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-05_helihoist-1_tom_gps.csv')
gps_helih_tb5.epoch= pd.to_datetime(gps_helih_tb5.epoch, unit= 's', utc=True)
gps_helih_tb5.set_index('epoch', inplace=True)

# READ CSV files of GPS Data: turbine 6

# sbitroot
gps_sbitroot_tb6= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-06_sbitroot_tom_gps.csv')
gps_sbitroot_tb6.epoch= pd.to_datetime(gps_sbitroot_tb6.epoch, unit= 's', utc=True)
gps_sbitroot_tb6.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb6= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-06_sbittip_tom_gps.csv')
gps_sbittip_tb6.epoch= pd.to_datetime(gps_sbittip_tb6.epoch, unit= 's', utc=True)
gps_sbittip_tb6.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb6= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-06_helihoist-1_tom_gps.csv')
gps_helih_tb6.epoch= pd.to_datetime(gps_helih_tb6.epoch, unit= 's', utc=True)
gps_helih_tb6.set_index('epoch', inplace=True)

# READ CSV files of GPS Data: turbine 7

# sbitroot
gps_sbitroot_tb7= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-07_sbitroot_tom_gps.csv')
gps_sbitroot_tb7.epoch= pd.to_datetime(gps_sbitroot_tb7.epoch, unit= 's', utc=True)
gps_sbitroot_tb7.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb7= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-07_sbittip_tom_gps.csv')
gps_sbittip_tb7.epoch= pd.to_datetime(gps_sbittip_tb7.epoch, unit= 's', utc=True)
gps_sbittip_tb7.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb7= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-07_helihoist-1_tom_gps.csv')
gps_helih_tb7.epoch= pd.to_datetime(gps_helih_tb7.epoch, unit= 's', utc=True)
gps_helih_tb7.set_index('epoch', inplace=True)


# READ CSV files of GPS Data: turbine 8

# sbitroot
gps_sbitroot_tb8= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-08_sbitroot_tom_gps.csv')
gps_sbitroot_tb8.epoch= pd.to_datetime(gps_sbitroot_tb8.epoch, unit= 's', utc=True)
gps_sbitroot_tb8.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb8= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-08_sbittip_tom_gps.csv')
gps_sbittip_tb8.epoch= pd.to_datetime(gps_sbittip_tb8.epoch, unit= 's', utc=True)
gps_sbittip_tb8.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb8= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-08_helihoist-1_tom_gps.csv')
gps_helih_tb8.epoch= pd.to_datetime(gps_helih_tb8.epoch, unit= 's', utc=True)
gps_helih_tb8.set_index('epoch', inplace=True)

# READ CSV files of GPS Data: turbine 10

# sbitroot
gps_sbitroot_tb10= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-10_sbitroot_tom_gps.csv')
gps_sbitroot_tb10.epoch= pd.to_datetime(gps_sbitroot_tb10.epoch, unit= 's', utc=True)
gps_sbitroot_tb10.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb10= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-10_sbittip_tom_gps.csv')
gps_sbittip_tb10.epoch= pd.to_datetime(gps_sbittip_tb10.epoch, unit= 's', utc=True)
gps_sbittip_tb10.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb10= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-10_helihoist-1_tom_gps.csv')
gps_helih_tb10.epoch= pd.to_datetime(gps_helih_tb10.epoch, unit= 's', utc=True)
gps_helih_tb10.set_index('epoch', inplace=True)

# READ CSV files of GPS Data: turbine 11

# sbitroot
gps_sbitroot_tb11= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-11_sbitroot_tom_gps.csv')
gps_sbitroot_tb11.epoch= pd.to_datetime(gps_sbitroot_tb11.epoch, unit= 's', utc=True)
gps_sbitroot_tb11.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb11= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-11_sbittip_tom_gps.csv')
gps_sbittip_tb11.epoch= pd.to_datetime(gps_sbittip_tb11.epoch, unit= 's', utc=True)
gps_sbittip_tb11.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb11= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-11_helihoist-1_tom_gps.csv')
gps_helih_tb11.epoch= pd.to_datetime(gps_helih_tb11.epoch, unit= 's', utc=True)
gps_helih_tb11.set_index('epoch', inplace=True)


# READ CSV files of GPS Data: turbine 12

# sbitroot
gps_sbitroot_tb12= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-12_sbitroot_tom_gps.csv')
gps_sbitroot_tb12.epoch= pd.to_datetime(gps_sbitroot_tb12.epoch, unit= 's', utc=True)
gps_sbitroot_tb12.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb12= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-12_sbittip_tom_gps.csv')
gps_sbittip_tb12.epoch= pd.to_datetime(gps_sbittip_tb12.epoch, unit= 's', utc=True)
gps_sbittip_tb12.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb12= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-12_helihoist-1_tom_gps.csv')
gps_helih_tb12.epoch= pd.to_datetime(gps_helih_tb12.epoch, unit= 's', utc=True)
gps_helih_tb12.set_index('epoch', inplace=True)


# READ CSV files of GPS Data: turbine 13

# sbitroot
gps_sbitroot_tb13= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-13_sbitroot_tom_gps.csv')
gps_sbitroot_tb13.epoch= pd.to_datetime(gps_sbitroot_tb13.epoch, unit= 's', utc=True)
gps_sbitroot_tb13.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb13= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-13_sbittip_tom_gps.csv')
gps_sbittip_tb13.epoch= pd.to_datetime(gps_sbittip_tb13.epoch, unit= 's', utc=True)
gps_sbittip_tb13.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb13= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-13_helihoist-1_tom_gps.csv')
gps_helih_tb13.epoch= pd.to_datetime(gps_helih_tb13.epoch, unit= 's', utc=True)
gps_helih_tb13.set_index('epoch', inplace=True)



# READ CSV files of GPS Data: turbine 14

# sbitroot
gps_sbitroot_tb14= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-14_sbitroot_tom_gps.csv')
gps_sbitroot_tb14.epoch= pd.to_datetime(gps_sbitroot_tb14.epoch, unit= 's', utc=True)
gps_sbitroot_tb14.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb14= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-14_sbittip_tom_gps.csv')
gps_sbittip_tb14.epoch= pd.to_datetime(gps_sbittip_tb14.epoch, unit= 's', utc=True)
gps_sbittip_tb14.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb14= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-14_helihoist-1_tom_gps.csv')
gps_helih_tb14.epoch= pd.to_datetime(gps_helih_tb14.epoch, unit= 's', utc=True)
gps_helih_tb14.set_index('epoch', inplace=True)


# READ CSV files of GPS Data: turbine 16

# sbitroot
gps_sbitroot_tb16= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-16_sbitroot_tom_gps.csv')
gps_sbitroot_tb16.epoch= pd.to_datetime(gps_sbitroot_tb16.epoch, unit= 's', utc=True)
gps_sbitroot_tb16.set_index('epoch', inplace=True)

# sbittip
gps_sbittip_tb16= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-16_sbittip_tom_gps.csv')
gps_sbittip_tb16.epoch= pd.to_datetime(gps_sbittip_tb16.epoch, unit= 's', utc=True)
gps_sbittip_tb16.set_index('epoch', inplace=True)

# helihoist
gps_helih_tb16= pd.read_csv('/Volumes/MASTERTHESE/MasterThese/GPS/turbine-16_helihoist-1_tom_gps.csv')
gps_helih_tb16.epoch= pd.to_datetime(gps_helih_tb16.epoch, unit= 's', utc=True)
gps_helih_tb16.set_index('epoch', inplace=True)

# %% OSCILLATION DATA

def concat_data(path):
    # concatenate files
    # indicate the correct path
    # files to concatenate must be in the same directory
    
    files = glob(path + "/*.csv")

    data = []

    for filename in files:
        df = pd.read_csv(filename, index_col=None, header=0)
        data.append(df)

    frame = pd.concat(data, axis=0, ignore_index=True)

    frame.epoch= pd.to_datetime(frame.epoch, unit= 's', utc=True)
    frame.set_index('epoch', inplace=True)
    frame = frame.sort_index()
    

    return frame


# TB 4

path_tb4_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb4/Blade_Landings/Helihoist'
hh_frame_tb4 = concat_data(path_tb4_hh)

path_tb4_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb4/Blade_Landings/sbitroot'
sbitroot_frame_tb4 = concat_data(path_tb4_sbitroot)


# TB 5

path_tb5_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb5/Blade_Landings/Helihoist'
hh_frame_tb5 = concat_data(path_tb5_hh)

path_tb5_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb5/Blade_Landings/sbitroot'
sbitroot_frame_tb5 = concat_data(path_tb5_sbitroot)


# TB 6

path_tb6_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb6/Blade_Landings/Helihoist'
hh_frame_tb6 = concat_data(path_tb6_hh)

path_tb6_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb6/Blade_Landings/sbitroot'
sbitroot_frame_tb6 = concat_data(path_tb6_sbitroot)


# TB 7

path_tb7_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb7/Blade_Landings/Helihoist'
hh_frame_tb7 = concat_data(path_tb7_hh)

path_tb7_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb7/Blade_Landings/sbitroot'
sbitroot_frame_tb7 = concat_data(path_tb7_sbitroot)

# TB 8 

path_tb8_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb8/Blade_Landings/Helihoist'
hh_frame_tb8 = concat_data(path_tb8_hh)

path_tb8_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb8/Blade_Landings/sbitroot'
sbitroot_frame_tb8 = concat_data(path_tb8_sbitroot)


# TB 10

path_tb10_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb10/Blade_Landings/Helihoist'
hh_frame_tb10 = concat_data(path_tb10_hh)

path_tb10_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb10/Blade_Landings/sbitroot'
sbitroot_frame_tb10 = concat_data(path_tb10_sbitroot)


# TB 11

path_tb11_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb11/Blade_Landings/Helihoist'
hh_frame_tb10 = concat_data(path_tb10_hh)

path_tb11_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb11/Blade_Landings/sbitroot'
sbitroot_frame_tb11 = concat_data(path_tb11_sbitroot)


# TB 12

path_tb12_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb12/Blade_Landings/Helihoist'
hh_frame_tb12 = concat_data(path_tb12_hh)

path_tb12_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb12/Blade_Landings/sbitroot'
sbitroot_frame_tb12 = concat_data(path_tb12_sbitroot)


# TB 13

path_tb13_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb13/Blade_Landings/Helihoist'
hh_frame_tb13 = concat_data(path_tb13_hh)

path_tb13_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb13/Blade_Landings/sbitroot'
sbitroot_frame_tb13 = concat_data(path_tb13_sbitroot)



# TB 14

path_tb14_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb14/Blade_Landings/Helihoist'
hh_frame_tb14 = concat_data(path_tb14_hh)

path_tb14_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb14/Blade_Landings/sbitroot'
sbitroot_frame_tb14 = concat_data(path_tb14_sbitroot)



# TB 16

path_tb16_hh = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb16/Blade_Landings/Helihoist'
hh_frame_tb16 = concat_data(path_tb16_hh)

path_tb16_sbitroot = r'/Volumes/MASTERTHESE/MasterThese/turbines/tb16/Blade_Landings/sbitroot'
sbitroot_frame_tb16 = concat_data(path_tb16_sbitroot)

# %% FUNCTIONS

def find_installationperiod(data_hh, data_sbitroot, data_sbittip):
    # Yield indices of installtion period.
    # Use altitude of dataset
    
    hub_height = 90 # hub height = 90m

    # smoothing the time series: cut the outliers and find the 20min mean value
    hh, sr, st = (data_hh.resample('1s').mean().rolling('20min').mean(), data_sbitroot.resample('1s').mean().rolling('20min').mean(), data_sbittip.resample('1s').mean().rolling('20min').mean())

    hh_sbi = hh[(hh > hub_height) & (sr > hub_height) & (st > hub_height)]
    sr_sbi = sr[(hh > hub_height) & (sr > hub_height) & (st > hub_height)]
    st_sbi = st[(hh > hub_height) & (sr > hub_height) & (st > hub_height)]

    # determine start and end period of single blade installations
    inst_period = sr_sbi[sr_sbi.index.to_series().diff() > pd.to_timedelta(60, unit='s')].index.to_list()
    inst_period.insert(0, sr_sbi.index[0])
    inst_period.insert(len(inst_period), sr_sbi.index[-1])
    sbi_indices = list()

    for i in range(len(inst_period) - 1):
        sbi_indices.append((inst_period[i], hh_sbi[inst_period[i]:inst_period[i+1]].index[-2]))
    
    return sbi_indices



def divide_chunks(lst, n):
    #Yield successive n-sized chunks from lst.
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
        
        
def find_impacts(acc_data, acc_data_check, acc_threshold, acc_threshold_check, time_limit, min_impact_time):
    # acc_data = acceleration data
    # acc_data_check = acceleration data to validate if it is really an impact
    # acc_threshold = acceleration threshold above which an acceleration is declared as an impact
    # acc_threshold_check = acceleration threshold above which an acceleration is declared as an impact (validation data)
    # time_limit = min. time between two impacts to avoid correlation
    # min_impact_time = min. impact duration
    
    
    # find start values of impact event

    sbitroot_ind = acc_data[(abs(acc_data) > acc_threshold) & (abs(acc_data_check) > acc_threshold_check)]

    # find the indices where the difference is bigger than the time limit (avoid correlation)

    deltaT_startImpact = sbitroot_ind[sbitroot_ind.index.to_series().diff() > time_limit].index.to_list()

    # find the points in time where the threshold is exceeded (start of the impact event)
    # add the start of the first impact event
    deltaT_startImpact.insert(0, sbitroot_ind.index[0])
    
    # find end values of impact event

    sbitroot_ind_inverse = sbitroot_ind.sort_index(ascending=False)

    # find the indices where the difference is bigger than the time limit (avoid correlation)

    deltaT_endImpact = sbitroot_ind_inverse[sbitroot_ind_inverse.index.to_series().diff() < -time_limit].index.to_list()

    # find the points in time where the threshold is exceeded (start of the impact event)
    # add the end of the last impact event
    deltaT_endImpact.insert(0, sbitroot_ind_inverse.index[0])
    deltaT_endImpact.sort(reverse=False)
    
    
    
    impact_times = list()
    for i in range(len(deltaT_endImpact)):
        if (deltaT_endImpact[i]- deltaT_startImpact[i]) > min_impact_time:
            # filter out measurement errors
            impact_times.append((deltaT_startImpact[i], deltaT_endImpact[i]))

    return impact_times


def find_indep_oscillations(sbi_indices, impact_times, wind_data_index, data):
    # sbi_indices = single blade installation times indices 
    # impact_times = impact indices
    # wind_data_index = index of wind data
    # data = the dataset where to find independent time periods
    
    # Find start values of sbi and impacts

    sbi_indices_start = [i[0] for i in sbi_indices]
    impact_times_start = [i[0] for i in impact_times]

    # Remove all impact starts after the end of the environmental data set, so that the deflection data set is of 
    #equal length to wind dataset. 

    impact_times_start= [x for x in impact_times_start if x < wind_data_index[-1]]


    # if the last first impact of the installation attempt gets cut off due to the shorter environmental data set, 
    # then add the last Datetime of environmental data in impacts (treated as impact event)

    if impact_times_start[-1]< sbi_indices_start[-1]:
        impact_times_start.append(wind_data_index[-1])
    
    # identify period from start sbi-period to first impact = INDEPENDENT OSCILLATION
    # write first impacts after start of blade installation into list
    # to identify independent oscillations, timestamp of impact needs to be bigger than timestamp of sbi-period
    # timestamp of impact needs to be the first impact after sbi-period

    # indices of first impacts
    first_impacts = []
    # timestamp of first impacts
    first_impacts_start = []

    for i in range (len(sbi_indices_start)):
        first_impacts.append(next(x for x, val in enumerate(impact_times_start)
                                      if val > sbi_indices_start[i] ))


    for i in range(len(sbi_indices_start)):
        first_impacts_start.append(impact_times_start[first_impacts[i]])
    
    independent_osc = []
    for i in range (len(sbi_indices_start)):
            independent_osc.append(data[sbi_indices_start[i]:impact_times_start[first_impacts[i]]])
    
    
    
    return independent_osc, sbi_indices_start, first_impacts_start



def block_maxima(data, sbi_indices_start, first_impacts_start):
    
    # calculate number of chunks for each independent interval 
    # number of chunks is the length of the independent interval divided by the time interval
    # therfore, the start value minus the end value of the independent interval is the time difference 

    time_interval = pd.to_timedelta(60, unit='s')

    indep_duration = []
    for i in range(len(sbi_indices_start)):
        indep_duration.append(first_impacts_start[i] - sbi_indices_start[i])

    num_chunks = []
    for i in range(len(sbi_indices_start)):
        num_chunks.append(indep_duration[i]/time_interval)
    
    
    # Determine the chunk size in each independent time interval 

    chunk_size_deflection = []
    for i in range(len(sbi_indices_start)):
        chunk_size_deflection.append(len(data[i])/ num_chunks[i])
        chunk_size_deflection[i] = math.floor(chunk_size_deflection[i])

    chunk_size_deflection = min(chunk_size_deflection) 
    
    # Create list with chunks of independent intervals 
    # Independent oscillations are split up into chunks
    # indep_blocks[i][j], here i indicates the installation attempt j indicates the blocks in each installation attempt

    indep_blocks = []
    for i in range(len(sbi_indices_start)):
        indep_blocks.append(list(divide_chunks(data[i], chunk_size_deflection)))
        
    # Determine block maxima, blocks that does not contain full 60 sec of data are filtered out. 

    block_maxima = []

    for i in range(len(sbi_indices_start)):
        for j in range(len(indep_blocks[i])):
            if len(indep_blocks[i][j]) == len(indep_blocks[0][0]): 
                block_maxima.append((indep_blocks[i][j].idxmax(), max(indep_blocks[i][j]) ))
    
    
    maxima_values = []
    for i in range (len(block_maxima)):
        maxima_values.append(block_maxima[i][1])
    
    return maxima_values



def block_mean(data, sbi_indices_start, first_impacts_start):
    # Determine the chunk size in each independent time interval 

    
    time_interval = pd.to_timedelta(60, unit='s')

    indep_duration = []
    for i in range(len(sbi_indices_start)):
        indep_duration.append(first_impacts_start[i] - sbi_indices_start[i])

    num_chunks = []
    for i in range(len(sbi_indices_start)):
        num_chunks.append(indep_duration[i]/time_interval)
    
    chunk_size_wind = []
    for i in range(len(sbi_indices_start)):
        chunk_size_wind.append(len(data[i])/ num_chunks[i])
        chunk_size_wind[i] = math.floor(chunk_size_wind[i])
        #chunk_size_wind[i] = math.ceil(chunk_size_wind[i])

    chunk_size_wind = min(chunk_size_wind) 
    
    # Create list with chunks of independent intervals 
    # Independent oscillations are split up into chunks
    # indep_blocks[i][j], here i indicates the installation attempt j indicates the blocks in each installation attempt

    indep_blocks_wind = []
    for i in range(len(sbi_indices_start)):
        indep_blocks_wind.append(list(divide_chunks(data[i], chunk_size_wind)))
        
        
    # Determine block maxima, blocks that does not contain full 60 sec of data are filtered out. 

    block_mean = []

    for i in range(len(sbi_indices_start)):
        for j in range(len(indep_blocks_wind[i])):
            if len(indep_blocks_wind[i][j]) == len(indep_blocks_wind[0][0]): 
                block_mean.append((indep_blocks_wind[i][j].mean() ))

    return block_mean

# %% INSTALLATION PERIODS

sbi_indices_tb4= find_installationperiod(gps_helih_tb4.altitude, gps_sbitroot_tb4.altitude, gps_sbittip_tb4.altitude)
sbi_indices_tb5= find_installationperiod(gps_helih_tb5.altitude, gps_sbitroot_tb5.altitude, gps_sbittip_tb5.altitude)
sbi_indices_tb6= find_installationperiod(gps_helih_tb6.altitude, gps_sbitroot_tb6.altitude, gps_sbittip_tb6.altitude)
#sbi_indices_tb7= find_installationperiod(gps_helih_tb7.altitude, gps_sbitroot_tb7.altitude, gps_sbittip_tb7.altitude)
sbi_indices_tb8= find_installationperiod(gps_helih_tb8.altitude, gps_sbitroot_tb8.altitude, gps_sbittip_tb8.altitude)
sbi_indices_tb10= find_installationperiod(gps_helih_tb10.altitude, gps_sbitroot_tb10.altitude, gps_sbittip_tb10.altitude)
sbi_indices_tb11= find_installationperiod(gps_helih_tb11.altitude, gps_sbitroot_tb11.altitude, gps_sbittip_tb11.altitude)
sbi_indices_tb12= find_installationperiod(gps_helih_tb12.altitude, gps_sbitroot_tb12.altitude, gps_sbittip_tb12.altitude)
#sbi_indices_tb13= find_installationperiod(gps_helih_tb13.altitude, gps_sbitroot_tb13.altitude, gps_sbittip_tb13.altitude)
sbi_indices_tb14= find_installationperiod(gps_helih_tb14.altitude, gps_sbitroot_tb14.altitude, gps_sbittip_tb14.altitude)
#sbi_indices_tb16= find_installationperiod(gps_helih_tb16.altitude, gps_sbitroot_tb16.altitude, gps_sbittip_tb16.altitude)


# %% OUTLIERS

# TB 4

# SBIT root 
median_x_tb4 = sbitroot_frame_tb4.loc[sbitroot_frame_tb4['acc_x']< abs(10), 'acc_x'].median()
median_z_tb4 = sbitroot_frame_tb4.loc[sbitroot_frame_tb4['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb4['acc_x'] = np.where(sbitroot_frame_tb4["acc_x"] > abs(10), median_x_tb4,sbitroot_frame_tb4['acc_x'])
sbitroot_frame_tb4['acc_z'] = np.where(sbitroot_frame_tb4["acc_z"] > abs(10), median_z_tb4,sbitroot_frame_tb4['acc_z'])


# TB 5

# SBIT root 
median_x_tb5 = sbitroot_frame_tb5.loc[sbitroot_frame_tb5['acc_x']< abs(10), 'acc_x'].median()
median_z_tb5 = sbitroot_frame_tb5.loc[sbitroot_frame_tb5['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb5['acc_x'] = np.where(sbitroot_frame_tb5["acc_x"] > abs(10), median_x_tb5,sbitroot_frame_tb5['acc_x'])
sbitroot_frame_tb5['acc_z'] = np.where(sbitroot_frame_tb5["acc_z"] > abs(10), median_z_tb5,sbitroot_frame_tb5['acc_z'])

# TB 6

# SBIT root 
median_x_tb6 = sbitroot_frame_tb6.loc[sbitroot_frame_tb6['acc_x']< abs(10), 'acc_x'].median()
median_z_tb6 = sbitroot_frame_tb6.loc[sbitroot_frame_tb6['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb6['acc_x'] = np.where(sbitroot_frame_tb6["acc_x"] > abs(10), median_x_tb6,sbitroot_frame_tb6['acc_x'])
sbitroot_frame_tb6['acc_z'] = np.where(sbitroot_frame_tb6["acc_z"] > abs(10), median_z_tb6,sbitroot_frame_tb6['acc_z'])

# TB 7

# SBIT root 
median_x_tb7 = sbitroot_frame_tb7.loc[sbitroot_frame_tb7['acc_x']< abs(10), 'acc_x'].median()
median_z_tb7 = sbitroot_frame_tb7.loc[sbitroot_frame_tb7['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb7['acc_x'] = np.where(sbitroot_frame_tb7["acc_x"] > abs(10), median_x_tb7,sbitroot_frame_tb7['acc_x'])
sbitroot_frame_tb7['acc_z'] = np.where(sbitroot_frame_tb7["acc_z"] > abs(10), median_z_tb7,sbitroot_frame_tb7['acc_z'])

# TB 8

# SBIT root 
median_x = sbitroot_frame_tb8.loc[sbitroot_frame_tb8['acc_x']< abs(10), 'acc_x'].median()
median_z = sbitroot_frame_tb8.loc[sbitroot_frame_tb8['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb8['acc_x'] = np.where(sbitroot_frame_tb8["acc_x"] > abs(10), median_x,sbitroot_frame_tb8['acc_x'])
sbitroot_frame_tb8['acc_z'] = np.where(sbitroot_frame_tb8["acc_z"] > abs(10), median_z,sbitroot_frame_tb8['acc_z'])


# TB 10

# SBIT root 
median_x_tb10 = sbitroot_frame_tb10.loc[sbitroot_frame_tb10['acc_x']< abs(10), 'acc_x'].median()
median_z_tb10 = sbitroot_frame_tb10.loc[sbitroot_frame_tb10['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb10['acc_x'] = np.where(sbitroot_frame_tb10["acc_x"] > abs(10), median_x_tb10,sbitroot_frame_tb10['acc_x'])
sbitroot_frame_tb10['acc_z'] = np.where(sbitroot_frame_tb10["acc_z"] > abs(10), median_z_tb10,sbitroot_frame_tb10['acc_z'])


# TB 11

# SBIT root 
median_x_tb11 = sbitroot_frame_tb11.loc[sbitroot_frame_tb11['acc_x']< abs(10), 'acc_x'].median()
median_z_tb11 = sbitroot_frame_tb11.loc[sbitroot_frame_tb11['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb11['acc_x'] = np.where(sbitroot_frame_tb11["acc_x"] > abs(10), median_x_tb11,sbitroot_frame_tb11['acc_x'])
sbitroot_frame_tb11['acc_z'] = np.where(sbitroot_frame_tb11["acc_z"] > abs(10), median_z_tb11,sbitroot_frame_tb11['acc_z'])


# TB 12

# SBIT root 
median_x_tb12 = sbitroot_frame_tb12.loc[sbitroot_frame_tb12['acc_x']< abs(10), 'acc_x'].median()
median_z_tb12 = sbitroot_frame_tb12.loc[sbitroot_frame_tb12['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb12['acc_x'] = np.where(sbitroot_frame_tb12["acc_x"] > abs(10), median_x_tb12,sbitroot_frame_tb12['acc_x'])
sbitroot_frame_tb12['acc_z'] = np.where(sbitroot_frame_tb12["acc_z"] > abs(10), median_z_tb12,sbitroot_frame_tb12['acc_z'])


# TB 13

# SBIT root 
median_x_tb13 = sbitroot_frame_tb13.loc[sbitroot_frame_tb13['acc_x']< abs(10), 'acc_x'].median()
median_z_tb13 = sbitroot_frame_tb13.loc[sbitroot_frame_tb13['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb13['acc_x'] = np.where(sbitroot_frame_tb13["acc_x"] > abs(10), median_x_tb13,sbitroot_frame_tb13['acc_x'])
sbitroot_frame_tb13['acc_z'] = np.where(sbitroot_frame_tb13["acc_z"] > abs(10), median_z_tb13,sbitroot_frame_tb13['acc_z'])



# TB 14

# SBIT root 
median_x_tb14 = sbitroot_frame_tb14.loc[sbitroot_frame_tb14['acc_x']< abs(10), 'acc_x'].median()
median_z_tb14 = sbitroot_frame_tb14.loc[sbitroot_frame_tb14['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb14['acc_x'] = np.where(sbitroot_frame_tb14["acc_x"] > abs(10), median_x_tb14,sbitroot_frame_tb14['acc_x'])
sbitroot_frame_tb14['acc_z'] = np.where(sbitroot_frame_tb14["acc_z"] > abs(10), median_z_tb14,sbitroot_frame_tb14['acc_z'])



# TB 16

# SBIT root 
median_x_tb16 = sbitroot_frame_tb16.loc[sbitroot_frame_tb16['acc_x']< abs(10), 'acc_x'].median()
median_z_tb16 = sbitroot_frame_tb16.loc[sbitroot_frame_tb16['acc_z']< abs(10), 'acc_z'].median()

sbitroot_frame_tb16['acc_x'] = np.where(sbitroot_frame_tb16["acc_x"] > abs(10), median_x_tb16,sbitroot_frame_tb16['acc_x'])
sbitroot_frame_tb16['acc_z'] = np.where(sbitroot_frame_tb16["acc_z"] > abs(10), median_z_tb16,sbitroot_frame_tb16['acc_z'])

# %% DETERMINE INSTALLTION PERIOD

# TB 4

sbitroot_installation_tb4 = pd.DataFrame()

for start, end in sbi_indices_tb4:
    sbitroot_installation_tb4 = sbitroot_installation_tb4.append(sbitroot_frame_tb4[start:end])


# TB 5

sbitroot_installation_tb5 = pd.DataFrame()

for start, end in sbi_indices_tb5:
    sbitroot_installation_tb5 = sbitroot_installation_tb5.append(sbitroot_frame_tb5[start:end])

# TB 6

sbitroot_installation_tb6 = pd.DataFrame()

for start, end in sbi_indices_tb6:
    sbitroot_installation_tb6 = sbitroot_installation_tb6.append(sbitroot_frame_tb6[start:end])

# TB 7

#sbitroot_installation_tb7 = pd.DataFrame()

#for start, end in sbi_indices_tb7:
    #sbitroot_installation_tb7 = sbitroot_installation_tb7.append(sbitroot_frame_tb7[start:end])
    
    
    
# TB 8

sbitroot_installation_tb8 = pd.DataFrame()

for start, end in sbi_indices_tb8:
    sbitroot_installation_tb8 = sbitroot_installation_tb8.append(sbitroot_frame_tb8[start:end])


# TB 10

sbitroot_installation_tb10 = pd.DataFrame()

for start, end in sbi_indices_tb10:
    sbitroot_installation_tb10 = sbitroot_installation_tb10.append(sbitroot_frame_tb10[start:end])



# TB 11

sbitroot_installation_tb11 = pd.DataFrame()

for start, end in sbi_indices_tb11:
    sbitroot_installation_tb11 = sbitroot_installation_tb11.append(sbitroot_frame_tb11[start:end])
    
    
    
# TB 12

sbitroot_installation_tb12 = pd.DataFrame()

for start, end in sbi_indices_tb12:
    sbitroot_installation_tb12 = sbitroot_installation_tb12.append(sbitroot_frame_tb12[start:end])



# TB 13

#sbitroot_installation_tb13 = pd.DataFrame()


#for start, end in sbi_indices_tb13:
    #sbitroot_installation_tb13 = sbitroot_installation_tb13.append(sbitroot_frame_tb13[start:end])
    


# TB 14

sbitroot_installation_tb14 = pd.DataFrame()

for start, end in sbi_indices_tb14:
    sbitroot_installation_tb14 = sbitroot_installation_tb14.append(sbitroot_frame_tb14[start:end])
    


# TB 16

#sbitroot_installation_tb16 = pd.DataFrame()

#for start, end in sbi_indices_tb16:
    #sbitroot_installation_tb16 = sbitroot_installation_tb16.append(sbitroot_frame_tb16[start:end])

# %% IMPACT THRESHOLDS

# Find independent oscillation periods

acc_threshold_x = 0.5 #acceleration threshold (m/s^2)
acc_threshold_z = 0.5
acc_threshold_y = 0.3

limit = pd.to_timedelta(60, unit='s') #time limit to avoid correlation
min_impact_time = pd.to_timedelta(10, unit='s') # minimum time of impact event, erasing measurment errors


list_of_turbines= [4,5,6,8,10,11,12,14]
print(list_of_turbines)

# %% IMPACTS X DIRECTION

impact_times_tb4_x= find_impacts(sbitroot_installation_tb4.acc_x, sbitroot_installation_tb4.acc_y, acc_threshold_x, acc_threshold_y, limit, min_impact_time)
impact_times_tb5_x= find_impacts(sbitroot_installation_tb5.acc_x, sbitroot_installation_tb5.acc_y, acc_threshold_x, acc_threshold_y, limit, min_impact_time)
impact_times_tb6_x= find_impacts(sbitroot_installation_tb6.acc_x, sbitroot_installation_tb6.acc_y, acc_threshold_x, acc_threshold_y, limit, min_impact_time)
impact_times_tb8_x= find_impacts(sbitroot_installation_tb8.acc_x, sbitroot_installation_tb8.acc_y, acc_threshold_x, acc_threshold_y, limit, min_impact_time)
impact_times_tb10_x= find_impacts(sbitroot_installation_tb10.acc_x, sbitroot_installation_tb10.acc_y, acc_threshold_x, acc_threshold_y, limit, min_impact_time)
impact_times_tb11_x= find_impacts(sbitroot_installation_tb11.acc_x, sbitroot_installation_tb11.acc_y, acc_threshold_x, acc_threshold_y, limit, min_impact_time)
impact_times_tb12_x= find_impacts(sbitroot_installation_tb12.acc_x, sbitroot_installation_tb12.acc_y, acc_threshold_x, acc_threshold_y, limit, min_impact_time)
impact_times_tb14_x= find_impacts(sbitroot_installation_tb14.acc_x, sbitroot_installation_tb14.acc_y, acc_threshold_x, acc_threshold_y, limit, min_impact_time)

# %% IMPACTS Z DIRECTION

impact_times_tb4_z= find_impacts(sbitroot_installation_tb4.acc_z, sbitroot_installation_tb4.acc_y, acc_threshold_z, acc_threshold_y, limit, min_impact_time)
impact_times_tb5_z= find_impacts(sbitroot_installation_tb5.acc_z, sbitroot_installation_tb5.acc_y, acc_threshold_z, acc_threshold_y, limit, min_impact_time)
impact_times_tb6_z= find_impacts(sbitroot_installation_tb6.acc_z, sbitroot_installation_tb6.acc_y, acc_threshold_z, acc_threshold_y, limit, min_impact_time)
impact_times_tb8_z= find_impacts(sbitroot_installation_tb8.acc_z, sbitroot_installation_tb8.acc_y, acc_threshold_z, acc_threshold_y, limit, min_impact_time)
impact_times_tb10_z= find_impacts(sbitroot_installation_tb10.acc_z, sbitroot_installation_tb10.acc_y, acc_threshold_z, acc_threshold_y, limit, min_impact_time)
impact_times_tb11_z= find_impacts(sbitroot_installation_tb11.acc_z, sbitroot_installation_tb11.acc_y, acc_threshold_z, acc_threshold_y, limit, min_impact_time)
impact_times_tb12_z= find_impacts(sbitroot_installation_tb12.acc_z, sbitroot_installation_tb12.acc_y, acc_threshold_z, acc_threshold_y, limit, min_impact_time)
impact_times_tb14_z= find_impacts(sbitroot_installation_tb14.acc_z, sbitroot_installation_tb14.acc_y, acc_threshold_z, acc_threshold_y, limit, min_impact_time)

# %% IMPACTS COMBINED

impact_times_tb4 = impact_times_tb4_z + impact_times_tb4_x
impact_times_tb4.sort()

impact_times_tb5 = impact_times_tb5_z + impact_times_tb5_x
impact_times_tb5.sort()

impact_times_tb6 = impact_times_tb6_z + impact_times_tb6_x
impact_times_tb6.sort()

impact_times_tb8 = impact_times_tb8_z + impact_times_tb8_x
impact_times_tb8.sort()

impact_times_tb10 = impact_times_tb10_z + impact_times_tb10_x
impact_times_tb10.sort()

impact_times_tb11 = impact_times_tb11_z + impact_times_tb11_x
impact_times_tb11.sort()

impact_times_tb12 = impact_times_tb12_z + impact_times_tb12_x
impact_times_tb12.sort()

impact_times_tb14 = impact_times_tb14_z + impact_times_tb14_x
impact_times_tb14.sort()

# %% INDEPENDENT DEFLECTION

indep_deflection_tb4, sbi_start_tb4, impact_start_tb4= find_indep_oscillations(sbi_indices_tb4, impact_times_tb4, wind_data.index, sbitroot_installation_tb4.deflection )
indep_deflection_tb5, sbi_start_tb5, impact_start_tb5= find_indep_oscillations(sbi_indices_tb5, impact_times_tb5, wind_data.index, sbitroot_installation_tb5.deflection )
indep_deflection_tb6, sbi_start_tb6, impact_start_tb6= find_indep_oscillations(sbi_indices_tb6, impact_times_tb6, wind_data.index, sbitroot_installation_tb6.deflection )
indep_deflection_tb8, sbi_start_tb8, impact_start_tb8= find_indep_oscillations(sbi_indices_tb8, impact_times_tb8, wind_data.index, sbitroot_installation_tb8.deflection )
indep_deflection_tb10, sbi_start_tb10, impact_start_tb10= find_indep_oscillations(sbi_indices_tb10, impact_times_tb10, wind_data.index, sbitroot_installation_tb10.deflection )
indep_deflection_tb11, sbi_start_tb11, impact_start_tb11= find_indep_oscillations(sbi_indices_tb11, impact_times_tb11, wind_data.index, sbitroot_installation_tb11.deflection )
indep_deflection_tb12, sbi_start_tb12, impact_start_tb12= find_indep_oscillations(sbi_indices_tb12, impact_times_tb12, wind_data.index, sbitroot_installation_tb12.deflection )
indep_deflection_tb14, sbi_start_tb14, impact_start_tb14= find_indep_oscillations(sbi_indices_tb14, impact_times_tb14, wind_data.index, sbitroot_installation_tb14.deflection )

# %% INDEPENDENT ENVIRONMENT

indep_wind_tb4, sbi_start_tb4, impact_start_tb4 = find_indep_oscillations(sbi_indices_tb4, impact_times_tb4, wind_data.index, wind_data.wind_speed_0)
indep_wind_tb5, sbi_start_tb5, impact_start_tb5 = find_indep_oscillations(sbi_indices_tb5, impact_times_tb5, wind_data.index, wind_data.wind_speed_0)
indep_wind_tb6, sbi_start_tb6, impact_start_tb6 = find_indep_oscillations(sbi_indices_tb6, impact_times_tb6, wind_data.index, wind_data.wind_speed_0)
indep_wind_tb8, sbi_start_tb8, impact_start_tb8 = find_indep_oscillations(sbi_indices_tb8, impact_times_tb8, wind_data.index, wind_data.wind_speed_0)
indep_wind_tb10, sbi_start_tb10, impact_start_tb10 = find_indep_oscillations(sbi_indices_tb10, impact_times_tb10, wind_data.index, wind_data.wind_speed_0)
indep_wind_tb11, sbi_start_tb11, impact_start_tb11 = find_indep_oscillations(sbi_indices_tb11, impact_times_tb11, wind_data.index, wind_data.wind_speed_0)
indep_wind_tb12, sbi_start_tb12, impact_start_tb12 = find_indep_oscillations(sbi_indices_tb12, impact_times_tb12, wind_data.index, wind_data.wind_speed_0)
indep_wind_tb14, sbi_start_tb14, impact_start_tb14 = find_indep_oscillations(sbi_indices_tb14, impact_times_tb14, wind_data.index, wind_data.wind_speed_0)


# %% BLOCK MAXIMA DEFLECTION

maxima_values_tb4= block_maxima(indep_deflection_tb4, sbi_start_tb4, impact_start_tb4)
maxima_values_tb5= block_maxima(indep_deflection_tb5, sbi_start_tb5, impact_start_tb5)
maxima_values_tb6= block_maxima(indep_deflection_tb6, sbi_start_tb6, impact_start_tb6)
maxima_values_tb8= block_maxima(indep_deflection_tb8, sbi_start_tb8, impact_start_tb8)
maxima_values_tb10= block_maxima(indep_deflection_tb10, sbi_start_tb10, impact_start_tb10)
maxima_values_tb11= block_maxima(indep_deflection_tb11, sbi_start_tb11, impact_start_tb11)
maxima_values_tb12= block_maxima(indep_deflection_tb12, sbi_start_tb12, impact_start_tb12)
maxima_values_tb14= block_maxima(indep_deflection_tb14, sbi_start_tb14, impact_start_tb14)


# %% BLOCK MEAN WIND

mean_wind_tb4= block_mean(indep_wind_tb4, sbi_start_tb4, impact_start_tb4)
mean_wind_tb5= block_mean(indep_wind_tb5, sbi_start_tb5, impact_start_tb5)
mean_wind_tb6= block_mean(indep_wind_tb6, sbi_start_tb6, impact_start_tb6)
mean_wind_tb8= block_mean(indep_wind_tb8, sbi_start_tb8, impact_start_tb8)
mean_wind_tb10= block_mean(indep_wind_tb10, sbi_start_tb10, impact_start_tb10)
mean_wind_tb11= block_mean(indep_wind_tb11, sbi_start_tb11, impact_start_tb11)
mean_wind_tb12= block_mean(indep_wind_tb12, sbi_start_tb12, impact_start_tb12)
mean_wind_tb14= block_mean(indep_wind_tb14, sbi_start_tb14, impact_start_tb14)

# %% RESPONSE EMULATOR DATA

maxima_deflection= maxima_values_tb4+ maxima_values_tb5+ maxima_values_tb6+ maxima_values_tb8+ maxima_values_tb10+ maxima_values_tb11+ maxima_values_tb12+ maxima_values_tb14
mean_wind= mean_wind_tb4 + mean_wind_tb5+ mean_wind_tb6+ mean_wind_tb8+ mean_wind_tb10+ mean_wind_tb11+ mean_wind_tb12+ mean_wind_tb14


data_unsorted = {'windspeed':mean_wind,'deflection':maxima_deflection}
data_unsorted = pd.DataFrame(data_unsorted)
data_unsorted["deflection"] = 100 * data_unsorted["deflection"] # convert deflection into cm
data_unsorted.to_csv('/Volumes/MASTERTHESE/MasterThese/data_unsorted.csv')


mean_wind.sort()
maxima_deflection.sort()

data_sorted = {'windspeed':mean_wind,'deflection':maxima_deflection}
data_sorted = pd.DataFrame(data_sorted)
data_sorted["deflection"] = 100 * data_sorted["deflection"] # convert deflection into cm
data_sorted.to_csv('/Volumes/MASTERTHESE/MasterThese/data_sorted.csv')

