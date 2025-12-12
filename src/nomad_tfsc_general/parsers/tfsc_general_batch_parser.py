#!/usr/bin/env python3
"""
Created on Fri Sep 27 09:08:03 2024

@author: a2853

Adapted for PERSEUS needs on Tue May 19 16:00:00 2024

@author: a5263
"""

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

import pandas as pd
from baseclasses.helper.solar_cell_batch_mapping import (
    get_reference,
    map_atomic_layer_deposition,
    map_basic_sample,
    map_batch,
    map_blade_coating,
    map_cleaning,
    map_evaporation,
    map_generic,
    map_gravure_printing,
    map_inkjet_printing,
    map_laser_scribing,
    map_screen_printing,
    map_sdc,
    map_spin_coating,
    map_sputtering,
    map_substrate,
)
from baseclasses.helper.utilities import create_archive
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.basesections import (
    Entity,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_tfsc_general.parsers.product_mapper import get_product_values
from nomad_tfsc_general.schema_packages.tfsc_general_package import (
    TFSC_General_AtomicLayerDeposition,
    TFSC_General_Batch,
    TFSC_General_BladeCoating,
    TFSC_General_Cleaning,
    TFSC_General_Evaporation,
    TFSC_General_GravurePrinting,
    TFSC_General_Inkjet_Printing,
    TFSC_General_LaserScribing,
    TFSC_General_Process,
    TFSC_General_Sample,
    TFSC_General_ScreenPrinting,
    TFSC_General_SlotDieCoating,
    TFSC_General_SpinCoating,
    TFSC_General_Sputtering,
    TFSC_General_Substrate,
)


def enrich_row_with_product_data(row, df_sheet_two):
    """
    Enrich a data row with product information based on chemical IDs.

    Args:
        row: pandas Series containing experimental data
        df_sheet_two: pandas DataFrame containing product information or None

    Returns:
        pandas Series with enriched product data (or original if no product sheet)
    """
    # Guard clause: If no product data sheet is available, return the original row
    if df_sheet_two is None:
        return row.copy()
    
    row_copy = row.copy()

    # Filter columns that contain 'Chemical ID' directly
    chemical_id_cols = [scol for scol in row.index if 'chemical ID' in scol]

    for scol in chemical_id_cols:
        chemical_id_value = row[scol]
        
        # Guard clause: Skip if Chemical ID has no value
        if pd.isna(chemical_id_value):
            continue
            
        product_data = get_product_values(df_sheet_two, chemical_id_value)
        
        # Guard clause: Skip if no product data found
        if product_data is None:
            continue
            
        # Extract prefix (e.g., "Solvent 1" from "Solvent 1 Chemical ID")
        prefix = scol.replace(' chemical ID', '').strip()

        # Add product data with prefix to avoid conflicts
        for key, value in product_data.items():
            # Guard clause: Skip NaN values
            if pd.isna(value):
                continue
                
            # Guard clause: Skip the Chemical ID column itself to avoid duplication
            if key == 'chemical ID':
                continue
                
            # Prefix the key with the chemical name
            prefixed_key = f'{prefix} {key}'
            row_copy[prefixed_key] = value

    return row_copy


class RawTFSCGeneralExperiment(EntryData):
    processed_archive = Quantity(type=Entity, shape=['*'])


class TFSCGeneralExperimentParser(MatchingParser):
    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ):
        is_mainfile_super = super().is_mainfile(filename, mime, buffer, decoded_buffer, compression)
        if not is_mainfile_super:
            return False
        try:
            df = pd.read_excel(filename, header=[0, 1])
            df['Experiment Info']['Nomad ID'].dropna().to_list()
        except Exception:
            return False
        return True

    def parse(self, mainfile: str, archive: EntryArchive, logger):  # noqa: PLR0912
        upload_id = archive.metadata.upload_id
        # xls = pd.ExcelFile(mainfile)
        df = pd.read_excel(mainfile, header=[0, 1])
        
        # Try to read the second sheet for product data, handle case where it doesn't exist
        try:
            df_sheet_two = pd.read_excel(mainfile, sheet_name=1, header=0)
        except (IndexError, ValueError):
            # No second sheet available, set to None
            df_sheet_two = None
            logger.info("No second sheet found - product data enrichment will be skipped")

        sample_ids = df['Experiment Info']['Nomad ID'].dropna().to_list()
        batch_id = '_'.join(sample_ids[0].split('_')[:-1])
        archives = [map_batch(sample_ids, batch_id, upload_id, TFSC_General_Batch)]
        substrates = []
        substrates_col = [
            'Date',
            'Sample dimension',
            'Sample area [cm^2]',
            'Pixel area [cm^2]',
            'Number of pixels',
            'Notes',
            'Substrate material',
            'Substrate conductive layer',
            'Transmission [%]',
            'Sheet Resistance [Ohms/square]',
            'TCO thickness [nm]',
        ]
        substrates_col = [s for s in substrates_col if s in df['Experiment Info'].columns]
        for i, sub in df['Experiment Info'][substrates_col].drop_duplicates().iterrows():
            if pd.isna(sub).all():
                continue
            substrates.append((f'{i}_substrate', sub, map_substrate(sub, TFSC_General_Substrate)))

        def find_substrate(d):
            for s in substrates:
                if d.equals(s[1]):
                    return s[0]

        def is_row_empty(row):
            """Check if all values in the row are NaN or empty"""
            return pd.isna(row).all()

        for i, row in df['Experiment Info'].iterrows():
            if is_row_empty(row):
                continue
            substrate_name = find_substrate(row[substrates_col]) + '.archive.json'
            archives.append(map_basic_sample(row, substrate_name, upload_id, TFSC_General_Sample))

        for i, col in enumerate(df.columns.get_level_values(0).unique()):
            if col == 'Experiment Info':
                continue

            df_dropped = df[col].drop_duplicates()
            for j, row in df_dropped.iterrows():
                lab_ids = [
                    x['Experiment Info']['Nomad ID']
                    for _, x in df[['Experiment Info', col]].iterrows()
                    if x[col].astype('object').equals(row.astype('object'))
                ]
                if is_row_empty(row):
                    continue

                if 'Cleaning' in col:
                    archives.append(map_cleaning(i, j, lab_ids, row, upload_id, TFSC_General_Cleaning))

                if 'Laser Scribing' in col:
                    archives.append(
                        map_laser_scribing(i, j, lab_ids, row, upload_id, TFSC_General_LaserScribing)
                    )

                if 'Generic Process' in col:  # move up
                    archives.append(map_generic(i, j, lab_ids, row, upload_id, TFSC_General_Process))

                if pd.isna(row.get('Material name')):
                    continue

                if 'Evaporation' in col:
                    # Use the generalized function to enrich row with product data
                    enriched_row = enrich_row_with_product_data(row, df_sheet_two)

                    archives.append(
                        map_evaporation(i, j, lab_ids, enriched_row, upload_id, TFSC_General_Evaporation)
                    )

                if 'Spin Coating' in col:
                    # Use the generalized function to enrich row with product data
                    enriched_row = enrich_row_with_product_data(row, df_sheet_two)

                    archives.append(
                        map_spin_coating(i, j, lab_ids, enriched_row, upload_id, TFSC_General_SpinCoating)
                    )

                if 'Slot Die Coating' in col:
                    # Use the generalized function to enrich row with product data
                    enriched_row = enrich_row_with_product_data(row, df_sheet_two)

                    archives.append(
                        map_sdc(i, j, lab_ids, enriched_row, upload_id, TFSC_General_SlotDieCoating)
                    )

                if 'Sputtering' in col:
                    # Use the generalized function to enrich row with product data
                    enriched_row = enrich_row_with_product_data(row, df_sheet_two)
                    
                    archives.append(map_sputtering(i, j, lab_ids, row, upload_id, TFSC_General_Sputtering))

                if 'Inkjet Printing' in col:
                    # Use the generalized function to enrich row with product data
                    enriched_row = enrich_row_with_product_data(row, df_sheet_two)

                    archives.append(
                        map_inkjet_printing(
                            i, j, lab_ids, enriched_row, upload_id, TFSC_General_Inkjet_Printing
                        )
                    )

                if 'ALD' in col:
                    # Use the generalized function to enrich row with product data
                    enriched_row = enrich_row_with_product_data(row, df_sheet_two)
                    
                    archives.append(
                        map_atomic_layer_deposition(
                            i,
                            j,
                            lab_ids,
                            row,
                            upload_id,
                            TFSC_General_AtomicLayerDeposition,
                        )
                    )

                if 'Blade Coating' in col:
                    # Use the generalized function to enrich row with product data
                    enriched_row = enrich_row_with_product_data(row, df_sheet_two)

                    archives.append(
                        map_blade_coating(
                            i,
                            j,
                            lab_ids,
                            enriched_row,
                            upload_id,
                            TFSC_General_BladeCoating,
                        )
                    )

                if 'Gravure Printing' in col:
                    # Use the generalized function to enrich row with product data
                    enriched_row = enrich_row_with_product_data(row, df_sheet_two)

                    archives.append(
                        map_gravure_printing(
                            i,
                            j,
                            lab_ids,
                            enriched_row,
                            upload_id,
                            TFSC_General_GravurePrinting,
                        )
                    )

                if 'Screen Printing' in col:
                    # Use the generalized function to enrich row with product data
                    enriched_row = enrich_row_with_product_data(row, df_sheet_two)

                    archives.append(
                        map_screen_printing(
                            i,
                            j,
                            lab_ids,
                            enriched_row,
                            upload_id,
                            TFSC_General_ScreenPrinting,
                        )
                    )

        refs = []
        for subs in substrates:
            file_name = f'{subs[0]}.archive.json'
            create_archive(subs[2], archive, file_name)
            refs.append(get_reference(upload_id, file_name))

        for a in archives:
            file_name = f'{a[0]}.archive.json'
            create_archive(a[1], archive, file_name)
            refs.append(get_reference(upload_id, file_name))

        archive.data = RawTFSCGeneralExperiment(processed_archive=refs)
