import json
import os
from sentence_transformers import SentenceTransformer

# Input and output paths
INPUT_FILE = "data/chunks/chunks.json"
OUTPUT_FILE = "data/embeddings/embeddings.json"

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


def load_chunks(file_path: str):
    """Load chunks from JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_embeddings(chunks):
    """Generate embeddings for each chunk."""
    embeddings = []

    for chunk in chunks:
        vector = model.encode(chunk["text"]).tolist()

        embeddings.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "embedding": vector
        })

    return embeddings


def save_embeddings(data, output_path):
    """Save embeddings into JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def main():
    chunks = load_chunks(INPUT_FILE)

    embeddings = generate_embeddings(chunks)

    save_embeddings(embeddings, OUTPUT_FILE)

    print(f"Generated embeddings for {len(embeddings)} chunks.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()