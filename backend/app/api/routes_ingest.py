"""API endpoint for uploading and ingesting new maintenance manual PDFs into the vector store."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.models.schemas import IngestResponse
from app.services.document_parser import parse_manual
from app.services.vector_store import add_chunks

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ingest", tags=["ingest"])
settings = get_settings()


@router.post("", response_model=IngestResponse)
async def ingest_manual(file: UploadFile = File(...)) -> IngestResponse:
    """Upload a PDF maintenance manual; it is parsed, chunked, embedded and stored in ChromaDB."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    manuals_dir = Path(settings.manuals_dir)
    manuals_dir.mkdir(parents=True, exist_ok=True)
    dest_path = manuals_dir / file.filename

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks = parse_manual(str(dest_path))
    indexed = add_chunks(chunks)
    pages = len({c.page for c in chunks})

    return IngestResponse(filename=file.filename, chunks_indexed=indexed, pages_parsed=pages)
