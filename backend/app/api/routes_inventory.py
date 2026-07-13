"""API endpoints exposing the mock spare-parts inventory tool."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.schemas import InventoryItem, InventoryStatus
from app.services import inventory

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryItem])
def get_all_inventory() -> list[InventoryItem]:
    """List the full mock spare-parts inventory."""
    return inventory.list_inventory()


@router.get("/check", response_model=InventoryStatus)
def check_part(
    part_name: str = Query(..., description="Part name to check, e.g. 'Coolant Pump'"),
    machine_id: str | None = Query(None),
) -> InventoryStatus:
    """Check stock availability for a given spare part."""
    return inventory.check_part_availability(part_name, machine_id=machine_id)
