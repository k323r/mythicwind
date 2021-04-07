#!/usr/bin/python3

# TODO make all time stamps time zone aware
# TODO insert time deltas for all available installations
# TODO add blade landing times from bas

import pandas as pd
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="xlsx sheet containing the time tracks of the installation")
    parser.add_argument("--installation-times", help="csv output file path")
    parser.add_argument("--blade-installation-times",
                        help="output file path to store the blade installation times")
    parser.add_argument("-v", "--verbose",
                        help="verbose flag", action='store_true')

    args = parser.parse_args()

    if not args.input:
        print("*! please provide an input file")
        exit()

    if not args.installation_times and not args.blade_installation_times:
        print("*! will not export any data!")

    if args.verbose:
        print('* reading in time tracking sheet: {}'.format(args.input))

    try:
        installationTimes = pd.read_excel(args.input,
                                          converters={
                                              'tower_installation_start': pd.to_datetime,
                                              'tower_installation_end': pd.to_datetime,
                                              'nacelle_installation_start': pd.to_datetime,
                                              'nacelle_installation_end': pd.to_datetime,
                                              'blade_installation_start': pd.to_datetime,
                                              'blade_installation_end': pd.to_datetime,
                                          },
                                          )
    except Exception as e:
        print("*! failed to read in ecxcel file: {}".format(e))
        exit()

    if args.verbose:
        print('* input file: {}'.format(args.input))

    # build a dictionary to rename columns
    rename_columns = {name: name.lower().replace(' ', '_')
                      for name in installationTimes.columns}

    # rename all columns
    installationTimes.rename(columns=rename_columns, inplace=True)

    # drop all empty lines
    installationTimes = installationTimes[~installationTimes['blade_installation_status'].isnull(
    )]

    # drop the names of the turbines
    installationTimes.drop(columns=['owec', ], inplace=True)

    # make a copy of the data to split it into TNH installation and blade installation
    bladeInstallationTimes = installationTimes.copy(deep=True)

    installationTimes = installationTimes[~installationTimes['tower_installation_end'].isnull(
    )]
    installationTimes.reset_index(inplace=True)

    # remove all blade installation related data
    installationTimes.drop(columns=['blade_number',
                                    'blade_installation_attempt',
                                    'blade_installation_start',
                                    'blade_installation_end',
                                    'blade_installation_status',
                                    'blade_installation_comment',
                                    'index'
                                    ], inplace=True)

    installationTimes.insert(loc=0,
                             column='turbine_name',
                             value=[f'turbine-{i:02d}' for i in installationTimes["installation_no"].astype(int)])
    installationTimes.insert(loc=0,
                             column='turbine_id',
                             value=[i for i in installationTimes["installation_no"].astype(int)])

    # installationTimes['Blade Installation Start'].apply(lambda dt: pd.to_datetime(dt))
    installationTimes["installation_no"] = installationTimes["installation_no"].apply(
        lambda x: int(x))

    # add epoch time stamps
    installationTimes.insert(loc=installationTimes.columns.to_list().index('tower_installation_start')+1,
                             column='tower_installation_start_epoch',
                             value=installationTimes.tower_installation_start.apply(
                                 lambda x: int(x.timestamp())),
                             )

    installationTimes.insert(loc=installationTimes.columns.to_list().index('tower_installation_end')+1,
                             column='tower_installation_end_epoch',
                             value=installationTimes.tower_installation_end.apply(
                                 lambda x: int(x.timestamp())),
                             )

    installationTimes.insert(loc=installationTimes.columns.to_list().index('nacelle_installation_start')+1,
                             column='nacelle_installation_start_epoch',
                             value=installationTimes.nacelle_installation_start.apply(
                                 lambda x: int(x.timestamp())),
                             )

    installationTimes.insert(loc=installationTimes.columns.to_list().index('nacelle_installation_end')+1,
                             column='nacelle_installation_end_epoch',
                             value=installationTimes.nacelle_installation_end.apply(
                                 lambda x: int(x.timestamp())),
                             )

    # Blade  installation times
    # fill nans
    bladeInstallationTimes.fillna(method='ffill', inplace=True)

    bladeInstallationTimes.insert(loc=0,
                                  column='blade_installation_id',
                                  value=[i+1 for i in range(len(bladeInstallationTimes['blade_number']))])
    # for the database to be used as a primary key
    bladeInstallationTimes.insert(loc=1,
                                  column='turbine_id',
                                  value=[i for i in bladeInstallationTimes["installation_no"].astype(int)])

    bladeInstallationTimes['installation_no'] = bladeInstallationTimes['installation_no'].apply(
        lambda x: int(x))
    bladeInstallationTimes['blade_installation_attempt'] = bladeInstallationTimes['blade_installation_attempt'].apply(
        lambda x: int(x))
    bladeInstallationTimes['blade_number'] = bladeInstallationTimes['blade_number'].apply(
        lambda x: int(x.split(' ')[1]))

    bladeInstallationTimes.reset_index(inplace=True)
    # remove all non-blade installation related stuff
    bladeInstallationTimes.drop(columns=['tower_installation_start',
                                         'tower_installation_end',
                                         'nacelle_installation_start',
                                         'nacelle_installation_end',
                                         'blade_installation_comment',
                                         'index'
                                         ], inplace=True)

    bladeInstallationTimes.insert(loc=bladeInstallationTimes.columns.to_list().index('blade_installation_start')+1,
                                  column='blade_installation_start_epoch',
                                  value=bladeInstallationTimes.blade_installation_start.apply(
                                      lambda x: int(x.timestamp())),
                                  )

    bladeInstallationTimes.insert(loc=bladeInstallationTimes.columns.to_list().index('blade_installation_end')+1,
                                  column='blade_installation_end_epoch',
                                  value=bladeInstallationTimes.blade_installation_end.apply(
                                      lambda x: int(x.timestamp())),
                                  )

    try:
        installationTimes.to_csv(args.installation_times, index=False)
    except Exception as e:
        print(f'failed to export data {e}')

    try:
        bladeInstallationTimes.to_csv(
            args.blade_installation_times, index=False)
    except Exception as e:
        print('*! failed to export time selection pickle: {}'.format(e))
