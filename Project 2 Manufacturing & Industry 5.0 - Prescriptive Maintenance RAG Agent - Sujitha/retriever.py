"""
retriever.py

Citation-aware retrieval pipeline for the
Prescriptive Maintenance RAG Agent.
"""

from typing import List, Dict
import chromadb


class ManualRetriever:
    """
    Retrieves relevant maintenance manual chunks
    together with citation metadata.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="maintenance_docs"
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Retrieve relevant maintenance instructions
        with document title, section and page citation.
        """

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        retrieved_results = []

        for document, metadata in zip(documents, metadatas):

            if not metadata:
                continue

            retrieved_results.append({
                "instruction": document,
                "document_title": metadata.get(
                    "document_title",
                    "Unknown Document"
                ),
                "section": metadata.get(
                    "section",
                    "Unknown Section"
                ),
                "page": metadata.get(
                    "page",
                    "Unknown Page"
                )
            })

        return retrieved_results

    def retrieve_with_citations(
        self,
        query: str,
        top_k: int = 3
    ) -> List[str]:
        """
        Return retrieved maintenance instructions
        formatted with citations.
        """

        results = self.retrieve(query, top_k)

        cited_results = []

        for result in results:

            citation = (
                f"{result['instruction']}\n"
                f"Source: {result['document_title']}, "
                f"Section: {result['section']}, "
                f"Page: {result['page']}"
            )

            cited_results.append(citation)

        return cited_results


if __name__ == "__main__":

    retriever = ManualRetriever()

    query = (
        "TURBINE-01 error code E-404 "
        "temperature 105°C vibration amplitude 4.8 mm/s "
        "repair procedure troubleshooting guide"
    )

    print("\n===== CITATION-AWARE RETRIEVAL TEST =====")

    results = retriever.retrieve_with_citations(query)

    if not results:
        print("No cited results found.")
    else:
        for index, result in enumerate(results, start=1):
            print(f"\n--- Result {index} ---")
            print(result)

    print("\n===== RETRIEVAL COMPLETE =====")