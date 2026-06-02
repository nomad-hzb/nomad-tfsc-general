from nomad.client import normalize_all
from utils import delete_json, get_archive


def test_jv_parser_hereon(monkeypatch):
    file = 'testt 205 J-V Data.jv.csv'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)
    assert archive.data
    assert 'jvm' in str(archive.data.m_def).lower()
    assert round(archive.data.jv_curve[3].voltage[0].magnitude, 3) == 1.398
    assert round(archive.data.jv_curve[3].efficiency, 7) == 0.0000024
    assert round(archive.data.jv_curve[3].fill_factor, 2) == 0.25
    assert round(archive.data.jv_curve[3].current_density[0].magnitude, 5) == 0.00011
    assert len(archive.data.jv_curve[3].voltage) == 19
    delete_json()


def test_jv_parser_loc_1(monkeypatch):
    file = 'PERS_1_1_C-2.jv.IV'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)
    assert archive.data
    assert 'jvm' in str(archive.data.m_def).lower()
    # Check that JV curves are parsed
    assert archive.data.jv_curve
    assert len(archive.data.jv_curve) > 0
    # Check voltage and current density data
    assert archive.data.active_area.magnitude == 0.0895
    assert archive.data.intensity.magnitude == 100
    assert round(archive.data.jv_curve[3].voltage[0].magnitude, 5) == -0.1002
    assert round(archive.data.jv_curve[3].current_density[0].magnitude, 5) == 18.50302
    assert round(archive.data.jv_curve[3].fill_factor, 2) == 0.41
    assert archive.data.jv_curve[3].efficiency == 8.3
    assert round(archive.data.jv_curve[3].potential_at_maximum_power_point.magnitude, 5) == 1.08677
    assert len(archive.data.jv_curve[3].voltage) == 66
    delete_json()


def test_jv_parser_loc_2(monkeypatch):
    file = 'PERS_1_1_C-1.jv.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)
    assert archive.data
    assert 'jvm' in str(archive.data.m_def).lower()
    # # Check that JV curves are parsed
    assert archive.data.jv_curve
    assert len(archive.data.jv_curve) > 0
    # Check voltage and current density data
    assert archive.data.active_area.magnitude == 0.15
    assert archive.data.intensity.magnitude == 100
    assert round(archive.data.jv_curve[3].voltage[0].magnitude, 5) == -0.2
    assert round(archive.data.jv_curve[3].current_density[0].magnitude, 5) == 6.31333
    assert round(archive.data.jv_curve[3].fill_factor, 4) == 0.6277
    assert archive.data.jv_curve[3].efficiency == 13.0256
    assert round(archive.data.jv_curve[3].potential_at_maximum_power_point.magnitude, 5) == 0.84
    assert len(archive.data.jv_curve[3].voltage) == 141
    delete_json()


def test_jv_parser_loc_2_format_2(monkeypatch):
    file = 'PERS_1_1_C-3.jv.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)
    assert archive.data
    assert archive.data.name == 'PERS_1_1_C-3 jv'
    assert archive.data.active_area.magnitude == 0.25
    assert archive.data.datetime.isoformat() == '2025-06-27T13:13:00+00:00'
    assert archive.data.jv_curve
    assert len(archive.data.jv_curve) > 0
    assert archive.data.jv_curve[-1].cell_name == '12_3_f_loc2_reverse.txt'
    assert round(archive.data.jv_curve[3].potential_at_maximum_power_point.magnitude, 5) == 0.59
    assert round(archive.data.jv_curve[3].current_density_at_maximun_power_point.magnitude, 5) == 10.56
    assert round(archive.data.jv_curve[3].voltage[0].magnitude, 5) == 1.2
    assert round(archive.data.jv_curve[3].current_density[0].magnitude, 5) == 50.744
    delete_json()
