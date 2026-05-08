from typing import Annotated
from fastapi import Depends
from poseidon.vessel_manager import VesselManager

_vessel_manager: VesselManager | None = None

def get_vessel_manager() -> VesselManager:
    """Dependency provider for the VesselManager."""
    if _vessel_manager is None:
        msg = "VesselManager not initialised"
        raise RuntimeError(msg)
    return _vessel_manager

VesselManagerDep = Annotated[VesselManager, Depends(get_vessel_manager)]