import os

from nomad.client import parse
from nomad.units import ureg
from utils import delete_json


def test_product_mapping_chemical_ids(monkeypatch):
    """Test that chemical IDs are correctly mapped to product information from the second Excel sheet."""
    
    # Setup monkeypatch to avoid external dependencies
    def mockreturn_search(*args, upload_id=None):
        return None

    monkeypatch.setattr(
        'nomad_tfsc_general.parsers.tfsc_general_measurement_parser.set_sample_reference',
        mockreturn_search,
    )

    monkeypatch.setattr(
        'nomad_tfsc_general.schema_packages.tfsc_general_package.set_sample_reference',
        mockreturn_search,
    )

    monkeypatch.setattr(
        'nomad_tfsc_general.parsers.tfsc_general_measurement_parser.update_general_process_entries',
        mockreturn_search,
    )
    
    # Parse the Excel file
    file_name = os.path.join('tests', 'data', 'product_mapping_test.xlsx')
    parse(file_name)[0]
    
    # Find the screen printing process archive
    measurement_archives = []
    for fname in os.listdir(os.path.join('tests/data')):
        if not fname.endswith('.archive.json'):
            continue
        if 'screen_printing' in fname:
            measurement_path = os.path.join('tests', 'data', fname)
            measurement_archive = parse(measurement_path)[0]
            measurement_archives.append(measurement_archive)
    
    # Use the first screen printing archive found
    assert len(measurement_archives) > 0, "No screen printing archive found"
    measurement_archive = measurement_archives[0]
    
    # Test Layer Chemical ID mapping (Layer1ID)
    assert len(measurement_archive.data.layer) > 0
    layer = measurement_archive.data.layer[0]
    
    assert layer.layer_chemical_id == "Layer1ID"
    assert hasattr(layer, 'product_info')
    
    layer_product_info = layer.product_info
    assert layer_product_info.product_number == "L1"
    assert layer_product_info.lot_number == "LOT1" 
    assert layer_product_info.product_volume == 50.0 * ureg('ml')
    assert layer_product_info.supplier == "InkCompany"
    assert layer_product_info.product_description == "Ink used directly for deposition"
    assert layer_product_info.cost == 30.0
    
    # Test Solution Chemical IDs mapping
    assert len(measurement_archive.data.solution) > 0
    solution = measurement_archive.data.solution[0]
    assert hasattr(solution, 'solution_details')
    
    # Test Solute Chemical ID mapping (Sol1)
    assert len(solution.solution_details.solute) > 0
    solute = solution.solution_details.solute[0]
    
    assert solute.chemical_id == "Sol1"
    assert hasattr(solute.chemical_2, 'product_info')
    
    solute_product_info = solute.chemical_2.product_info
    assert solute_product_info.lot_number == "SFK42EA"
    assert solute_product_info.product_volume == 230.0 * ureg('ml')
    assert solute_product_info.supplier == "Solaveni"
    assert solute_product_info.product_description == "PbI2 from PbSO4"
    assert solute_product_info.cost == 5.0
    
    # Test Additive Chemical ID mapping (Ava2)
    assert len(solution.solution_details.additive) > 0
    additive = solution.solution_details.additive[0]
    
    assert additive.chemical_id == "Ava2"
    assert hasattr(additive.chemical_2, 'product_info')
    
    additive_product_info = additive.chemical_2.product_info
    assert additive_product_info.product_number == "N-31"
    assert additive_product_info.product_volume == 10.0 * ureg('ml')
    assert additive_product_info.supplier == "Avantama"
    assert additive_product_info.product_description == "2.5wt% SnO2 in mixture of Butanols"
    assert additive_product_info.cost == 10.0
    
    # Test Solvent Chemical ID mapping (Od5)
    assert len(solution.solution_details.solvent) > 0
    solvent = solution.solution_details.solvent[0]
    
    assert solvent.chemical_id == "Od5"
    assert hasattr(solvent.chemical_2, 'product_info')
    
    solvent_product_info = solvent.chemical_2.product_info
    assert solvent_product_info.product_weight == 0.5 * ureg('gram')
    assert solvent_product_info.supplier == "ODTU"
    assert solvent_product_info.product_description == "Large ammonium cations"
    assert solvent_product_info.cost == 20.0
    
    # Cleanup
    delete_json()


def test_evaporation_product_mapping(monkeypatch):
    """Test that evaporation process chemical IDs are correctly mapped to product information."""
    
    # Setup monkeypatch to avoid external dependencies
    def mockreturn_search(*args, upload_id=None):
        return None

    monkeypatch.setattr(
        'nomad_tfsc_general.parsers.tfsc_general_measurement_parser.set_sample_reference',
        mockreturn_search,
    )

    monkeypatch.setattr(
        'nomad_tfsc_general.schema_packages.tfsc_general_package.set_sample_reference',
        mockreturn_search,
    )

    monkeypatch.setattr(
        'nomad_tfsc_general.parsers.tfsc_general_measurement_parser.update_general_process_entries',
        mockreturn_search,
    )
    
    # Parse the Excel file
    file_name = os.path.join('tests', 'data', 'product_mapping_test.xlsx')
    parse(file_name)[0]
    
    # Find the evaporation process archive
    measurement_archives = []
    for fname in os.listdir(os.path.join('tests/data')):
        if not fname.endswith('.archive.json'):
            continue
        if 'evaporation' in fname:
            measurement_path = os.path.join('tests', 'data', fname)
            measurement_archive = parse(measurement_path)[0]
            measurement_archives.append(measurement_archive)
    
    # Use the first evaporation archive found
    assert len(measurement_archives) > 0, "No evaporation archive found"
    measurement_archive = measurement_archives[0]
    
    # Test Carbon Layer Chemical ID mapping (Car5)
    assert len(measurement_archive.data.layer) > 0
    layer = measurement_archive.data.layer[0]
    
    assert layer.layer_chemical_id == "Car5"
    assert hasattr(layer, 'product_info')
    
    layer_product_info = layer.product_info
    assert layer_product_info.lot_number == "90"
    assert layer_product_info.product_weight == 10.0 * ureg('gram')
    assert layer_product_info.supplier == "CB"
    assert layer_product_info.product_description == "Carbon Paste"
    assert layer_product_info.cost == 1.0
    
    # Cleanup
    delete_json()
