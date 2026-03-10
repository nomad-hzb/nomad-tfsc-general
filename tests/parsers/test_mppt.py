from nomad.client import normalize_all
from utils import delete_json, get_archive

# def test_mppt_parser_loc_1(monkeypatch):
#     file = 'PERS_loc1_mppt.MPP'
#     archive = get_archive(file, monkeypatch)
#     normalize_all(archive)

#     delete_json()


def test_mppt_parser_loc_2(monkeypatch):
    file = 'PERS_loc2_mppt.mpp.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)
    assert archive.data
    assert 'mpp' in str(archive.data.m_def).lower()
    #assert archive.data.datetime.isoformat() == '2026-02-04T10:36:00+00:00'
    # Check that curves are parsed
    #assert len(archive.data.time)== 103
    #assert len(archive.data.time) == len(archive.data.power_density)
    assert len(archive.data.voltage) == len(archive.data.current_density)
    #assert archive.data.time[-1] == 204
    # Check specific curve values
    assert round(archive.data.power_density[5].magnitude, 5) == -0.01351
    delete_json()