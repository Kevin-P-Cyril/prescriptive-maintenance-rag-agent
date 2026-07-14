import chromadb

# Create a persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Create or load the collection
collection = client.get_or_create_collection(name="maintenance_docs")

# Search function
def search(query):
    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    print("\nTop 3 Results:\n")

    for i, doc in enumerate(results["documents"][0], start=1):
        print(f"{i}. {doc}\n")


# Test
search("motor overheating fix")