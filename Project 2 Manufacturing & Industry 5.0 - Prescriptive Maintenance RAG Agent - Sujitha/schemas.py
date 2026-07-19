from pydantic import BaseModel, Field, ConfigDict


class SensorAlert(BaseModel):
    machine_id: str = Field(
        ...,
        description="Unique ID of the machine",
        examples=["TURBINE-001"]
    )

    temperature: float = Field(
        ...,
        ge=-50,
        le=300,
        description="Machine temperature in °C",
        examples=[92.5]
    )

    vibration: float = Field(
        ...,
        ge=0,
        le=100,
        description="Vibration amplitude in mm/s",
        examples=[4.8]
    )

    status: str = Field(
        ...,
        description="Current operating status",
        examples=["OVERHEATING"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "machine_id": "TURBINE-001",
                "temperature": 92.5,
                "vibration": 4.8,
                "status": "OVERHEATING"
            }
        }
    )