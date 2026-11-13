import os

import pytest
from nomad.client import normalize_all, parse
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
    # 1 batch, 1 subbatch, 3 substrates (module columns are part of the substrate key), 3 samples
    assert len(file_archive.data.processed_archive) == 8

    # collect all archives
    measurement_archives = []
    for fname in os.listdir(os.path.join('tests', 'data')):
        if 'archive.json' not in fname:
            continue
        measurement_archives.append(parse(os.path.join('tests', 'data', fname))[0])
    for m in measurement_archives:
        normalize_all(m)

    # find substrate archives
    sub_archives = [
        s for s in measurement_archives if getattr(s.data, 'substrate_dimension', '') == '1 cm x 1 cm'
    ]
    assert len(sub_archives) == 3
    normalize_all(sub_archives[0])
    s = sub_archives[0]
    assert s.data.pixel_area == 0.16 * ureg('cm**2')
    assert s.data.number_of_pixels == 6

    # find sample archives where module info is
    mod_archives = {m.data.lab_id: m for m in measurement_archives if hasattr(m.data, 'module_configuration')}
    assert len(mod_archives) == 3
    for m in mod_archives.values():
        m.data.substrate = s.data
        normalize_all(m)
        assert m.data.module_configuration.is_module
        assert m.data.module_configuration.pixel_connection == 'parallel'
        assert (
            m.results.properties.optoelectronic.solar_cell.device_area
            == m.data.module_configuration.module_active_area
        )

    # C-1: active area, dead area and fill factor entered; only aperture area is derived
    module = mod_archives['PERS_Project_1_1_C-1'].data.module_configuration
    assert module.module_active_area == 0.9 * ureg('cm**2')
    assert module.module_dead_area == 0.1 * ureg('cm**2')
    assert module.module_geometrical_fill_factor == 0.9
    assert module.module_aperture_area == 1 * ureg('cm**2')

    # C-2: fill factor empty -> aperture = active + dead, fill factor = active / aperture
    module = mod_archives['PERS_Project_1_1_C-2'].data.module_configuration
    assert module.module_active_area == 5.0 * ureg('cm**2')
    assert module.module_dead_area == 0.5 * ureg('cm**2')
    assert module.module_aperture_area == 5.5 * ureg('cm**2')
    assert module.module_geometrical_fill_factor == pytest.approx(5.0 / 5.5)

    # C-3: dead area empty -> aperture = active / fill factor, dead = aperture - active
    module = mod_archives['PERS_Project_1_1_C-3'].data.module_configuration
    assert module.module_active_area == 5.0 * ureg('cm**2')
    assert module.module_geometrical_fill_factor == 0.8
    assert module.module_aperture_area == 6.25 * ureg('cm**2')
    assert module.module_dead_area == 1.25 * ureg('cm**2')
    delete_json()
