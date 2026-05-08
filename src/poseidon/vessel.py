from datetime import datetime
from dataclasses import dataclass


class VesselReading:
    """Raw telemetry report. Stored as-is, validated only by pandas later."""
    def __init__(
        self,
        vessel_id: str,
        readings: dict[str, float],
        timestamp: datetime,
    ) -> None:
        self.vessel_id = vessel_id
        self.readings = readings
        self.timestamp = timestamp

    def to_dict(self) -> dict[str, object]:
        return {
            "vessel_id": self.vessel_id,
            "readings": self.readings,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class VesselInfo:
    """Static vessel metadata + last known state."""
    id: str
    location: str            # original WKT POINT string
    longitude: float
    latitude: float
    metadata: dict[str, str]
    last_reading: dict[str, float] | None
    last_update: datetime | None