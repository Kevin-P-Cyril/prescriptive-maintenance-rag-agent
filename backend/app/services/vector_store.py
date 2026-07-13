"""
Vector store service.

Wraps a local, persistent ChromaDB collection (no server, no cost) used to
store and retrieve embedded chunks of the maintenance manuals.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from langchain_chroma import Chroma

from app.config import get_settings
from app.services.document_parser import ParsedChunk
from app.services.embeddings import get_embedding_function

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache
def get_vectorstore() -> Chroma:
    """Return a cached handle to the persistent Chroma collection."""
    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embedding_function(),
        persist_directory=settings.chroma_persist_dir,
    )


def add_chunks(chunks: list[ParsedChunk]) -> int:
    """Embed and persist a batch of parsed chunks. Returns number indexed."""
    if not chunks:
        return 0

    store = get_vectorstore()
    texts = [c.text for c in chunks]
    metadatas = [c.metadata for c in chunks]
    ids = [f"{c.source}-p{c.page}-c{c.chunk_index}" for c in chunks]

    store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    logger.info("Indexed %s chunks into ChromaDB", len(chunks))
    return len(chunks)


def similarity_search(query: str, k: int | None = None, machine_type: str | None = None):
    """Retrieve the top-k most relevant chunks for a query."""
    store = get_vectorstore()
    top_k = k or settings.retrieval_top_k
    filt = {"source": machine_type} if machine_type else None
    try:
        results = store.similarity_search(query, k=top_k, filter=filt)
    except Exception:
        # Filter not matching any metadata field - fall back to unfiltered search
        results = store.similarity_search(query, k=top_k)
    return results


def collection_count() -> int:
    store = get_vectorstore()
    try:
        return store._collection.count()  # noqa: SLF001 - Chroma has no public counter
    except Exception:
        return 0
