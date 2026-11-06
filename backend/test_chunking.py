
import json
from pathlib import Path

from app.services.chunking_service import ChunkingService


VIDEO_ID = "xB1C1xZZW4k"


def main():

    transcript_file = Path(
        f"data/transcripts/{VIDEO_ID}.json"
    )

    with open(transcript_file, "r", encoding="utf-8") as file:
        transcript_data = json.load(file)

    service = ChunkingService(
        chunk_size=150,
        overlap=30
    )

    chunks = service.create_chunks(transcript_data)

    output_dir = Path("data/chunks")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{VIDEO_ID}_chunks.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            chunks,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nChunking completed!")

    print("Video ID:", VIDEO_ID)
    print("Transcript segments:", len(transcript_data["transcript"]))
    print("Total chunks:", len(chunks))

    print("\nFirst 3 chunks:\n")

    for chunk in chunks[:3]:

        print("Chunk ID:", chunk["chunk_id"])
        print("Start:", chunk["start_time"])
        print("End:", chunk["end_time"])
        print("Words:", chunk["word_count"])
        print("Text:", chunk["text"][:300])
        print("-" * 50)

    print("\nSaved to:", output_file)


if __name__ == "__main__":
    main()
