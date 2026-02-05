import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg
from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'screen_printing_test.xlsx',
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
N_PROCESSED_ARCHIVES = 5
MATERIAL_NAME = 'Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3'
LAYER_TYPE = 'Absorber Layer'
LAYER_THICKNESS = 15 * ureg('nm')
MORPHOLOGY = 'Uniform'
NOTES = 'Batch supplier-ID-Opened at-remaining shelf life'
TOOL_NAME = 'Loc Box'
VISCOSITY = 0.5 * ureg('mPa*s')
CONTACT_ANGLE = 30 * ureg('°')
ROOM_TEMP = ureg.Quantity(23, ureg('°C'))
ROOM_HUM = 45
O2_LEVEL = 10
SOLVENT = 'DMF'
SOLVENT_VOL = 10 * ureg('uL')
SOLUTE = 'PbI2'
SOLUTE_MOL = 1.42 * ureg('mM')
SOLUTION_VOLUME = 100 * ureg('uL')

# Screen printing specific constants
MESH_MATERIAL = 'Polyester'
MESH_COUNT = 120
MESH_THICKNESS = 50 * ureg('um')
THREAD_DIAMETER = 34 * ureg('um')
MESH_OPENING = 49 * ureg('um')
MESH_TENSION = 20 * ureg('N/cm')
MESH_ANGLE = 22.5 * ureg('°')
EMULSION_MATERIAL = 'Photopolymer'
EMULSION_THICKNESS = 15 * ureg('um')
SQUEEGEE_MATERIAL = 'Polyurethane'
SQUEEGEE_SHAPE = 'Rectangle'
SQUEEGEE_ANGLE = 75 * ureg('°')
PRINTING_SPEED = 50 * ureg('mm/s')
PRINTING_DIRECTION = 'Forward'
PRINTING_PRESSURE = 2.5 * ureg('bar')
SNAP_OFF_DISTANCE = 1.5 * ureg('mm')
PRINTING_METHOD = 'R2R'

# IR Annealing constants
ANNEALING_TIME = 30 * ureg('minute')
ANNEALING_TEMP = ureg.Quantity(120, ureg('°C'))
ANNEALING_ATMOSPHERE = 'N2'
IR_POWER = 100 * ureg('W')
IR_DISTANCE = 50 * ureg('mm')

# Corona cleaning constants
CORONA_TIME = 5 * ureg('s')
CORONA_POWER = 50 * ureg('W')
CORONA_TOOL = 'Corona tool'


def test_tfsc_batch_parser(monkeypatch):
    file = 'screen_printing_test.xlsx'
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
        'pers_project_1_1': check_batch,
        'pers_project_1_1_c-1': check_sample,
        'substrate 1 cm x 1 cm soda lime glass ito': check_substrate,
        # Step-specific process checks
        ('cleaning', 1.0): check_corona_cleaning,
        ('screen printing', 2.0): check_screen_printing,
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
    assert m.data.name == 'PERS_Project_1_1_C-1'
    assert m.data.lab_id == 'PERS_Project_1_1_C-1'
    assert m.data.datetime.isoformat() == '2025-05-21T00:00:00+00:00'
    assert m.data.description == '1000 rpm'
    assert m.data.number_of_junctions == 1


def check_batch(m):
    assert m.data.name == 'PERS_Project_1_1'
    assert m.data.lab_id == 'PERS_Project_1_1'
    assert len(m.data.entities) == 1
    assert m.data.entities[0].lab_id == 'PERS_Project_1_1_C-1'


def check_substrate(m):
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


def check_corona_cleaning(m):
    assert m.data.name == 'Cleaning'
    assert m.data.description == 'Corona cleaning notes'
    assert m.data.location == CORONA_TOOL
    assert m.data.positon_in_experimental_plan == 1.0
    assert m.data.cleaning_corona[0]['time'] == CORONA_TIME
    assert m.data.cleaning_corona[0]['power'] == CORONA_POWER


def check_screen_printing(m):
    assert m.data.name.startswith('screen printing')
    assert m.data.layer[0]['layer_type'] == LAYER_TYPE
    assert m.data.layer[0]['layer_material_name'] == MATERIAL_NAME
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == MORPHOLOGY
    assert m.data.solution[0]['solution_details']['solute'][0]['chemical_2']['name'] == SOLUTE
    assert m.data.solution[0]['solution_details']['solute'][0]['concentration_mol'] == SOLUTE_MOL
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_2']['name'] == SOLVENT
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_volume'] == SOLVENT_VOL
    assert m.data.solution[0]['solution_details']['solvent'][0]['amount_relative'] == 1.5
    assert m.data.solution[0]['solution_volume'] == SOLUTION_VOLUME
    assert m.data.solution[0]['solution_viscosity'] == VISCOSITY
    assert m.data.solution[0]['solution_contact_angle'] == CONTACT_ANGLE
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.description == NOTES
    assert m.data.location == TOOL_NAME

    # Screen printing specific properties
    assert m.data.properties['screen_mesh']['mesh_material'] == MESH_MATERIAL
    assert m.data.properties['screen_mesh']['mesh_count'] == MESH_COUNT
    assert m.data.properties['screen_mesh']['mesh_thickness'] == MESH_THICKNESS
    assert m.data.properties['screen_mesh']['thread_diameter'] == THREAD_DIAMETER
    assert m.data.properties['screen_mesh']['mesh_opening'] == MESH_OPENING
    assert m.data.properties['screen_mesh']['mesh_tension'] == MESH_TENSION
    assert m.data.properties['screen_mesh']['mesh_angle'] == MESH_ANGLE
    assert m.data.properties['emulsion_material'] == EMULSION_MATERIAL
    assert m.data.properties['emulsion_thickness'] == EMULSION_THICKNESS
    assert m.data.properties['squeegee_material'] == SQUEEGEE_MATERIAL
    assert m.data.properties['squeegee_shape'] == SQUEEGEE_SHAPE
    assert m.data.properties['squeegee_angle'] == SQUEEGEE_ANGLE
    assert m.data.properties['sp_speed'] == PRINTING_SPEED
    assert m.data.properties['sp_direction'] == PRINTING_DIRECTION
    assert m.data.properties['sp_pressure'] == PRINTING_PRESSURE
    assert m.data.properties['snap_off'] == SNAP_OFF_DISTANCE
    assert m.data.properties['sp_method'] == PRINTING_METHOD

    # IR Annealing check
    assert m.data.annealing['time'] == ANNEALING_TIME
    assert m.data.annealing['temperature'] == ANNEALING_TEMP
    assert m.data.annealing['atmosphere'] == ANNEALING_ATMOSPHERE
    assert m.data.annealing.m_def.name.endswith('IRAnnealing')
    assert m.data.annealing['power'] == IR_POWER
    assert m.data.annealing['distance'] == IR_DISTANCE
