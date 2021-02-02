import pandas as pd
import numpy as np
from multiprocessing import Pool
from glob import glob 
from os import path

def read_frame(file_path):
    try:
        frame = pd.read_csv(file_path)
    except:
        print('* failed to read in file: {} ... skipping'.format(file_path))
        return pd.DataFrame()
    
    frame.epoch = pd.to_datetime(frame.epoch, unit='s', utc=True)
    frame.set_index('epoch', inplace=True)
    return frame

def read_frames_parallel(input_dir, pattern='*.csv', n_procs=8):
    
    pool = Pool(n_procs)
    frames = list()
    for data_file in sorted(glob(path.join(input_dir, pattern))):
        frames.append(pool.apply_async(read_frame, (data_file,)))

    pool.close()
    pool.join()
    
    return [frame.get() for frame in frames]

def write_frame(frame, out_file_path, precision='%1.5f'):

    # numpy copy
    frame_np = frame.to_numpy()
    header = str(frame.columns.to_list()).replace('[','').replace(']','')
    
    try:
        np.savetxt(out_file_path, frame_np, '%1.5f', header=header)
    except Exception as e:
        print(f'failed to export data {e} - skippig file {out_file_path}')

def generate_datetime_str(df_index):
    frame_start_time = "{:04}-{:02}-{:02}-{:02}-{:02}-{:02}".format(
        df_index[0].year,
        df_index[0].month,
        df_index[0].day,
        df_index[0].hour,
        df_index[0].minute,
        df_index[0].second,
    ) 
    
    frame_end_time = "{:04}-{:02}-{:02}-{:02}-{:02}-{:02}".format(
        df_index[-1].year,
        df_index[-1].month,
        df_index[-1].day,
        df_index[-1].hour,
        df_index[-1].minute,
        df_index[-1].second,
    )

    return f'{frame_start_time}_{frame_end_time}'

def export_data(dataframes, args):
    """
    export a list of dataframes as csv's
    """
    for df in dataframes:
        out_file_name = f'{args.output_prefix}_{generate_datetime_str(df.index)}.csv'
        out_file_path = path.join(args.output, out_file_name)
        if args.verbose: print('* exporting data file: {}'.format(out_file_path))
        write_frame(frame=df, out_file_path=out_file_path)



def export_data_parallel(dataframes, args):
    """
    exports a list of dataframes in parallel
    """

    pool = Pool(args.procs)
    
    for df in dataframes:
        # parse name
        out_file_name = f'{args.output_prefix}_{generate_datetime_str(df.index)}.csv'
        
        out_file_path = path.join(args.output, out_file_name)
        
        if args.verbose: print(f'* exporting data file: {out_file_path}')

        pool.apply(write_frame, (df, out_file_path))

    pool.close()
    pool.join()