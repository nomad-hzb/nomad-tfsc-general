import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg
from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'gravure_printing_test.xlsx',
    ]
)
def parsed_archive(request, monkeypatch):
    """
    Sets up data for testing and cleans up after the test.
    """
    yield get_archive(request.param, monkeypatch)


def test_normalize_all(parsed_archive, monkeypatch):
    normalize_all(parsed_archive)
    delete_json()


# Constants for test assertions
N_PROCESSED_ARCHIVES = 4
SOLVENT_CLEAN = 'Hellmanex'
MATERIAL_NAME = 'Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3'
LAYER_TYPE = 'Absorber'
LAYER_THICKNESS = 25 * ureg('nm')
MORPHOLOGY = 'Uniform'
CONCENTRATION = 1.42 * ureg('mol/ml')
NOTES = 'Batch supplier-ID-Opened at-remaining shelf life'
TOOL_NAME = 'SAU Box'
VISCOCITY = 0.0005 * ureg('Pa*s')
CONTACT_ANGLE = 30 * ureg('°')
ROOM_TEMP = ureg.Quantity(23, ureg('°C'))
ROOM_HUM = 45
O2_LEVEL = 10
SOLVENT = 'DMF'
SOLVENT_VOL = 0.01 * ureg('ml')
SOLUTE = 'PbI2'
SOLUTE_MOL = 0.00142 * ureg('mmol/ml')
SOLUTION_VOLUME = 0.1 * ureg('ml')
ROT_SPEED = 3000 * ureg('rpm')
ROT_TIME = 31 * ureg('s')
ROT_ACC = 1001 * ureg('rpm/s')


def test_tfsc_batch_parser(monkeypatch):
    file = 'gravure_printing_test.xlsx'
    file_name = os.path.join('tests', 'data', file)
    file_archive = parse(file_name)[0]
    assert len(file_archive.data.processed_archive) == N_PROCESSED_ARCHIVES

    measurement_archives = []
    for fname in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in fname:
            continue
        measurement = os.path.join('tests', 'data', fname)
        measurement_archives.append(parse(measurement)[0])
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    PROCESS_CHECKS = {
        # Exact name matches for batch, sample, substrate (lowercased)
        'sau_geso_1_1': check_batch,
        'sau_geso_1_1_c-1': check_sample,
        'substrate 1 cm x 1 cm soda lime glass ito': check_substrate,
        # Step-specific process checks
        ('gravure printing', 1.0): check_gravure_printing,
    }

    for m in measurement_archives:
        name = getattr(m.data, 'name', None)
        step = getattr(m.data, 'positon_in_experimental_plan', None)
        found = False
        name_lc = name.lower() if name else ''
        # Try tuple keys first (for step-specific checks)
        for k, func in PROCESS_CHECKS.items():
            if isinstance(k, tuple) and len(k) == 2:
                key_name, key_step = k
                if name_lc.startswith(key_name) and step == key_step:
                    if isinstance(func, list):
                        for f in func:
                            f(m)
                    else:
                        func(m)
                    found = True
                    break
        if not found:
            # Try exact string key match (for batch, sample, substrate)
            for k, func in PROCESS_CHECKS.items():
                if isinstance(k, str) and k == name_lc:
                    func(m)
                    found = True
                    break
        if not found:
            # Try string keys as prefix (for generic checks)
            for k, func in PROCESS_CHECKS.items():
                if isinstance(k, str) and name_lc.startswith(k):
                    func(m)
                    found = True
                    break
        if not found:
            print(f'No check function for process: {name} at step {step}')
    delete_json()


# Helper functions for each process type


def check_sample(m):
    assert m.data.name in ['SAU_GeSo_1_1_C-1', 'SAU_GeSo_1_1_C-2']
    assert m.data.lab_id in ['SAU_GeSo_1_1_C-1', 'SAU_GeSo_1_1_C-2']
    assert m.data.datetime.isoformat() == '2025-08-05T00:00:00+00:00'
    assert m.data.description == '1000 rpm'
    assert m.data.number_of_junctions == 1


def check_batch(m):
    assert m.data.name == 'SAU_GeSo_1_1'
    assert m.data.lab_id == 'SAU_GeSo_1_1'
    assert len(m.data.entities) == 1
    assert m.data.entities[0].lab_id == 'SAU_GeSo_1_1_C-1'


def check_substrate(m):
    assert m.data.datetime.isoformat() == '2025-08-05T00:00:00+00:00'
    assert m.data.name == 'Substrate 1 cm x 1 cm Soda Lime Glass ITO'
    assert m.data.solar_cell_area == 0.16 * ureg('cm**2')
    assert m.data.number_of_pixels == 6.0
    assert m.data.pixel_area == 0.16 * ureg('cm**2')
    assert m.data.substrate == 'Soda Lime Glass'
    assert m.data.conducting_material == ['ITO']
    assert m.data.substrate_properties[0]['layer_type'] == 'Substrate Conductive Layer'
    assert m.data.substrate_properties[0]['layer_material_name'] == 'ITO'
    assert m.data.substrate_properties[0]['layer_thickness'] == 150.0 * ureg('nm')
    assert m.data.substrate_properties[0]['layer_transmission'] == 90.0
    assert m.data.substrate_properties[0]['layer_sheet_resistance'] == 10.0 * ureg('ohm')


def check_gravure_printing(m):
    assert m.data.name.startswith('gravure printing')
    assert m.data.layer[0]['layer_type'] == LAYER_TYPE
    assert m.data.layer[0]['layer_material_name'] == MATERIAL_NAME
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == MORPHOLOGY
    assert m.data.solution[0]['solution_details']['solute'][0]['chemical_2']['name'] == SOLUTE
    assert m.data.solution[0]['solution_details']['solute'][0]['concentration_mol'] == SOLUTE_MOL
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_2']['name'] == SOLVENT
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_volume'] == SOLVENT_VOL
    assert m.data.solution[0]['solution_details']['solvent'][0]['amount_relative'] == 1.5
    assert m.data.solution[0]['solution_details']['additive'][0]['chemical_2']['name'] == 'starch'
    assert m.data.solution[0]['solution_details']['additive'][0]['concentration_mass'] == 1.5 * ureg('mg/ml')
    assert m.data.solution[0]['solution_viscosity'] == 0.5 * ureg('mPa*s')
    assert m.data.solution[0]['solution_contact_angle'] == CONTACT_ANGLE
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['oxygen_level_ppm'] == O2_LEVEL
    assert m.data.description == NOTES
    assert m.data.location == TOOL_NAME
    assert m.data.properties['gp_coating_speed'] == 1 * ureg('m/minute')
    assert m.data.properties['screen_ruling'] == 150
    assert m.data.properties['gp_method'] == 'R2R'
    assert m.data.properties['gp_direction'] == 'Forward'
    assert m.data.properties['cell_type'] == 'Diamond'
    assert m.data.annealing['time'] == 30 * ureg('minute')
    assert m.data.annealing['temperature'] == ureg.Quantity(120, ureg('°C'))
    assert m.data.annealing['atmosphere'] == 'N2'
    assert m.data.quenching.m_def.name.endswith('AirKnifeGasQuenching')
    assert m.data.quenching['air_knife_angle'] == 45 * ureg('°')
    assert m.data.quenching['air_knife_distance_to_thin_film'] == 5000.0 * ureg('um')
    assert m.data.quenching['bead_volume'] == 2 * ureg('mm/s')
    assert m.data.quenching['drying_speed'] == 30 * ureg('cm/minute')
    assert m.data.quenching['drying_gas_temperature'] == ureg.Quantity(60, ureg('°C'))
    assert m.data.quenching['heat_transfer_coefficient'] == 3 * ureg('W/(K*m**2)')
