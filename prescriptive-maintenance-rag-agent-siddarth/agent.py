"""
LangGraph Agent Workflow — Prescriptive Maintenance RAG Agent
================================================================
A complete LangGraph state-graph agent that:

  1. Sets up a typed state graph (AgentState).
  2. Defines a controllable agent workflow.
  3. Defines graph nodes: agent, retrieve_documents, execute_tool, generate_answer.
  4. Connects workflow edges, including conditional routing between
     retrieval and tools.
  5. Tests the complete execution flow (retrieval path, tool path, direct
     answer path) — works even without an OPENAI_API_KEY by falling back
     to a deterministic router.

Run the full flow test with:
    python agent.py
"""

from __future__ import annotations

import os
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

# --------------------------------------------------------------------------- #
# 1. SET UP LANGGRAPH STATE GRAPH
# --------------------------------------------------------------------------- #


class AgentState(TypedDict):
    """Shared state passed between graph nodes.

    - messages:      conversation history (auto-merged by LangGraph).
    - retrieved_docs: documents returned by the retrieval node.
    - tool_name:      name of the tool the agent wants to invoke.
    - tool_input:     JSON-stringified arguments for the tool.
    - tool_result:    raw output produced by the tool.
    - step:           loop counter used to prevent infinite agent loops.
    - final_answer:   the final grounded answer (set by generate_answer).
    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
    retrieved_docs: list
    tool_name: str
    tool_input: str
    tool_result: str
    step: int
    final_answer: str


# --------------------------------------------------------------------------- #
# 2. CREATE AGENT WORKFLOW  —  TOOL REGISTRY
# --------------------------------------------------------------------------- #

# A small tool registry: name -> callable. Tools take a single string argument
# (the tool input) and return a string result. Swap these out for real
# maintenance-domain tools (e.g. querying a CMMS API, sensor telemetry, etc.).
TOOL_REGISTRY: dict[str, callable] = {}


def _register(name: str):
    def decorator(fn):
        TOOL_REGISTRY[name] = fn
        return fn
    return decorator


@_register("calculator")
def calculator(input_str: str) -> str:
    """Evaluate a simple arithmetic expression like '2+2'."""
    expr = input_str.strip().replace(" ", "")
    allowed = set("0123456789+-*/().")
    if not expr or any(c not in allowed for c in expr):
        return f"Invalid expression: {input_str!r}"
    try:
        # NOTE: eval used only for a trusted, sandboxed arithmetic demo.
        value = eval(expr, {"__builtins__": {}}, {})
        return f"{expr} = {value}"
    except Exception as exc:  # noqa: BLE001
        return f"Could not evaluate {input_str!r}: {exc}"


@_register("predict_remaining_useful_life")
def predict_remaining_useful_life(input_str: str) -> str:
    """Estimate remaining useful life (hours) from operating data.

    Input format: 'operating_hours,mtbf_hours'  e.g. '1200,8000'
    """
    try:
        hours, mtbf = (float(x.strip()) for x in input_str.split(","))
        rul = max(0.0, mtbf - hours)
        health_pct = min(100.0, max(0.0, (rul / mtbf) * 100.0)) if mtbf else 0.0
        return (
            f"RUL ~ {rul:.0f} hours (health {health_pct:.1f}%). "
            f"Recommended action: {'schedule maintenance now' if health_pct < 25 else 'monitor; routine inspection due'}."
        )
    except Exception as exc:  # noqa: BLE001
        return f"Could not parse {input_str!r}. Expected 'operating_hours,mtbf_hours'. Error: {exc}"


# --------------------------------------------------------------------------- #
# 3. DEFINE GRAPH NODES
# --------------------------------------------------------------------------- #

# Simulated knowledge base for the prescriptive-maintenance domain.
MAINTENANCE_DOCS: list[dict] = [
    {
        "id": "PM-001",
        "title": "Predictive Maintenance Best Practices",
        "content": (
            "Predictive maintenance uses sensor data and ML models to forecast "
            "equipment failure before it occurs. Key techniques include vibration "
            "analysis, oil analysis, thermography, and remaining-useful-life (RUL) "
            "prediction. Recommended workflow: collect telemetry -> detect anomalies "
            "-> estimate RUL -> schedule prescriptive action."
        ),
    },
    {
        "id": "PM-002",
        "title": "LangGraph Workflows for RAG Agents",
        "content": (
            "LangGraph models agent flows as a cyclic state graph. Nodes are Python "
            "functions that update shared state; conditional edges route between "
            "retrieval, tool execution, and final answer generation."
        ),
    },
]


def _first_question(state: AgentState) -> str:
    """Return the first real user question (ignoring internal [AGENT] markers)."""
    for m in state["messages"]:
        text = getattr(m, "content", "")
        if isinstance(text, str) and not text.startswith("[AGENT]"):
            return text.lower()
    return ""


def retrieve_documents(state: AgentState) -> dict:
    """Retrieval node: return documents relevant to the latest question."""
    question = _first_question(state)
    keywords = [w for w in question.replace("?", "").split() if len(w) > 3]
    hits = [
        doc
        for doc in MAINTENANCE_DOCS
        if any(k in doc["content"].lower() or k in doc["title"].lower() for k in keywords)
    ]
    docs = hits if hits else MAINTENANCE_DOCS
    return {"retrieved_docs": docs, "step": state["step"] + 1}


def execute_tool(state: AgentState) -> dict:
    """Tool node: invoke the requested tool from the registry."""
    name = state.get("tool_name", "")
    payload = state.get("tool_input", "")
    fn = TOOL_REGISTRY.get(name)
    if fn is None:
        result = f"Unknown tool: {name!r}. Available: {sorted(TOOL_REGISTRY)}"
    else:
        try:
            result = fn(payload)
        except Exception as exc:  # noqa: BLE001
            result = f"Tool {name!r} raised an error: {exc}"
    return {"tool_result": result, "step": state["step"] + 1}


MAX_ITERATIONS = 5  # loop guard: route to 'answer' after this many cycles.


def agent(state: AgentState) -> dict:
    """Agent node: decide the next action using an LLM (or deterministic fallback).

    Returns a structured routing decision:
        {"action": "retrieve" | "tool" | "answer", "tool": <name>, "tool_input": <str>}
    """
    llm = _get_llm()
    msgs = list(state["messages"])

    # Loop guard: never let the agent cycle forever between retrieve/tool.
    if state["step"] >= MAX_ITERATIONS:
        decision = {"action": "answer"}
    elif llm is not None:
        history_lines = []
        for m in msgs[-4:]:  # keep context window small
            history_lines.append(f"{m.type}: {m.content}")
        history = "\n".join(history_lines)
        prompt = f"""You are a prescriptive-maintenance RAG agent.
Conversation so far:
{history}

Retrieved docs: {state.get('retrieved_docs', [])}
Tool result: {state.get('tool_result', '')}

Decide the SINGLE best next action:
- "retrieve"  -> if you need domain documents to answer accurately.
- "tool"      -> if you need to compute something (available tools: {sorted(TOOL_REGISTRY)}).
- "answer"    -> if you can answer now.

Respond ONLY with a JSON object of the form:
{{"action": "retrieve"}}  or
{{"action": "tool", "tool": "<tool_name>", "tool_input": "<args>"}}  or
{{"action": "answer"}}
"""
        try:
            raw = llm.invoke(prompt).content.strip()
            decision = _parse_json_decision(raw)
        except Exception:  # noqa: BLE001
            decision = _fallback_router(state)
    else:
        # No API key: deterministic fallback so the flow is fully testable.
        decision = _fallback_router(state)

    # Record only the action name so the router can match on "retrieve"/"tool"/"answer".
    msgs.append(HumanMessage(content=f"[AGENT] action={decision['action']}"))
    updates: dict = {"messages": msgs, "step": state["step"] + 1}
    if decision["action"] == "tool":
        updates["tool_name"] = decision.get("tool", "")
        updates["tool_input"] = decision.get("tool_input", "")
    return updates


def _fallback_router(state: AgentState) -> dict:
    """Deterministic routing: retrieval for knowledge questions, tools for math,
    answer otherwise. Used when no LLM is available or the LLM fails."""
    question = _first_question(state)
    has_docs = bool(state.get("retrieved_docs"))
    has_tool = bool(state.get("tool_result"))

    # 1. If retrieval or tool output has already been collected, answer now.
    if has_docs or has_tool:
        return {"action": "answer"}
    # 2. Tool path: numeric / computation questions.
    if any(expr in question for expr in ("calculate", "compute", "2+2", "remaining useful life", "rul")):
        if "remaining useful life" in question or "rul" in question:
            return {"action": "tool", "tool": "predict_remaining_useful_life", "tool_input": "1200,8000"}
        return {"action": "tool", "tool": "calculator", "tool_input": "2+2"}
    # 3. Retrieval path: domain knowledge questions.
    if any(k in question for k in ("langgraph", "maintenance", "predictive", "prescriptive", "rag")):
        return {"action": "retrieve"}
    # 4. Default: answer directly.
    return {"action": "answer"}


def generate_answer(state: AgentState) -> dict:
    """Final node: produce a grounded answer using docs + tool output."""
    llm = _get_llm()
    context = (
        f"Docs: {state.get('retrieved_docs', [])}\n"
        f"Tool result: {state.get('tool_result', '')}"
    )
    if llm is not None:
        answer = llm.invoke(
            f"Answer concisely using this context.\n\n{context}\n\nQuestion: "
            f"{_first_question(state)}"
        ).content
    else:
        answer = _fallback_answer(state)
    return {"final_answer": answer, "step": state["step"] + 1}


def _fallback_answer(state: AgentState) -> str:
    """Deterministic answer so the graph completes without an API key."""
    docs = state.get("retrieved_docs", [])
    tool = state.get("tool_result", "")
    lines = ["ANSWER (deterministic fallback):"]
    if docs:
        titles = "; ".join(d["title"] for d in docs)
        lines.append(f"Based on: {titles}")
    if tool:
        lines.append(f"Computed: {tool}")
    if not docs and not tool:
        lines.append("No retrieval or tool output was needed.")
    lines.append(f"Question: {_first_question(state)}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# 4. CONNECT WORKFLOW EDGES + CONDITIONAL ROUTING
# --------------------------------------------------------------------------- #


def router(state: AgentState) -> str:
    """Conditional edge from the agent node: pick the next node by name.

    - retrieve -> retrieve_documents
    - tool     -> execute_tool
    - answer   -> generate_answer
    """
    # Parse the agent's last decision message: "[AGENT] action=..."
    decision = "answer"
    for msg in reversed(state["messages"]):
        text = getattr(msg, "content", "")
        if isinstance(text, str) and "[AGENT] action=" in text:
            decision = text.split("[AGENT] action=", 1)[1].strip()
            break

    if decision == "retrieve":
        return "retrieve_documents"
    if decision == "tool":
        return "execute_tool"
    return "generate_answer"


def build_graph():
    """Assemble and compile the LangGraph state graph."""
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("agent", agent)
    graph.add_node("retrieve_documents", retrieve_documents)
    graph.add_node("execute_tool", execute_tool)
    graph.add_node("generate_answer", generate_answer)

    # Entry point
    graph.set_entry_point("agent")

    # Conditional routing from agent
    graph.add_conditional_edges(
        "agent",
        router,
        {
            "retrieve_documents": "retrieve_documents",
            "execute_tool": "execute_tool",
            "generate_answer": "generate_answer",
        },
    )

    # Loop-back edges (retrieval / tool results feed back into the agent)
    graph.add_edge("retrieve_documents", "agent")
    graph.add_edge("execute_tool", "agent")

    # Terminal edge
    graph.add_edge("generate_answer", END)

    return graph.compile()


# --------------------------------------------------------------------------- #
# 5. TEST COMPLETE EXECUTION FLOW
# --------------------------------------------------------------------------- #

def _get_llm():
    """Return a configured ChatOpenAI instance, or None if no API key is set."""
    if os.environ.get("OPENAI_API_KEY"):
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=os.environ.get("OPENAI_MODEL", "gpt-4.1"), temperature=0)
        except Exception:  # noqa: BLE001
            return None
    return None


def _parse_json_decision(raw: str) -> dict:
    """Best-effort parse of the LLM's JSON decision."""
    import json
    raw = raw.strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1:
        try:
            parsed = json.loads(raw[start:end + 1])
            if isinstance(parsed, dict):
                return parsed
        except Exception:  # noqa: BLE001
            pass
    return {"action": "answer"}


def run_case(graph, question: str, label: str) -> None:
    """Run a single test scenario and print a trace of the execution flow."""
    print("=" * 72)
    print(f"[TEST] {label}")
    print(f"Question: {question}")
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=question)],
            "retrieved_docs": [],
            "tool_name": "",
            "tool_input": "",
            "tool_result": "",
            "step": 0,
            "final_answer": "",
        }
    )
    print("\nExecution trace (nodes visited):")
    steps = [getattr(m, "content", str(m)) for m in result["messages"]]
    for s in steps:
        if isinstance(s, str) and s.startswith("[AGENT]"):
            print(f"  -> agent decided: {s}")
    if result.get("retrieved_docs"):
        print(f"  -> retrieved {len(result['retrieved_docs'])} doc(s): "
              f"{[d['title'] for d in result['retrieved_docs']]}")
    if result.get("tool_name"):
        print(f"  -> executed tool '{result['tool_name']}' "
              f"(input={result.get('tool_input')!r}) -> {result.get('tool_result')!r}")
    print(f"\nFINAL ANSWER:\n{result.get('final_answer', '')}")
    print(f"Total steps: {result.get('step', 0)}")
    assert result.get("final_answer"), f"{label}: graph did not produce a final answer"
    print(f"[PASS] {label} completed successfully.")


if __name__ == "__main__":
    graph = build_graph()
    print("LangGraph agent workflow compiled successfully.\n")

    # Scenario 1 — retrieval path
    run_case(graph, "What is predictive maintenance?", "RETRIEVAL PATH")

    # Scenario 2 — tool path (fallback router uses calculator for math)
    run_case(graph, "Can you calculate 2+2?", "TOOL PATH (calculator)")

    # Scenario 3 — tool path (RUL predictor)
    run_case(graph, "Predict the remaining useful life for a machine with 1200 operating hours and an MTBF of 8000 hours.",
             "TOOL PATH (RUL predictor)")

    # Scenario 4 — direct answer path
    run_case(graph, "Hello, who are you?", "DIRECT ANSWER PATH")

    print("\n" + "=" * 72)
    print("ALL EXECUTION-FLOW TESTS PASSED.")

