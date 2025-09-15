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

import datetime
import os
import sys

from baseclasses.helper.utilities import (
    create_archive,
    get_entry_id_from_file_name,
    get_reference,
    set_sample_reference,
)
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    Entity,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_tfsc_general.schema_packages.tfsc_general_package import (
    TFSC_General_EQEmeasurement,
    TFSC_General_JVmeasurement,
    TFSC_General_Measurement,
    TFSC_General_SimpleMPPTracking,
)


class RawFileTFSCGeneral(EntryData):
    processed_archive = Quantity(
        type=Entity,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


def update_general_process_entries(entry, entry_id, archive, logger):
    from nomad import files
    from nomad.search import search

    query = {
        'entry_id': entry_id,
    }
    search_result = search(owner='all', query=query, user_id=archive.metadata.main_author.user_id)
    entry_type = search_result.data[0].get('entry_type') if len(search_result.data) == 1 else None
    if entry_type != 'TFSC_General_Measurement':
        return None
    new_entry_dict = entry.m_to_dict()
    res = search_result.data[0]
    try:
        # Open Archives
        with files.UploadFiles.get(upload_id=res['upload_id']).read_archive(entry_id=res['entry_id']) as ar:
            entry_id = res['entry_id']
            entry_data = ar[entry_id]['data']
            entry_data.pop('m_def', None)
            new_entry_dict.update(entry_data)
    except Exception:
        pass
        # logger.error('Error in processing data: ', e)
    new_entry = getattr(sys.modules[__name__], type(entry).__name__).m_from_dict(new_entry_dict)
    return new_entry


class TFSCGeneralParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        mainfile_split = os.path.basename(mainfile).split('.')

        entry = TFSC_General_Measurement()

        # iv for loc 1,  txt for loc 2.
        if 'iv' in os.path.basename(mainfile).lower() or 'txt' in os.path.basename(mainfile).lower():
            entry = TFSC_General_JVmeasurement()
        if 'eqe' in os.path.basename(mainfile).lower():
            entry = TFSC_General_EQEmeasurement()
        if 'mpp' in os.path.basename(mainfile).lower():
            entry = TFSC_General_SimpleMPPTracking()
        archive.metadata.entry_name = os.path.basename(mainfile)

        search_id = mainfile_split[0]
        set_sample_reference(archive, entry, search_id, archive.metadata.upload_id)

        entry.name = f'{search_id} {".".join(mainfile_split[1:-1])}'
        entry.data_file = os.path.basename(mainfile)
        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        eid = get_entry_id_from_file_name(file_name, archive)
        archive.data = RawFileTFSCGeneral(processed_archive=get_reference(archive.metadata.upload_id, eid))
        new_entry_created = create_archive(entry, archive, file_name)
        if not new_entry_created:
            new_entry = update_general_process_entries(entry, eid, archive, logger)
            if new_entry is not None:
                create_archive(new_entry, archive, file_name, overwrite=True)
