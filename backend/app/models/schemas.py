"""Pydantic schemas shared across the API layer and the agent."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class IoTAlert(BaseModel):
    """A simulated alert coming from a machine's IoT sensor/controller."""

    machine_id: str = Field(..., examples=["CNC-204"])
    machine_type: str = Field(..., examples=["CNC Milling Machine"])
    error_code: str = Field(..., examples=["E-108"])
    description: str = Field(..., examples=["Spindle overheating detected during operation"])
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    sensor_reading: Optional[str] = Field(
        None, examples=["Spindle temp: 92°C (threshold: 75°C)"]
    )


class Citation(BaseModel):
    source: str
    page: int
    snippet: str


class InventoryStatus(BaseModel):
    part_name: str
    in_stock: bool
    quantity: int
    location: Optional[str] = None


class MaintenanceResponse(BaseModel):
    machine_id: str
    diagnosis: str
    steps: list[str]
    citations: list[Citation]
    parts_required: list[InventoryStatus] = []
    raw_answer: str


class ChatRequest(BaseModel):
    question: str = Field(..., examples=["How do I replace the spindle bearing on CNC-204?"])
    machine_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


class IngestResponse(BaseModel):
    filename: str
    chunks_indexed: int
    pages_parsed: int


class InventoryItem(BaseModel):
    part_name: str
    sku: str
    quantity: int
    location: str
    compatible_machines: list[str] = []
