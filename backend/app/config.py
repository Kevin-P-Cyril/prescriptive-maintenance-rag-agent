"""
Central configuration for the Prescriptive Maintenance Assistant.

All values are loaded from environment variables / .env file so that no
secrets or machine-specific paths are hard-coded. Every default here uses
free, locally-running components (Ollama + Sentence-Transformers + Chroma)
so the project incurs zero API cost.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM (local via Ollama - free)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Embeddings (local via Sentence-Transformers - free)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector store
    chroma_persist_dir: str = str(BASE_DIR / "data" / "chroma_db")
    chroma_collection_name: str = "maintenance_manuals"

    # Documents
    manuals_dir: str = str(BASE_DIR / "data" / "manuals")
    inventory_file: str = str(BASE_DIR / "data" / "inventory.json")

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 120

    # Retrieval
    retrieval_top_k: int = 4

    # API
    app_env: str = "development"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
