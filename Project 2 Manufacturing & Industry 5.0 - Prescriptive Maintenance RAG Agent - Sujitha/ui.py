"""
ui.py

Streamlit User Interface for the
Prescriptive Maintenance RAG Agent.
"""

import streamlit as st

from agent import run_agent


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Prescriptive Maintenance RAG Agent",
    page_icon="⚙️",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("⚙️ Prescriptive Maintenance RAG Agent")

st.markdown(
    """
    ### Manufacturing & Industry 5.0

    An intelligent maintenance system that processes IoT alerts,
    retrieves verified maintenance instructions, checks spare-part
    availability, and generates a maintenance work-order ticket.
    """
)

st.divider()


# ============================================================
# SIDEBAR - IoT ALERT
# ============================================================

st.sidebar.header("🔔 IoT Sensor Alert")

machine_id = st.sidebar.text_input(
    "Machine ID",
    value="TURBINE-01"
)

error_code = st.sidebar.text_input(
    "Error Code",
    value="E-404"
)

temperature = st.sidebar.number_input(
    "Temperature (°C)",
    min_value=0.0,
    max_value=500.0,
    value=105.0,
    step=0.1
)

vibration = st.sidebar.number_input(
    "Vibration (mm/s)",
    min_value=0.0,
    max_value=100.0,
    value=4.8,
    step=0.1
)

st.sidebar.divider()

analyze_button = st.sidebar.button(
    "🚀 Analyze Maintenance Alert",
    type="primary"
)


# ============================================================
# MAIN WORKFLOW
# ============================================================

if analyze_button:

    # --------------------------------------------------------
    # CREATE SENSOR DATA
    # --------------------------------------------------------

    sensor_data = {
        "machine_id": machine_id,
        "error_code": error_code,
        "temperature": temperature,
        "vibration": vibration
    }


    # --------------------------------------------------------
    # RUN LANGGRAPH AGENT
    # --------------------------------------------------------

    with st.spinner(
        "Running Prescriptive Maintenance Agent..."
    ):

        try:

            result = run_agent(
                sensor_data
            )

        except Exception as e:

            st.error(
                f"Agent execution failed: {e}"
            )

            st.stop()


    # ========================================================
    # 1. INCOMING IoT ALERT
    # ========================================================

    st.header("🔔 Incoming IoT Alert")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Machine ID",
            machine_id
        )

    with col2:

        st.metric(
            "Error Code",
            error_code
        )

    with col3:

        st.metric(
            "Temperature",
            f"{temperature} °C"
        )

    with col4:

        st.metric(
            "Vibration",
            f"{vibration} mm/s"
        )


    st.divider()


    # ========================================================
    # 2. GENERATED SEARCH QUERY
    # ========================================================

    st.header("🔎 Generated Maintenance Search Query")

    search_query = result.get(
        "search_query",
        ""
    )

    if search_query:

        st.code(
            search_query,
            language="text"
        )

    else:

        st.warning(
            "No search query was generated."
        )


    st.divider()


    # ========================================================
    # 3. RETRIEVED MAINTENANCE MANUALS
    # ========================================================

    st.header(
        "📚 Retrieved Maintenance Instructions"
    )

    retrieved_chunks = result.get(
        "retrieved_chunks",
        []
    )

    if retrieved_chunks:

        for index, chunk in enumerate(
            retrieved_chunks,
            start=1
        ):

            instruction = chunk.get(
                "instruction",
                ""
            )

            document = chunk.get(
                "document_title",
                "Unknown Document"
            )

            section = chunk.get(
                "section",
                "Unknown Section"
            )

            page = chunk.get(
                "page",
                "Unknown Page"
            )


            with st.expander(
                f"Retrieved Result {index}",
                expanded=(index == 1)
            ):

                st.markdown(
                    f"**Maintenance Instruction:**  \n"
                    f"{instruction}"
                )

                st.markdown(
                    f"**Document:** {document}"
                )

                st.markdown(
                    f"**Section:** {section}"
                )

                st.markdown(
                    f"**Page:** {page}"
                )

    else:

        st.warning(
            "No relevant maintenance instructions were retrieved."
        )


    st.divider()


    # ========================================================
    # 4. PRESCRIPTIVE MAINTENANCE RECOMMENDATION
    # ========================================================

    st.header(
        "🛠️ Prescriptive Maintenance Recommendation"
    )

    recommendation = result.get(
        "maintenance_recommendation",
        {}
    )

    if recommendation:

        diagnosis = recommendation.get(
            "diagnosis",
            ""
        )

        action = recommendation.get(
            "action",
            ""
        )

        source = recommendation.get(
            "source",
            {}
        )


        # ----------------------------------------------------
        # DIAGNOSIS
        # ----------------------------------------------------

        st.subheader(
            "Diagnosis"
        )

        if diagnosis:

            st.info(
                diagnosis
            )

        else:

            st.warning(
                "No verified diagnosis available."
            )


        # ----------------------------------------------------
        # RECOMMENDED ACTION
        # ----------------------------------------------------

        st.subheader(
            "Recommended Action"
        )

        if action:

            st.success(
                action
            )

        else:

            st.warning(
                "No verified maintenance instruction found."
            )


        # ----------------------------------------------------
        # CITATION
        # ----------------------------------------------------

        if source:

            st.subheader(
                "📖 Source Citation"
            )

            citation_col1, citation_col2, citation_col3 = (
                st.columns(3)
            )

            with citation_col1:

                st.markdown(
                    "**Document**"
                )

                st.write(
                    source.get(
                        "document",
                        "Unknown"
                    )
                )

            with citation_col2:

                st.markdown(
                    "**Section**"
                )

                st.write(
                    source.get(
                        "section",
                        "Unknown"
                    )
                )

            with citation_col3:

                st.markdown(
                    "**Page**"
                )

                st.write(
                    source.get(
                        "page",
                        "Unknown"
                    )
                )

    else:

        st.warning(
            "No verified maintenance recommendation found."
        )


    st.divider()


    # ========================================================
    # 5. INVENTORY STATUS
    # ========================================================

    st.header(
        "📦 Spare Part Inventory Status"
    )

    tool_required = result.get(
        "tool_required",
        False
    )

    tool_result = result.get(
        "tool_result",
        {}
    )

    inventory = tool_result.get(
        "inventory",
        []
    )


    if tool_required and inventory:

        for item in inventory:

            part_id = item.get(
                "part_id",
                "Unknown"
            )

            available = item.get(
                "available",
                False
            )

            quantity = item.get(
                "quantity",
                0
            )


            col1, col2, col3 = st.columns(3)

            with col1:

                st.markdown(
                    f"**Spare Part:** `{part_id}`"
                )

            with col2:

                if available:

                    st.success(
                        "✓ Available"
                    )

                else:

                    st.error(
                        "✗ Unavailable"
                    )

            with col3:

                st.markdown(
                    f"**Stock Quantity:** {quantity}"
                )


        tool_recommendation = tool_result.get(
            "recommendation",
            ""
        )

        if tool_recommendation:

            st.info(
                tool_recommendation
            )

    else:

        st.info(
            "No spare-part lookup was required."
        )


    st.divider()


    # ========================================================
    # 6. MAINTENANCE TICKET
    # ========================================================

    st.header(
        "🎫 Maintenance Work Order"
    )

    ticket = result.get(
        "ticket",
        {}
    )


    if ticket:

        ticket_col1, ticket_col2 = st.columns(2)


        # ----------------------------------------------------
        # TICKET INFORMATION
        # ----------------------------------------------------

        with ticket_col1:

            st.markdown(
                "**Ticket ID**"
            )

            st.code(
                ticket.get(
                    "ticket_id",
                    "N/A"
                )
            )


            st.markdown(
                "**Status**"
            )

            status = ticket.get(
                "status",
                "Open"
            )

            if status.lower() == "open":

                st.success(
                    status
                )

            else:

                st.info(
                    status
                )


        # ----------------------------------------------------
        # REPAIR SUMMARY
        # ----------------------------------------------------

        with ticket_col2:

            st.markdown(
                "**Repair Summary**"
            )

            repair_summary = ticket.get(
                "repair_summary",
                recommendation.get(
                    "action",
                    ""
                )
            )

            st.write(
                repair_summary
            )


        st.success(
            "✓ Maintenance work order generated successfully."
        )


        # ----------------------------------------------------
        # TICKET JSON
        # ----------------------------------------------------

        with st.expander(
            "View Complete Ticket Data"
        ):

            st.json(
                ticket
            )


    else:

        st.warning(
            "No maintenance ticket was generated."
        )


    st.divider()


    # ========================================================
    # 7. COMPLETE WORKFLOW
    # ========================================================

    st.header(
        "🔄 Complete Agent Workflow"
    )

    workflow_col1, workflow_col2, workflow_col3, workflow_col4, workflow_col5 = (
        st.columns(5)
    )


    with workflow_col1:

        st.markdown(
            """
            ### 1️⃣

            **IoT Alert**

            Machine sensor data
            """
        )


    with workflow_col2:

        st.markdown(
            """
            ### 2️⃣

            **RAG Retrieval**

            ChromaDB manual search
            """
        )


    with workflow_col3:

        st.markdown(
            """
            ### 3️⃣

            **Recommendation**

            Citation-aware action
            """
        )


    with workflow_col4:

        st.markdown(
            """
            ### 4️⃣

            **Inventory**

            Spare-part check
            """
        )


    with workflow_col5:

        st.markdown(
            """
            ### 5️⃣

            **Ticket**

            Work-order generation
            """
        )


# ============================================================
# INITIAL SCREEN
# ============================================================

else:

    st.info(
        """
        Enter the IoT sensor alert details in the sidebar
        and click **🚀 Analyze Maintenance Alert** to start
        the Prescriptive Maintenance workflow.
        """
    )


    st.header(
        "System Components"
    )

    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            """
            ### 🔎 RAG Retrieval

            Retrieves relevant maintenance instructions
            from the ChromaDB vector database with
            document, section, and page citations.
            """
        )


    with col2:

        st.markdown(
            """
            ### 📦 Inventory Tool

            Automatically detects relevant spare parts
            and checks their availability and stock
            quantity.
            """
        )


    with col3:

        st.markdown(
            """
            ### 🎫 Maintenance Ticket

            Generates a maintenance work-order ticket
            containing the repair summary and required
            spare parts.
            """
        )