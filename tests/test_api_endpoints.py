from fastapi.testclient import TestClient

def test_welcome_page(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "Project Poseidon API" in response.text

def test_status_endpoint(client: TestClient):
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "active_vessels" in data

def test_successful_ingest(client: TestClient):
    payload = {
        "vessel_id": "vessel_test_001",
        "readings": {"speed_knots": 12.5, "draft_m": 8.0, "heading_deg": 180, "fuel_rate_lph": 250.0}
    }
    response = client.post("/report", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_unauthorized_vessel_is_rejected(client: TestClient):
    payload = {
        "vessel_id": "pirate_ship_999",
        "readings": {"speed_knots": 10.0}
    }
    response = client.post("/report", json=payload)
    assert response.status_code == 403
    assert "not in whitelist" in response.json()["detail"]

def test_pydantic_validation_failure(client: TestClient):
    payload = {
        "vessel_id": "",
        "readings": {"speed_knots": 10.0},
        "captain": "Ahab"
    }
    response = client.post("/report", json=payload)
    assert response.status_code == 422  

def test_visual_endpoints_return_html(client: TestClient):
    assert client.get("/map").status_code == 200
    
    assert client.get("/history/vessel_test_001").status_code == 200
    assert client.get("/history/unknown").status_code == 404
    
    assert client.get("/distribution/2025/2").status_code == 404
    assert client.get("/distribution/2025/1").status_code == 200