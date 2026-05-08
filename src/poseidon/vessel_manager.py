import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

from poseidon.vessel import VesselInfo, VesselReading
from poseidon.models import IngestRequest, IngestResponse, StatusResponse
from poseidon.config_loader import parse_point
from poseidon.data_cleaning import DataCleaner
import poseidon.persistence as persistence

logger = logging.getLogger(__name__)

class UnauthorizedVesselError(Exception):
    """Raised when an unknown vessel_id attempts to submit telemetry."""
    pass

class InvalidReportError(Exception):
    """Raised when telemetry data fails logical validation."""
    pass


class VesselManager:
    def __init__(self, config_path: str | Path, vessels_path: str | Path):
        self.uptime_start = datetime.now(timezone.utc)
        self.total_reports = 0
        self.vessels: dict[str, VesselInfo] = {}
        
        with open(config_path, encoding="utf-8") as f:
            self.config = json.load(f)
            
        with open(vessels_path, encoding="utf-8") as f:
            vessels_data = json.load(f)
            for v in vessels_data:
                try:
                    lon, lat = parse_point(v["location"])
                    self.vessels[v["id"]] = VesselInfo(
                        id=v["id"],
                        location=v["location"],
                        longitude=lon,
                        latitude=lat,
                        metadata=v["metadata"],
                        last_reading=None,
                        last_update=None
                    )
                except ValueError as e:
                    logger.error(f"Skipping vessel {v['id']}: {e}")

        hist_file = self.config.get("historical_data_file", "data/historical_readings.csv")
        raw_df = persistence.load_historical_csv(hist_file)
        if not raw_df.empty:
            self.historical_df = DataCleaner.clean_historical_batch(raw_df)
            logger.info(f"Loaded {len(self.historical_df)} clean historical rows.")
        else:
            self.historical_df = pd.DataFrame()
            
        self.storage_file = self.config.get("storage_file", "data/readings.json")
        past_readings = persistence.load_json_state(self.storage_file)
        
        for r in past_readings:
            v_id = r["vessel_id"]
            if v_id in self.vessels:
                self.vessels[v_id].last_reading = r["readings"]
                self.vessels[v_id].last_update = datetime.fromisoformat(r["timestamp"])
                self.total_reports += 1

    @classmethod
    def for_tests(cls, tmp_path: Path):
        """
        Factory method to instantiate a test-safe VesselManager 
        pointing to temporary files instead of the real filesystem.
        """
        config_path = tmp_path / "test_config.json"
        vessels_path = tmp_path / "test_vessels.json"
        
        config_data = {
            "storage_file": str(tmp_path / "test_readings.json"),
            "historical_data_file": str(tmp_path / "test_history.csv"),
            "thresholds": {"speed_safe": 10.0, "speed_moderate": 15.0, "speed_danger": 22.0}
        }
        
        vessels_data = [{
            "id": "vessel_test_001",
            "location": "POINT(10.0 50.0)",
            "metadata": {"flag_state": "Germany", "home_port": "Test Port"}
        }]
        
        with open(config_path, "w") as f: json.dump(config_data, f)
        with open(vessels_path, "w") as f: json.dump(vessels_data, f)
        
        dummy_data = pd.DataFrame({
            "vessel_id": ["vessel_test_001"],
            "timestamp": ["2025-01-01T12:00:00Z"],
            "speed_knots": [12.5],
            "draft_m": [8.0],
            "heading_deg": [180.0],
            "fuel_rate_lph": [250.0],
            "position": ["POINT(10.0 50.0)"]
        })
        dummy_data.to_csv(config_data["historical_data_file"], index=False)
        
        return cls(config_path, vessels_path)

    def ingest_reading(self, request: IngestRequest) -> IngestResponse:
        """Processes incoming telemetry, validates, persists, and updates state."""
        # 1. Security Authorization
        if request.vessel_id not in self.vessels:
            raise UnauthorizedVesselError(f"Vessel {request.vessel_id} not in whitelist.")
            
        # 2. Business Logic Validation
        is_valid, errors = DataCleaner.validate_report(request.readings)
        if not is_valid:
            raise InvalidReportError(f"Invalid telemetry: {', '.join(errors)}")
            
        timestamp = datetime.now(timezone.utc)
        
        # 3. Create Domain Model (Clean Architecture separation)
        reading = VesselReading(request.vessel_id, request.readings, timestamp)
        
        # 4. Persist Data
        persistence.append_json_state(self.storage_file, reading.to_dict())
        
        # 5. Update State Machine
        v_info = self.vessels[request.vessel_id]
        v_info.last_reading = request.readings
        v_info.last_update = timestamp
        self.total_reports += 1
        
        return IngestResponse(
            status="success",
            message="Telemetry recorded securely",
            vessel_id=request.vessel_id,
            timestamp=timestamp
        )

    def get_status(self) -> StatusResponse:
        """Compiles health metrics for the /status endpoint."""
        active_vessels = sum(1 for v in self.vessels.values() if v.last_update is not None)
        uptime = (datetime.now(timezone.utc) - self.uptime_start).total_seconds()
        
        # Safely find the latest update across the fleet
        latest_update = max(
            (v.last_update for v in self.vessels.values() if v.last_update is not None),
            default=None
        )
        
        status_flag = "healthy" if active_vessels > 0 else "degraded"
        
        return StatusResponse(
            status=status_flag,
            uptime_seconds=round(uptime, 2),
            active_vessels=active_vessels,
            total_reports=self.total_reports,
            last_update=latest_update
        )