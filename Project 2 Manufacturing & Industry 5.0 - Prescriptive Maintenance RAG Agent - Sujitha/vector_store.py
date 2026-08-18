import chromadb

# Create persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Create/load collection
collection = client.get_or_create_collection(
    name="maintenance_docs"
)


def add_maintenance_documents():
    """
    Add maintenance documents with citation metadata.
    """

    documents = [
        "Motor overheating can occur due to poor ventilation.",
        "Replace worn bearings to reduce vibration.",
        "Check lubrication levels regularly to avoid equipment failure."
    ]

    metadatas = [
        {
            "document_title": "Sample Maintenance Manual",
            "section": "Motor Overheating",
            "page": 1
        },
        {
            "document_title": "Sample Maintenance Manual",
            "section": "Bearing Maintenance",
            "page": 2
        },
        {
            "document_title": "Sample Maintenance Manual",
            "section": "Lubrication Maintenance",
            "page": 3
        }
    ]

    ids = ["1", "2", "3"]

    # Clear existing documents
    existing = collection.get()

    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    # Add documents with metadata
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print("Maintenance documents added successfully.")
    print(f"Total documents: {collection.count()}")


def search(query, top_k=3):
    """
    Search maintenance documents.
    """

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    print("\nTop Results:\n")

    for i, document in enumerate(results["documents"][0], start=1):

        metadata = results["metadatas"][0][i - 1]

        print(f"{i}. {document}")
        print(f"   Document: {metadata['document_title']}")
        print(f"   Section: {metadata['section']}")
        print(f"   Page: {metadata['page']}")
        print()


if __name__ == "__main__":

    add_maintenance_documents()

    search("motor overheating repair")