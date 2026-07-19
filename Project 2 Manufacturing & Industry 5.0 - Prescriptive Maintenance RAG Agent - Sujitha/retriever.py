"""
retriever.py

Wrapper around the existing ChromaDB search.
Uses the same collection created in vector_store.py
but returns results instead of printing them.
"""

from typing import List
import chromadb


class ManualRetriever:
    """
    Retrieves the most relevant manual chunks
    from the ChromaDB vector database.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")

        self.collection = self.client.get_or_create_collection(
            name="maintenance_docs"
        )

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve the top matching manual chunks.

        Parameters
        ----------
        query : str
            Natural language search query.

        top_k : int
            Number of documents to retrieve.

        Returns
        -------
        List[str]
            List of retrieved manual chunks.
        """

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        return results["documents"][0]