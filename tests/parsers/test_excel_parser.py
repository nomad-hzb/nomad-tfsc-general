# dip coating, blade coating, sublimation, Annealing class and seq/co-evaporation are not tracked yet. antisolvent, vacuum and gas quenching get mapped only to spin coating, and air knife quenching only to slot die coating.

import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg
from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'tfsc_test_exp_parser.xlsx',
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
N_PROCESSED_ARCHIVES = 15
N_PIXELS = 6
SOLAR_CELL_AREA = 0.16 * ureg('centimeter ** 2')
PIXEL_AREA = 0.16 * ureg('centimeter ** 2')
CLEANING_TEMP = ureg.Quantity(61, ureg('°C'))
CLEANING_SOLVENT = 'Hellmanex'
PLASMA_POWER = 50.0 * ureg('watt')
PLASMA_TYPE = 'Oxygen'
CLEANING_UV_TIME = 15.0 * ureg('minute')
SPIN_COATING_LAYER = 'Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3'
ANNEALING_TEMP = ureg.Quantity(120.0, ureg('°C'))
QUENCHING_SOLVENT = 'Toluene'
SLOT_DIE_ANGLE = 45.0 * ureg('°')
SLOT_DIE_FLOW = 0.025 * ureg('ml/minute')
INKJET_DROP_DENSITY = 400.0
INKJET_HEAD_NAME = 'Spectra 0.8uL'
LASER_WAVELENGTH = 532.0 * ureg('nm')
LASER_POWER_PERCENT = 75.0
LAYER_THICKNESS = 25.0 * ureg('nm')
EVAP_LAYER_TRANSMISSION = 95.0
ALD_SOURCE = 'TMA'
ALD_MATERIAL = 'TMA'
ALD_OXIDIZER = 'H2O'
GENERIC_PROCESS_STEP = 12.0
# Evaporation/ALD/Sputtering constants
ROOM_TEMP = ureg.Quantity(23, ureg('°C'))
EVAP_RH = 45.0
EVAP_O2 = 10.0
EVAP_LAYER_THICKNESS_VAL = 25.0 * ureg('nm')
EVAP_LAYER_THICKNESS_AG = 25.0 * ureg('nm')
EVAP_LAYER_TYPE_C = 'Carbon Paste Layer'
EVAP_LAYER_TYPE_AG = 'Electrode Layer'
EVAP_LAYER_TYPE_ITO = 'Electrode'
EVAP_LAYER_TYPE_ELECTRODE = 'Electrode Layer'
EVAP_LAYER_MORPH = 'Uniform'
EVAP_SUPPLIER = 'X_Company/23-001'
EVAP_BATCH = '30.0'
EVAP_DRYING_TIME = 90.0 * ureg('s')
EVAP_COST = 50.0
EVAP_PRESSURE = 0.001 * ureg('mbar')
EVAP_PRESSURE_START = 0.005000000000000001 * ureg('mbar')
EVAP_PRESSURE_END = 0.0030000000000000005 * ureg('mbar')
EVAP_START_RATE = 0.5 * ureg('angstrom/s')
EVAP_TARGET_RATE = 1.0 * ureg('angstrom/s')
EVAP_SUBSTRATE_TEMP = ureg.Quantity(25, ureg('°C'))
EVAP_TOOLING_FACTOR = '1.5'
EVAP_TEMPERATURES = [ureg.Quantity(150, ureg('°C')), ureg.Quantity(160, ureg('°C'))]
EVAP_CHEMICAL_C = 'C'
EVAP_CHEMICAL_ITO = 'ITO'
EVAP_CHEMICAL_AG = 'Ag'
SPUTTER_PRESSURE = 0.01 * ureg('mbar')
SPUTTER_TEMP = ureg.Quantity(200.0, ureg('°C'))
SPUTTER_BURNIN = 60.0 * ureg('s')
SPUTTER_DEPOSITION = 300.0 * ureg('s')
SPUTTER_POWER = 150.0 * ureg('W')
SPUTTER_GAS_FLOW = 20.0 * ureg('cm**3/minute')
SPUTTER_ROTATION = 30.0 * ureg('rpm')
SPUTTER_GAS = 'Argon'
ALD_TEMP = ureg.Quantity(150, ureg('°C'))
ALD_RATE = 0.1 * ureg('angstrom/s')
ALD_TIME = 1800.0 * ureg('s')
ALD_CYCLES = 250
ALD_PULSE = 0.2 * ureg('s')
ALD_MANIFOLD = ureg.Quantity(80, ureg('°C'))
ALD_BOTTLE = ureg.Quantity(25, ureg('°C'))
ALD_OX_PULSE = 0.1 * ureg('s')
ALD_OX_MANIFOLD = ureg.Quantity(70, ureg('°C'))

# Additional constants for magic values
LASER_PULSE_TIME = 8.0 * ureg('ps')
LASER_PULSE_FREQUENCY = 80.0 * ureg('kHz')
LASER_SPEED = 100.0 * ureg('mm/s')
LASER_FLUENCE = 0.5 * ureg('J/cm**2')
CLEANING_TIME = 0.5166666666666666 * ureg('minute')
PLASMA_TIME = 3.0 * ureg('minute')
ATMOSPHERE_TEMP = ureg.Quantity(23, ureg('°C'))
ATMOSPHERE_RH = 45.0
ATMOSPHERE_O2 = 10.0
SOLUTION_VOLUME = 0.1 * ureg('ml')
SOLUTION_VISCOSITY = 0.0005 * ureg('Pa*s')
SOLUTION_CONTACT_ANGLE = 30.0 * ureg('degree')
SOLUTE_CONC = 1.42e-06 * ureg('mol/ml')
SOLVENT_VOL1 = 0.01 * ureg('ml')
SOLVENT_VOL2 = 0.02 * ureg('ml')
SOLVENT_REL = 1.5
ANNEAL_TIME = 1800.0 * ureg('s')
QUENCH_VOL = 0.3 * ureg('ml')
QUENCH_DROP_TIME = 25.0 * ureg('s')
QUENCH_FLOW = 50.0 * ureg('ul/s')
QUENCH_HEIGHT = 30.0 * ureg('mm')
RECIPE_TIME1 = 31.0 * ureg('s')
RECIPE_SPEED1 = 3001.0 * ureg('rpm')
RECIPE_ACCEL1 = 1001.0 * ureg('rpm/s')
RECIPE_TIME2 = 32.0 * ureg('s')
RECIPE_SPEED2 = 3002.0 * ureg('rpm')
RECIPE_ACCEL2 = 1002.0 * ureg('rpm/s')
N_ENTITIES = 2

# Process step constants
STEP_LASER_SCRIBING = 1.0
STEP_CLEANING_2 = 2.0
STEP_CLEANING_3 = 3.0
STEP_CLEANING_4 = 4.0
STEP_SPIN_COATING = 5.0
STEP_SLOT_DIE = 6.0
STEP_INKJET = 7.0
STEP_EVAP_C = 8.0
STEP_EVAP_ITO = 8.0
STEP_EVAP_CS = 9.0
STEP_EVAP_AG = 9.0
STEP_SPUTTER_C = 10.0
STEP_SPUTTER_AG = 10.0
STEP_ALD_C = 11.0
STEP_ALD_AG = 11.0


def test_tfsc_batch_parser(monkeypatch):
    file = 'tfsc_test_exp_parser.xlsx'
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
        'Sample': check_sample,
        'Batch': check_batch,
        'Substrate': check_substrate,
        (STEP_LASER_SCRIBING,): check_laser_scribing,
        (STEP_CLEANING_2,): check_cleaning_2,
        (STEP_CLEANING_3,): check_cleaning_3,
        (STEP_CLEANING_4,): check_cleaning_4,
        (STEP_SPIN_COATING,): check_spin_coating,
        (STEP_SLOT_DIE,): check_slot_die,
        (STEP_INKJET,): check_inkjet,
        (STEP_EVAP_C, 'evaporation C'): check_evap_c,
        (STEP_EVAP_ITO, 'evaporation ITO'): check_evap_ito,
        (
            STEP_EVAP_CS,
            'evaporation Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3',
        ): check_evap_cs,
        (STEP_EVAP_AG, 'evaporation Ag'): check_evap_ag,
        (STEP_SPUTTER_C, 'sputtering C'): check_sputter_c,
        (STEP_SPUTTER_AG, 'sputtering Ag'): check_sputter_ag,
        (STEP_ALD_C, 'atomic layer deposition C'): check_ald_c,
        (STEP_ALD_AG, 'atomic layer deposition Ag'): check_ald_ag,
        (GENERIC_PROCESS_STEP,): check_generic_process,
    }

    for m in measurement_archives:
        t = str(type(m.data))
        if t in PROCESS_CHECKS:
            PROCESS_CHECKS[t](m)
            continue
        step = getattr(m.data, 'positon_in_experimental_plan', None)
        name = getattr(m.data, 'name', None)
        if (step, name) in PROCESS_CHECKS:
            PROCESS_CHECKS[(step, name)](m)
        elif (step,) in PROCESS_CHECKS:
            PROCESS_CHECKS[(step,)](m)
    delete_json()


# Helper functions for each process type


def check_sample(m):
    assert m.data.name in ['SAU_GeSo_1_1_C-1', 'SAU_GeSo_1_1_C-2']
    assert m.data.lab_id in ['SAU_GeSo_1_1_C-1', 'SAU_GeSo_1_1_C-2']
    assert m.data.description == '1000 rpm'
    assert m.data.number_of_junctions == 1


def check_batch(m):
    assert m.data.name == 'SAU_GeSo_1_1'
    assert m.data.lab_id == 'SAU_GeSo_1_1'
    assert len(m.data.entities) == N_ENTITIES
    assert m.data.entities[0]['lab_id'] == 'SAU_GeSo_1_1_C-1'
    assert m.data.entities[1]['lab_id'] == 'SAU_GeSo_1_1_C-2'


def check_substrate(m):
    assert m.data.name == 'Substrate 1 cm x 1 cm Soda Lime Glass ITO'
    assert m.data.lab_id == ''
    assert m.data.description == 'Experiment Notes'
    assert m.data.solar_cell_area == SOLAR_CELL_AREA
    assert m.data.number_of_pixels == N_PIXELS
    assert m.data.pixel_area == PIXEL_AREA
    assert m.data.substrate == 'Soda Lime Glass'
    assert m.data.conducting_material[0] == 'ITO'
    assert m.data.substrate_properties[0]['layer_type'] == 'Substrate Conductive Layer'
    assert m.data.substrate_properties[0]['layer_material_name'] == 'ITO'


def check_laser_scribing(m):
    assert m.data.name == 'laser scribing'
    assert m.data.description == 'Platform:EP3'
    assert m.data.recipe_file == 'test_scribing_recipe.xml'
    assert m.data.patterning == 'P1,P2,P3, commercially etched'
    assert m.data.layout == 'BBBB, minimodule'
    assert m.data.properties['laser_wavelength'] == LASER_WAVELENGTH
    assert m.data.properties['laser_pulse_time'] == LASER_PULSE_TIME
    assert m.data.properties['laser_pulse_frequency'] == LASER_PULSE_FREQUENCY
    assert m.data.properties['speed'] == LASER_SPEED
    assert m.data.properties['fluence'] == LASER_FLUENCE
    assert m.data.properties['power_in_percent'] == LASER_POWER_PERCENT


def check_cleaning_2(m):
    assert m.data.name == 'Cleaning'
    assert m.data.description == 'Can be disclosed:Yes/No, Recipe'
    assert m.data.location == 'HZB Glovebox1'
    assert m.data.cleaning[0]['time'] == CLEANING_TIME
    assert m.data.cleaning[0]['temperature'] == CLEANING_TEMP
    assert m.data.cleaning[0]['solvent_2']['name'] == CLEANING_SOLVENT
    # Second cleaning step may have different values
    assert m.data.cleaning[1]['time'] == CLEANING_TIME
    assert m.data.cleaning[1]['temperature'] == CLEANING_TEMP
    assert m.data.cleaning[1]['solvent_2']['name'] == CLEANING_SOLVENT


def check_cleaning_3(m):
    assert m.data.name == 'Cleaning'
    assert m.data.description == 'Plasma cleaning notes'
    assert m.data.location == 'SAU Box'
    assert m.data.cleaning_plasma[0]['time'] == PLASMA_TIME
    assert m.data.cleaning_plasma[0]['power'] == PLASMA_POWER
    assert m.data.cleaning_plasma[0]['plasma_type'] == PLASMA_TYPE


def check_cleaning_4(m):
    assert m.data.name == 'Cleaning'
    assert m.data.description == 'Ozone cleaning notes'
    assert m.data.location == 'SAU Box'
    assert m.data.cleaning_uv[0]['time'] == CLEANING_UV_TIME


def check_spin_coating(m):
    assert m.data.name == 'spin coating Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3'
    assert m.data.description == 'Batch supplier-ID-Opened at-remaining shelf life'
    assert m.data.location == 'SAU Box'
    assert m.data.atmosphere['temperature'] == ATMOSPHERE_TEMP
    assert m.data.atmosphere['relative_humidity'] == ATMOSPHERE_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == ATMOSPHERE_O2
    assert m.data.layer[0]['layer_type'] == 'Absorber'
    assert m.data.layer[0]['layer_material_name'] == SPIN_COATING_LAYER
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == 'Uniform'
    assert m.data.solution[0]['solution_volume'] == SOLUTION_VOLUME
    assert m.data.solution[0]['solution_viscosity'] == SOLUTION_VISCOSITY
    assert m.data.solution[0]['solution_contact_angle'] == SOLUTION_CONTACT_ANGLE
    solutes = m.data.solution[0]['solution_details']['solute']
    assert solutes[0]['concentration_mol'] == SOLUTE_CONC
    assert solutes[0]['chemical_2']['name'] == 'PbI2'
    solvents = m.data.solution[0]['solution_details']['solvent']
    assert solvents[0]['chemical_volume'] == SOLVENT_VOL1
    assert solvents[0]['amount_relative'] == SOLVENT_REL
    assert solvents[0]['chemical_2']['name'] == 'DMF'
    assert solvents[1]['chemical_volume'] == SOLVENT_VOL2
    assert solvents[1]['amount_relative'] == SOLVENT_REL
    assert solvents[1]['chemical_2']['name'] == 'DMF'
    assert m.data.annealing['temperature'] == ANNEALING_TEMP
    assert m.data.annealing['time'] == ANNEAL_TIME
    assert m.data.annealing['atmosphere'] == 'N2'
    assert m.data.quenching['anti_solvent_volume'] == QUENCH_VOL
    assert m.data.quenching['anti_solvent_dropping_time'] == QUENCH_DROP_TIME
    assert m.data.quenching['anti_solvent_dropping_flow_rate'] == QUENCH_FLOW
    assert m.data.quenching['anti_solvent_dropping_height'] == QUENCH_HEIGHT
    assert m.data.quenching['anti_solvent_2']['name'] == QUENCHING_SOLVENT
    assert m.data.recipe_steps[0]['time'] == RECIPE_TIME1
    assert m.data.recipe_steps[0]['speed'] == RECIPE_SPEED1
    assert m.data.recipe_steps[0]['acceleration'] == RECIPE_ACCEL1
    assert m.data.recipe_steps[1]['time'] == RECIPE_TIME2
    assert m.data.recipe_steps[1]['speed'] == RECIPE_SPEED2
    assert m.data.recipe_steps[1]['acceleration'] == RECIPE_ACCEL2


def check_slot_die(m):
    assert m.data.name.startswith('slot die coating')
    assert m.data.description == 'Batch supplier-ID-Opened at-remaining shelf life'
    assert m.data.location == 'SAU Box'
    assert m.data.atmosphere['temperature'] == ATMOSPHERE_TEMP
    assert m.data.atmosphere['relative_humidity'] == ATMOSPHERE_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == ATMOSPHERE_O2
    assert m.data.layer[0]['layer_type'] == 'Absorber'
    assert m.data.layer[0]['layer_material_name'] == SPIN_COATING_LAYER
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == 'Uniform'
    assert m.data.solution[0]['solution_volume'] == SOLUTION_VOLUME
    assert m.data.solution[0]['solution_viscosity'] == SOLUTION_VISCOSITY
    assert m.data.solution[0]['solution_contact_angle'] == SOLUTION_CONTACT_ANGLE
    solutes = m.data.solution[0]['solution_details']['solute']
    assert solutes[0]['concentration_mol'] == SOLUTE_CONC
    assert solutes[0]['chemical_2']['name'] == 'PbI2'
    solvents = m.data.solution[0]['solution_details']['solvent']
    assert solvents[0]['chemical_volume'] == SOLVENT_VOL1
    assert solvents[0]['amount_relative'] == SOLVENT_REL
    assert solvents[0]['chemical_2']['name'] == 'DMF'
    assert m.data.annealing['temperature'] == ANNEALING_TEMP
    assert m.data.annealing['time'] == ANNEAL_TIME
    assert m.data.annealing['atmosphere'] == 'N2'
    assert m.data.quenching['air_knife_angle'] == SLOT_DIE_ANGLE
    assert m.data.properties['flow_rate'] == SLOT_DIE_FLOW


def check_inkjet(m):
    assert m.data.name.startswith('inkjet printing')
    assert m.data.description == 'Batch supplier-ID-Opened at-remaining shelf life'
    assert m.data.location == 'SAU Box'
    assert m.data.atmosphere['temperature'] == ATMOSPHERE_TEMP
    assert m.data.atmosphere['relative_humidity'] == ATMOSPHERE_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == ATMOSPHERE_O2
    assert m.data.layer[0]['layer_type'] == 'Absorber'
    assert m.data.layer[0]['layer_material_name'] == SPIN_COATING_LAYER
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == 'Uniform'
    assert m.data.properties['drop_density'] == INKJET_DROP_DENSITY * ureg('1/in')
    assert (
        m.data.properties['print_head_properties']['print_head_name']
        == INKJET_HEAD_NAME
    )


def check_evap_c(m):
    assert m.data.description == 'Processability'
    assert m.data.location == 'SAU Box'
    assert m.data.co_evaporation is False
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == EVAP_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == EVAP_O2
    layer = m.data.layer[0]
    assert layer['layer_type'] == EVAP_LAYER_TYPE_C
    assert layer['layer_material_name'] == EVAP_CHEMICAL_C
    assert layer['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
    assert layer['supplier'] == EVAP_SUPPLIER
    assert layer['batch'] == EVAP_BATCH
    assert layer['drying_time'] == EVAP_DRYING_TIME
    assert layer['cost'] == EVAP_COST
    evap = m.data.organic_evaporation[0]
    assert evap['pressure'] == EVAP_PRESSURE
    assert evap['pressure_start'] == EVAP_PRESSURE_START
    assert evap['pressure_end'] == EVAP_PRESSURE_END
    assert evap['start_rate'] == EVAP_START_RATE
    assert evap['target_rate'] == EVAP_TARGET_RATE
    assert evap['substrate_temparature'] == EVAP_SUBSTRATE_TEMP
    assert evap['tooling_factor'] == EVAP_TOOLING_FACTOR
    assert set(evap['temparature']) == set(EVAP_TEMPERATURES)
    assert evap['chemical_2']['name'] == EVAP_CHEMICAL_C
    assert evap['chemical_2']['load_data'] is False


def check_evap_ito(m):
    assert m.data.description == ''
    assert m.data.location == 'SAU Box'
    assert m.data.co_evaporation is False
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == EVAP_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == EVAP_O2
    layer = m.data.layer[0]
    assert layer['layer_type'] == EVAP_LAYER_TYPE_ITO
    assert layer['layer_material_name'] == EVAP_CHEMICAL_ITO
    assert layer['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
    assert layer['layer_transmission'] == EVAP_LAYER_TRANSMISSION
    assert layer['layer_morphology'] == EVAP_LAYER_MORPH
    evap = m.data.organic_evaporation[0]
    assert evap['pressure'] == EVAP_PRESSURE
    assert evap['pressure_start'] == EVAP_PRESSURE_START
    assert evap['pressure_end'] == EVAP_PRESSURE_END
    assert evap['start_rate'] == EVAP_START_RATE
    assert evap['target_rate'] == EVAP_TARGET_RATE
    assert evap['substrate_temparature'] == EVAP_SUBSTRATE_TEMP
    assert evap['tooling_factor'] == EVAP_TOOLING_FACTOR
    assert set(evap['temparature']) == set(EVAP_TEMPERATURES)
    assert evap['chemical_2']['name'] == EVAP_CHEMICAL_ITO
    assert evap['chemical_2']['load_data'] is False


def check_evap_cs(m):
    assert m.data.location == 'SAU Box'
    assert m.data.co_evaporation is False
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == EVAP_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == EVAP_O2
    layer = m.data.layer[0]
    assert layer['layer_type'] == 'Absorber'
    assert layer['layer_material_name'] == SPIN_COATING_LAYER
    assert layer['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
    assert layer['layer_morphology'] == EVAP_LAYER_MORPH


def check_evap_ag(m):
    assert m.data.location == 'SAU Box'
    assert m.data.co_evaporation is False
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == EVAP_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == EVAP_O2
    assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_AG
    assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_AG
    assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_AG
    assert m.data.layer[0]['layer_transmission'] == EVAP_LAYER_TRANSMISSION
    assert m.data.layer[0]['layer_morphology'] == EVAP_LAYER_MORPH


def check_sputter_c(m):
    assert m.data.location == 'SAU Box'
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == EVAP_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == EVAP_O2
    assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_C
    assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C
    assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
    proc = m.data.processes[0]
    assert proc['pressure'] == SPUTTER_PRESSURE
    assert proc['temperature'] == SPUTTER_TEMP
    assert proc['burn_in_time'] == SPUTTER_BURNIN
    assert proc['deposition_time'] == SPUTTER_DEPOSITION
    assert proc['power'] == SPUTTER_POWER
    assert proc['gas_flow_rate'] == SPUTTER_GAS_FLOW
    assert proc['rotation_rate'] == SPUTTER_ROTATION
    assert proc['target_2']['name'] == EVAP_CHEMICAL_C
    assert proc['gas_2']['name'] == SPUTTER_GAS


def check_sputter_ag(m):
    assert m.data.location == 'SAU Box'
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == EVAP_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == EVAP_O2
    assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_AG
    assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_AG
    assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_AG
    assert m.data.layer[0]['layer_transmission'] == EVAP_LAYER_TRANSMISSION
    assert m.data.layer[0]['layer_morphology'] == EVAP_LAYER_MORPH
    proc = m.data.processes[0]
    assert proc['pressure'] == SPUTTER_PRESSURE
    assert proc['temperature'] == SPUTTER_TEMP
    assert proc['burn_in_time'] == SPUTTER_BURNIN
    assert proc['deposition_time'] == SPUTTER_DEPOSITION
    assert proc['power'] == SPUTTER_POWER
    assert proc['gas_flow_rate'] == SPUTTER_GAS_FLOW
    assert proc['rotation_rate'] == SPUTTER_ROTATION
    assert proc['target_2']['name'] == EVAP_CHEMICAL_AG
    assert proc['gas_2']['name'] == SPUTTER_GAS


def check_ald_c(m):
    assert m.data.location == 'SAU Box'
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == EVAP_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == EVAP_O2
    assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_C
    assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C
    assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
    props = m.data.properties
    assert props['source'] == ALD_SOURCE
    assert props['temperature'] == ALD_TEMP
    assert props['rate'] == ALD_RATE
    assert props['time'] == ALD_TIME
    assert props['number_of_cycles'] == ALD_CYCLES
    assert props['material']['pulse_duration'] == ALD_PULSE
    assert props['material']['manifold_temperature'] == ALD_MANIFOLD
    assert props['material']['bottle_temperature'] == ALD_BOTTLE
    assert props['material']['material']['name'] == ALD_MATERIAL
    assert props['oxidizer_reducer']['pulse_duration'] == ALD_OX_PULSE
    assert props['oxidizer_reducer']['manifold_temperature'] == ALD_OX_MANIFOLD
    assert props['oxidizer_reducer']['material']['name'] == ALD_OXIDIZER


def check_ald_ag(m):
    assert m.data.location == 'SAU Box'
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == EVAP_RH
    assert m.data.atmosphere['oxygen_level_ppm'] == EVAP_O2
    assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_AG
    assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_AG
    assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_AG
    assert m.data.layer[0]['layer_transmission'] == EVAP_LAYER_TRANSMISSION
    assert m.data.layer[0]['layer_morphology'] == EVAP_LAYER_MORPH
    props = m.data.properties
    assert props['source'] == ALD_SOURCE
    assert props['temperature'] == ALD_TEMP
    assert props['rate'] == ALD_RATE
    assert props['time'] == ALD_TIME
    assert props['number_of_cycles'] == ALD_CYCLES
    assert props['material']['pulse_duration'] == ALD_PULSE
    assert props['material']['manifold_temperature'] == ALD_MANIFOLD
    assert props['material']['bottle_temperature'] == ALD_BOTTLE
    assert props['material']['material']['name'] == ALD_MATERIAL
    assert props['oxidizer_reducer']['pulse_duration'] == ALD_OX_PULSE
    assert props['oxidizer_reducer']['manifold_temperature'] == ALD_OX_MANIFOLD
    assert props['oxidizer_reducer']['material']['name'] == ALD_OXIDIZER


def check_generic_process(m):
    assert m.data.name == 'Test Generic Process'
    assert m.data.description == 'This is a test generic process'
    assert m.data.positon_in_experimental_plan == GENERIC_PROCESS_STEP
