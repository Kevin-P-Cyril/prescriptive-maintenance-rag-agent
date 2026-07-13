"""Shared state passed between LangGraph nodes in the maintenance agent."""
from __future__ import annotations

from typing import Optional, TypedDict


class RetrievedDoc(TypedDict):
    text: str
    source: str
    page: int


class AgentState(TypedDict, total=False):
    # Input
    machine_id: str
    machine_type: str
    error_code: str
    description: str
    severity: str
    sensor_reading: Optional[str]
    query: str  # free-form question, used by the chat endpoint

    # Working memory
    search_query: str
    retrieved_docs: list[RetrievedDoc]
    candidate_parts: list[str]
    inventory_results: list[dict]

    # Output
    diagnosis: str
    steps: list[str]
    final_answer: str
    citations: list[dict]
