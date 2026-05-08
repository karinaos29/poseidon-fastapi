# Project Poseidon

Enterprise-grade distributed Maritime Vessel Traffic Monitor backend built with **FastAPI**, **Pydantic v2**, **pandas**, and **Plotly**.

---

## Overview

Project Poseidon simulates a real-world maritime telemetry monitoring system for AIS-instrumented commercial vessels operating across:

* Netherlands
* Germany
* Poland
* Denmark

The system:

* Ingests hourly vessel telemetry
* Stores real-time and historical readings
* Provides interactive geospatial dashboards
* Performs temporal and statistical analysis
* Uses a configuration-driven clean architecture

---

# Features

## Core Features

* FastAPI REST API
* Dependency Injection with `Depends`
* Modern FastAPI `lifespan`
* Configuration-driven architecture
* Clean Architecture + DDD separation
* Historical telemetry analysis
* Interactive Plotly dashboards
* JSON persistence
* Vectorized pandas data cleaning
* Full pytest test suite

## Visualizations

* Real-time vessel monitoring map
* Time-series telemetry dashboard
* Monthly fleet risk distribution charts

## Data Engineering

* Regex-based WKT parsing
* Vectorized `.str.extract()` parsing
* `pyarrow` pandas backend
* Named aggregations
* Method chaining workflows

---

# Tech Stack

| Area            | Technology       |
| --------------- | ---------------- |
| Runtime         | Python 3.13+     |
| API             | FastAPI          |
| Validation      | Pydantic v2      |
| Data Processing | pandas + pyarrow |
| Visualization   | Plotly           |
| Testing         | pytest           |
| Linting         | Ruff             |
| Type Checking   | mypy             |
| Environment     | uv               |

---

# Architecture

```text
poseidon/
├── config/
│   ├── server_config.json
│   └── vessels.json
├── data/
│   ├── historical_readings.csv
│   └── readings.json
├── src/poseidon/
│   ├── main.py
│   ├── dependencies.py
│   ├── vessel_manager.py
│   ├── vessel.py
│   ├── models.py
│   ├── data_cleaning.py
│   ├── config_loader.py
│   ├── persistence.py
│   ├── visualization.py
│   └── temporal_visualization.py
├── tests/
├── pyproject.toml
├── uv.lock
├── run.sh
└── README.md
```

---

# Architecture Layers

## Web Layer

Handles:

* FastAPI routes
* Request/response DTOs
* HTTP exception translation
* Dependency injection

No business logic is stored here.

---

## Service Layer

Contains:

* Vessel authorization
* Telemetry ingestion
* State management
* Business rules
* Custom exceptions

Framework-independent and unit-testable.

---

## Data Layer

Responsible for:

* JSON persistence
* CSV loading
* Historical data hydration
* Fault-tolerant file handling

---

## Domain Layer

Contains plain Python classes:

* `VesselReading`
* `VesselInfo`

No Pydantic or validation logic inside domain models.

---

# Installation

## 1. Clone Repository

```bash
git clone <repository-url>
cd poseidon
```

---

## 2. Install Dependencies

Using `uv`:

```bash
uv sync
```

Or manually:

```bash
uv add "fastapi>=0.135" "uvicorn[standard]>=0.42" \
       "pydantic>=2.12" "pandas>=2.2" \
       "pyarrow>=18.0" "plotly>=6.0"

uv add --dev "pytest>=9.0" "pytest-cov>=6.0" \
              "httpx>=0.28" "ruff>=0.8" \
              "mypy>=1.13"
```

---

# Running the Server

```bash
uv run uvicorn poseidon.main:app --reload
```

Server runs on:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

# API Endpoints

| Method | Endpoint                       | Description                     |
| ------ | ------------------------------ | ------------------------------- |
| POST   | `/report`                      | Ingest telemetry                |
| GET    | `/map`                         | Real-time vessel dashboard      |
| GET    | `/status`                      | System health                   |
| GET    | `/history/{vessel_id}`         | Vessel telemetry history        |
| GET    | `/distribution/{year}/{month}` | Risk distribution by flag state |
| GET    | `/`                            | Welcome page                    |
| GET    | `/docs`                        | Swagger UI                      |

---

# Endpoint Examples

## POST `/report`

### Request

```json
{
  "vessel_id": "vessel_rotterdam_001",
  "readings": {
    "speed_knots": 18.4,
    "draft_m": 11.2,
    "heading_deg": 274,
    "fuel_rate_lph": 310
  }
}
```

### Example cURL

```bash
curl -X POST "http://localhost:8000/report" \
     -H "Content-Type: application/json" \
     -d '{
       "vessel_id": "vessel_rotterdam_001",
       "readings": {
         "speed_knots": 18.4,
         "draft_m": 11.2,
         "heading_deg": 274,
         "fuel_rate_lph": 310
       }
     }'
```

---

## GET `/map`

Returns an interactive Plotly map displaying:

* Vessel locations
* Speed-based risk levels
* Hover metadata
* Real-time telemetry

```bash
curl http://localhost:8000/map
```

---

## GET `/status`

Returns:

```json
{
  "status": "healthy",
  "uptime_seconds": 5231,
  "active_vessels": 12,
  "total_reports": 1823,
  "last_update": "2026-05-08T12:00:00Z"
}
```

---

## GET `/history/{vessel_id}`

Interactive time-series visualization with:

* Speed
* Draft
* Heading
* Fuel rate

Includes Plotly range slider.

```bash
curl http://localhost:8000/history/vessel_hamburg_001
```

---

## GET `/distribution/{year}/{month}`

Returns a 100%-stacked bar chart grouped by flag state.

```bash
curl http://localhost:8000/distribution/2025/2
```

---

# Configuration

## `server_config.json`

Controls:

* Storage paths
* Thresholds
* Host/port
* Map defaults
* Risk bands

Example:

```json
{
  "storage_file": "data/readings.json",
  "historical_data_file": "data/historical_readings.csv",
  "host": "0.0.0.0",
  "port": 8000
}
```

---

## `vessels.json`

Stores authorized vessels and metadata.

Example:

```json
{
  "id": "vessel_rotterdam_001",
  "location": "POINT(4.4792 51.9225)",
  "metadata": {
    "flag_state": "Netherlands",
    "home_port": "Rotterdam",
    "vessel_class": "container"
  }
}
```

---

# WKT Parsing

Project Poseidon implements two WKT parsing approaches:

## Single String Parsing

Used for vessel whitelist loading.

```python
WKT_POINT_PATTERN = re.compile(
    r"POINT\s*\(\s*(?P<lon>-?\d+\.?\d*)\s+(?P<lat>-?\d+\.?\d*)\s*\)",
    re.IGNORECASE,
)
```

---

## Vectorized Batch Parsing

Used for pandas data processing.

```python
coords = (
    df["position"]
    .str.extract(wkt_pattern)
    .astype("float32[pyarrow]")
)
```

---

# Data Cleaning Pipeline

Historical data is cleaned using fully vectorized pandas operations.

## Cleaning Rules

* Remove missing `vessel_id`
* Remove missing timestamps
* Remove negative measurements
* Remove impossible AIS speeds (`> 50 knots`)
* Normalize heading to `[0, 360)`
* Parse UTC timestamps

---

# Visualization

## Real-Time Map

Built using:

```python
px.scatter_map()
```

Features:

* MapLibre rendering
* Configurable styles
* Risk-band coloring
* Hover metadata

---

## Time-Series Dashboard

Features:

* Four telemetry traces
* Unified hover
* Range slider
* ~8760 hourly points per vessel

---

## Distribution Chart

Features:

* 100% stacked bars
* Monthly filtering
* Risk categorization
* Consistent color palette

---

# Testing

Run tests:

```bash
uv run pytest
```

Coverage:

```bash
uv run pytest --cov
```

---

## Testing Features

* FastAPI `TestClient`
* `dependency_overrides`
* Temporary filesystem fixtures
* Service-layer unit tests
* API integration tests

---

# Code Quality

## Ruff

```bash
uv run ruff check src tests
```

Format:

```bash
uv run ruff format src tests
```

---

## mypy

```bash
uv run mypy src
```

---

# Example Risk Bands

| Risk Level | Condition                                      |
| ---------- | ---------------------------------------------- |
| Safe       | `speed_knots <= speed_safe`                    |
| Moderate   | `speed_safe < speed_knots <= speed_moderate`   |
| Unsafe     | `speed_moderate < speed_knots <= speed_danger` |
| Danger     | `speed_knots > speed_danger`                   |

---

# Historical Dataset

Expected dataset size:

```text
15 vessels × 365 days × 24 hours = 131,400 rows
```

The CSV dataset contains:

* Vessel telemetry
* Hourly timestamps
* Risk indicators
* Historical operational behavior

---

# Key Design Principles

## Clean Architecture

* DTOs separated from domain models
* Framework-independent business logic
* Clear layer boundaries

---

## Dependency Injection

Uses:

```python
Annotated[T, Depends()]
```

and:

```python
app.dependency_overrides
```

for testing.

---

## Modern FastAPI

Uses:

* `lifespan`
* Pydantic v2
* sync route handlers
* strict validation

---

# Verification Checklist

Before submission:

* [ ] `uv sync` works
* [ ] All endpoints respond correctly
* [ ] `uv run pytest` passes
* [ ] Coverage ≥ 80%
* [ ] Ruff clean
* [ ] mypy clean
* [ ] Map renders correctly
* [ ] Distribution chart works
* [ ] No hardcoded paths or thresholds

---

# Common Pitfalls

* Do not validate inside domain models
* Do not use `.split()` for WKT parsing
* Do not use deprecated `scatter_mapbox`
* Do not mutate globals in tests
* Do not hardcode thresholds

---

# Learning Objectives

This project demonstrates:

* FastAPI backend engineering
* Modern pandas workflows
* Plotly visualization
* Dependency Injection
* Clean Architecture
* Domain-Driven Design
* Data engineering patterns
* Automated testing

---

# License

Educational project for ELTE Python Course.

---


