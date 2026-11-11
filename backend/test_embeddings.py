
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent

CHUNK_FILE = (
    BASE_DIR
    / "data"
    / "chunks"
    / "xB1C1xZZW4k_chunks.json"
)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Model loaded successfully.")

    with open(CHUNK_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    print("Total chunks available:", len(chunks))

    test_chunks = chunks[:5]

    texts = [
        chunk["text"]
        for chunk in test_chunks
    ]

    print("\nGenerating embeddings for 5 chunks...")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    print("\n========== EMBEDDING RESULTS ==========")

    print("Number of chunks:", len(texts))
    print("Embedding shape:", embeddings.shape)
    print("Dimensions per embedding:", embeddings.shape[1])

    for index, embedding in enumerate(embeddings):

        print(f"\nChunk {index}")
        print("Video ID:", test_chunks[index]["video_id"])
        print("Chunk ID:", test_chunks[index]["chunk_id"])
        print("Vector dimensions:", len(embedding))
        print("First 10 values:", embedding[:10].tolist())


if __name__ == "__main__":
    main()
