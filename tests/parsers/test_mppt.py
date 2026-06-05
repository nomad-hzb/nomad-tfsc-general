from nomad.client import normalize_all
from nomad.units import ureg
from utils import delete_json, get_archive


def test_mppt_parser_loc_1(monkeypatch):
    file = 'PERS_loc1_mppt.MPP'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    assert archive.data
    assert archive.data.datetime.isoformat() == '2025-07-23T15:20:24+00:00'

    # Check that curves are parsed
    assert len(archive.data.time) == 39
    assert len(archive.data.time) == len(archive.data.power_density)
    assert len(archive.data.voltage) == len(archive.data.current_density)
    # Check specific curve values
    assert round(archive.data.time[-1], 5) == 121.48237 * ureg('s')
    assert round(archive.data.power_density[5], 5) == 11.26418 * ureg('mW/cm^2')
    assert round(archive.data.current_density[5], 5) == 15.86504 * ureg('mA/cm^2')
    assert round(archive.data.voltage[-1], 5) == 0.68000 * ureg('volt')
    assert round(archive.data.properties.perturbation_voltage, 2) == 0.01 * ureg('volt')
    delete_json()


def test_mppt_parser_loc_2_debug(monkeypatch):
    file = 'PERS_loc2_mppt_20260204_093607.mpp.txt'

    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    assert archive.data
    assert archive.data.datetime.isoformat() == '2026-02-04T09:36:07+00:00'

    # Check that curves are parsed
    assert len(archive.data.time) == 103
    assert len(archive.data.time) == len(archive.data.power_density)
    assert len(archive.data.voltage) == len(archive.data.current_density)
    # Check specific curve values
    assert round(archive.data.time[-1], 5) == 204.0 * ureg('s')
    assert round(archive.data.power_density[5], 5) == -13.51071 * ureg('mW/cm^2')
    assert round(archive.data.current_density[5], 5) == -15.71013 * ureg('mA/cm^2')
    assert round(archive.data.voltage[-1], 5) == 0.85 * ureg('volt')
    assert round(archive.data.properties.perturbation_voltage, 2) == 0.01 * ureg('volt')

    delete_json()
