"""
Builds the LangGraph StateGraph that powers the Prescriptive Maintenance
Agent's reasoning workflow:

    START -> analyze_alert -> retrieve_manual_sections -> identify_candidate_parts
          -> check_inventory -> generate_instructions -> END
"""
from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, StateGraph

from app.agent import nodes
from app.agent.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze_alert", nodes.analyze_alert)
    graph.add_node("retrieve_manual_sections", nodes.retrieve_manual_sections)
    graph.add_node("identify_candidate_parts", nodes.identify_candidate_parts)
    graph.add_node("check_inventory", nodes.check_inventory)
    graph.add_node("generate_instructions", nodes.generate_instructions)

    graph.set_entry_point("analyze_alert")
    graph.add_edge("analyze_alert", "retrieve_manual_sections")
    graph.add_edge("retrieve_manual_sections", "identify_candidate_parts")
    graph.add_edge("identify_candidate_parts", "check_inventory")
    graph.add_edge("check_inventory", "generate_instructions")
    graph.add_edge("generate_instructions", END)

    return graph.compile()


@lru_cache
def get_agent():
    """Cached, compiled LangGraph agent instance."""
    return build_graph()


def run_agent(initial_state: dict) -> dict:
    agent = get_agent()
    return agent.invoke(initial_state)
