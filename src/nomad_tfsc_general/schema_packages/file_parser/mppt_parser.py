#!/usr/bin/env python3
"""
Created on Thur Feb  19 10:00:00 2026

@author: a5263
"""

""""
MPPT measurement of the best pixel as per the following protocol:
1.Measure IV-sweep for all pixels of the sample
2.Remeasure the IV-sweep for the best pixel
3.MPPT for the best pixel: starting voltage from the second IV-sweep
4.Measure IV-sweep for the best pixel 3rd time
"""
from io import StringIO

import numpy as np
import pandas as pd

from baseclasses.helper.utilities import convert_datetime

#i want to get timestamp from vtt's filename, remember to pass from read_mppt_file function

def get_value(val):
    try:
        return float(val)
    except Exception:
        return None
    
def find_step_size(df_curve):
    for i in range(5):
        dV= abs(df_curve.iloc[i,1] - df_curve.iloc[i+1,1])
        if dV!= 0:
            return dV
    return ValueError("No non-zero voltage step found in the first 5 rows")

def get_mppt_data_location_1(filedata, filename=None):
    date = filedata.split('\t')[0].split('\n')[0].split(' ')[-2]
    time = filedata.split('\t')[0].split('\n')[0].split(' ')[-1]
    convert_datetime(f'{date} {time}', '%d-%m-%Y %H:%M:%S')

def get_mppt_data_location_2(filedata, filename=None):            
    df_header = pd.read_csv(
        StringIO(filedata),
        nrows=1, 
        sep=':\t', 
        encoding='unicode_escape', 
        engine='python',
        )
    
    
    df_curve = pd.read_csv(
        StringIO(filedata),
        header=10,
        sep='\t',
        encoding='unicode_escape',
        engine='python',
        )
    
    df_curve = df_curve.dropna(how='any', axis=0)

    
    mppt_dict = {}
    if filename:
        date = filename.split('_')[-2]
        time = filename.split('_')[-1].split('.')[0]
        mppt_dict['datetime'] = convert_datetime(f'{date} {time}', '%Y%m%d %H%M%S')
    mppt_dict['total_time'] = get_value(df_curve.iloc[-1, 0])
    mppt_dict['step_size'] = find_step_size(df_curve)

    mppt_dict['time_data'] = np.array(df_curve['Time (s)'], dtype=np.float64)
    mppt_dict['voltage_data'] = np.array(df_curve['Voltage (V)'], dtype=np.float64)
    mppt_dict['current_density_data'] = np.array(df_curve['Current density (mA/cm2)'], dtype=np.float64)
    mppt_dict['power_data'] = np.array(df_curve['power'], dtype=np.float64)

    return mppt_dict

def get_mppt_data(filedata):
    #selection logic for the two data types
    pass