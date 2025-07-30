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


def get_jv_data_tno(filedata):
    df = pd.read_csv(
        StringIO(filedata),
        header=None,
        sep='\t',
        index_col=0,
        engine='python',
        encoding='unicode_escape',
        usecols=range(8),
        skipfooter=1,
    )

    df_curves = pd.read_csv(
        StringIO(filedata),
        header=None,
        sep='\t',
        index_col=None,
        engine='python',
        encoding='unicode_escape',
        usecols=range(8),
        skipfooter=6,
    )

    df_curves = df_curves.dropna(how='all', axis=1)

    df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

    jv_dict = {}
    jv_dict['datetime'] = convert_datetime(df.iloc[-2].name, '%H:%M:%S %b %d %Y')

    jv_dict['jv_curve'] = []
    for column in range(0, len(df_curves.columns), 2):
        jv_dict['jv_curve'].append(
            {
                'name': '_'.join(['pixel', str((column + 2) // 2)]),
                'voltage': df_curves[column].values,
                'current_density': df_curves[column + 1].values,
            }
        )

    return jv_dict


def get_jv_data(filedata):
    return get_jv_data_tno(filedata), 'TNO'
