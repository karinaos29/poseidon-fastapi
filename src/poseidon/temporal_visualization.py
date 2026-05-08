import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from poseidon.visualization import RISK_COLORS

def create_time_series(df: pd.DataFrame, vessel_id: str) -> go.Figure:

    df = df.sort_values("timestamp")
    
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("Speed over Ground (knots)", "Draft (meters)", "Heading (degrees)", "Fuel Rate (L/hr)")
    )

    # Trace 1: Speed
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["speed_knots"], name="Speed", line=dict(color="#1f77b4")),
        row=1, col=1
    )
    # Trace 2: Draft
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["draft_m"], name="Draft", line=dict(color="#ff7f0e")),
        row=2, col=1
    )
    # Trace 3: Heading 
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["heading_deg"], name="Heading", mode="markers", marker=dict(size=2, color="#2ca02c")),
        row=3, col=1
    )
    # Trace 4: Fuel
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["fuel_rate_lph"], name="Fuel", line=dict(color="#d62728")),
        row=4, col=1
    )

    fig.update_layout(
        height=800,
        title_text=f"Yearly Telemetry Profile: {vessel_id}",
        hovermode="x unified",  # Cursor creates a vertical line showing all 4 values at once
        showlegend=False
    )
    
    fig.update_xaxes(rangeslider_visible=True, row=4, col=1)
    
    return fig


def create_distribution_chart(
    df: pd.DataFrame, 
    thresholds: dict[str, float], 
    year: int, 
    month: int
) -> go.Figure:

    df["percentage"] = df.groupby("flag_state")["reports"].transform(lambda x: (x / x.sum()) * 100)
    
    fig = px.bar(
        df,
        x="flag_state",
        y="percentage",
        color="risk_band",
        color_discrete_map=RISK_COLORS,
        text_auto=".1f", 
        labels={
            "percentage": "Percentage of Reports (%)",
            "flag_state": "Flag State",
            "risk_band": "Risk Threshold"
        },
        title=f"Fleet Safety Distribution: {month:02d}/{year}"
    )
    
    fig.update_traces(
        textfont_size=12, 
        textangle=0, 
        textposition="inside", 
        cliponaxis=False,
        texttemplate="%{y:.1f}%" 
    )
    
    fig.update_layout(yaxis=dict(range=[0, 100]))
    
    return fig