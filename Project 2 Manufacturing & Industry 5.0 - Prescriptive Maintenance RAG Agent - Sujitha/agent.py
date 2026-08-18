from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END

from query_generator import generate_search_query
from retriever import ManualRetriever
from tool_handler import handle_tools
from ticket import generate_ticket


# ============================================================
# AGENT STATE
# ============================================================

class AgentState(TypedDict, total=False):
    sensor_data: Dict[str, Any]
    search_query: str
    retrieved_chunks: List[Dict[str, Any]]

    tool_required: bool
    tool_result: Dict[str, Any]

    maintenance_recommendation: Dict[str, Any]

    ticket: Dict[str, Any]

    final_response: Dict[str, Any]


# ============================================================
# RETRIEVER
# ============================================================

retriever = ManualRetriever()


# ============================================================
# NODE 1 — GENERATE SEARCH QUERY
# ============================================================

def generate_query_node(
    state: AgentState
) -> AgentState:
    """
    Convert the sensor alert into a maintenance
    search query.
    """

    search_query = generate_search_query(
        state["sensor_data"]
    )

    return {
        "search_query": search_query
    }


# ============================================================
# NODE 2 — RETRIEVE MAINTENANCE MANUAL
# ============================================================

def retrieve_manual_node(
    state: AgentState
) -> AgentState:
    """
    Retrieve Top-K relevant maintenance manual
    sections from ChromaDB.
    """

    chunks = retriever.retrieve(
        state["search_query"],
        top_k=3
    )

    return {
        "retrieved_chunks": chunks
    }


# ============================================================
# ROUTING — RETRIEVAL → TOOL OR RECOMMENDATION
# ============================================================

def route_after_retrieval(
    state: AgentState
) -> str:
    """
    Determine whether retrieved instructions
    require spare-part inventory lookup.
    """

    chunks = state.get(
        "retrieved_chunks",
        []
    )

    text_parts = []

    for chunk in chunks:

        if isinstance(chunk, dict):

            text_parts.append(
                str(
                    chunk.get(
                        "instruction",
                        ""
                    )
                )
            )

        else:

            text_parts.append(
                str(chunk)
            )

    text = " ".join(
        text_parts
    ).lower()

    spare_part_keywords = [
        "bearing",
        "cooling fan",
        "fan",
        "motor",
        "pump",
        "filter",
        "lubricant"
    ]

    for keyword in spare_part_keywords:

        if keyword in text:

            return "tool"

    return "recommendation"


# ============================================================
# NODE 3 — INVENTORY / TOOL HANDLER
# ============================================================

def tool_handler_node(
    state: AgentState
) -> AgentState:
    """
    Detect required spare parts and check
    their availability in inventory.
    """

    result = handle_tools(
        state.get(
            "retrieved_chunks",
            []
        )
    )

    return {
        "tool_required": True,
        "tool_result": result
    }


# ============================================================
# NODE 4 — CREATE CITATION-AWARE RECOMMENDATION
# ============================================================

def create_recommendation_node(
    state: AgentState
) -> AgentState:
    """
    Create a grounded maintenance recommendation
    using only retrieved manual information.

    Every recommendation contains:
    Document + Section + Page.
    """

    chunks = state.get(
        "retrieved_chunks",
        []
    )

    # --------------------------------------------------------
    # No retrieval result
    # --------------------------------------------------------

    if not chunks:

        recommendation = {
            "diagnosis":
                "No verified maintenance information found.",

            "action":
                "No verified maintenance instruction found "
                "in the available manuals.",

            "source": {}
        }

        return {
            "maintenance_recommendation":
                recommendation
        }

    # --------------------------------------------------------
    # Use highest-ranked retrieved result
    # --------------------------------------------------------

    best_chunk = chunks[0]

    instruction = best_chunk.get(
        "instruction",
        ""
    )

    document = best_chunk.get(
        "document_title"
    )

    section = best_chunk.get(
        "section"
    )

    page = best_chunk.get(
        "page"
    )

    # --------------------------------------------------------
    # Citation validation
    # --------------------------------------------------------

    if (
        not instruction
        or not document
        or not section
        or page is None
    ):

        recommendation = {
            "diagnosis":
                "No verified maintenance information found.",

            "action":
                "No verified maintenance instruction found "
                "in the available manuals.",

            "source": {}
        }

        return {
            "maintenance_recommendation":
                recommendation
        }

    # --------------------------------------------------------
    # Sensor information
    # --------------------------------------------------------

    sensor_data = state.get(
        "sensor_data",
        {}
    )

    machine_id = sensor_data.get(
        "machine_id",
        "Unknown machine"
    )

    error_code = sensor_data.get(
        "error_code",
        "Unknown error"
    )

    temperature = sensor_data.get(
        "temperature"
    )

    vibration = sensor_data.get(
        "vibration"
    )

    # --------------------------------------------------------
    # Grounded diagnosis
    # --------------------------------------------------------

    diagnosis = (
        f"{machine_id} reported error code "
        f"{error_code} with temperature "
        f"{temperature}°C and vibration "
        f"{vibration} mm/s."
    )

    # --------------------------------------------------------
    # Final recommendation
    # --------------------------------------------------------

    recommendation = {

        "diagnosis":
            diagnosis,

        "action":
            instruction,

        "source": {

            "document":
                document,

            "section":
                section,

            "page":
                page
        }
    }

    return {
        "maintenance_recommendation":
            recommendation
    }


# ============================================================
# NODE 5 — CREATE MAINTENANCE TICKET
# ============================================================

def create_ticket_node(
    state: AgentState
) -> AgentState:
    """
    Generate a maintenance work-order ticket
    containing:

    - Asset details
    - Repair recommendation
    - Required spare parts
    - Ticket ID
    - Ticket status
    """

    recommendation = state.get(
        "maintenance_recommendation",
        {}
    )

    repair_summary = recommendation.get(
        "action",
        ""
    )

    tool_result = state.get(
        "tool_result",
        {}
    )

    spare_parts = tool_result.get(
        "inventory",
        []
    )

    ticket = generate_ticket(

        sensor_data=state.get(
            "sensor_data",
            {}
        ),

        repair_summary=repair_summary,

        spare_parts=spare_parts
    )

    return {
        "ticket": ticket
    }


# ============================================================
# NODE 6 — FINAL RESPONSE
# ============================================================

def finish_node(
    state: AgentState
) -> AgentState:
    """
    Combine all workflow results into the
    final agent response.
    """

    final_response = {

        "search_query":
            state.get(
                "search_query",
                ""
            ),

        "sensor_data":
            state.get(
                "sensor_data",
                {}
            ),

        "retrieved_chunks":
            state.get(
                "retrieved_chunks",
                []
            ),

        "maintenance_recommendation":
            state.get(
                "maintenance_recommendation",
                {}
            ),

        "tool_required":
            state.get(
                "tool_required",
                False
            ),

        "tool_result":
            state.get(
                "tool_result",
                {}
            ),

        "ticket":
            state.get(
                "ticket",
                {}
            )
    }

    return {
        "final_response":
            final_response
    }


# ============================================================
# BUILD LANGGRAPH WORKFLOW
# ============================================================

def build_agent():

    graph = StateGraph(
        AgentState
    )

    # --------------------------------------------------------
    # Add nodes
    # --------------------------------------------------------

    graph.add_node(
        "generate_query",
        generate_query_node
    )

    graph.add_node(
        "retrieve_manual",
        retrieve_manual_node
    )

    graph.add_node(
        "tool_handler",
        tool_handler_node
    )

    graph.add_node(
        "create_recommendation",
        create_recommendation_node
    )

    graph.add_node(
        "create_ticket",
        create_ticket_node
    )

    graph.add_node(
        "finish",
        finish_node
    )

    # --------------------------------------------------------
    # Start → Query
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "generate_query"
    )

    # --------------------------------------------------------
    # Query → Retrieval
    # --------------------------------------------------------

    graph.add_edge(
        "generate_query",
        "retrieve_manual"
    )

    # --------------------------------------------------------
    # Retrieval → Tool / Recommendation
    # --------------------------------------------------------

    graph.add_conditional_edges(

        "retrieve_manual",

        route_after_retrieval,

        {
            "tool":
                "tool_handler",

            "recommendation":
                "create_recommendation"
        }
    )

    # --------------------------------------------------------
    # Tool → Recommendation
    # --------------------------------------------------------

    graph.add_edge(
        "tool_handler",
        "create_recommendation"
    )

    # --------------------------------------------------------
    # Recommendation → Ticket
    # --------------------------------------------------------

    graph.add_edge(
        "create_recommendation",
        "create_ticket"
    )

    # --------------------------------------------------------
    # Ticket → Finish
    # --------------------------------------------------------

    graph.add_edge(
        "create_ticket",
        "finish"
    )

    # --------------------------------------------------------
    # Finish → End
    # --------------------------------------------------------

    graph.add_edge(
        "finish",
        END
    )

    return graph.compile()


# ============================================================
# CREATE AGENT
# ============================================================

agent = build_agent()


# ============================================================
# RUN AGENT
# ============================================================

def run_agent(
    sensor_data: Dict[str, Any]
) -> Dict[str, Any]:

    initial_state: AgentState = {

        "sensor_data":
            sensor_data
    }

    return agent.invoke(
        initial_state
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_alert = {

        "machine_id":
            "TURBINE-01",

        "error_code":
            "E-404",

        "temperature":
            105,

        "vibration":
            4.8
    }

    result = run_agent(
        sample_alert
    )

    print(
        "\n===== LANGGRAPH AGENT TEST ====="
    )

    # --------------------------------------------------------
    # Search Query
    # --------------------------------------------------------

    print(
        "\nGenerated Query:"
    )

    print(
        result.get(
            "search_query",
            ""
        )
    )

    # --------------------------------------------------------
    # Retrieved Manual Results
    # --------------------------------------------------------

    print(
        "\nRetrieved Maintenance Instructions:"
    )

    for i, chunk in enumerate(

        result.get(
            "retrieved_chunks",
            []
        ),

        start=1
    ):

        print(
            f"\n--- Result {i} ---"
        )

        print(
            f"Instruction: "
            f"{chunk.get('instruction')}"
        )

        print(
            f"Document: "
            f"{chunk.get('document_title')}"
        )

        print(
            f"Section: "
            f"{chunk.get('section')}"
        )

        print(
            f"Page: "
            f"{chunk.get('page')}"
        )

    # --------------------------------------------------------
    # Maintenance Recommendation
    # --------------------------------------------------------

    print(
        "\nMaintenance Recommendation:"
    )

    recommendation = result.get(
        "maintenance_recommendation",
        {}
    )

    print(
        f"Diagnosis: "
        f"{recommendation.get('diagnosis', '')}"
    )

    print(
        f"Recommended Action: "
        f"{recommendation.get('action', '')}"
    )

    source = recommendation.get(
        "source",
        {}
    )

    if source:

        print(
            f"Document: "
            f"{source.get('document')}"
        )

        print(
            f"Section: "
            f"{source.get('section')}"
        )

        print(
            f"Page: "
            f"{source.get('page')}"
        )

    # --------------------------------------------------------
    # Inventory
    # --------------------------------------------------------

    print(
        "\nTool Required:"
    )

    print(
        result.get(
            "tool_required",
            False
        )
    )

    if result.get(
        "tool_result"
    ):

        print(
            "\nInventory Results:"
        )

        for item in result[
            "tool_result"
        ].get(
            "inventory",
            []
        ):

            print(

                f"{item['part_id']} "
                f"-> Available: "
                f"{item['available']}, "
                f"Quantity: "
                f"{item['quantity']}"
            )

        print(
            "\nTool Recommendation:"
        )

        print(
            result[
                "tool_result"
            ].get(
                "recommendation",
                ""
            )
        )

    # --------------------------------------------------------
    # Maintenance Ticket
    # --------------------------------------------------------

    print(
        "\nMaintenance Ticket:"
    )

    ticket = result.get(
        "ticket",
        {}
    )

    if ticket:

        print(
            f"Ticket ID: "
            f"{ticket.get('ticket_id')}"
        )

        print(
            f"Status: "
            f"{ticket.get('status')}"
        )

        print(
            f"Repair Summary: "
            f"{ticket.get('repair_summary')}"
        )

        print(
            f"Ticket File: "
            f"{ticket.get('ticket_id')}.json"
        )

    else:

        print(
            "No maintenance ticket generated."
        )

    print(
        "\n===== COMPLETE AGENT EXECUTION ====="
    )