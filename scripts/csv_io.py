import pandas as pd
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

def write_output_file(frame, out_file_path):
    try:
        frame.to_csv(out_file_path)
    except:
        print('failed to export data - skippig file {}'.format(out_file_path))