# coding: utf-8
import pandas as pd
from glob import glob

blade_landing = pd.to_datetime('2019-10-15 10:57', utc=True)

files = glob('turbine-08_sbitroot_tom_acc-vel-pos_2019-10-1*.csv')

for f in files:
    
    f_start = pd.to_datetime(f.split('_')[4], utc=True, format='%Y-%m-%d-%H-%M-%S')
    f_end = pd.to_datetime(f.split('_')[5].split('.')[0], utc=True, format='%Y-%m-%d-%H-%M-%S')
    if f_start < blade_landing and f_end > blade_landing:
        print(f'found file: {f}: {f_start}, {f_end}')
        
