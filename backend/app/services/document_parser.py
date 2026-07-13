"""
Document parsing service.

Responsible for turning industrial maintenance manual PDFs into clean,
page-aware text chunks that preserve tables (converted to a readable
markdown-like layout) so that downstream retrieval keeps technical
specifications intact instead of mangling them into unreadable text soup.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ParsedChunk:
    text: str
    source: str
    page: int
    chunk_index: int
    metadata: dict = field(default_factory=dict)


def _table_to_markdown(table: list[list[str | None]]) -> str:
    """Render a pdfplumber table (list of rows) as a markdown table string."""
    if not table:
        return ""
    rows = [[(cell or "").strip().replace("\n", " ") for cell in row] for row in table]
    header, *body = rows
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def extract_pages(pdf_path: str) -> list[dict]:
    """
    Extract per-page content: body text (via PyMuPDF, fast & reliable) and
    tables (via pdfplumber, which is far more accurate for tabular layouts).
    Tables are appended to the page text as markdown so a table's structure
    survives the chunking/embedding step instead of collapsing into noise.
    """
    pages: list[dict] = []
    doc = fitz.open(pdf_path)
    try:
        with pdfplumber.open(pdf_path) as plumber_doc:
            for page_index in range(len(doc)):
                fitz_page = doc[page_index]
                text = fitz_page.get_text("text").strip()

                tables_md = []
                try:
                    plumber_page = plumber_doc.pages[page_index]
                    for table in plumber_page.extract_tables():
                        md = _table_to_markdown(table)
                        if md:
                            tables_md.append(md)
                except Exception as exc:  # pragma: no cover - defensive
                    logger.warning("Table extraction failed on page %s: %s", page_index + 1, exc)

                combined = text
                if tables_md:
                    combined += "\n\n[TABLE]\n" + "\n\n[TABLE]\n".join(tables_md)

                pages.append({"page": page_index + 1, "text": combined})
    finally:
        doc.close()

    return pages


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Simple sliding-window chunker on whitespace-normalised text."""
    words = text.split()
    if not words:
        return []

    chunks = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]
        if not chunk_words:
            continue
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break
    return chunks


def parse_manual(pdf_path: str) -> list[ParsedChunk]:
    """Parse a manual PDF into page-aware, citation-ready chunks."""
    source_name = Path(pdf_path).name
    pages = extract_pages(pdf_path)

    parsed_chunks: list[ParsedChunk] = []
    for page in pages:
        page_chunks = chunk_text(page["text"], settings.chunk_size, settings.chunk_overlap)
        for idx, chunk in enumerate(page_chunks):
            if not chunk.strip():
                continue
            parsed_chunks.append(
                ParsedChunk(
                    text=chunk,
                    source=source_name,
                    page=page["page"],
                    chunk_index=idx,
                    metadata={"source": source_name, "page": page["page"]},
                )
            )

    logger.info("Parsed %s into %s chunks across %s pages", source_name, len(parsed_chunks), len(pages))
    return parsed_chunks
