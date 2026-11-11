
import json
import numpy as np

from pathlib import Path
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent

CHUNK_DIR = BASE_DIR / "data" / "chunks"
OUTPUT_DIR = BASE_DIR / "data" / "embeddings"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

BATCH_SIZE = 16


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    all_chunks = []

    chunk_files = sorted(CHUNK_DIR.glob("*_chunks.json"))

    print("Reading chunk files...")

    for chunk_file in chunk_files:

        with open(chunk_file, "r", encoding="utf-8") as file:
            chunks = json.load(file)

        all_chunks.extend(chunks)

    print("Total chunks:", len(all_chunks))

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    print("\nGenerating embeddings...")

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        convert_to_numpy=True,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    print("\nSaving embeddings...")

    np.save(
        OUTPUT_DIR / "embeddings.npy",
        embeddings
    )

    with open(
        OUTPUT_DIR / "chunk_metadata.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========== EMBEDDING SUMMARY ==========")

    print("Total chunks:", len(all_chunks))
    print("Embedding shape:", embeddings.shape)
    print("Embedding dimensions:", embeddings.shape[1])
    print("Batch size:", BATCH_SIZE)

    print("Embeddings saved to:", OUTPUT_DIR / "embeddings.npy")
    print("Metadata saved to:", OUTPUT_DIR / "chunk_metadata.json")


if __name__ == "__main__":
    main()
