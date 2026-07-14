import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Input and output file paths
INPUT_FILE = "data/parsed/sample_manual.txt"
OUTPUT_FILE = "data/chunks/chunks.json"

# Chunking configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def load_text(file_path: str) -> str:
    """
    Load parsed text from the parser output.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def split_text(text: str) -> list[str]:
    """
    Split text into overlapping chunks using LangChain.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return splitter.split_text(text)


def save_chunks(chunks: list[str], output_path: str) -> None:
    """
    Save chunks into JSON format.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = []

    for index, chunk in enumerate(chunks, start=1):
        data.append(
            {
                "chunk_id": index,
                "text": chunk
            }
        )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def main():
    text = load_text(INPUT_FILE)

    chunks = split_text(text)

    save_chunks(chunks, OUTPUT_FILE)

    print(f"Total Chunks: {len(chunks)}")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
