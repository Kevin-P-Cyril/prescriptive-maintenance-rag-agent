# Prescriptive Maintenance Assistant

An agentic **Retrieval-Augmented Generation (RAG)** system for industrial machinery
maintenance. It receives simulated **IoT alerts**, retrieves the relevant repair
procedure from technical manuals, checks **spare-parts inventory** via a tool call, and
generates a **cited, step-by-step repair procedure** — all through a **LangGraph** agent.

> 💸 **Zero API cost.** Every AI component runs locally and for free:
> - **LLM:** [Ollama](https://ollama.com) running an open model (`llama3.2` by default) — replaces paid Gemini/OpenAI APIs.
> - **Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`), local, no key required.
> - **Vector DB:** ChromaDB, an embedded local database — no hosted service or key.
> - **Inventory "ERP":** a local mock JSON file standing in for a real (paid) inventory system.

---

## Architecture

```
                     ┌─────────────────────┐
   IoT Alert  ─────▶ │   FastAPI backend    │
 (simulated JSON)    │  /api/alerts /chat   │
                     └──────────┬───────────┘
                                │
                       ┌────────▼─────────┐
                       │   LangGraph Agent │
                       │                   │
                       │ 1. analyze_alert  │
                       │ 2. retrieve docs  │──▶ ChromaDB (embedded manual chunks)
                       │ 3. find parts     │
                       │ 4. check_inventory│──▶ Mock spare-parts inventory (tool call)
                       │ 5. generate_steps │──▶ Ollama (local LLM)
                       └────────┬──────────┘
                                │
                     ┌──────────▼───────────┐
                     │   React frontend      │
                     │ (Alert console, chat,  │
                     │  inventory browser)    │
                     └────────────────────────┘
```

**Document ingestion pipeline:** PDF manuals → PyMuPDF (text) + pdfplumber (tables,
rendered as markdown so specs survive chunking) → sliding-window chunker → Sentence-
Transformer embeddings → ChromaDB, with `source` + `page` metadata preserved on every
chunk so every generated claim can be cited back to an exact manual page.

---

## Project structure

```
pma/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph state, nodes, graph wiring
│   │   ├── api/             # FastAPI routers (alerts, chat, inventory, ingest)
│   │   ├── models/          # Pydantic schemas
│   │   ├── services/        # document parsing, embeddings, vector store, LLM, inventory
│   │   ├── config.py
│   │   └── main.py
│   ├── data/
│   │   ├── manuals/         # PDF manuals (sample one is auto-generated)
│   │   ├── chroma_db/       # persisted vector store (generated)
│   │   └── inventory.json   # mock spare-parts inventory
│   ├── scripts/generate_sample_manual.py
│   ├── ingest.py            # CLI: (re)index all manuals into ChromaDB
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # React (Vite) app
│   └── src/
│       ├── components/      # AlertForm, DiagnosticOutput, ChatPanel, InventoryPanel...
│       ├── App.jsx
│       └── api.js
├── setup.bat / setup.sh     # one-time install (Windows / macOS-Linux)
├── run.bat / run.sh         # start backend + frontend
└── README.md
```

---

## Prerequisites

| Tool     | Why                                | Get it |
|----------|-------------------------------------|--------|
| Python 3.10+ | Backend (FastAPI, LangGraph, RAG) | https://www.python.org/downloads/ |
| Node.js 18+  | Frontend (React/Vite)             | https://nodejs.org/ |
| Ollama       | **Free** local LLM runtime        | https://ollama.com/download |

No API keys, no billing accounts, no cloud services required.

---

## Quick start (Windows)

```bat
setup.bat
run.bat
```

`setup.bat` will:
1. Create a Python virtual environment and install backend dependencies.
2. Install frontend npm dependencies.
3. Pull the local LLM model via Ollama (`ollama pull llama3.2`).
4. Generate a sample CNC machine manual PDF and ingest it into ChromaDB.

`run.bat` starts Ollama, the FastAPI backend (`localhost:8000`), and the React frontend
(`localhost:5173`) each in their own window, then opens the app in your browser.

## Quick start (macOS / Linux)

```bash
./setup.sh
./run.sh
```

---

## Using the app

1. **Alert Console** — submit a simulated IoT alert (machine ID, error code, description,
   severity, sensor reading). The agent retrieves the matching manual section, checks
   spare-parts stock, and returns a diagnosis, numbered repair steps, and page citations.
2. **Ask the Manuals** — free-form Q&A chat over the ingested manuals, with citations.
3. **Inventory** — browse the mock spare-parts warehouse used by the agent's tool call.

Try the pre-filled sample alert (`CNC-204`, error `E-108`, spindle overheating) — it
matches the bundled sample manual out of the box.

### Adding your own manuals

Drop PDF files into `backend/data/manuals/` and run:

```bash
cd backend
python ingest.py
```

or upload one directly via `POST /api/ingest` (see the interactive API docs at
`http://localhost:8000/docs`).

---

## Swapping the local LLM model

Any [Ollama model](https://ollama.com/library) works. Edit `backend/.env`:

```
OLLAMA_MODEL=llama3.2
```

then `ollama pull <model_name>` and restart the backend. Larger models (e.g. `llama3.1:8b`,
`mistral`, `qwen2.5`) generally give better reasoning at the cost of speed/RAM.

---

## Tech stack

Backend: **Python, FastAPI** · Frontend: **React (Vite)** · Document parsing:
**PyMuPDF, pdfplumber** · RAG framework: **LangChain** · Embeddings:
**Sentence-Transformers** · Vector DB: **ChromaDB** · LLM: **Ollama (local, free)** ·
Agent framework: **LangGraph** · Utilities: **python-dotenv, Git**

---

## Notes on production readiness

- All services are modular and independently testable (`app/services/*`, `app/agent/*`).
- Configuration is centralized in `app/config.py` and driven entirely by environment
  variables (`.env`), no hard-coded paths or secrets.
- The LLM call is wrapped with a clear, actionable error (`LLMUnavailableError`) rather
  than crashing the API if Ollama isn't running.
- CORS, structured Pydantic request/response models, and OpenAPI docs (`/docs`) are
  included out of the box.
- `data/chroma_db/` and `.env` are git-ignored; only source code and the sample manual
  are versioned.
