"""
CLI script to ingest every PDF manual in `data/manuals/` into the local
ChromaDB vector store. Run this once after adding new manuals, or whenever
you set up the project for the first time.

Usage:
    python ingest.py
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import get_settings  # noqa: E402
from app.services.document_parser import parse_manual  # noqa: E402
from app.services.vector_store import add_chunks, collection_count  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("ingest")


def main() -> None:
    settings = get_settings()
    manuals_dir = Path(settings.manuals_dir)
    manuals_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(manuals_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(
            "No PDF manuals found in %s. Add manuals there (or use the /api/ingest "
            "endpoint) before querying the assistant.",
            manuals_dir,
        )
        return

    total_chunks = 0
    for pdf_path in pdf_files:
        logger.info("Parsing %s ...", pdf_path.name)
        chunks = parse_manual(str(pdf_path))
        indexed = add_chunks(chunks)
        total_chunks += indexed
        logger.info("  -> indexed %s chunks", indexed)

    logger.info(
        "Ingestion complete. %s new chunks indexed. Collection now holds %s chunks total.",
        total_chunks,
        collection_count(),
    )


if __name__ == "__main__":
    main()
