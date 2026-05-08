import pytest
from poseidon.vessel_manager import VesselManager, UnauthorizedVesselError, InvalidReportError
from poseidon.models import IngestRequest

def test_manager_initializes_with_test_data(test_manager: VesselManager):
    assert "vessel_test_001" in test_manager.vessels
    assert test_manager.vessels["vessel_test_001"].metadata["flag_state"] == "Germany"

def test_ingest_updates_state(test_manager: VesselManager):
    req = IngestRequest(
        vessel_id="vessel_test_001",
        readings={"speed_knots": 15.0, "draft_m": 9.0, "heading_deg": 45.0, "fuel_rate_lph": 200.0}
    )
    
    test_manager.ingest_reading(req)
    
    vessel = test_manager.vessels["vessel_test_001"]
    assert vessel.last_reading["speed_knots"] == 15.0
    assert vessel.last_update is not None
    assert test_manager.total_reports == 1

def test_logical_validation_raises_domain_error(test_manager: VesselManager):
    req = IngestRequest(
        vessel_id="vessel_test_001",
        readings={"speed_knots": -5.0} # Negative speed is physically impossible
    )
    
    with pytest.raises(InvalidReportError):
        test_manager.ingest_reading(req)