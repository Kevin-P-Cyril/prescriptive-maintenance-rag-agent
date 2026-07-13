"""API endpoints for free-form Q&A against the ingested maintenance manuals."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.agent.graph import run_agent
from app.models.schemas import ChatRequest, ChatResponse, Citation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Ask a free-form maintenance question; the agent retrieves and cites manual sections."""
    try:
        result = run_agent({"query": request.question, "machine_id": request.machine_id or ""})
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Agent execution failed")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc

    citations = [Citation(**c) for c in result.get("citations", [])]
    return ChatResponse(answer=result.get("final_answer", ""), citations=citations)
