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

from io import StringIO

import numpy as np
import pandas as pd
from baseclasses.helper.utilities import convert_datetime


def get_jv_data_location_1(filedata):
    # Parse Location 1 IV format - tab-separated data with each row as measurement repetition
    lines = filedata.strip().split('\n')
    data = [line.strip().split('\t') for line in lines]

    # each row in the datafile represents a measurement repetition.
    # here i'm only parsing out the last repetition.

    date = data[-1][1]  # measurement date, the time is the last pixel measurement time
    time, month, day, year = date.split()
    month = {"maa": "mar", "mei": "may", "okt": "oct"}.get(month, month)
    fixed_date = time+" "+month+" "+day+" "+year

    v_start = float(data[-1][2])  # v start [V]
    v_end = float(data[-1][3])  # v end [V]
    v_delta = float(data[-1][4])  # v step [V]
    p1_cell_area = float(data[-1][6])  # cell area pixel 1 [cm2]

    Jsc_rev = data[-1][10:14]  # Jsc of reverse sweeps
    # Clean up the 'hysteresis$' string from Jsc_rev
    Jsc_rev = [float(val.replace('hysteresis$', '')) for val in Jsc_rev]

    Voc_rev = data[-1][18:22]  # Voc of reverse sweeps
    Voc_fw = data[-1][22:26]  # Voc of forward sweeps
    # Voc is in mV, convert to V
    Voc_rev = [float(val) / 1000 for val in Voc_rev]
    Voc_fw = [float(val) / 1000 for val in Voc_fw]

    FF_rev = [float(val) for val in data[-1][26:30]]  # FF of reverse sweeps

    MPP_rev = [float(val) for val in data[-1][34:38]]  # MPP of reverse sweeps

    # calculate the amount of measurements points
    sweep_point_count = int((abs(v_end - v_start) / v_delta) + 1)
    sweep_point_count *= 2  # because hysteresis

    # get the current density data for all 4 pixels
    area_corrected_I = []
    for i in range(4):
        start = 42 + sweep_point_count * i
        end = start + sweep_point_count
        area_corrected_I_range = [float(val) for val in data[-1][start:end]]
        area_corrected_I.append(area_corrected_I_range)

    # get the voltage data for all 4 pixels
    # voltage range from v_start -> v_end -> v_start
    voltage = []
    for i in range(4):
        offset = 42 + sweep_point_count * 4
        start = offset + sweep_point_count * i
        end = start + sweep_point_count
        voltage_range = [float(val) for val in data[-1][start:end]]
        voltage.append(voltage_range)

    jv_dict = {}
    jv_dict['datetime'] = convert_datetime(fixed_date, '%H:%M:%S %b %d %Y')
    jv_dict['active_area'] = p1_cell_area  # Use first pixel as default
    jv_dict['intensity'] = 100.0  # Default 100 mW/cm² for efficiency calculation.
    # Use reverse sweep data as primary values (similar to IRIS format)
    jv_dict['J_sc'] = [abs(x) for x in Jsc_rev]
    jv_dict['V_oc'] = Voc_rev
    jv_dict['Fill_factor'] = [ff * 0.01 for ff in FF_rev]

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
    # Split the hysteresis data: first half is reverse (v_start -> v_end), second half is forward
    # (v_end -> v_start). Double check with definition of forward and reverse if it is p-i-n or n-i-p.
    sweep_half = sweep_point_count // 2

    for i in range(4):
        # Reverse sweep (first half of data)
        jv_dict['jv_curve'].append(
            {
                'name': f'Pixel_{i + 1}_reverse',
                'dark': False,
                'voltage': np.array(voltage[i][:sweep_half]),
                'current_density': np.array(area_corrected_I[i][:sweep_half]),
            }
        )

        # Forward sweep (second half of data)
        jv_dict['jv_curve'].append(
            {
                'name': f'Pixel_{i + 1}_forward',
                'dark': False,
                'voltage': np.array(voltage[i][sweep_half:]),
                'current_density': np.array(area_corrected_I[i][sweep_half:]),
            }
        )
    return jv_dict


def get_jv_data_location_2(filedata):
    lines = filedata.splitlines()
    curve_header_idx = next(
        (idx for idx, line in enumerate(lines) if line.startswith('U [V]/Exposure [h]')),
        None,
    )
    if curve_header_idx is None:
        return None

    header_text = '\n'.join(lines[:curve_header_idx]).strip()
    curves_text = '\n'.join(lines[curve_header_idx:]).strip()

    df_header = pd.read_csv(
        StringIO(header_text),
        header=0,
        sep='\t',
        encoding='unicode_escape',
        engine='python',
    )

    df_header = df_header[
        df_header['File'].notna() & (df_header['File'].astype(str).str.strip() != '')
    ].reset_index(drop=True)
    if df_header.empty:
        return None

    # measurement date, the time is the first pixel measurement time
    date = df_header['File'][0].split('_')[-3]
    time = df_header['File'][0].split('_')[-2]

    df_curves = pd.read_csv(
        StringIO(curves_text),
        header=0,
        sep='\t',
        encoding='unicode_escape',
        engine='python',
    )

    df_curves = df_curves.dropna(how='all', axis=1)

    jv_dict = {}

    def numeric_series(column_name):
        return pd.to_numeric(df_header[column_name], errors='coerce').fillna(0.0)

    jv_dict['datetime'] = convert_datetime(f'{date} {time}', '%Y%m%d %H%M')
    area_mm2 = numeric_series('Solar Cell Area [mm2]')
    intensity = numeric_series('Solar sim. intensity [mW/cm2]')
    impp = numeric_series('Impp [A]').abs()

    jv_dict['active_area'] = area_mm2.iloc[0] / 100 if len(area_mm2) > 0 else 0
    jv_dict['intensity'] = intensity.iloc[0] if len(intensity) > 0 else 0
    jv_dict['J_sc'] = list(numeric_series('JSC [mA/cm2]').abs())
    jv_dict['V_oc'] = list(numeric_series('Voc [V]').abs())
    jv_dict['Fill_factor'] = list(numeric_series('FF').abs())
    jv_dict['Efficiency'] = list(numeric_series('PCE [%]').abs())
    jv_dict['P_MPP'] = list(numeric_series('Pmpp [mW]').abs())
    jv_dict['U_MPP'] = list(numeric_series('Vmpp [V]'))

    area_cm2 = (area_mm2 / 100).replace(0, np.nan)
    jv_dict['J_MPP'] = list((impp * 1000 / area_cm2).fillna(0.0))  # in mA/cm²

    jv_dict['jv_curve'] = []

    def extract_name_prefix(name):
        parts = name.split('_')
        # Keep everything except the last 5 parts (indices -1 to -5)
        return '_'.join(parts[:-5]) if len(parts) > 5 else name

    n_curves = min(len(df_header), max(df_curves.shape[1] - 1, 0))

    for i in range(n_curves):
        voltage = pd.to_numeric(df_curves.iloc[:, 0], errors='coerce')
        current_density = pd.to_numeric(df_curves.iloc[:, i + 1], errors='coerce')
        valid_mask = ~(voltage.isna() | current_density.isna())

        jv_dict['jv_curve'].append(
            {
                'name': (
                    f'{extract_name_prefix(df_header["File"][i])}_loc2_{df_header["File"][i].split("_")[-1]}'
                ),
                'dark': False,
                'voltage': np.array(voltage[valid_mask]),
                'current_density': np.array(current_density[valid_mask]),
            }
        )
    return jv_dict


def get_jv_data_location_3(filedata):
    df = pd.read_csv(
        StringIO(filedata),
        header=[0, 1],
        sep=',',
        encoding='unicode_escape',
        engine='python',
    )
    columns = pd.DataFrame(df.columns.tolist())
    columns.loc[columns[0].str.startswith('Unnamed:'), 0] = np.nan
    columns[0] = columns[0].ffill()
    df.columns = columns

    jv_dict = {'location': 'Hereon'}

    jv_dict['jv_curve'] = []

    for col in df.columns[::2]:
        jv_dict['jv_curve'].append(
            {
                'name': f'{col[0]}',
                'dark': False,
                'voltage': np.array(df[col]),
                'current_density': np.array(df[(col[0], 'J (A/cm^2)')]),
            }
        )
    return jv_dict


def get_jv_data(filedata):
    # Check if it is Location 1 IV format by looking for tab-separated numeric data structure
    lines = filedata.strip().split('\n')
    if lines and '\t' in filedata and any(len(line.split('\t')) > 40 for line in lines):
        return get_jv_data_location_1(filedata), 'Location 1 IV Format'
    elif 'U [V]/Exposure [h]' in filedata:
        return get_jv_data_location_2(filedata), 'Location 2 txt Format'
    elif 'Pixel 1' in filedata and 'J (A/cm^2)' in filedata and 'V (V)' in filedata:
        return get_jv_data_location_3(filedata), 'Hereon csv Format'
    else:
        return None, 'Unknown format'
