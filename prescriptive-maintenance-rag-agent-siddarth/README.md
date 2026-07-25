# IoT Alert Simulator & Prescriptive Maintenance API

A comprehensive simulation engine and FastAPI service designed to test, validate, and stream IoT sensor telemetry alerts for equipment predictive and prescriptive maintenance.

## Features

- ⚡ **FastAPI Endpoint (`main.py`)**: Real-time `/sensor-alert` POST endpoint with strict Pydantic payload validation, severity scoring (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and prescriptive maintenance action recommendations.
- 📡 **Multi-Mode Simulator (`simulate_alert.py`)**:
  - **Automated Test Mode (`--mode test`)**: Executes automated verification covering valid telemetries, invalid data types, missing fields, out-of-bound values, and status enums.
  - **Sample Payload Mode (`--mode sample`)**: Sends pre-configured JSON payload files to the endpoint and logs structured responses.
  - **Streaming Telemetry Mode (`--mode stream`)**: Continuous real-time IoT alert streaming at configurable intervals and anomaly injection rates.
  - **Random Telemetry Mode (`--mode random`)**: Generates and dispatches randomized equipment telemetries.
- 📁 **Comprehensive Sample Payloads (`sample_payloads/`)**: Pre-configured JSON samples covering normal operation, overheating, critical failure, warning states, missing fields, invalid types, and out-of-range metrics.
- 🧪 **Automated Test Suite (`test_simulator.py`)**: Pytest integration and unit tests verifying API validation, endpoint behavior, and payload generators.

---

## Directory Structure

```
prescriptive-maintenance-rag-agent-siddarth/
├── main.py                  # FastAPI server with /sensor-alert endpoint & Pydantic models
├── simulate_alert.py        # IoT Alert Simulator CLI tool & automated test harness
├── test_simulator.py        # Pytest test suite for endpoint & simulator validation
├── sample_payloads/         # Sample JSON payload test cases
│   ├── valid_payload.json             # Overheating alert sample (HTTP 200)
│   ├── normal_payload.json            # Normal baseline operation sample (HTTP 200)
│   ├── warning_payload.json           # Elevated metrics warning sample (HTTP 200)
│   ├── critical_failure_payload.json  # Emergency failure alert sample (HTTP 200)
│   ├── invalid_payload.json           # String temperature & negative vibration (HTTP 422)
│   ├── missing_fields_payload.json    # Missing required machine_id (HTTP 422)
│   └── out_of_range_payload.json      # Exceeds max temperature bound (HTTP 422)
└── README.md                # Project documentation
```

---

## Quick Start Guide

### 1. Prerequisites & Dependencies

Ensure dependencies are installed:
```bash
pip install fastapi uvicorn requests pytest httpx
```

---

### 2. Start the FastAPI Server

Launch the API backend locally:
```bash
uvicorn main:app --reload --port 8000
```
- API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### 3. Run the IoT Alert Simulator

#### Mode 1: Automated Scenario Test Suite (Default)
Executes a full scenario battery testing valid payloads and error handling (422 responses):
```bash
python simulate_alert.py --mode test
```

#### Mode 2: Send Sample JSON Payloads
Reads and sends all JSON files in `sample_payloads/`:
```bash
python simulate_alert.py --mode sample
```
Or send a specific JSON file:
```bash
python simulate_alert.py --mode sample --payload-file sample_payloads/critical_failure_payload.json
```

#### Mode 3: Continuous Telemetry Streaming
Simulate continuous live equipment telemetry (e.g., 10 alerts at 1-second intervals with 30% anomaly probability):
```bash
python simulate_alert.py --mode stream --count 10 --interval 1.0 --anomaly-rate 0.3
```

---

### 4. CLI Arguments Reference

| Argument | Choices | Default | Description |
|---|---|---|---|
| `--url` | Text | `http://127.0.0.1:8000/sensor-alert` | FastAPI endpoint target URL |
| `--mode` | `test`, `sample`, `stream`, `random` | `test` | Simulation mode |
| `--count` | Integer | `5` | Number of telemetries to send in stream/random mode |
| `--interval` | Float | `1.0` | Delay between streaming requests (seconds) |
| `--anomaly-rate` | Float `[0.0 - 1.0]` | `0.2` | Probability of generating high severity anomaly |
| `--payload-file` | Path | `None` | Specific JSON payload file path for sample mode |

---

## Running Automated Tests

Run the complete test suite using `pytest`:
```bash
pytest test_simulator.py -v
```