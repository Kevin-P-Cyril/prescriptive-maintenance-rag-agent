from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="IoT Alert Receiver API",
    description="Receives sensor alerts from manufacturing machines",
    version="1.0"
)


class SensorAlert(BaseModel):
    machine_id: str
    temperature: float
    vibration: float
    status: str


@app.get("/")
def home():
    return {"message": "IoT Alert Receiver API is running"}


@app.post("/sensor-alert")
def sensor_alert(alert: SensorAlert):
    return {
        "message": "Sensor alert received successfully",
        "machine_id": alert.machine_id,
        "temperature": alert.temperature,
        "vibration": alert.vibration,
        "status": alert.status
    }