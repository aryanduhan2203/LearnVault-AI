
import json
from pathlib import Path
from collections import Counter

from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
CHUNK_DIR = BASE_DIR / "data" / "chunks"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    tokenizer = model.tokenizer
    max_length = model.max_seq_length

    print("Model loaded successfully.")
    print("Maximum sequence length:", max_length)

    chunk_files = sorted(CHUNK_DIR.glob("*_chunks.json"))

    total_chunks = 0
    safe_chunks = 0
    oversized_chunks = 0

    token_counts = []
    oversized_examples = []

    print("\nChecking chunk token counts...\n")

    for chunk_file in chunk_files:

        with open(chunk_file, "r", encoding="utf-8") as file:
            chunks = json.load(file)

        for chunk in chunks:

            text = chunk["text"]

            encoded = tokenizer(
                text,
                add_special_tokens=True,
                truncation=False
            )

            token_count = len(encoded["input_ids"])

            total_chunks += 1
            token_counts.append(token_count)

            if token_count <= max_length:
                safe_chunks += 1
            else:
                oversized_chunks += 1

                if len(oversized_examples) < 10:
                    oversized_examples.append({
                        "video_id": chunk["video_id"],
                        "chunk_id": chunk["chunk_id"],
                        "word_count": chunk["word_count"],
                        "token_count": token_count
                    })

    print("========== TOKENIZER VALIDATION ==========")
    print("Videos checked:", len(chunk_files))
    print("Total chunks:", total_chunks)
    print("Safe chunks:", safe_chunks)
    print("Oversized chunks:", oversized_chunks)

    if token_counts:
        print("Minimum tokens:", min(token_counts))
        print("Maximum tokens:", max(token_counts))
        print("Average tokens:", round(sum(token_counts) / len(token_counts), 2))

    print("\n========== OVERSIZED CHUNK EXAMPLES ==========")

    if oversized_examples:
        for example in oversized_examples:
            print(example)
    else:
        print("No oversized chunks found.")

    print("\n========== TOKEN COUNT DISTRIBUTION ==========")

    ranges = {
        "0-64": 0,
        "65-128": 0,
        "129-192": 0,
        "193-256": 0,
        "257+": 0
    }

    for count in token_counts:
        if count <= 64:
            ranges["0-64"] += 1
        elif count <= 128:
            ranges["65-128"] += 1
        elif count <= 192:
            ranges["129-192"] += 1
        elif count <= 256:
            ranges["193-256"] += 1
        else:
            ranges["257+"] += 1

    for label, count in ranges.items():
        print(f"{label} tokens: {count}")


if __name__ == "__main__":
    main()
