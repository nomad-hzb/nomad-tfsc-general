#seq-evaporation not tracked yet

import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg

from utils import delete_json, get_archive
from datetime import datetime, timezone


@pytest.fixture(
    params=[
        'tfsc_experiment_parser_test.xlsx',
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
N_PROCESSED_ARCHIVES = 24
N_PIXELS = 6
SOLAR_CELL_AREA = 0.16
PIXEL_AREA = 0.16
CLEANING_TEMP = ureg.Quantity(61, ureg('°C'))
CLEANING_SOLVENT = 'Hellmanex'
PLASMA_POWER = 50.0
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
GENERIC_PROCESS_STEP = 15.0
# Evaporation/ALD/Sputtering constants
EVAP_TEMP = ureg.Quantity(23, ureg('°C'))
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
EVAP_BATCH = '30'
EVAP_DRYING_TIME = 90.0 * ureg('s')
EVAP_COST = 50.0
EVAP_PRESSURE = 0.001 * ureg('mbar')
EVAP_PRESSURE_START = 0.005000000000000001 * ureg('mbar')
EVAP_PRESSURE_END = 0.0030000000000000005 * ureg('mbar')
EVAP_START_RATE = 0.5
EVAP_TARGET_RATE = 1.0
EVAP_SUBSTRATE_TEMP = ureg.Quantity(25, ureg('°C'))
EVAP_TOOLING_FACTOR = '1.5'
EVAP_TEMPERATURES = [150.0, 160.0]
EVAP_CHEMICAL_C = 'C'
EVAP_CHEMICAL_ITO = 'ITO'
EVAP_CHEMICAL_AG = 'Ag'
SPUTTER_PRESSURE = 0.01 * ureg('mbar')
SPUTTER_TEMP = ureg.Quantity(200.0, ureg('°C'))
SPUTTER_BURNIN = 60.0 * ureg('s')
SPUTTER_DEPOSITION = 300.0  * ureg('s')
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


def test_tfsc_batch_parser(monkeypatch):
    file = 'tfsc_experiment_parser_test.xlsx'
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

    for m in measurement_archives:
        t = str(type(m.data))
        # Sample
        if 'Sample' in t:
            assert m.data.name in ['SAU_GeSo_1_1_C-1', 'SAU_GeSo_1_1_C-2']
            assert m.data.lab_id in ['SAU_GeSo_1_1_C-1', 'SAU_GeSo_1_1_C-2']
            assert m.data.description == '1000 rpm'
            assert m.data.number_of_junctions == 1
        # Batch
        elif 'Batch' in t:
            assert m.data.name == 'SAU_GeSo_1_1'
            assert m.data.lab_id == 'SAU_GeSo_1_1'
            assert len(m.data.entities) == 2
            assert m.data.entities[0]['lab_id'] == 'SAU_GeSo_1_1_C-1'
            assert m.data.entities[1]['lab_id'] == 'SAU_GeSo_1_1_C-2'
        # Substrate
        elif 'Substrate' in t:
            assert m.data.name == 'Substrate 1 cm x 1 cm Soda Lime Glass ITO'
            assert m.data.lab_id == ''
            assert m.data.description == 'Experiment Notes'
            assert m.data.solar_cell_area == SOLAR_CELL_AREA * ureg('cm**2')
            assert m.data.number_of_pixels == N_PIXELS
            assert m.data.pixel_area == PIXEL_AREA * ureg('cm**2')
            assert m.data.substrate == 'Soda Lime Glass'
            assert m.data.conducting_material[0] == 'ITO'
            assert m.data.substrate_properties[0]['layer_type'] == 'Substrate Conductive Layer'
            assert m.data.substrate_properties[0]['layer_material_name'] == 'ITO'
        # Laser Scribing
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 1.0:
            assert m.data.name == 'laser scribing'
            assert m.data.description == 'Platform:EP3'
            assert m.data.recipe_file == 'test_scribing_recipe.xml'
            assert m.data.patterning == 'P1,P2,P3, commercially etched'
            assert m.data.layout == 'BBBB, minimodule'
            assert m.data.properties['laser_wavelength'] == LASER_WAVELENGTH
            assert m.data.properties['laser_pulse_time'] == 8.0 * ureg('ps')
            assert m.data.properties['laser_pulse_frequency'] == 80.0 *ureg('kHz')
            assert m.data.properties['speed'] == 100.0 * ureg('mm/s')
            assert m.data.properties['fluence'] == 0.5 * ureg('J/cm**2')
            assert m.data.properties['power_in_percent'] == LASER_POWER_PERCENT
        # Cleaning 2_0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 2.0:
            assert m.data.name == 'Cleaning'
            assert m.data.description == 'Can be disclosed:Yes/No, Recipe'
            assert m.data.location == 'HZB Glovebox1'
            assert m.data.cleaning[0]['time'] == 0.5166666666666666 * ureg('minute')
            assert m.data.cleaning[0]['temperature'] == CLEANING_TEMP
            assert m.data.cleaning[0]['solvent_2']['name'] == CLEANING_SOLVENT
            assert m.data.cleaning[1]['time'] == 0.5166666666666666 * ureg('minute')
            assert m.data.cleaning[1]['temperature'] == CLEANING_TEMP
            assert m.data.cleaning[1]['solvent_2']['name'] == CLEANING_SOLVENT
        # Cleaning 3_0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 3.0:
            assert m.data.name == 'Cleaning'
            assert m.data.description == 'Plasma cleaning notes'
            assert m.data.location == 'SAU Box'
            assert m.data.cleaning_plasma[0]['time'] == 3.0 * ureg('minute')
            assert m.data.cleaning_plasma[0]['power'] == PLASMA_POWER * ureg('W')
            assert m.data.cleaning_plasma[0]['plasma_type'] == PLASMA_TYPE
        # Cleaning 4_0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 4.0:
            assert m.data.name == 'Cleaning'
            assert m.data.description == 'Ozone cleaning notes'
            assert m.data.location == 'SAU Box'
            assert m.data.cleaning_uv[0]['time'] == CLEANING_UV_TIME

        # Spin Coating 5_0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 5.0:
            assert m.data.name == 'spin coating Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3'
            assert m.data.description == 'Batch supplier-ID-Opened at-remaining shelf life'
            assert m.data.location == 'SAU Box'
            assert m.data.atmosphere['temperature'] == ureg.Quantity(23, ureg('°C'))
            assert m.data.atmosphere['relative_humidity'] == 45.0
            assert m.data.atmosphere['oxygen_level_ppm'] == 10.0
            assert m.data.layer[0]['layer_type'] == 'Absorber'
            assert m.data.layer[0]['layer_material_name'] == SPIN_COATING_LAYER
            assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
            assert m.data.layer[0]['layer_morphology'] == 'Uniform'
            assert m.data.solution[0]['solution_volume'] == 0.1 * ureg('ml')
            assert m.data.solution[0]['solution_viscosity'] == 0.0005 * ureg('Pa*s')
            assert m.data.solution[0]['solution_contact_angle'] == 30.0 * ureg('degree')
            solutes = m.data.solution[0]['solution_details']['solute']
            assert solutes[0]['concentration_mol'] == 1.42e-06 * ureg('mol/ml')
            assert solutes[0]['chemical_2']['name'] == 'PbI2'
            if len(solutes) > 1:
                assert solutes[1]['concentration_mol'] == 1.42e-06 * ureg('mol/ml')
                assert solutes[1]['chemical_2']['name'] == 'PbI2'
            solvents = m.data.solution[0]['solution_details']['solvent']
            assert solvents[0]['chemical_volume'] == 0.01 * ureg('ml')
            assert solvents[0]['amount_relative'] == 1.5
            assert solvents[0]['chemical_2']['name'] == 'DMF'
            assert solvents[1]['chemical_volume'] == 0.02 * ureg('ml')
            assert solvents[1]['amount_relative'] == 1.5
            assert solvents[1]['chemical_2']['name'] == 'DMF'
            assert m.data.annealing['temperature'] == ANNEALING_TEMP
            assert m.data.annealing['time'] == 1800.0 * ureg('s')
            assert m.data.annealing['atmosphere'] == 'N2'
            assert m.data.quenching['anti_solvent_volume'] == 0.3 * ureg('ml')
            assert m.data.quenching['anti_solvent_dropping_time'] == 25.0 * ureg('s')
            assert m.data.quenching['anti_solvent_dropping_flow_rate'] == 50.0 * ureg('ul/s')
            assert m.data.quenching['anti_solvent_dropping_height'] == 30.0 * ureg('mm')
            assert m.data.quenching['anti_solvent_2']['name'] == QUENCHING_SOLVENT
            assert m.data.recipe_steps[0]['time'] == 31.0 * ureg('s')
            assert m.data.recipe_steps[0]['speed'] == 3001.0 * ureg('rpm')
            assert m.data.recipe_steps[0]['acceleration'] == 1001.0 * ureg('rpm/s')
            assert m.data.recipe_steps[1]['time'] == 32.0 * ureg('s')
            assert m.data.recipe_steps[1]['speed'] == 3002.0 * ureg('rpm')
            assert m.data.recipe_steps[1]['acceleration'] == 1002.0 * ureg('rpm/s')
        # Slot Die Coating 6_0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 6.0:
            assert m.data.name.startswith('slot die coating')
            assert (
                m.data.layer[0]['layer_material_name'] == SPIN_COATING_LAYER
            )
            assert m.data.annealing['temperature'] == ANNEALING_TEMP
            assert m.data.annealing['time'] == 1800.0 * ureg('s')
            assert m.data.annealing['atmosphere'] == 'N2'
            # Only check anti_solvent_volume if present (not for AirKnifeGasQuenching)
            if 'anti_solvent_volume' in m.data.quenching:
                assert m.data.quenching['anti_solvent_volume'] == 0.3 * ureg('ml')
            assert m.data.quenching['air_knife_angle'] == SLOT_DIE_ANGLE
            if hasattr(m.data, 'recipe_steps') and m.data.recipe_steps:
                assert m.data.recipe_steps[0]['time'] == 31.0 * ureg('s')
                assert m.data.recipe_steps[0]['speed'] == 3001.0 * ureg('rpm')
                assert m.data.recipe_steps[0]['acceleration'] == 1001.0 * ureg('rpm/s')
                assert m.data.recipe_steps[1]['time'] == 32.0 * ureg('s')
                assert m.data.recipe_steps[1]['speed'] == 3002.0 * ureg('rpm')
                assert m.data.recipe_steps[1]['acceleration'] == 1002.0 * ureg('rpm/s')
        # Inkjet Printing 7_0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 7.0:
            assert m.data.name.startswith('inkjet printing')
            assert (
                m.data.layer[0]['layer_material_name'] == SPIN_COATING_LAYER
            )
            assert m.data.properties['drop_density'] == INKJET_DROP_DENSITY * ureg('1/in')
            assert (
                m.data.properties['print_head_properties']['print_head_name'] == INKJET_HEAD_NAME
            )
            assert m.data.atmosphere['temperature'] == ureg.Quantity(23, ureg('°C'))
            assert m.data.atmosphere['relative_humidity'] == 45.0
            assert m.data.atmosphere['oxygen_level_ppm'] == 10.0
            assert m.data.layer[0]['layer_type'] == 'Absorber'
            assert m.data.layer[0]['layer_material_name'] == SPIN_COATING_LAYER
            assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
            assert m.data.layer[0]['layer_morphology'] == 'Uniform'
            assert m.data.solution[0]['solution_volume'] == 0.1 * ureg('ml')
            assert m.data.solution[0]['solution_viscosity'] == 0.0005 * ureg('Pa*s')
            assert m.data.solution[0]['solution_contact_angle'] == 30.0 * ureg('degree')
            solutes = m.data.solution[0]['solution_details']['solute']
            assert solutes[0]['concentration_mol'] == 1.42e-06 * ureg('mol/ml')
            assert solutes[0]['chemical_2']['name'] == 'PbI2'
            if len(solutes) > 1:
                assert solutes[1]['concentration_mol'] == 1.42e-06 * ureg('mol/ml')
                assert solutes[1]['chemical_2']['name'] == 'PbI2'
            solvents = m.data.solution[0]['solution_details']['solvent']
            assert solvents[0]['chemical_volume'] == 0.01 * ureg('ml')
            assert solvents[0]['amount_relative'] == 1.5
            assert solvents[0]['chemical_2']['name'] == 'DMF'
            assert solvents[1]['chemical_volume'] == 0.02 * ureg('ml')
            assert solvents[1]['amount_relative'] == 1.5
            assert solvents[1]['chemical_2']['name'] == 'DMF'
            assert m.data.annealing['temperature'] == ANNEALING_TEMP
            assert m.data.annealing['time'] == 1800.0 * ureg('s')
            assert m.data.annealing['atmosphere'] == 'N2'
            assert m.data.quenching['anti_solvent_volume'] == 0.3 * ureg('ml')
            assert m.data.quenching['anti_solvent_dropping_time'] == 25.0 * ureg('s')
            assert m.data.quenching['anti_solvent_dropping_flow_rate'] == 50.0 * ureg('ul/s')
            assert m.data.quenching['anti_solvent_dropping_height'] == 30.0 * ureg('mm')
            assert m.data.quenching['anti_solvent_2']['name'] == QUENCHING_SOLVENT
            assert m.data.recipe_steps[0]['time'] == 31.0 * ureg('s')
            assert m.data.recipe_steps[0]['speed'] == 3001.0 * ureg('rpm')
            assert m.data.recipe_steps[0]['acceleration'] == 1001.0 * ureg('rpm/s')
            assert m.data.recipe_steps[1]['time'] == 32.0 * ureg('s')
            assert m.data.recipe_steps[1]['speed'] == 3002.0 * ureg('rpm')
            assert m.data.recipe_steps[1]['acceleration'] == 1002.0 * ureg('rpm/s')
        # Evaporation 8.0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 8.0:
            if m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C:
                assert m.data.name == 'evaporation C'
                assert m.data.description == 'Evaporation Test'
                assert m.data.location == 'SAU Box'
                assert m.data.co_evaporation is False
                assert m.data.atmosphere['temperature'] == EVAP_TEMP
                assert m.data.atmosphere['relative_humidity'] == EVAP_RH
                assert m.data.atmosphere['oxygen_level_ppm'] == EVAP_O2
                assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_C
                assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C
                assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
                assert m.data.layer[0]['supplier'] == EVAP_SUPPLIER
                assert m.data.layer[0]['batch'] == EVAP_BATCH
                # drying_time and cost only in 8_0 and 8_1
                if 'drying_time' in m.data.layer[0]:
                    assert m.data.layer[0]['drying_time'] == EVAP_DRYING_TIME
                if 'cost' in m.data.layer[0]:
                    assert m.data.layer[0]['cost'] == EVAP_COST
                # inorganic_evaporation or organic_evaporation
                if hasattr(m.data, 'inorganic_evaporation') and m.data.inorganic_evaporation:
                    evap = m.data.inorganic_evaporation[0]
                elif hasattr(m.data, 'organic_evaporation') and m.data.organic_evaporation:
                    evap = m.data.organic_evaporation[0]
                else:
                    evap = None
                if evap:
                    assert evap['pressure'] == EVAP_PRESSURE
                    assert evap['pressure_start'] == EVAP_PRESSURE_START
                    assert evap['pressure_end'] == EVAP_PRESSURE_END
                    assert evap['start_rate'] == EVAP_START_RATE
                    assert evap['target_rate'] == EVAP_TARGET_RATE
                    assert evap['substrate_temparature'] == EVAP_SUBSTRATE_TEMP
                    assert evap['tooling_factor'] == EVAP_TOOLING_FACTOR
                    assert evap['temparature'] == EVAP_TEMPERATURES
                    assert evap['chemical_2']['name'] == EVAP_CHEMICAL_C
                    assert evap['chemical_2']['load_data'] is False
        # Evaporation 9.0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 9.0:
            if m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C:
                assert m.data.name == 'evaporation C'
                assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_C
                assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C
                assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
                # Only inorganic_evaporation
                evap = m.data.inorganic_evaporation[0]
                assert evap['pressure'] == EVAP_PRESSURE
                assert evap['pressure_start'] == EVAP_PRESSURE_START
                assert evap['pressure_end'] == EVAP_PRESSURE_END
                assert evap['start_rate'] == EVAP_START_RATE
                assert evap['target_rate'] == EVAP_TARGET_RATE
                assert evap['substrate_temparature'] == EVAP_SUBSTRATE_TEMP
                assert evap['tooling_factor'] == EVAP_TOOLING_FACTOR
                assert evap['temparature'] == EVAP_TEMPERATURES
                assert evap['chemical_2']['name'] == EVAP_CHEMICAL_C
                assert evap['chemical_2']['load_data'] is False
            elif m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_ITO:
                assert m.data.name == 'evaporation ITO'
                assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_ITO
                assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_ITO
                assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
                assert m.data.layer[0]['layer_transmission'] == EVAP_LAYER_TRANSMISSION
                assert m.data.layer[0]['layer_morphology'] == EVAP_LAYER_MORPH
                evap = m.data.organic_evaporation[0]
                assert evap['pressure'] == EVAP_PRESSURE
                assert evap['pressure_start'] == EVAP_PRESSURE_START
                assert evap['pressure_end'] == EVAP_PRESSURE_END
                assert evap['start_rate'] == EVAP_START_RATE
                assert evap['target_rate'] == EVAP_TARGET_RATE
                assert evap['substrate_temparature'] == EVAP_SUBSTRATE_TEMP
                assert evap['tooling_factor'] == EVAP_TOOLING_FACTOR
                assert evap['temparature'] == EVAP_TEMPERATURES
                assert evap['chemical_2']['name'] == EVAP_CHEMICAL_ITO
                assert evap['chemical_2']['load_data'] is False
        # Evaporation 10.0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 10.0:
            if m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C:
                assert m.data.name == 'evaporation C'
                assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_C
                assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C
                assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
            elif m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_AG:
                assert m.data.name == 'evaporation Ag'
                assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_AG
                assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_AG
                assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
                assert m.data.layer[0]['layer_transmission'] == EVAP_LAYER_TRANSMISSION
                assert m.data.layer[0]['layer_morphology'] == EVAP_LAYER_MORPH
        # Evaporation 11.0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 11.0:
            if m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C:
                assert m.data.name == 'evaporation C'
                assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_C
                assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C
                assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
            elif m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_AG:
                assert m.data.name == 'evaporation Ag'
                assert m.data.layer[0]['layer_type'] == EVAP_LAYER_TYPE_AG
                assert m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_AG
                assert m.data.layer[0]['layer_thickness'] == EVAP_LAYER_THICKNESS_VAL
                assert m.data.layer[0]['layer_transmission'] == EVAP_LAYER_TRANSMISSION
                assert m.data.layer[0]['layer_morphology'] == EVAP_LAYER_MORPH
        # Sputtering 12.0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 12.0:
            if m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C:
                assert m.data.name == 'sputtering C'
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
            elif m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_AG:
                assert m.data.name == 'sputtering Ag'
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
        # ALD 13.0
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 13.0:
            if m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_C:
                assert m.data.name == 'atomic layer deposition C'
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
            elif m.data.layer[0]['layer_material_name'] == EVAP_CHEMICAL_AG:
                assert m.data.name == 'atomic layer deposition Ag'
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
        # Test Generic Process
        elif getattr(m.data, 'positon_in_experimental_plan', None) == GENERIC_PROCESS_STEP:
            assert m.data.name == 'Test Generic Process'
            assert m.data.description == 'This is a test generic process'
            assert m.data.positon_in_experimental_plan == GENERIC_PROCESS_STEP
    delete_json()

