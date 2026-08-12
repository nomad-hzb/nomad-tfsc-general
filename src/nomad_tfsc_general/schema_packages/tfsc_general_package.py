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


import numpy as np
from baseclasses import (
    BaseMeasurement,
    BaseProcess,
    Batch,
    LayerDeposition,
)
from baseclasses.helper.add_solar_cell import add_band_gap
from baseclasses.helper.utilities import (
    get_encoding,
    set_sample_reference,
)
from baseclasses.material_processes_misc import (
    Cleaning,
    CoronaCleaning,
    Encapsulation,
    Lamination,
    LaserScribing,
    PlasmaCleaning,
    SolutionCleaning,
    UVCleaning,
)
from baseclasses.solar_energy import (
    EQEMeasurement,
    JVMeasurement,
    MPPTracking,
    MPPTrackingProperties,
    SolarCellEQECustom,
    SolcarCellSample,
    Substrate,
)
from baseclasses.vapour_based_deposition import (
    ALDPropertiesIris,
    AtomicLayerDeposition,
    Evaporations,
    Sputtering,
)
from baseclasses.voila import VoilaNotebook
from baseclasses.wet_chemical_deposition import (
    BladeCoating,
    GravurePrinting,
    LP50InkjetPrinting,
    ScreenPrinting,
    SlotDieCoating,
    SpinCoating,
    WetChemicalDeposition,
)
from nomad.datamodel.data import EntryData
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection
from nomad.metainfo.elasticsearch_extension import Elasticsearch

m_package = SchemaPackage()


# %% ####################### Entities


class TFSC_General_VoilaNotebook(VoilaNotebook, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id']))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class TFSC_General_Substrate(Substrate, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'components', 'elemental_composition'],
            properties=dict(
                order=[
                    'datetime',
                    'name',
                    'substrate',
                    'conducting_material',
                    'substrate_dimension',
                    'solar_cell_area',
                    'pixel_area',
                    'active_area',
                    'dead_area',
                    'aperture_area',
                    'geometrical_fill_factor',
                    'number_of_pixels',
                    'layer_thickness',
                    'layer_sheet_resistance',
                    'layer_transmission',
                ]
            ),
        )
    )


# Maps the dict key a product_info-bearing section is nested under to a short,
# human-readable context label, used to disambiguate e.g. a solvent vs. an
# additive from the same supplier. Sections not under any of these keys (i.e.
# any future/unrecognized product_info location) simply get no suffix.
_SUPPLIER_CONTEXT_LABELS = {
    'layer': 'layer',
    'solvent': 'solvent',
    'solute': 'solute',
    'additive': 'additive',
    'barrier_lamination': 'barrier lamination',
    'adhesive_application': 'adhesive layer',
}


def _find_supplier_materials(data, suppliers, supplier_materials, context=None, material=None):
    """Recursively walk a raw (dict/list) archive data structure collecting
    ProductInfo.supplier values, together with the material each one applies
    to. product_info subsections can live at varying depths depending on the
    process type (directly under a layer, under a solution's
    solvent/solute/additive chemicals, under encapsulation's barrier
    lamination or adhesive layer, ...), so rather than hard-coding every
    possible path this scans for any 'product_info' key, and separately uses
    `_SUPPLIER_CONTEXT_LABELS` to add a readable context suffix when the
    location is a recognized one.

    The material name usually sits one or two levels above product_info
    itself (e.g. a solvent's `name` is a sibling of `chemical_2`, which is
    where `chemical_2.product_info` actually lives), so the nearest material
    name found while descending is carried down and used as a fallback.
    """
    if isinstance(data, dict):
        material = (
            data.get('layer_material_name')
            or data.get('layer_material')
            or data.get('name')
            or data.get('barrier_foil')
            or material
        )
        product_info = data.get('product_info')
        if isinstance(product_info, dict):
            supplier = product_info.get('supplier')
            if supplier:
                suppliers.add(supplier)
                label = f'{supplier} — {material}' if material else supplier
                if context:
                    label = f'{label} ({context})'
                supplier_materials.add(label)
        for key, value in data.items():
            _find_supplier_materials(
                value,
                suppliers,
                supplier_materials,
                _SUPPLIER_CONTEXT_LABELS.get(key, context),
                material,
            )
    elif isinstance(data, list):
        for item in data:
            _find_supplier_materials(item, suppliers, supplier_materials, context, material)


def collect_supplier_info(archive, logger):
    """Find suppliers of materials used by the processes that produced this
    sample, along with which material each supplier applies to. Process
    entries (SpinCoating, Encapsulation, ...) are separate top-level entries
    that reference this sample (directly, or copied from their batch), so
    they are found via a reverse search on `entry_references.target_entry_id`,
    the same mechanism baseclasses' `collectSampleData` uses to pull in
    JV/EQE data.

    Returns a `(suppliers, supplier_materials)` tuple of sorted lists.
    """
    import inspect

    import baseclasses
    from nomad import files
    from nomad.app.v1.models import MetadataPagination
    from nomad.search import search

    query = {'entry_references.target_entry_id': archive.metadata.entry_id}
    pagination = MetadataPagination()
    pagination.page_size = 100
    search_result = search(
        owner='all',
        query=query,
        pagination=pagination,
        user_id=archive.metadata.main_author.user_id,
    )

    suppliers = set()
    supplier_materials = set()
    for res in search_result.data:
        try:
            with files.UploadFiles.get(upload_id=res['upload_id']).read_archive(
                entry_id=res['entry_id']
            ) as arch:
                entry_id = res['entry_id']
                entry_data = arch[entry_id]['data']
                module = entry_data['m_def'].split('.')[0]
                eval(f"exec('import {module}')")
                if baseclasses.BaseProcess in inspect.getmro(eval(entry_data['m_def'])):
                    _find_supplier_materials(entry_data, suppliers, supplier_materials)
        except Exception:
            if logger:
                logger.warning(
                    'Error collecting supplier info from referencing entry.',
                    exc_info=True,
                )

    return sorted(suppliers), sorted(supplier_materials)


class TFSC_General_Sample(SolcarCellSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition'],
            properties=dict(
                order=['datetime', 'name', 'substrate', 'architecture', 'batch_id', 'subbatch_id']
            ),
        ),
        label_quantity='sample_id',
    )

    batch_id = Quantity(
        type=str,
        description="""
        Batch identifier, derived from the sample ID (Nomad ID). Samples created via
        the PERSEUS/TFSC batch parser follow the naming convention
        `PERS_PROJECT_BATCH_SUBBATCH_SAMPLE`, so the batch id is the sample id with
        the last two underscore-separated segments (subbatch and sample) removed.
        """,
        a_eln=dict(component='StringEditQuantity'),
    )

    subbatch_id = Quantity(
        type=str,
        description="""
        Subbatch identifier, derived from the sample ID (Nomad ID). Samples created via
        the PERSEUS/TFSC batch parser follow the naming convention
        `PERS_PROJECT_BATCH_SUBBATCH_SAMPLE`, so the subbatch id is the sample id with
        the last underscore-separated segment (sample) removed.
        """,
        a_eln=dict(component='StringEditQuantity'),
    )

    suppliers = Quantity(
        type=str,
        shape=['*'],
        description="""
        Suppliers of materials (additives, solvents, layers, encapsulation, ...) used
        in the processes that produced this sample. Derived by scanning every process
        entry referencing this sample for `product_info.supplier`, since that
        information can live at varying depths depending on the process type.
        """,
        # NOMAD's automatic search-quantity resolution for custom schemas only
        # covers scalar (shape=[]) fields - repeating quantities need an
        # explicit annotation to be searchable at all, otherwise the search API
        # rejects the field with a "not a doc quantity" error.
        a_elasticsearch=Elasticsearch(),
    )

    supplier_materials = Quantity(
        type=str,
        shape=['*'],
        description="""
        Supplier/material pairs, e.g. "Sigma-Aldrich — MAPbI3 (layer)", derived
        alongside `suppliers`. NOMAD does not yet support nested/correlated search
        for custom-schema quantities, so this packs the supplier and the material it
        applies to into a single searchable string rather than two separately
        filterable fields.
        """,
        a_elasticsearch=Elasticsearch(),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        lab_id = self.lab_id or self.name
        parts = lab_id.split('_') if lab_id else []

        if not self.batch_id and len(parts) > 2:
            self.batch_id = '_'.join(parts[:-2])

        if not self.subbatch_id and len(parts) > 1:
            self.subbatch_id = '_'.join(parts[:-1])

        self.suppliers, self.supplier_materials = collect_supplier_info(archive, logger)


class TFSC_General_Batch(Batch, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'samples'],
            properties=dict(order=['name', 'export_batch_ids', 'csv_export_file']),
        )
    )


class TFSC_General_SubBatch(Batch, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'samples'],
            properties=dict(order=['name', 'export_batch_ids', 'csv_export_file']),
        )
    )


# %% ####################### Cleaning
class TFSC_General_Cleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        )
    )

    cleaning = SubSection(section_def=SolutionCleaning, repeats=True)

    cleaning_uv = SubSection(section_def=UVCleaning, repeats=True)

    cleaning_plasma = SubSection(section_def=PlasmaCleaning, repeats=True)

    cleaning_corona = SubSection(section_def=CoronaCleaning, repeats=True)


# %% ### Printing


class TFSC_General_Inkjet_Printing(LP50InkjetPrinting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'recipe_used',
                    'print_head_used',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'print_head_path',
                    'nozzle_voltage_profile',
                    'quenching',
                    'annealing',
                    'atmosphere',
                ]
            ),
        ),
    )


# %% ### Spin Coating
class TFSC_General_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
                'recipe',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                    'atmosphere',
                ]
            ),
        ),
    )


# %% ### Screen Printing


class TFSC_General_ScreenPrinting(ScreenPrinting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                    'atmosphere',
                ]
            ),
        ),
    )


# %% ### Slot Die Coating


class TFSC_General_SlotDieCoating(SlotDieCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                    'atmosphere',
                ]
            ),
        ),
    )


# %% ### Blade Coating
class TFSC_General_BladeCoating(BladeCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                    'atmosphere',
                ]
            ),
        ),
    )


# %% ### Gravure Printing
class TFSC_General_GravurePrinting(GravurePrinting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                    'atmosphere',
                ]
            ),
        ),
    )


# %% ### Sputterring
class TFSC_General_Sputtering(Sputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                    'atmosphere',
                ]
            ),
        )
    )


# %% ### AtomicLayerDepositio
class TFSC_General_AtomicLayerDeposition(AtomicLayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                    'atmosphere',
                ]
            ),
        )
    )

    properties = SubSection(section_def=ALDPropertiesIris)


# %% ### Evaporation
class TFSC_General_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                    'atmosphere',
                ]
            ),
        )
    )


# %% ## Laser Scribing
class TFSC_General_LaserScribing(LaserScribing, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(order=['name', 'location', 'present', 'datetime', 'batch', 'samples']),
        )
    )


# %% ## Lamination
class TFSC_General_Lamination(Lamination, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(order=['name', 'location', 'present', 'datetime', 'batch', 'samples']),
        )
    )


# %% ## Encapsulation
class TFSC_General_Encapsulation(Encapsulation, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'encapsulation_method',
                    'sides_encapsulated',
                    'adhesive_application',
                    'barrier_lamination',
                    'curing',
                    'layer',
                ]
            ),
        ),
    )


# %%####################################### Measurements


class TFSC_General_JVmeasurement(JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'active_area',
                    'corrected_active_area',
                    'intensity',
                    'integration_time',
                    'settling_time',
                    'averaging',
                    'compliance',
                    'samples',
                ]
            ),
        ),
        a_plot=[
            {
                'x': 'jv_curve/:/voltage',
                'y': 'jv_curve/:/current_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        from nomad_tfsc_general.schema_packages.file_parser.jv_archive import get_jv_archive
        from nomad_tfsc_general.schema_packages.file_parser.jv_parser import (
            get_jv_data,
        )

        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)

        if self.data_file:
            # todo detect file format
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
                jv_dict, location = get_jv_data(f.read(), self.data_file)
                self.location = location
                get_jv_archive(jv_dict, self.data_file, self, archive)

        super().normalize(archive, logger)


class TFSC_General_SimpleMPPTracking(MPPTracking, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'properties',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'x': 'time',
                'y': 'power_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        from nomad_tfsc_general.schema_packages.file_parser.mppt_parser import (
            read_mppt_file,
        )

        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)

        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
                data = read_mppt_file(f.read(), self.data_file)

            self.datetime = data['datetime']
            self.time = data['time_data']
            self.voltage = data['voltage_data']
            self.current_density = data['current_density_data']
            self.power_density = data['power_data']
            self.properties = MPPTrackingProperties(
                time=data['total_time'], perturbation_voltage=data['step_size']
            )
        super().normalize(archive, logger)


class TFSC_General_EQEmeasurement(EQEMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'data',
                'header_lines',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'x': 'eqe_data/:/photon_energy_array',
                'y': 'eqe_data/:/eqe_array',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        from nomad_hysprint.schema_packages.file_parser.eqe_parser import (
            read_file,
            read_file_multiple,
        )

        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id)

        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)
            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
                filedata = f.read()
                if filedata.startswith('[Header]'):
                    data_list = [read_file(filedata, 8)]
                else:
                    data_list = read_file_multiple(filedata)
            eqe_data = []
            for d in data_list:
                entry = SolarCellEQECustom(
                    photon_energy_array=d.get('photon_energy'),
                    raw_photon_energy_array=d.get('photon_energy_raw'),
                    eqe_array=d.get('intensity'),
                    raw_eqe_array=d.get('intensty_raw'),
                )
                entry.normalize(archive, logger)
                eqe_data.append(entry)
            self.eqe_data = eqe_data

        if eqe_data:
            band_gaps = np.array([d.bandgap_eqe.magnitude for d in eqe_data])

            add_band_gap(archive, band_gaps[np.isfinite(band_gaps)].mean())

        super().normalize(archive, logger)


# %%####################################### Generic Entries


class TFSC_General_Process(BaseProcess, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'present', 'data_file', 'batch', 'samples']),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class TFSC_General_WetChemicalDepoistion(WetChemicalDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class TFSC_General_Deposition(LayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class TFSC_General_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        )
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id)
        super().normalize(archive, logger)


m_package.__init_metainfo__()
