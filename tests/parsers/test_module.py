import os

import pytest
from nomad.client import normalize_all, parse, normalize
from nomad.units import ureg
from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'module_test.xlsx',
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

def test_module(monkeypatch):
    file = 'module_test.xlsx'

    file_name = os.path.join('tests', 'data', file)
    file_archive = parse(file_name)[0]
    assert len(file_archive.data.processed_archive) == 4

    # collect all archives
    measurement_archives = []
    for fname in os.listdir(os.path.join('tests','data')):
        if 'archive.json' not in fname:
            continue
        measurement_archives.append(parse(os.path.join('tests', 'data', fname))[0])
    for m in measurement_archives:
        normalize_all(m)

    # find substrate archives
    sub_archives = [s for s in measurement_archives if getattr(s.data,'substrate_dimension','') == "1 cm x 1 cm"]
    assert len(sub_archives) == 1
    normalize_all(sub_archives[0])
    print(sub_archives[0])
    s = sub_archives[0]
    assert s.data.active_area == 0.9 * ureg('cm**2')
    assert s.data.dead_area == 0.1 * ureg('cm**2')
    assert s.data.geometrical_fill_factor == 0.9

    # find sample archives where module info is
    mod_archives = [m for m in measurement_archives if hasattr(m.data, 'module_configuration')]
    assert len(mod_archives) == 1
    normalize_all(mod_archives[0])
    print(mod_archives[0])
    m = mod_archives[0]
    assert m.data.module_configuration.is_module 
    assert m.data.module_configuration.pixel_connection == 'parallel'
    assert m.data.module_configuration.module_active_area == 5.4 * ureg('cm**2')