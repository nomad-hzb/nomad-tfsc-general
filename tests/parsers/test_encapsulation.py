import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg
from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'encapsulation_test.xlsx',
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
NOTES = 'Encapsulation notes'
DATETIME_ISO = '2025-05-21T14:30:00+00:00'
ENCAPSULATION_METHOD = 'R2R'
SIDES_ENCAPSULATED = 'Both Sides'
ADHESIVE_METHOD = 'Dispensing'
ADHESIVE_NAME = 'EVA'
ADHESIVE_THICKNESS = 450 * ureg('um')
BARRIER_FOIL = 'PET/AlOx'
LAM_AREA = 100 * ureg('mm**2')
LAM_PRESSURE = 50 * ureg('MPa')
LAM_TEMPERATURE = ureg.Quantity(100, ureg('°C'))
CURING_LAMP_DETAILS = 'UV LED array'
CURING_WAVELENGTH = 365 * ureg('nm')
CURING_INTENSITY = 100 * ureg('mW/cm**2')
CURING_EXPOSURE_TIME = 30 * ureg('s')
CURING_DISTANCE = 50 * ureg('mm')
CURING_ATMOSPHERE = 'N2'


def test_encapsulation_parser(monkeypatch):
    file = 'encapsulation_test.xlsx'
    file_name = os.path.join('tests', 'data', file)
    file_archive = parse(file_name)[0]
    assert len(file_archive.data.processed_archive) == N_PROCESSED_ARCHIVES

    measurement_archives = []
    for fname in os.listdir(os.path.join('tests', 'data')):
        if 'archive.json' not in fname:
            continue
        measurement_archives.append(parse(os.path.join('tests', 'data', fname))[0])
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    PROCESS_CHECKS = {
        'pers_project_1': check_batch,
        'pers_project_1_1': check_subbatch,
        'pers_project_1_1_c-1': check_sample,
        'substrate 1 cm x 1 cm soda lime glass ito': check_substrate,
        ('encapsulation', 1.0): check_encapsulation,
    }

    for m in measurement_archives:
        name = getattr(m.data, 'name', None)
        step = getattr(m.data, 'positon_in_experimental_plan', None)
        name_lc = name.lower() if name else ''
        found = False
        for k, func in PROCESS_CHECKS.items():
            if isinstance(k, tuple) and len(k) == 2:
                key_name, key_step = k
                if name_lc.startswith(key_name) and step == key_step:
                    func(m)
                    found = True
                    break
        if not found:
            for k, func in PROCESS_CHECKS.items():
                if isinstance(k, str) and k == name_lc:
                    func(m)
                    found = True
                    break
        if not found:
            print(f'No check function for process: {name} at step {step}')

    delete_json()


def check_batch(m):
    assert m.data.name == 'PERS_Project_1'
    assert m.data.lab_id == 'PERS_Project_1'
    assert len(m.data.entities) == 1
    assert m.data.entities[0].lab_id == 'PERS_Project_1_1_C-1'


def check_subbatch(m):
    assert m.data.name == 'PERS_Project_1_1'
    assert m.data.lab_id == 'PERS_Project_1_1'
    assert len(m.data.entities) == 1
    assert m.data.entities[0].lab_id == 'PERS_Project_1_1_C-1'


def check_sample(m):
    assert m.data.name == 'PERS_Project_1_1_C-1'
    assert m.data.lab_id == 'PERS_Project_1_1_C-1'
    assert m.data.datetime.isoformat() == '2025-05-21T00:00:00+00:00'
    assert m.data.description == '1000 rpm'
    assert m.data.number_of_junctions == 1


def check_substrate(m):
    assert m.data.datetime.isoformat() == '2025-05-21T00:00:00+00:00'
    assert m.data.name == 'Substrate 1 cm x 1 cm Soda Lime Glass ITO'
    assert m.data.pixel_area == 0.16 * ureg('cm**2')
    assert m.data.number_of_pixels == 6.0
    assert m.data.substrate == 'Soda Lime Glass'
    assert m.data.conducting_material == ['ITO']
    assert m.data.substrate_properties[0]['layer_type'] == 'Substrate Conductive Layer'
    assert m.data.substrate_properties[0]['layer_material_name'] == 'ITO'
    assert m.data.substrate_properties[0]['layer_thickness'] == 150.0 * ureg('nm')
    assert m.data.substrate_properties[0]['layer_transmission'] == 90.0
    assert m.data.substrate_properties[0]['layer_sheet_resistance'] == 10.0 * ureg('ohm')


def check_encapsulation(m):
    assert m.data.name == 'Encapsulation'
    assert m.data.description == NOTES
    assert m.data.location == ''
    assert m.data.datetime.isoformat() == DATETIME_ISO
    assert m.data.encapsulation_method == ENCAPSULATION_METHOD
    assert m.data.sides_encapsulated == SIDES_ENCAPSULATED

    # Adhesive application, including the adhesive layer info / product info
    adhesive = m.data.adhesive_application
    assert adhesive.method == ADHESIVE_METHOD
    layer_info = adhesive.adhesive_layer_info
    assert layer_info.layer_material_name == ADHESIVE_NAME
    assert layer_info.layer_thickness.to('um').magnitude == pytest.approx(ADHESIVE_THICKNESS.magnitude)
    adhesive_product_info = layer_info.product_info
    assert adhesive_product_info.product_number is None
    assert adhesive_product_info.lot_number == '123.0'
    assert adhesive_product_info.supplier == 'Pers1'
    assert adhesive_product_info.cost == 1.0

    # Barrier foil lamination, including its product info
    barrier = m.data.barrier_lamination
    assert barrier.barrier_foil == BARRIER_FOIL
    barrier_product_info = barrier.product_info
    assert barrier_product_info.product_number == '456.0'
    assert barrier_product_info.lot_number is None
    assert barrier_product_info.supplier == 'Pers2'
    assert barrier_product_info.cost == 2.0
    assert barrier.area == LAM_AREA
    assert barrier.pressure == LAM_PRESSURE
    assert barrier.temperature == LAM_TEMPERATURE

    # UV curing
    curing = m.data.curing
    assert curing.lamp_details == CURING_LAMP_DETAILS
    assert curing.wavelength == CURING_WAVELENGTH
    assert curing.intensity == CURING_INTENSITY
    assert curing.exposure_time == CURING_EXPOSURE_TIME
    assert curing.distance == CURING_DISTANCE
    assert curing.atmosphere == CURING_ATMOSPHERE
