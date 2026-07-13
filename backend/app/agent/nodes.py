"""
LangGraph node functions for the Prescriptive Maintenance Agent.

Pipeline:
    analyze_alert -> retrieve_manual_sections -> check_inventory -> generate_instructions

Each node is a pure function: (AgentState) -> partial AgentState update,
which is how LangGraph merges node outputs back into the shared state.
"""
from __future__ import annotations

import logging
import re

from app.agent.state import AgentState
from app.services import inventory, vector_store
from app.services.llm_service import LLMUnavailableError, generate

logger = logging.getLogger(__name__)

PART_KEYWORDS = [
    "bearing", "belt", "pump", "seal", "relay", "encoder", "filter",
    "switch", "motor", "sensor", "valve", "gasket", "fuse", "coupling",
    "hose", "cable", "fan", "spindle",
]


def analyze_alert(state: AgentState) -> dict:
    """Turn a structured IoT alert (or free-form question) into a retrieval query."""
    if state.get("query"):
        search_query = state["query"]
    else:
        search_query = (
            f"{state.get('machine_type', '')} error {state.get('error_code', '')}: "
            f"{state.get('description', '')}. {state.get('sensor_reading', '') or ''}"
        ).strip()

    logger.info("Agent search query: %s", search_query)
    return {"search_query": search_query}


def retrieve_manual_sections(state: AgentState) -> dict:
    """Retrieve the most relevant manual chunks from ChromaDB for the query."""
    query = state.get("search_query") or state.get("query", "")
    docs = vector_store.similarity_search(query)

    retrieved = [
        {
            "text": d.page_content,
            "source": d.metadata.get("source", "unknown"),
            "page": d.metadata.get("page", -1),
        }
        for d in docs
    ]
    return {"retrieved_docs": retrieved}


def identify_candidate_parts(state: AgentState) -> dict:
    """Scan retrieved manual text + alert description for spare-part mentions."""
    text_blob = " ".join(d["text"] for d in state.get("retrieved_docs", []))
    text_blob += " " + state.get("description", "")
    text_blob_lower = text_blob.lower()

    found = set()
    for keyword in PART_KEYWORDS:
        if keyword in text_blob_lower:
            # Try to capture a short phrase around the keyword, e.g. "spindle bearing"
            match = re.search(rf"(\b\w+\s+)?{keyword}(\s\w+)?", text_blob_lower)
            if match:
                found.add(match.group(0).strip())
            else:
                found.add(keyword)

    return {"candidate_parts": list(found)[:5]}


def check_inventory(state: AgentState) -> dict:
    """Tool call: look up spare-parts availability for each candidate part."""
    machine_id = state.get("machine_id", "")
    results = []
    for part in state.get("candidate_parts", []):
        status = inventory.check_part_availability(part, machine_id=machine_id)
        results.append(status.model_dump())
    return {"inventory_results": results}


def generate_instructions(state: AgentState) -> dict:
    """Use the local LLM to synthesize a cited, step-by-step maintenance response."""
    context_blocks = []
    for i, doc in enumerate(state.get("retrieved_docs", []), start=1):
        context_blocks.append(
            f"[Source {i} | {doc['source']} p.{doc['page']}]\n{doc['text']}"
        )
    context = "\n\n".join(context_blocks) if context_blocks else "No manual sections were retrieved."

    inventory_lines = []
    for item in state.get("inventory_results", []):
        stock_txt = (
            f"IN STOCK ({item['quantity']} units, {item['location']})"
            if item["in_stock"]
            else "OUT OF STOCK"
        )
        inventory_lines.append(f"- {item['part_name']}: {stock_txt}")
    inventory_text = "\n".join(inventory_lines) if inventory_lines else "No specific parts identified."

    if state.get("query") and not state.get("machine_id"):
        task_description = f"Question: {state['query']}"
    else:
        task_description = (
            f"Machine ID: {state.get('machine_id')}\n"
            f"Machine type: {state.get('machine_type')}\n"
            f"Error code: {state.get('error_code')}\n"
            f"Description: {state.get('description')}\n"
            f"Sensor reading: {state.get('sensor_reading')}\n"
            f"Severity: {state.get('severity')}"
        )

    prompt = f"""You are an expert industrial maintenance assistant. Use ONLY the manual excerpts below \
to diagnose the issue and produce a precise, numbered, step-by-step repair procedure. \
Cite the source and page number after every factual claim, like this: (Source: {{filename}}, p.{{page}}). \
If the manual excerpts do not contain enough information, clearly say so instead of guessing. \
Also mention spare-parts availability from the inventory check below where relevant, and advise \
ordering replacements if a required part is out of stock.

--- MANUAL EXCERPTS ---
{context}

--- SPARE PARTS INVENTORY CHECK ---
{inventory_text}

--- TASK ---
{task_description}

Respond in this format:
DIAGNOSIS: <one to two sentence root-cause diagnosis>
STEPS:
1. ...
2. ...
...
"""

    try:
        raw_answer = generate(prompt)
    except LLMUnavailableError as exc:
        raw_answer = (
            "DIAGNOSIS: Unable to reach the local LLM (Ollama).\n"
            f"STEPS:\n1. {exc}\n"
        )

    diagnosis, steps = _parse_answer(raw_answer)
    citations = [
        {"source": d["source"], "page": d["page"], "snippet": d["text"][:220]}
        for d in state.get("retrieved_docs", [])
    ]

    return {
        "final_answer": raw_answer,
        "diagnosis": diagnosis,
        "steps": steps,
        "citations": citations,
    }


def _parse_answer(raw: str) -> tuple[str, list[str]]:
    """Best-effort parsing of the LLM's DIAGNOSIS/STEPS format into structured fields."""
    diagnosis = ""
    steps: list[str] = []

    diag_match = re.search(r"DIAGNOSIS:\s*(.+?)(?:\n\s*STEPS:|\Z)", raw, re.IGNORECASE | re.DOTALL)
    if diag_match:
        diagnosis = diag_match.group(1).strip()

    steps_match = re.search(r"STEPS:\s*(.+)", raw, re.IGNORECASE | re.DOTALL)
    if steps_match:
        step_block = steps_match.group(1).strip()
        for line in step_block.splitlines():
            line = line.strip()
            cleaned = re.sub(r"^\d+[\.\)]\s*", "", line)
            if cleaned:
                steps.append(cleaned)

    if not diagnosis and not steps:
        diagnosis = raw.strip()[:300]

    return diagnosis, steps
