#!/usr/bin/python3

import pandas as pd
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', help='Time Tracking excel sheet', type=str)
    parser.add_argument('-o', '--output', help='Output pickle file', type=str)
    parser.add_argument('--output-csv', help='Output csv file', default=None)
 
    args = parser.parse_args()

    try:
        tt = pd.read_excel(args.input)
    except Exception as e:
        print('failed to read in excel file: {}'.format(e))

    tt.fillna(method='ffill', inplace=True)

    BWs = [bw.replace(' ', '') for bw in tt['OWEC'].unique()]

    # extract nacelle installation end
    start = tt['Nacelle Installation End'].unique()

    # convert time zone 
    start = [pd.to_datetime(s).tz_localize('Europe/Berlin') for s in start]

    #sucessful blade one installation
    blade1_start = tt.loc[(tt['Blade Number'] == 'Blade 1') & (tt['Blade Installation Status'] == 'successful')]['Blade Installation Start'].unique()
    blade1_end = tt.loc[(tt['Blade Number'] == 'Blade 1') & (tt['Blade Installation Status'] == 'successful')]['Blade Installation End'].unique()

    blade1_start = [pd.to_datetime(t).tz_localize('Europe/Berlin') for t in blade1_start]
    blade1_end = [pd.to_datetime(t).tz_localize('Europe/Berlin') for t in blade1_end]

    #sucessful blade two installation
    blade2_start = tt.loc[(tt['Blade Number'] == 'Blade 2') & (tt['Blade Installation Status'] == 'successful')]['Blade Installation Start'].unique()
    blade2_end = tt.loc[(tt['Blade Number'] == 'Blade 2') & (tt['Blade Installation Status'] == 'successful')]['Blade Installation End'].unique()

    blade2_start = [pd.to_datetime(t).tz_localize('Europe/Berlin') for t in blade2_start]
    blade2_end = [pd.to_datetime(t).tz_localize('Europe/Berlin') for t in blade2_end]

    #sucessful blade two installation
    blade3_start = tt.loc[
            (tt['Blade Number'] == 'Blade 3') 
            & 
            (tt['Blade Installation Status'] == 'successful')
            ]['Blade Installation Start'].unique()

    blade3_end = tt.loc[(tt['Blade Number'] == 'Blade 3') & (tt['Blade Installation Status'] == 'successful')]['Blade Installation End'].unique()

    blade3_start = [pd.to_datetime(t).tz_localize('Europe/Berlin') for t in blade3_start]
    blade3_end = [pd.to_datetime(t).tz_localize('Europe/Berlin') for t in blade3_end]

    installationTimes = pd.DataFrame({'BW' : BWs,
                                      'start' : start,
                                      'blade1_start' : blade1_start,
                                      'blade1_end' : blade1_end,
                                      'blade1_delta' : [pd.Timedelta(e - s, unit='s') for e, s in zip(blade1_end, blade1_start)],
                                      'blade2_start' : blade2_start,
                                      'blade2_end' : blade2_end,
                                      'blade2_delta' : [pd.Timedelta(e - s, unit='s') for e, s in zip(blade2_end, blade2_start)],
                                      'blade3_start' : blade3_start,
                                      'blade3_end' : blade3_end,
                                      'blade3_delta' : [ pd.Timedelta(e - s, unit='s') for e, s in zip(blade3_end, blade3_start)],
                                      'installation_delta' : [pd.Timedelta(e - s, unit='s') for e, s in zip(blade3_end, start)],
                                     })

    installationTimes.set_index('BW', inplace=True)

    # export installation times dataframe
    installationTimes.to_pickle(args.output)
    if args.output_csv:
        installationTimes.to_csv(args.output_csv)


