# pyright: reportMissingImports=false
import json
import os
import glob
import pytest  # type: ignore
from fastapi.testclient import TestClient  # type: ignore
from main import app, ALERT_LOG
from simulate_alert import AlertGenerator, AlertClient, TestRunner

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_alert_log():
    ALERT_LOG.clear()
    yield
    ALERT_LOG.clear()

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "IoT Alert API"

def test_valid_normal_alert():
    payload = {
        "machine_id": "TURBINE-001",
        "temperature": 45.0,
        "vibration": 1.5,
        "status": "NORMAL"
    }
    response = client.post("/sensor-alert", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "alert_id" in data
    assert data["severity"] == "LOW"
    assert "NORMAL" in data["prescription"]

def test_valid_overheating_alert():
    payload = {
        "machine_id": "TURBINE-002",
        "temperature": 95.0,
        "vibration": 5.5,
        "status": "OVERHEATING"
    }
    response = client.post("/sensor-alert", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "HIGH"
    assert "Temperature threshold exceeded" in data["prescription"]

def test_valid_critical_failure_alert():
    payload = {
        "machine_id": "COMPRESSOR-003",
        "temperature": 130.0,
        "vibration": 12.0,
        "status": "FAILURE"
    }
    response = client.post("/sensor-alert", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "CRITICAL"
    assert "Immediate emergency shutdown" in data["prescription"]

def test_invalid_temperature_type():
    payload = {
        "machine_id": "TURBINE-004",
        "temperature": "EXTREME_HOT",
        "vibration": 2.0,
        "status": "NORMAL"
    }
    response = client.post("/sensor-alert", json=payload)
    assert response.status_code == 422

def test_invalid_negative_vibration():
    payload = {
        "machine_id": "TURBINE-005",
        "temperature": 50.0,
        "vibration": -5.0,
        "status": "NORMAL"
    }
    response = client.post("/sensor-alert", json=payload)
    assert response.status_code == 422

def test_missing_machine_id():
    payload = {
        "temperature": 50.0,
        "vibration": 2.0,
        "status": "NORMAL"
    }
    response = client.post("/sensor-alert", json=payload)
    assert response.status_code == 422

def test_invalid_status_enum():
    payload = {
        "machine_id": "PUMP-006",
        "temperature": 50.0,
        "vibration": 2.0,
        "status": "EXPLODING"
    }
    response = client.post("/sensor-alert", json=payload)
    assert response.status_code == 422

def test_out_of_range_temperature():
    payload = {
        "machine_id": "PUMP-007",
        "temperature": 999.0,
        "vibration": 2.0,
        "status": "NORMAL"
    }
    response = client.post("/sensor-alert", json=payload)
    assert response.status_code == 422

def test_sample_payload_files_processing():
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_payloads")
    assert os.path.exists(sample_dir)
    
    files = glob.glob(os.path.join(sample_dir, "*.json"))
    assert len(files) >= 5, "Should have at least 5 sample JSON files"
    
    for filepath in files:
        with open(filepath, 'r') as f:
            payload = json.load(f)
        fname = os.path.basename(filepath)
        response = client.post("/sensor-alert", json=payload)
        
        if fname in ["valid_payload.json", "normal_payload.json", "warning_payload.json", "critical_failure_payload.json"]:
            assert response.status_code == 200, f"Expected 200 for {fname}, got {response.status_code}"
        elif fname in ["invalid_payload.json", "missing_fields_payload.json", "out_of_range_payload.json"]:
            assert response.status_code == 422, f"Expected 422 for {fname}, got {response.status_code}"

def test_alert_history_logging():
    payload = {
        "machine_id": "TURBINE-001",
        "temperature": 45.0,
        "vibration": 1.5,
        "status": "NORMAL"
    }
    client.post("/sensor-alert", json=payload)
    
    history_res = client.get("/alerts")
    assert history_res.status_code == 200
    hdata = history_res.json()
    assert hdata["total_alerts"] == 1
    assert hdata["recent_alerts"][0]["machine_id"] == "TURBINE-001"
    
    clear_res = client.delete("/alerts")
    assert clear_res.status_code == 200
    assert clear_res.json()["total_alerts"] == 0

def test_generator_random_payload():
    payload = AlertGenerator.random_payload(anomaly_rate=0.5)
    assert "machine_id" in payload
    assert "temperature" in payload
    assert "vibration" in payload
    assert "status" in payload
    assert payload["status"] in ["NORMAL", "WARNING", "OVERHEATING", "FAILURE"]

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))

