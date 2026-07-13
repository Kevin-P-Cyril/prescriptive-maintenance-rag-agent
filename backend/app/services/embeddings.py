"""
Embeddings service.

Uses Sentence-Transformers running fully locally (no API key, no cost).
The model weights are downloaded once from Hugging Face on first run and
then cached, so subsequent runs work fully offline.
"""
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import get_settings

settings = get_settings()


@lru_cache
def get_embedding_function() -> HuggingFaceEmbeddings:
    """Return a cached embedding function backed by a local ST model."""
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
