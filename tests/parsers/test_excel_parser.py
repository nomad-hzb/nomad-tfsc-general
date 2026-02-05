"""
dip coating, sublimation, Annealing class and seq/co-evaporation are not tracked yet.
Antisolvent, vacuum and gas quenching get mapped only to spin coating, and air knife quenching
only to slot die coating.
"""

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
N_PROCESSED_ARCHIVES = 18
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
        # Exact name matches for batch, sample, substrate (lowercased)
        'sau_geso_1_1': check_batch,
        'sau_geso_1_1_c-1': check_sample,
        'sau_geso_1_1_c-2': check_sample,
        'substrate 1 cm x 1 cm soda lime glass ito': check_substrate,
        # Step-specific process checks
        ('laser scribing', 1.0): check_laser_scribing,
        ('cleaning', 2.0): check_cleaning_2,
        ('cleaning', 3.0): check_cleaning_3,
        ('cleaning', 4.0): check_cleaning_4,
        ('spin coating', 5.0): check_spin_coating_antisolvent,
        ('spin coating', 6.0): check_spin_coating_vaccumq,
        ('spin coating', 7.0): check_spin_coating_gasq,
        ('slot die coating', 8.0): check_slot_die,
        ('inkjet printing', 9.0): check_inkjet,
        # For evaporation, check both org and inorg if present
        ('evaporation', 10.0): [check_evap_org, check_evap_inorg],
        ('sputtering', 11.0): check_sputter,
        ('atomic layer deposition', 12.0): check_ald,
        ('test generic process', 13.0): check_generic_process,
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
    assert m.data.datetime.isoformat() == '2025-05-21T00:00:00+00:00'
    assert m.data.description == '1000 rpm'
    assert m.data.number_of_junctions == 1


def check_batch(m):
    assert m.data.name == 'SAU_GeSo_1_1'
    assert m.data.lab_id == 'SAU_GeSo_1_1'
    assert len(m.data.entities) == 2
    assert m.data.entities[0].lab_id == 'SAU_GeSo_1_1_C-1'
    assert m.data.entities[1].lab_id == 'SAU_GeSo_1_1_C-2'


def check_substrate(m):
    assert m.data.datetime.isoformat() == '2025-05-21T00:00:00+00:00'
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


def check_laser_scribing(m):
    assert m.data.name == 'laser scribing'
    assert m.data.description == 'Platform:EP3'
    assert m.data.positon_in_experimental_plan == 1.0
    assert m.data.recipe_file == 'test_scribing_recipe.xml'
    assert m.data.patterning == 'P1,P2,P3, commercially etched'
    assert m.data.layout == 'BBBB, minimodule'
    assert m.data.properties['laser_wavelength'] == 532.0 * ureg('nm')
    assert m.data.properties['laser_pulse_time'] == 8.0 * ureg('ps')
    assert m.data.properties['laser_pulse_frequency'] == 80.0 * ureg('kHz')
    assert m.data.properties['speed'] == 100.0 * ureg('mm/s')
    assert m.data.properties['fluence'] == 0.5 * ureg('J/cm**2')
    assert m.data.properties['power_in_percent'] == 75.0


def check_cleaning_2(m):
    assert m.data.name == 'Cleaning'
    assert m.data.description == 'Can be disclosed:Yes/No, Recipe'
    assert m.data.location == 'HZB Glovebox1'
    assert m.data.positon_in_experimental_plan == 2.0
    assert m.data.cleaning[0]['time'] == 0.5166666666666666 * ureg('minute')
    assert m.data.cleaning[0]['temperature'] == ureg.Quantity(61, ureg('°C'))
    assert m.data.cleaning[0]['solvent_2']['name'] == SOLVENT_CLEAN
    assert m.data.cleaning[1]['time'] == 0.5333333333333333 * ureg('minute')
    assert m.data.cleaning[1]['temperature'] == ureg.Quantity(62, ureg('°C'))
    assert m.data.cleaning[1]['solvent_2']['name'] == SOLVENT_CLEAN


def check_cleaning_3(m):
    assert m.data.name == 'Cleaning'
    assert m.data.description == 'Plasma cleaning notes'
    assert m.data.location == 'SAU Box'
    assert m.data.positon_in_experimental_plan == 3.0
    assert m.data.cleaning_plasma[0]['time'] == 3.0 * ureg('minute')
    assert m.data.cleaning_plasma[0]['power'] == 50.0 * ureg('W')
    assert m.data.cleaning_plasma[0]['plasma_type'] == 'Oxygen'


def check_cleaning_4(m):
    assert m.data.name == 'Cleaning'
    assert m.data.description == 'Ozone cleaning notes'
    assert m.data.location == 'SAU Box'
    assert m.data.positon_in_experimental_plan == 4.0
    assert m.data.cleaning_uv[0]['time'] == 15.0 * ureg('minute')


def check_spin_coating_antisolvent(m):
    assert m.data.name.startswith('spin coating')
    assert m.data.description == NOTES
    assert m.data.location == TOOL_NAME
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.layer[0]['layer_type'] == LAYER_TYPE
    assert m.data.layer[0]['layer_material_name'] == MATERIAL_NAME
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == MORPHOLOGY
    assert m.data.solution[0]['solution_volume'] == SOLUTION_VOLUME
    assert m.data.solution[0]['solution_viscosity'] == VISCOCITY
    assert m.data.solution[0]['solution_contact_angle'] == CONTACT_ANGLE
    assert m.data.solution[0]['solution_details']['solute'][0]['concentration_mol'] == SOLUTE_MOL
    assert m.data.solution[0]['solution_details']['solute'][0]['chemical_2']['name'] == SOLUTE
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_volume'] == SOLVENT_VOL
    assert m.data.solution[0]['solution_details']['solvent'][0]['amount_relative'] == 1.5
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_2']['name'] == SOLVENT
    assert m.data.quenching.m_def.name.endswith('AntiSolventQuenching')
    assert m.data.quenching['anti_solvent_volume'] == 0.3 * ureg('ml')
    assert m.data.quenching['anti_solvent_dropping_time'] == 25.0 * ureg('s')
    assert m.data.quenching['anti_solvent_dropping_flow_rate'] == 50.0 * ureg('ul/s')
    assert m.data.quenching['anti_solvent_dropping_height'] == 30.0 * ureg('mm')
    assert m.data.quenching['anti_solvent_2']['name'] == 'Toluene'
    assert m.data.recipe_steps[0]['time'] == 31.0 * ureg('s')
    assert m.data.recipe_steps[0]['speed'] == 3001.0 * ureg('rpm')
    assert m.data.recipe_steps[0]['acceleration'] == 1001.0 * ureg('rpm/s')
    assert m.data.recipe_steps[1]['time'] == 32.0 * ureg('s')
    assert m.data.recipe_steps[1]['speed'] == 3002.0 * ureg('rpm')
    assert m.data.recipe_steps[1]['acceleration'] == 1002.0 * ureg('rpm/s')


def check_spin_coating_vaccumq(m):
    assert m.data.name.startswith('spin coating')
    assert m.data.description == NOTES
    assert m.data.location == TOOL_NAME
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.layer[0]['layer_type'] == LAYER_TYPE
    assert m.data.layer[0]['layer_material_name'] == MATERIAL_NAME
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == MORPHOLOGY
    assert m.data.solution[0]['solution_volume'] == SOLUTION_VOLUME
    assert m.data.solution[0]['solution_viscosity'] == VISCOCITY
    assert m.data.solution[0]['solution_contact_angle'] == CONTACT_ANGLE
    assert m.data.solution[0]['solution_details']['solute'][0]['concentration_mol'] == SOLUTE_MOL
    assert m.data.solution[0]['solution_details']['solute'][0]['chemical_2']['name'] == SOLUTE
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_volume'] == SOLVENT_VOL
    assert m.data.solution[0]['solution_details']['solvent'][0]['amount_relative'] == 1.5
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_2']['name'] == SOLVENT
    assert m.data.quenching.m_def.name.endswith('VacuumQuenching')
    assert m.data.quenching['pressure'].to('mbar').magnitude == pytest.approx(10.0)
    assert str(m.data.quenching['pressure'].units) == 'millibar'
    assert m.data.quenching['start_time'] == 8.0 * ureg('s')
    assert m.data.quenching['duration'] == 20.0 * ureg('s')
    assert m.data.recipe_steps[0]['time'] == 30.0 * ureg('s')
    assert m.data.recipe_steps[0]['speed'] == 1500.0 * ureg('rpm')
    assert m.data.recipe_steps[0]['acceleration'] == 500.0 * ureg('rpm/s')


def check_spin_coating_gasq(m):
    assert m.data.name.startswith('spin coating')
    assert m.data.description == NOTES
    assert m.data.location == TOOL_NAME
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.layer[0]['layer_type'] == LAYER_TYPE
    assert m.data.layer[0]['layer_material_name'] == MATERIAL_NAME
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == MORPHOLOGY
    assert m.data.solution[0]['solution_volume'] == SOLUTION_VOLUME
    assert m.data.solution[0]['solution_viscosity'] == VISCOCITY
    assert m.data.solution[0]['solution_contact_angle'] == CONTACT_ANGLE
    assert m.data.solution[0]['solution_details']['solute'][0]['concentration_mol'] == SOLUTE_MOL
    assert m.data.solution[0]['solution_details']['solute'][0]['chemical_2']['name'] == SOLUTE
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_volume'] == SOLVENT_VOL
    assert m.data.solution[0]['solution_details']['solvent'][0]['amount_relative'] == 1.5
    assert m.data.solution[0]['solution_details']['solvent'][0]['chemical_2']['name'] == SOLVENT
    assert m.data.quenching.m_def.name.endswith('GasQuenchingWithNozzle')
    assert m.data.quenching['gas'] == 'Nitrogen'
    assert m.data.quenching['starting_delay'] == 5.0 * ureg('s')
    assert m.data.quenching['flow_rate'] == 20.0 * ureg('ml/s')
    assert m.data.quenching['height'] == 10.0 * ureg('mm')
    assert m.data.quenching['duration'] == 15.0 * ureg('s')
    assert m.data.quenching['pressure'] == 1.2 * ureg('bar')
    assert m.data.quenching['velocity'] == 2.5 * ureg('m/s')
    assert m.data.quenching['nozzle_shape'] == 'Round'
    assert m.data.quenching['nozzle_size'] == '3'
    assert m.data.recipe_steps[0]['time'] == 30.0 * ureg('s')
    assert m.data.recipe_steps[0]['speed'] == 1500.0 * ureg('rpm')
    assert m.data.recipe_steps[0]['acceleration'] == 500.0 * ureg('rpm/s')


def check_slot_die(m):
    assert m.data.name.startswith('slot die coating')
    assert m.data.description == NOTES
    assert m.data.location == TOOL_NAME
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.layer[0]['layer_type'] == LAYER_TYPE
    assert m.data.layer[0]['layer_material_name'] == MATERIAL_NAME
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == MORPHOLOGY
    assert m.data.solution[0]['solution_volume'] == SOLUTION_VOLUME
    assert m.data.solution[0]['solution_viscosity'] == VISCOCITY
    assert m.data.solution[0]['solution_contact_angle'] == CONTACT_ANGLE
    assert m.data.quenching.m_def.name.endswith('AirKnifeGasQuenching')
    assert m.data.quenching['air_knife_angle'] == 45.0 * ureg('°')
    assert m.data.quenching['air_knife_distance_to_thin_film'] == 5000.0 * ureg('um')
    assert m.data.quenching['bead_volume'] == 2.0 * ureg('mm/s')
    assert m.data.quenching['drying_speed'] == 30.0 * ureg('cm/minute')
    assert m.data.quenching['drying_gas_temperature'] == ureg.Quantity(60, ureg('°C'))
    assert m.data.quenching['heat_transfer_coefficient'] == 3.0 * ureg('W/(K*m**2)')
    assert m.data.properties['flow_rate'] == 0.025 * ureg('ml/minute')
    assert m.data.properties['slot_die_head_distance_to_thinfilm'] == 0.3 * ureg('mm')
    assert m.data.properties['slot_die_head_speed'] == 15.0 * ureg('mm/s')


def check_inkjet(m):
    assert m.data.name.startswith('inkjet printing')
    assert m.data.description == NOTES
    assert m.data.location == TOOL_NAME
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.layer[0]['layer_type'] == LAYER_TYPE
    assert m.data.layer[0]['layer_material_name'] == MATERIAL_NAME
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_morphology'] == MORPHOLOGY
    assert m.data.solution[0]['solution_viscosity'] == VISCOCITY
    assert m.data.solution[0]['solution_contact_angle'] == CONTACT_ANGLE
    assert m.data.annealing['temperature'] == ureg.Quantity(120, ureg('°C'))
    assert m.data.annealing['time'] == 1800.0 * ureg('s')
    assert m.data.annealing['atmosphere'] == 'N2'
    assert m.data.properties['drop_density'] == 400.0 * ureg('1/in')
    assert m.data.properties['substrate_temperature'] == ureg.Quantity(40, ureg('°C'))
    assert m.data.properties['cartridge_pressure'] == 300.0 * ureg('mbar')
    assert m.data.properties['printed_area'] == 100.0 * ureg('mm**2')
    assert m.data.properties['print_head_properties']['print_head_name'] == 'Spectra 0.8uL'
    assert m.data.properties['print_head_properties']['print_head_temperature'] == ureg.Quantity(
        35, ureg('°C')
    )
    assert m.data.properties['print_head_properties']['print_nozzle_drop_volume'] == 10.0 * ureg('pl')
    assert m.data.properties['print_head_properties']['print_nozzle_drop_frequency'] == 5000.0 * ureg('1/s')
    assert m.data.properties['print_head_properties']['number_of_active_print_nozzles'] == 128
    assert m.data.print_head_path['quality_factor'] == '3'
    assert m.data.print_head_path['step_size'] == '10'


def check_evap_org(m):
    if not getattr(m.data, 'organic_evaporation', None) or len(m.data.organic_evaporation) == 0:
        return
    assert m.data.name == 'evaporation C'
    assert m.data.description == 'Processability'
    assert m.data.location == TOOL_NAME
    assert m.data.positon_in_experimental_plan == 10.0
    assert m.data.co_evaporation is False
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.layer[0]['layer_type'] == 'Carbon Paste Layer'
    assert m.data.layer[0]['layer_material_name'] == 'C'
    assert m.data.layer[0]['layer_thickness'] == 25.0 * ureg('nm')
    assert m.data.layer[0]['drying_time'] == 90.0 * ureg('s')
    org = m.data.organic_evaporation[0]
    assert org['pressure'].to('mbar').magnitude == pytest.approx(0.001)
    assert str(org['pressure'].units) == 'millibar'
    assert org['pressure_start'].to('mbar').magnitude == pytest.approx(0.005)
    assert str(org['pressure_start'].units) == 'millibar'
    assert org['pressure_end'].to('mbar').magnitude == pytest.approx(0.003)
    assert str(org['pressure_end'].units) == 'millibar'
    assert org['start_rate'].to('angstrom/s').magnitude == pytest.approx(0.5)
    assert str(org['start_rate'].units) == 'angstrom / second'
    assert org['target_rate'].to('angstrom/s').magnitude == pytest.approx(1.0)
    assert str(org['target_rate'].units) == 'angstrom / second'
    assert org['substrate_temparature'] == ureg.Quantity(25, ureg('°C'))
    assert org['tooling_factor'] == '1.5'
    assert org['temparature'][0] == ureg.Quantity(150, ureg('°C'))
    assert org['temparature'][1] == ureg.Quantity(160, ureg('°C'))
    assert org['chemical_2']['name'] == 'C'


def check_evap_inorg(m):
    if not getattr(m.data, 'inorganic_evaporation', None) or len(m.data.inorganic_evaporation) == 0:
        return
    assert m.data.name == 'evaporation C'
    assert m.data.description == 'Processability'
    assert m.data.location == TOOL_NAME
    assert m.data.positon_in_experimental_plan == 10.0
    assert m.data.co_evaporation is False
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.layer[0]['layer_type'] == 'Carbon Paste Layer'
    assert m.data.layer[0]['layer_material_name'] == 'C'
    assert m.data.layer[0]['layer_thickness'] == 25.0 * ureg('nm')

    inorg = m.data.inorganic_evaporation[0]
    assert inorg['pressure'].to('mbar').magnitude == pytest.approx(0.001)
    assert str(inorg['pressure'].units) == 'millibar'
    assert inorg['pressure_start'].to('mbar').magnitude == pytest.approx(0.005)
    assert str(inorg['pressure_start'].units) == 'millibar'
    assert inorg['pressure_end'].to('mbar').magnitude == pytest.approx(0.003)
    assert str(inorg['pressure_end'].units) == 'millibar'
    assert inorg['start_rate'].to('angstrom/s').magnitude == pytest.approx(0.5)
    assert str(inorg['start_rate'].units) == 'angstrom / second'
    assert inorg['target_rate'].to('angstrom/s').magnitude == pytest.approx(1.0)
    assert str(inorg['target_rate'].units) == 'angstrom / second'
    assert inorg['substrate_temparature'] == ureg.Quantity(25, ureg('°C'))
    assert inorg['tooling_factor'] == '1.5'
    assert inorg['temparature'][0] == ureg.Quantity(150, ureg('°C'))
    assert inorg['temparature'][1] == ureg.Quantity(160, ureg('°C'))
    assert inorg['chemical_2']['name'] == 'C'


def check_sputter(m):
    assert m.data.name.startswith('sputtering')
    assert m.data.description == 'Test Sputtering'
    assert m.data.location == TOOL_NAME
    assert m.data.positon_in_experimental_plan == 11.0
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.layer[0]['layer_type'] == LAYER_TYPE
    assert m.data.layer[0]['layer_material_name'] == MATERIAL_NAME
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_transmission'] == 95.0
    assert m.data.layer[0]['layer_morphology'] == MORPHOLOGY
    proc = m.data.processes[0]
    assert proc['pressure'] == 0.01 * ureg('mbar')
    assert proc['temperature'] == ureg.Quantity(200, ureg('°C'))
    assert proc['burn_in_time'] == 60.0 * ureg('s')
    assert proc['deposition_time'] == 300.0 * ureg('s')
    assert proc['power'] == 150.0 * ureg('W')
    assert proc['gas_flow_rate'] == 20.0 * ureg('cm**3/minute')
    assert proc['rotation_rate'] == 30.0 * ureg('rpm')
    assert proc['target_2']['name'] == MATERIAL_NAME
    assert proc['gas_2']['name'] == 'Argon'


def check_ald(m):
    assert m.data.name.startswith('atomic layer deposition')
    assert m.data.location == TOOL_NAME
    assert m.data.positon_in_experimental_plan == 12.0
    assert m.data.atmosphere['temperature'] == ROOM_TEMP
    assert m.data.atmosphere['relative_humidity'] == ROOM_HUM
    assert m.data.atmosphere['start_oxygen_level_ppm'] == O2_LEVEL
    assert m.data.layer[0]['layer_type'] == LAYER_TYPE
    assert m.data.layer[0]['layer_material_name'] == MATERIAL_NAME
    assert m.data.layer[0]['layer_thickness'] == LAYER_THICKNESS
    assert m.data.layer[0]['layer_transmission'] == 95.0
    assert m.data.layer[0]['layer_morphology'] == MORPHOLOGY
    props = m.data.properties
    assert props['source'] == 'TMA'
    assert props['temperature'] == ureg.Quantity(150, ureg('°C'))
    assert props['rate'] == 0.1 * ureg('angstrom/s')
    assert props['time'] == 1800.0 * ureg('s')
    assert props['number_of_cycles'] == 250
    assert props['material']['pulse_duration'] == 0.2 * ureg('s')
    assert props['material']['manifold_temperature'] == ureg.Quantity(80, ureg('°C'))
    assert props['material']['bottle_temperature'] == ureg.Quantity(25, ureg('°C'))
    assert props['material']['material']['name'] == 'TMA'
    assert props['oxidizer_reducer']['pulse_duration'] == 0.1 * ureg('s')
    assert props['oxidizer_reducer']['manifold_temperature'] == ureg.Quantity(70, ureg('°C'))
    assert props['oxidizer_reducer']['material']['name'] == 'H2O'


def check_generic_process(m):
    assert m.data.name == 'Test Generic Process'
    assert m.data.description == 'This is a test generic process'
    assert m.data.positon_in_experimental_plan == 13.0
    assert len(m.data.samples) == 2
    assert m.data.samples[0].lab_id == 'SAU_GeSo_1_1_C-1'
    assert m.data.samples[1].lab_id == 'SAU_GeSo_1_1_C-2'
