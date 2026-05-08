import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from poseidon.main import app
from poseidon.dependencies import get_vessel_manager
from poseidon.vessel_manager import VesselManager

@pytest.fixture
def test_manager(tmp_path: Path) -> VesselManager:
    return VesselManager.for_tests(tmp_path)

@pytest.fixture
def client(test_manager: VesselManager):
    app.dependency_overrides[get_vessel_manager] = lambda: test_manager
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()