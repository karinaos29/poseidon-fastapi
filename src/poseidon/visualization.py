import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure

RISK_COLORS = {
    "Safe": "#00CC96",       # Green
    "Moderate": "#FECB52",   # Yellow
    "Unsafe": "#FFA15A",     # Orange
    "Danger": "#EF553B",     # Red
    "No data": "#B6E880"     # Gray-ish green
}

def _determine_risk_band(speed: float | None, thresholds: dict[str, float]) -> str:
    """Helper to assign a risk band based on current speed."""
    if speed is None:
        return "No data"
    if speed <= thresholds["speed_safe"]:
        return "Safe"
    if speed <= thresholds["speed_moderate"]:
        return "Moderate"
    if speed <= thresholds["speed_danger"]:
        return "Unsafe"
    return "Danger"

def create_realtime_map(vessels: dict, config: dict) -> Figure:
    """
    Builds an interactive MapLibre map of the fleet's current positions.
    Uses px.scatter_map (modern Plotly 6 API).
    """
    map_config = config.get("map_config", {})
    thresholds = config.get("thresholds", {})
    
    map_data = []
    for v_id, info in vessels.items():
        speed = info.last_reading.get("speed_knots") if info.last_reading else None
        draft = info.last_reading.get("draft_m") if info.last_reading else None
        heading = info.last_reading.get("heading_deg") if info.last_reading else None
        
        map_data.append({
            "vessel_id": v_id,
            "longitude": info.longitude,
            "latitude": info.latitude,
            "vessel_class": info.metadata.get("vessel_class", "Unknown"),
            "home_port": info.metadata.get("home_port", "Unknown"),
            "flag_state": info.metadata.get("flag_state", "Unknown"),
            "speed_knots": speed,
            "draft_m": draft,
            "heading_deg": heading,
            "Risk": _determine_risk_band(speed, thresholds)
        })
        
    df = pd.DataFrame(map_data)
    
    fig = px.scatter_map(
        df,
        lat="latitude",
        lon="longitude",
        color="Risk",
        color_discrete_map=RISK_COLORS,
        hover_name="vessel_id",
        hover_data={
            "latitude": False, 
            "longitude": False,
            "Risk": False,
            "vessel_class": True,
            "home_port": True,
            "flag_state": True,
            "speed_knots": True,
            "heading_deg": True,
            "draft_m": True
        },
        zoom=map_config.get("default_zoom", 5),
        center=map_config.get("center", {"lat": 54.5, "lon": 8.5})
    )
    
    fig.update_layout(
        map_style=map_config.get("map_style", "carto-positron"),
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title="Real-Time Fleet Telemetry"
    )
    
    return fig