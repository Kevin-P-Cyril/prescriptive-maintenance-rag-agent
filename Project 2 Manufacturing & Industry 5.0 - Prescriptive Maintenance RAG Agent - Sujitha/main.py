from fastapi import FastAPI
from retriever import ManualRetriever
from query_generator import generate_search_query
from schemas import SensorAlert

app = FastAPI(title="IoT Alert Receiver API")
retriever = ManualRetriever()




@app.get("/")
def root():
    return {"message": "IoT Alert Receiver API is running"}


@app.post("/sensor-alert")
def sensor_alert(alert: SensorAlert):

    sensor_data = {
        "machine_id": alert.machine_id,
        "error_code": "UNKNOWN",
        "temperature": alert.temperature,
        "vibration": alert.vibration,
    }

    search_query = generate_search_query(sensor_data)
    retrieved_chunks = retriever.retrieve(search_query)

    return {
    "message": "Sensor alert received successfully",
    "machine_id": alert.machine_id,
    "temperature": alert.temperature,
    "vibration": alert.vibration,
    "status": alert.status,
    "generated_query": search_query,
    "retrieved_chunks": retrieved_chunks
}