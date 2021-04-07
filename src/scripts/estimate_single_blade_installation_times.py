import sys
from os import path
import argparse

# from ..mythicwind.tom import process_data_set_parallel

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from mythicwind.gps import read_gps_frame

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help='input gps track data')
    parser.add_argument('--output', type=str, required=True, help='output csv file containing sbit meta data')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    print(f'input: {args.input}')
    print(f'output: {args.output}')

