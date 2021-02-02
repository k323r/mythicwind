#!/usr/bin/env python3

import pandas as pd


COLS_FFILL = [
    'Installation No',
    'OWEC',
    'Tower Installation Start',
    'Tower Installation End',
    'Nacelle Installation Start',
    'Nacelle Installation End',
    'Blade Number']


df = pd.read_excel(
    'Time-Tracking_TWBII_Master_Overview.xlsx',
    sheet_name='Installation Times')
df.loc[:, COLS_FFILL] = df.loc[:, COLS_FFILL].ffill()
df.to_csv('clean_installation_times.csv', index=False)
