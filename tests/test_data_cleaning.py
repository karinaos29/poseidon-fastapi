import pandas as pd
from poseidon.data_cleaning import DataCleaner
from poseidon.config_loader import parse_point
import pytest

def test_wkt_flavour_1_single_parse():
    lon, lat = parse_point("POINT(4.4792 51.9225)")
    assert lon == 4.4792
    assert lat == 51.9225
    
    lon, lat = parse_point("POINT ( -10.5   40.0 ) ") 
    assert lat == 40.0

def test_wkt_flavour_1_out_of_bounds():
    with pytest.raises(ValueError):
        parse_point("POINT(200.0 50.0)") # Invalid Longitude

def test_wkt_flavour_2_vectorized_parse():
    df = pd.DataFrame({"position": ["POINT(1.0 2.0)", "POINT(-5.0 10.5)"]})
    coords = DataCleaner.parse_wkt_column(df["position"])
    
    assert "lon" in coords.columns
    assert "lat" in coords.columns
    assert coords.iloc[1]["lon"] == -5.0

def test_clean_historical_batch():
    raw_data = {
        "vessel_id": ["v1", "v2", "v3", None],
        "timestamp": ["2025-01-01T10:00:00Z", "2025-01-01T11:00:00Z", "2025-01-01T12:00:00Z", "2025-01-01T13:00:00Z"],
        "speed_knots": [10.0, -5.0, 60.0, 10.0], 
        "draft_m": [8.0, 8.0, 8.0, 8.0],
        "heading_deg": [180, 180, 400, 180], 
        "fuel_rate_lph": [200.0, 200.0, 200.0, 200.0]
    }
    df = pd.DataFrame(raw_data)
    
    cleaned = DataCleaner.clean_historical_batch(df)
    
    # Should drop v2 (negative speed), v3 (speed > 50), and the None vessel
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["vessel_id"] == "v1"