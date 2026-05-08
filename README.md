# Project Poseidon

Enterprise-grade distributed Maritime Vessel Traffic Monitor backend built with **FastAPI**, **Pydantic v2**, **pandas**, and **Plotly**.

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



