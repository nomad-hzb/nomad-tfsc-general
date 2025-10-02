from nomad.client import normalize_all
from utils import delete_json, get_archive


def test_jv_parser_hereon(monkeypatch):
    file = 'testt 205 J-V Data.IV.csv'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)
    assert archive.data
    assert 'jvm' in str(archive.data.m_def).lower()
    print(str(archive.data.m_def).lower())
    print(archive.data.jv_curve)
    assert round(archive.data.jv_curve[3].voltage[0].magnitude, 3) == 1.398
    assert round(archive.data.jv_curve[3].efficiency, 7) == 0.0000024
    assert round(archive.data.jv_curve[3].fill_factor, 2) == 0.25
    assert round(archive.data.jv_curve[3].current_density[0].magnitude, 5) == 0.00011
    assert len(archive.data.jv_curve[3].voltage) == 19
    delete_json()
