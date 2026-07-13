"""
Prescriptive Maintenance Assistant - FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_alerts, routes_chat, routes_ingest, routes_inventory
from app.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Prescriptive Maintenance Assistant",
    description=(
        "An agentic RAG system that receives simulated IoT machine alerts, retrieves "
        "relevant repair procedures from industrial maintenance manuals, checks spare-parts "
        "inventory, and generates cited, step-by-step repair instructions."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_alerts.router)
app.include_router(routes_chat.router)
app.include_router(routes_inventory.router)
app.include_router(routes_ingest.router)


@app.get("/", tags=["health"])
def root():
    return {
        "status": "ok",
        "service": "Prescriptive Maintenance Assistant",
        "docs": "/docs",
    }


@app.get("/api/health", tags=["health"])
def health_check():
    from app.services.llm_service import is_ollama_available
    from app.services.vector_store import collection_count

    return {
        "status": "ok",
        "ollama_reachable": is_ollama_available(),
        "indexed_chunks": collection_count(),
    }
