from contextlib import asynccontextmanager
from typing import Annotated
from pathlib import Path

from fastapi import FastAPI, Path as APIPath, HTTPException, status
from fastapi.responses import HTMLResponse

import poseidon.dependencies as deps
from poseidon.vessel_manager import VesselManager, UnauthorizedVesselError, InvalidReportError
from poseidon.models import IngestRequest, IngestResponse, StatusResponse
from poseidon.data_cleaning import DataCleaner
from poseidon import visualization as viz
from poseidon import temporal_visualization as tviz

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan handler for app startup and shutdown."""
    config_path = Path("config/server_config.json")
    vessels_path = Path("config/vessels.json")
    
    manager = VesselManager(config_path, vessels_path)
    
    deps._vessel_manager = manager
    
    yield  
    
    deps._vessel_manager = None

app = FastAPI(title="Project Poseidon", version="1.0.0", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
def welcome_page():
    """Welcome page with navigation links to endpoints."""
    return """
    <html>
        <head><title>Project Poseidon</title></head>
        <body style="font-family: sans-serif; padding: 2rem;">
            <h1>⚓ Project Poseidon API</h1>
            <ul>
                <li><a href="/docs">Swagger API Documentation</a></li>
                <li><a href="/status">System Status (JSON)</a></li>
                <li><a href="/map">Real-Time Fleet Map</a></li>
                <li><a href="/distribution/2025/2">Sample Distribution (Feb 2025)</a></li>
            </ul>
        </body>
    </html>
    """

@app.post("/report", response_model=IngestResponse)
def report(request: IngestRequest, manager: deps.VesselManagerDep) -> IngestResponse:
    try:
        return manager.ingest_reading(request)
    except UnauthorizedVesselError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidReportError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/status", response_model=StatusResponse)
def status_endpoint(manager: deps.VesselManagerDep) -> StatusResponse:
    return manager.get_status()

@app.get("/map", response_class=HTMLResponse)
def get_map(manager: deps.VesselManagerDep):
    fig = viz.create_realtime_map(manager.vessels, manager.config)
    return fig.to_html(include_plotlyjs="cdn", full_html=True)

@app.get("/history/{vessel_id}", response_class=HTMLResponse)
def get_history(
    vessel_id: Annotated[str, APIPath(min_length=1)],
    manager: deps.VesselManagerDep
):
    if vessel_id not in manager.vessels:
        raise HTTPException(status_code=404, detail="Vessel ID not recognized.")
        
    vessel_data = manager.historical_df[manager.historical_df["vessel_id"] == vessel_id]
    if vessel_data.empty:
        raise HTTPException(status_code=404, detail="No historical data found for vessel.")
        
    fig = tviz.create_time_series(vessel_data, vessel_id)
    return fig.to_html(include_plotlyjs="cdn", full_html=True)

@app.get("/distribution/{year}/{month}", response_class=HTMLResponse)
def get_distribution(
    year: Annotated[int, APIPath(ge=2020, le=2100)],
    month: Annotated[int, APIPath(ge=1, le=12)],
    manager: deps.VesselManagerDep
):
    
    flag_map = {
        v_id: info.metadata.get("flag_state", "Unknown") 
        for v_id, info in manager.vessels.items()
    }
    
    df_with_flags = manager.historical_df.assign(
        flag_state=lambda x: x["vessel_id"].map(flag_map)
    )
    
    df = DataCleaner.distribution_by_flag(
        df_with_flags, 
        manager.config["thresholds"], 
        year, 
        month
    )
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data exists for the requested period.")
        
    fig = tviz.create_distribution_chart(df, manager.config["thresholds"], year, month)
    return fig.to_html(include_plotlyjs="cdn", full_html=True)