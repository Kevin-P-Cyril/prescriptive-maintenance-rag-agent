"""
Inventory service.

A mock spare-parts inventory backed by a local JSON file, standing in for a
real ERP/inventory-management API integration (which would typically be a
paid enterprise system). This keeps the project fully free to run while
still demonstrating a realistic "tool call" the agent can invoke.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

from app.config import get_settings
from app.models.schemas import InventoryItem, InventoryStatus

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache
def _load_inventory() -> list[InventoryItem]:
    path = Path(settings.inventory_file)
    if not path.exists():
        logger.warning("Inventory file not found at %s; returning empty inventory", path)
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [InventoryItem(**item) for item in raw]


def list_inventory() -> list[InventoryItem]:
    return _load_inventory()


def check_part_availability(part_name: str, machine_id: str | None = None) -> InventoryStatus:
    """
    Tool function used by the agent: given a (possibly fuzzy) part name,
    find the closest matching inventory record and report stock status.
    """
    items = _load_inventory()
    query = part_name.lower().strip()

    best_match: InventoryItem | None = None
    for item in items:
        name = item.part_name.lower()
        if query == name or query in name or name in query:
            best_match = item
            break

    if best_match is None:
        # Fallback: token overlap scoring for loose matches
        query_tokens = set(query.split())
        best_score = 0
        for item in items:
            score = len(query_tokens & set(item.part_name.lower().split()))
            if score > best_score:
                best_score = score
                best_match = item

    if best_match is None:
        return InventoryStatus(part_name=part_name, in_stock=False, quantity=0, location=None)

    return InventoryStatus(
        part_name=best_match.part_name,
        in_stock=best_match.quantity > 0,
        quantity=best_match.quantity,
        location=best_match.location,
    )
