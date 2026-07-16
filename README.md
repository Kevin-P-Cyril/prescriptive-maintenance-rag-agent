# Manufacturing & Industry 5.0 – Prescriptive Maintenance RAG Agent

## Overview

The Prescriptive Maintenance RAG Agent is an Agentic Retrieval-Augmented Generation (RAG) application developed for Industry 5.0 manufacturing environments. The system assists maintenance engineers by automatically retrieving relevant repair procedures from industrial equipment manuals and generating prescriptive maintenance recommendations.

Instead of manually searching through hundreds of pages of machinery manuals after an equipment failure, the AI agent analyzes a machine alert, retrieves the relevant technical documentation, and produces a step-by-step repair guide along with the required tools and spare parts. :contentReference[oaicite:2]{index=2}

---

# Problem Statement

Traditional predictive maintenance systems can detect that a machine is likely to fail, but they do not provide guidance on how to repair it.

Maintenance engineers must manually search large PDF manuals to identify the correct troubleshooting procedure, increasing the Mean Time to Repair (MTTR).

This project addresses that problem by combining Retrieval-Augmented Generation (RAG), Large Language Models, and Agentic AI to automatically retrieve the appropriate maintenance procedure and generate an actionable repair plan. :contentReference[oaicite:3]{index=3}

---

# Business Objective

The primary objective of this project is to reduce Mean Time to Repair (MTTR) by enabling maintenance engineers to quickly access accurate repair instructions extracted from technical manuals.

The system is evaluated based on:

- Retrieval accuracy
- Correct identification of maintenance procedures
- Context-aware repair recommendations
- Reduction of manual document searching
- Reliable grounding without hallucinating maintenance or safety procedures :contentReference[oaicite:4]{index=4}

---

# User Personas

### Maintenance Technician

- Receives equipment failure alerts.
- Queries the AI assistant for repair procedures.
- Obtains standard operating procedures (SOPs), required tools, and spare parts.

### Plant Manager

- Reviews AI-generated maintenance recommendations.
- Uses the generated repair plan to minimize downtime.
- Automates maintenance work-order preparation. :contentReference[oaicite:5]{index=5}

---

# Technology Stack

## Backend

- Python
- FastAPI

## LLM

- Google Gemini API

## RAG

- LangChain
- ChromaDB
- HuggingFace Embeddings

## Document Parsing

- LlamaParse
- PyMuPDF (Fallback)

## Agent Framework

- LangGraph

## Frontend

- Streamlit

---

# System Architecture

```
Industrial PDF Manuals
          │
          ▼
 Document Parser
(LlamaParse / PyMuPDF)
          │
          ▼
 Parsed Text
          │
          ▼
 Text Chunking
          │
          ▼
 Embedding Generation
          │
          ▼
 ChromaDB Vector Store
          │
          ▼
 Retriever
          │
          ▼
 LangGraph Agent
          │
          ▼
 Google Gemini
          │
          ▼
 Prescriptive Repair Plan
          │
          ▼
 Inventory Tool
          │
          ▼
 Streamlit UI
```

---

# Minimum Viable Product (MVP)

The application includes:

- Parsing industrial PDF manuals
- Preserving document structure during extraction
- Chunking documents for semantic search
- Generating vector embeddings
- Storing vectors in ChromaDB
- Retrieving relevant maintenance procedures
- Using an LLM to generate repair recommendations
- Producing a prescriptive maintenance plan for the user :contentReference[oaicite:6]{index=6}

---

# Project Structure

```
prescriptive-maintenance-rag-agent/

│
├── data/
│   ├── raw/
│   ├── parsed/
│   └── chunks/
│
├── docs/
│
├── tests/
│
├── parser.py
├── chunker.py
├── embedder.py
├── vector_store.py
├── retriever.py
├── agent.py
├── app.py
├── config.py
├── utils.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Four Week Development Roadmap

## Week 1

- Collect industrial machinery manuals
- Parse PDF manuals
- Extract clean text
- Split documents into chunks
- Generate embeddings
- Store embeddings in ChromaDB

## Week 2

- Integrate simulated IoT telemetry
- Receive machine alerts
- Convert alerts into semantic search queries

Example:

```json
{
  "machine_id": "PUMP-01",
  "error_code": "E-404",
  "temperature": 105
}
```

## Week 3

- Build LangGraph workflow
- Query maintenance manuals
- Retrieve repair procedures
- Generate prescriptive maintenance instructions
- Cite the source manual and page number

## Week 4

- Integrate inventory lookup tool
- Check spare part availability
- Deploy Streamlit user interface
- Final GitHub documentation and deployment :contentReference[oaicite:7]{index=7}

---

# Future Enhancements

- Multi-manual support
- Real-time IoT integration
- Tool calling for inventory management
- Automated work-order generation
- Multi-agent reasoning workflow
- Maintenance history tracking
- Dashboard analytics

---

# Contributors

- Kevin
- Sujitha
- Naresh
- Siddarth

---

# License

This project is developed as part of the Infotact Advanced Generative AI Internship Program for educational and learning purposes.
