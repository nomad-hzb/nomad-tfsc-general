import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg
from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'lamination_test.xlsx',
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
TOOL_NAME = 'Laminator1'
NOTES = 'Lamination notes'
LAM_TEMP = ureg.Quantity(150, ureg('°C'))
LAM_TIME = 300 * ureg('s')
LAM_PRESSURE = 0.5 * ureg('MPa')
LAM_FORCE = 500 * ureg('N')
LAM_AREA = 100 * ureg('mm**2')
LAM_HEAT_UP_TIME = 60 * ureg('s')
LAM_COOL_DOWN_TIME = 120 * ureg('s')
STAMP_MATERIAL = 'EVA'
STAMP_THICKNESS = 0.5 * ureg('mm')
STAMP_AREA = 100 * ureg('mm**2')


def test_lamination_parser(monkeypatch):
    file = 'lamination_test.xlsx'
    file_name = os.path.join('tests', 'data', file)
    file_archive = parse(file_name)[0]
    assert len(file_archive.data.processed_archive) == N_PROCESSED_ARCHIVES

    # Collect all generated archive JSONs and find the lamination one
    measurement_archives = []
    for fname in os.listdir(os.path.join('tests', 'data')):
        if 'archive.json' not in fname:
            continue
        measurement_archives.append(parse(os.path.join('tests', 'data', fname))[0])

    lam_archives = [m for m in measurement_archives if getattr(m.data, 'name', '').lower() == 'lamination']
    assert len(lam_archives) == 1
    m = lam_archives[0]

    assert m.data.name == 'Lamination'
    assert m.data.description == NOTES
    assert m.data.location == TOOL_NAME
    assert m.data.positon_in_experimental_plan == 1.0
    assert m.data.settings['temperature'] == LAM_TEMP
    assert m.data.settings['time'] == LAM_TIME
    assert m.data.settings['pressure'] == LAM_PRESSURE
    assert m.data.settings['force'] == LAM_FORCE
    assert m.data.settings['area'] == LAM_AREA
    assert m.data.settings['heat_up_time'] == LAM_HEAT_UP_TIME
    assert m.data.settings['cool_down_time'] == LAM_COOL_DOWN_TIME
    assert m.data.settings['stamp_material'] == STAMP_MATERIAL
    assert m.data.settings['stamp_thickness'] == STAMP_THICKNESS
    assert m.data.settings['stamp_area'] == STAMP_AREA

    delete_json()
