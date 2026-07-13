"""API endpoints for receiving simulated IoT alerts and returning prescriptive maintenance guidance."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.agent.graph import run_agent
from app.models.schemas import Citation, IoTAlert, InventoryStatus, MaintenanceResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("", response_model=MaintenanceResponse)
def receive_alert(alert: IoTAlert) -> MaintenanceResponse:
    """
    Accepts a simulated IoT alert, runs the LangGraph agent (retrieve manual
    sections -> check spare-parts inventory -> generate cited repair steps),
    and returns structured, actionable maintenance guidance.
    """
    try:
        result = run_agent(alert.model_dump())
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Agent execution failed")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc

    citations = [Citation(**c) for c in result.get("citations", [])]
    parts_required = [InventoryStatus(**p) for p in result.get("inventory_results", [])]

    return MaintenanceResponse(
        machine_id=alert.machine_id,
        diagnosis=result.get("diagnosis", ""),
        steps=result.get("steps", []),
        citations=citations,
        parts_required=parts_required,
        raw_answer=result.get("final_answer", ""),
    )
