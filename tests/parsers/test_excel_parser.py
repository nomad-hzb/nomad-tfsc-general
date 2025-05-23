import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg

from utils import delete_json, get_archive
from datetime import datetime, timezone


@pytest.fixture(
    params=[
        'tfsc_test_experiment.xlsx',
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


def test_tfsc_batch_parser(monkeypatch):
    file = 'tfsc_test_experiment.xlsx'
    file_name = os.path.join('tests', 'data', file)
    file_archive = parse(file_name)[0]
    assert len(file_archive.data.processed_archive) == 16

    measurement_archives = []
    for fname in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in fname:
            continue
        measurement = os.path.join('tests', 'data', fname)
        measurement_archives.append(parse(measurement)[0])
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    for m in measurement_archives:
        if 'Sample' in str(type(m.data)):
            assert m.data.description == '1000 rpm'
            assert m.data.number_of_junctions == 1
        elif 'Batch' in str(type(m.data)):
            assert m.data.name == 'SAU_GeSo_1_1'
        elif 'Substrate' in str(type(m.data)):
            assert m.data.solar_cell_area == 0.16 * ureg('cm**2')
            assert m.data.pixel_area == 0.16 * ureg('cm**2')
            assert m.data.number_of_pixels == 6
            assert m.data.description == 'Experiment Notes'
            assert m.data.substrate == 'Soda Lime Glass'
            assert m.data.conducting_material[0] == 'ITO'
            assert m.data.substrate_properties[0]['layer_type'] == 'Substrate Conductive Layer'
            assert m.data.substrate_properties[0]['layer_material_name'] == 'ITO'
            assert m.data.substrate_properties[0]['layer_thickness'] == 150 * ureg('nm')
            assert m.data.substrate_properties[0]['layer_transmission'] == 90
            assert m.data.substrate_properties[0]['layer_sheet_resistance'] == 10 * ureg('ohm')
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 1.0:
            assert 'LaserScribing' in str(type(m.data))
            assert m.data.description == 'Platform:EP3'
            assert m.data.patterning == 'P1,P2,P3, commercially etched'
            assert m.data.layout == 'BBBB, minimodule'
            assert m.data.properties.laser_wavelength == 532 * ureg('nm')
            assert m.data.properties.laser_pulse_time == 8 * ureg('ps')
            assert m.data.properties.laser_pulse_frequency == 80 * ureg('kHz')
            assert m.data.properties.speed == 100 * ureg('mm/s')
            assert m.data.properties.fluence == 0.5 * ureg('J/cm**2')
            assert m.data.properties.power_in_percent == 75
            assert m.data.recipe_file == 'test_scribing_recipe.xml'
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 2.0:
            assert 'Cleaning' in str(type(m.data))
            assert m.data.cleaning[0].solvent_2.name == 'Hellmanex'
            assert m.data.cleaning[0].time == 0.5166666666666666 * ureg('minute')
            assert m.data.cleaning[0].temperature == ureg.Quantity(61, ureg('°C'))
            assert m.data.cleaning[1].solvent_2.name == 'Hellmanex'
            assert m.data.cleaning[1].time == 0.5333333333333333 * ureg('minute')
            assert m.data.cleaning[1].temperature == ureg.Quantity(62, ureg('°C'))
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 3.0:
            assert 'Cleaning' in str(type(m.data))
            assert m.data.cleaning_plasma[0].plasma_type == 'Oxygen'
            assert m.data.cleaning_plasma[0].time == 3 * ureg('minute') # cleaning time is filled in in seconds but class quantity is in minutes
            assert m.data.cleaning_plasma[0].power == 50 * ureg('W')
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 4.0:
            assert 'Cleaning' in str(type(m.data))
            assert m.data.cleaning_uv[0].time == 15 * ureg('minute')
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 5.0:
            assert 'SpinCoating' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Absorber'
            assert m.data.layer[0].layer_material_name == 'Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3'
            assert m.data.annealing.temperature == ureg.Quantity(120, ureg('°C'))
            assert m.data.annealing.time == 1800 * ureg('s')
            assert m.data.solution[0].solution_details.solute[0].chemical_2.name == 'PbI2'
            assert m.data.solution[0].solution_details.solvent[0].chemical_2.name == 'DMF'
            assert m.data.solution[0].solution_details.solvent[0].chemical_volume == 0.01 * ureg('ml')
            assert m.data.solution[0].solution_details.solvent[0].amount_relative == 1.5
            assert m.data.recipe_steps[0].speed == 3001 * ureg('rpm')
            assert m.data.recipe_steps[0].time == 31 * ureg('s')
            assert m.data.recipe_steps[0].acceleration == 1001 * ureg('rpm/s')
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 6.0:
            assert 'SlotDieCoating' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Absorber'
            assert m.data.layer[0].layer_material_name == 'Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3'
            assert m.data.annealing.temperature == ureg.Quantity(120, ureg('°C'))
            assert m.data.annealing.time == 1800 * ureg('s')
            assert m.data.properties.flow_rate == 0.025 * ureg('ml/minute')
            assert m.data.properties.slot_die_head_distance_to_thinfilm == 0.3 * ureg('mm')
            assert m.data.properties.slot_die_head_speed == 15.0 * ureg('mm/s')
            assert m.data.quenching.air_knife_angle == 45.0 * ureg('degree')
            assert m.data.quenching.air_knife_distance_to_thin_film == 5000.0 * ureg('um')
            assert m.data.quenching.bead_volume == 2.0 * ureg('mm/s')
            assert m.data.quenching.drying_speed == 30.0 * ureg('cm/minute')
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 7.0:
            assert 'Inkjet' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Absorber'
            assert m.data.layer[0].layer_material_name == 'Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3'
            assert m.data.atmosphere.temperature == ureg.Quantity(23, ureg('°C'))
            assert m.data.atmosphere.relative_humidity == 45
            assert m.data.atmosphere.oxygen_level_ppm == 10
            assert m.data.properties.drop_density == 400 * ureg('1/in')
            assert m.data.properties.substrate_temperature == ureg.Quantity(40, ureg('°C'))
            assert m.data.properties.cartridge_pressure == 300 * ureg('mbar')
            assert m.data.properties.printed_area == 100 * ureg('mm**2')
            assert m.data.properties.print_head_properties.print_head_name == 'Spectra 0.8uL'
            assert m.data.properties.print_head_properties.print_head_temperature == ureg.Quantity(35, ureg('°C'))
            assert m.data.properties.print_head_properties.print_nozzle_drop_volume == 10 * ureg('pl')
            assert m.data.properties.print_head_properties.print_nozzle_drop_frequency == 5000 * ureg('1/s')
            assert m.data.properties.print_head_properties.number_of_active_print_nozzles == 128
            assert m.data.print_head_path.quality_factor == '3'
            assert m.data.print_head_path.step_size == '10'
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 8.0:
            assert 'Evaporation' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Carbon Paste Layer'
            assert m.data.layer[0].layer_material_name == 'C'
            assert m.data.layer[0].layer_thickness == 25 * ureg('nm')
            assert m.data.layer[0].supplier == 'X_Company/23-001'
            assert m.data.layer[0].batch == '30'
            assert m.data.layer[0].drying_time == 90 * ureg('s')
            assert m.data.layer[0].cost == 50
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 9.0:
            assert 'Evaporation' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Carbon Paste Layer'
            assert m.data.layer[0].layer_material_name == 'C'
            assert m.data.layer[0].layer_thickness == 25 * ureg('nm')
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 10.0:
            assert 'Evaporation' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Carbon Paste Layer'
            assert m.data.layer[0].layer_material_name == 'C'
            assert m.data.layer[0].layer_thickness == 25 * ureg('nm')
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 11.0:
            assert 'Sputtering' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Carbon Paste Layer'
            assert m.data.layer[0].layer_material_name == 'C'
            assert m.data.layer[0].layer_thickness == 25 * ureg('nm')
            assert m.data.processes[0].pressure == 0.01 * ureg('mbar')
            assert m.data.processes[0].temperature == ureg.Quantity(200.0 ,ureg('°C'))
            assert m.data.processes[0].burn_in_time == 60.0 * ureg('s')
            assert m.data.processes[0].deposition_time == 300.0 * ureg('s')
            assert m.data.processes[0].power == 150.0 * ureg('W')
            assert m.data.processes[0].gas_flow_rate == 20.0 * ureg('cm**3/minute')
            assert m.data.processes[0].rotation_rate == 30.0 * ureg('rpm')
            assert m.data.processes[0].target_2.name == 'C'
            assert m.data.processes[0].gas_2.name == 'Argon'
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 12.0:
            assert 'AtomicLayerDeposition' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Carbon Paste Layer'
            assert m.data.layer[0].layer_material_name == 'C'
            assert m.data.layer[0].layer_thickness == 25 * ureg('nm')
            assert m.data.properties.source == 'TMA'
            assert m.data.properties.temperature == ureg.Quantity(150.0, ureg('°C'))
            assert m.data.properties.rate == 0.1 *ureg('angstrom/s')
            assert m.data.properties.time == 1800.0 * ureg('s')
            assert m.data.properties.number_of_cycles == 250
            assert m.data.properties.material.pulse_duration == 0.2 * ureg('s')
            assert m.data.properties.material.manifold_temperature == ureg.Quantity(80.0, ureg('°C'))
            assert m.data.properties.material.bottle_temperature == ureg.Quantity(25.0, ureg('°C'))
            assert m.data.properties.material.material.name == 'TMA'
            assert m.data.properties.oxidizer_reducer.pulse_duration == 0.1 * ureg('s')
            assert m.data.properties.oxidizer_reducer.manifold_temperature == ureg.Quantity(70.0, ureg('°C'))
            assert m.data.properties.oxidizer_reducer.material.name == 'H2O'
        elif getattr(m.data, 'positon_in_experimental_plan', None) == 14.0:
            assert 'Process' in str(type(m.data))
            assert m.data.name == 'Test Generic Process'
            assert m.data.description == 'This is a test generic process'
    delete_json()

