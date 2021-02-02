import pandas as pd 
import argparse
from os import path
import sys

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from mythicwind.csv_io import write_frame

def parse_arguments():
    parser = argparse.ArgumentParser()
    
    # I/O arguments
    parser.add_argument("--verbose", help="turn on detailed output", action="store_true")
    parser.add_argument("--input", nargs='+', help='input: single file or list of files')
    parser.add_argument("--output", help="output: directory for output files", type=str)
    parser.add_argument("--output-prefix", help="output file prefix. Default is acceleration-velocity-position", type=str, default='acceleration-velocity-position')
    parser.add_argument("--procs", help="number of processors to use", type=int)
    parser.add_argument("--min-elements", help='number of minimum data elements for export', default=6, type=int)
    parser.add_argument("--waves", help='special flag to convert wave pickles', action="store_true")  

    return parser.parse_args()



if __name__ == '__main__':
    args = parse_arguments()
    
    data = list()

    for pickle_file in args.input:
        if args.verbose: print(f'processing {pickle_file}')
        if path.isfile(pickle_file):
            try:
                data.append(pd.read_pickle(pickle_file))
            except Exception as e:
                print(f'failed to read in pickle {pickle_file}: {e} ... skipping')
        else:
            print(f'* not a file: {pickle_file}')
    if args.verbose: print(f'converting to csv')
    
    
    for df in data:
        if args.waves:
            df.drop(columns=['Zeitpunkt gerundet', 'Date/Time', 'Date/Time.1'], inplace=True)

        # check if the epoch column is present
        if not hasattr(df, 'epoch'):
            # convert index to epoch and insert into data
            df.insert(
                loc=0,
                column='epoch',
                value=df.index.astype('int64')/1.0e9
            )

        for day, data in df.groupby(pd.Grouper(freq='D')):
            if len(data) < args.min_elements:         # 10 min
                if args.verbose: print('* skipping day: {}'.format(day))
                continue

            datestring = '{:04d}-{:02d}-{:02d}'.format(day.year, day.month, day.day)
            export_csv_path = path.join(args.output, "{}_{}.csv".format(args.output_prefix, datestring))

            if args.verbose: print(f'regrouping to pickle into days: {export_csv_path}')
            if args.verbose: print("*   exporting {}".format(export_csv_path))

            write_frame(frame=data, out_file_path=export_csv_path)

