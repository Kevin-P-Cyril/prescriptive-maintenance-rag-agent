# pyright: reportMissingImports=false
from fastapi import FastAPI, HTTPException, status  # type: ignore
from pydantic import BaseModel, Field, field_validator  # type: ignore
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

app = FastAPI(
    title="IoT Prescriptive Maintenance Alert API",
    description="API for processing sensor alerts, validating IoT telemetry payloads, and providing prescriptive maintenance actions.",
    version="1.0.0"
)

# In-memory storage for received alerts
ALERT_LOG: List[Dict[str, Any]] = []

class SensorAlert(BaseModel):
    machine_id: str = Field(..., min_length=1, max_length=50, description="Machine identifier, e.g. TURBINE-001")
    temperature: float = Field(..., ge=-50.0, le=300.0, description="Temperature reading in °C")
    vibration: float = Field(..., ge=0.0, le=100.0, description="Vibration reading in mm/s RMS")
    status: str = Field(..., description="Operational status: NORMAL, WARNING, OVERHEATING, or FAILURE")
    pressure: Optional[float] = Field(default=1.0, ge=0.0, description="System pressure in Bar")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp string")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"NORMAL", "WARNING", "OVERHEATING", "FAILURE"}
        upper_v = v.upper()
        if upper_v not in valid_statuses:
            raise ValueError(f"Status must be one of {sorted(list(valid_statuses))}, got '{v}'")
        return upper_v

def evaluate_prescriptive_action(alert: SensorAlert) -> Dict[str, str]:
    """Generates severity classification and prescriptive maintenance action recommendations."""
    temp = alert.temperature
    vib = alert.vibration
    st = alert.status.upper()

    if st == "FAILURE" or temp > 100.0 or vib > 8.0:
        return {
            "severity": "CRITICAL",
            "action": "CRITICAL: Immediate emergency shutdown advised. Inspect rotor bearings, cooling loop, and mechanical integrity."
        }
    elif st == "OVERHEATING" or temp > 80.0:
        return {
            "severity": "HIGH",
            "action": "HIGH: Temperature threshold exceeded. Reduce load, check coolant levels, and verify heat exchanger operation."
        }
    elif st == "WARNING" or vib > 4.0:
        return {
            "severity": "MEDIUM",
            "action": "MEDIUM: Elevated vibration/temperature observed. Schedule preventative maintenance inspection within 24 hours."
        }
    else:
        return {
            "severity": "LOW",
            "action": "NORMAL: Machine metrics within standard operational baseline. No immediate intervention required."
        }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "IoT Alert API", "alerts_logged": len(ALERT_LOG)}

@app.post("/sensor-alert", status_code=status.HTTP_200_OK)
def process_sensor_alert(alert: SensorAlert):
    """Processes incoming equipment telemetry alert and provides prescriptive maintenance advice."""
    alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
    processed_time = alert.timestamp or datetime.now(timezone.utc).isoformat()
    
    evaluation = evaluate_prescriptive_action(alert)
    
    record = {
        "alert_id": alert_id,
        "received_at": processed_time,
        "machine_id": alert.machine_id,
        "temperature": alert.temperature,
        "vibration": alert.vibration,
        "status": alert.status,
        "pressure": alert.pressure,
        "severity": evaluation["severity"],
        "prescription": evaluation["action"]
    }
    
    ALERT_LOG.append(record)
    
    return {
        "status": "success",
        "alert_id": alert_id,
        "processed_at": processed_time,
        "severity": evaluation["severity"],
        "prescription": evaluation["action"],
        "data": alert.model_dump()
    }

@app.get("/alerts")
def get_alert_history(limit: int = 50):
    """Retrieve logged alerts history."""
    return {
        "total_alerts": len(ALERT_LOG),
        "recent_alerts": ALERT_LOG[-limit:]
    }

@app.delete("/alerts")
def clear_alert_history():
    """Clear in-memory alert history for clean test runs."""
    ALERT_LOG.clear()
    return {"status": "cleared", "total_alerts": 0}
