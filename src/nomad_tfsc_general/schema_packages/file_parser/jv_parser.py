#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import ast
from io import StringIO

import numpy as np
import pandas as pd
from baseclasses.helper.utilities import convert_datetime


def get_jv_data_location_1(filedata):
    # Parse Location 1 IV format - tab-separated data with each row as measurement repetition
    lines = filedata.strip().split('\n')
    data = [line.strip().split("\t") for line in lines]

    #each row in the datafile represents a measurement repetition.
    #here i'm only parsing out the last repetition. 
  
    date = data[-1][1]                      #measurement date
    v_start = float(data[-1][2])            #v start [V] 
    v_end = float(data[-1][3])              #v end [V]
    v_delta = float(data[-1][4])            #v step [V]
    p1_cell_area = float(data[-1][6])       #cell area pixel 1 [cm2]

    Jsc_rev = data[-1][10:14]               #Jsc of reverse sweeps
    # Clean up the 'hysteresis$' string from Jsc_rev
    Jsc_rev = [float(val.replace('hysteresis$', '')) for val in Jsc_rev]
    Jsc_fw = [float(val) for val in data[-1][14:18]]   #Jsc of forward sweeps

    Voc_rev = data[-1][18:22]               #Voc of reverse sweeps
    Voc_fw = data[-1][22:26]                #Voc of forward sweeps
    # Voc is in mV, convert to V
    Voc_rev = [float(val)/1000 for val in Voc_rev]
    Voc_fw = [float(val)/1000 for val in Voc_fw]

    FF_rev = [float(val) for val in data[-1][26:30]]                #FF of reverse sweeps
    FF_fw = [float(val) for val in data[-1][30:34]]                 #FF of forward sweeps

    MPP_rev = [float(val) for val in data[-1][34:38]]               #MPP of reverse sweeps
    MPP_fw = [float(val) for val in data[-1][38:42]]                #MPP of forward sweeps

    #calculate the amount of measurements points
    sweep_point_count = int((abs(v_end - v_start) / v_delta) + 1)
    sweep_point_count *= 2 #because hysteresis

    #get the current density data for all 4 pixels
    area_corrected_I = []
    for i in range(4):
        start = 42 + sweep_point_count * i
        end = start + sweep_point_count
        area_corrected_I_range = [float(val) for val in data[-1][start:end]]
        area_corrected_I.append(area_corrected_I_range)

    #get the voltage data for all 4 pixels
    #voltage range from v_start -> v_end -> v_start
    voltage = []
    for i in range(4):
        offset = 42 + sweep_point_count * 4
        start = offset + sweep_point_count * i
        end = start + sweep_point_count
        voltage_range = [float(val) for val in data[-1][start:end]]
        voltage.append(voltage_range)
    
    jv_dict = {}
    jv_dict['datetime'] = convert_datetime(date, '%Y%m%d') if date.isdigit() else date
    jv_dict['active_area'] = p1_cell_area  # Use first pixel as default
    jv_dict['intensity'] = 100.0  # Default 100 mW/cm² for efficiency calculation. 
    # Use reverse sweep data as primary values (similar to IRIS format)
    jv_dict['J_sc'] = [abs(x) for x in Jsc_rev]
    jv_dict['V_oc'] = Voc_rev
    jv_dict['Fill_factor'] = FF_rev
    
    # Calculate efficiency for each pixel
    jv_dict['Efficiency'] = [
        (voc * jsc * ff / jv_dict['intensity']) 
        for voc, jsc, ff in zip(Voc_rev, [abs(x) for x in Jsc_rev], FF_rev)
    ]
    
    jv_dict['P_MPP'] = [abs(x) for x in MPP_rev]
    jv_dict['J_MPP'] = [abs(x) for x in Jsc_rev]  # Approximation
    jv_dict['U_MPP'] = Voc_rev  # Approximation
    
    jv_dict['jv_curve'] = []
    # Create JV curves for each pixel - both forward and reverse sweeps
    # Split the hysteresis data: first half is reverse (v_start -> v_end), second half is forward (v_end -> v_start) Double check with definition of forward and reverse if it is p-i-n or n-i-p.
    sweep_half = sweep_point_count // 2
    
    for i in range(4):
        # Reverse sweep (first half of data)
        jv_dict['jv_curve'].append({
            'name': f'Pixel_{i+1}_reverse',
            'dark': False,
            'voltage': np.array(voltage[i][:sweep_half]),
            'current_density': np.array(area_corrected_I[i][:sweep_half]),
        })
        
        # Forward sweep (second half of data)
        jv_dict['jv_curve'].append({
            'name': f'Pixel_{i+1}_forward',
            'dark': False,
            'voltage': np.array(voltage[i][sweep_half:]),
            'current_density': np.array(area_corrected_I[i][sweep_half:]),
        })
    return jv_dict

def get_jv_data_location_2(filedata):
    pass

def get_jv_data(filedata):
    # Check if it is Location 1 IV format by looking for tab-separated numeric data structure
    lines = filedata.strip().split('\n')
    if lines and '\t' in filedata and any(len(line.split('\t')) > 40 for line in lines):
        return get_jv_data_location_1(filedata), 'Location 1 IV Format'
    else:
        return None, 'Unknown format'