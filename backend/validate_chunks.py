
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CHUNK_DIR = BASE_DIR / "data" / "chunks"


def main():

    chunk_files = sorted(CHUNK_DIR.glob("*_chunks.json"))

    total_chunks = 0
    invalid_chunks = 0
    seen_ids = set()

    for chunk_file in chunk_files:

        with open(chunk_file, "r", encoding="utf-8") as file:
            chunks = json.load(file)

        for chunk in chunks:

            total_chunks += 1
            errors = []

            if not chunk.get("text", "").strip():
                errors.append("Empty text")

            if chunk.get("start_time") is None:
                errors.append("Missing start time")

            if chunk.get("end_time") is None:
                errors.append("Missing end time")

            if (
                chunk.get("start_time") is not None
                and chunk.get("end_time") is not None
                and chunk["end_time"] <= chunk["start_time"]
            ):
                errors.append("Invalid timestamps")

            if not chunk.get("video_id"):
                errors.append("Missing video ID")

            if chunk.get("chunk_id") is None:
                errors.append("Missing chunk ID")

            unique_id = (
                chunk.get("video_id"),
                chunk.get("chunk_id")
            )

            if unique_id in seen_ids:
                errors.append("Duplicate chunk ID")

            seen_ids.add(unique_id)

            if errors:
                invalid_chunks += 1
                print(
                    f"INVALID: {chunk_file.name} "
                    f"| Chunk {chunk.get('chunk_id')} "
                    f"| {', '.join(errors)}"
                )

    print("\n========== CHUNK VALIDATION ==========")
    print("Videos checked:", len(chunk_files))
    print("Total chunks:", total_chunks)
    print("Invalid chunks:", invalid_chunks)
    print("Valid chunks:", total_chunks - invalid_chunks)

    if invalid_chunks == 0:
        print("\nAll chunks passed validation.")
    else:
        print("\nSome chunks need attention.")


if __name__ == "__main__":
    main()
