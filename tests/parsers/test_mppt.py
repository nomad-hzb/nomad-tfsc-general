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
    assert len(archive.data.time)== 39
    assert len(archive.data.time) == len(archive.data.power_density)
    assert len(archive.data.voltage) == len(archive.data.current_density)
    # Check specific curve values
    assert round(archive.data.time[-1],5) == 121.48237 * ureg('s')
    assert round(archive.data.power_density[5], 5) == 11.26418 * ureg('mW/cm^2')
    assert round(archive.data.current_density[5], 5) == 15.86504 * ureg('mA/cm^2')
    assert round(archive.data.voltage[-1], 5) == 0.68000 * ureg('volt')
    assert round(archive.data.properties.perturbation_voltage, 2) == 0.01 * ureg('volt')
    delete_json()


# def test_mppt_parser_loc_2(monkeypatch):
#     file = 'PERS_loc2_mppt.mpp.txt'
#     archive = get_archive(file, monkeypatch)
#     normalize_all(archive)
    
#     # Debug: Check specific measurement attributes
#     print(f"After normalize - Archive data: {archive.data}")
#     print(f"Archive data type: {type(archive.data)}")
#     print(f"Directory: {dir(archive.data)}")
#     print(f"time attribute: {archive.data.time}")
#     print(f"voltage attribute: {archive.data.voltage}")
#     print(f"current_density attribute: {archive.data.current_density}")
#     print(f"power_density attribute: {archive.data.power_density}")
#     print(f"datetime attribute: {getattr(archive.data, 'datetime', 'Not found')}")
    
#     # Check if the file was actually parsed
#     if hasattr(archive.data, 'normalize'):
#         print("Archive data has normalize method - it should have been called")
    
#     delete_json()