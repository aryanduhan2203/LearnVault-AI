
import json
import numpy as np

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

EMBEDDING_FILE = (
    BASE_DIR / "data" / "embeddings" / "embeddings.npy"
)

METADATA_FILE = (
    BASE_DIR / "data" / "embeddings" / "chunk_metadata.json"
)


def main():

    print("Loading embeddings...")

    embeddings = np.load(EMBEDDING_FILE)

    print("Loading metadata...")

    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    print("\n========== VALIDATION ==========")

    print("Embedding shape:", embeddings.shape)
    print("Metadata records:", len(metadata))

    assert len(embeddings) == len(metadata), (
        "Embedding and metadata counts do not match!"
    )

    assert embeddings.shape[1] == 384, (
        "Unexpected embedding dimension!"
    )

    assert np.isfinite(embeddings).all(), (
        "Embeddings contain NaN or infinite values!"
    )

    norms = np.linalg.norm(embeddings, axis=1)

    print("Minimum vector norm:", norms.min())
    print("Maximum vector norm:", norms.max())

    assert np.allclose(norms, 1.0, atol=1e-5), (
        "Embeddings are not normalized!"
    )

    print("\n========== SAMPLE ALIGNMENT ==========")

    for i in [0, 1, 2, 100, 500, 1000, 2000]:

        if i >= len(metadata):
            continue

        print(f"\nIndex: {i}")
        print("Video ID:", metadata[i]["video_id"])
        print("Chunk ID:", metadata[i]["chunk_id"])
        print("Text:", metadata[i]["text"][:150])
        print("Vector dimensions:", len(embeddings[i]))

    print("\nAll embedding validations passed!")


if __name__ == "__main__":
    main()
