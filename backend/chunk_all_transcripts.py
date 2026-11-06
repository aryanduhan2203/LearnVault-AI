
import json
from pathlib import Path

from app.services.chunking_service import ChunkingService


BASE_DIR = Path(__file__).resolve().parent

TRANSCRIPT_DIR = BASE_DIR / "data" / "transcripts"
CHUNK_DIR = BASE_DIR / "data" / "chunks"
REPORT_PATH = BASE_DIR / "data" / "chunking_report.json"


def main():

    CHUNK_DIR.mkdir(parents=True, exist_ok=True)

    transcript_files = sorted(TRANSCRIPT_DIR.glob("*.json"))

    if not transcript_files:
        print("No transcript files found.")
        return

    chunking_service = ChunkingService(
        chunk_size=150,
        overlap=30
    )

    report = {
        "total_transcripts": len(transcript_files),
        "successful": 0,
        "failed": 0,
        "total_chunks": 0,
        "total_words": 0,
        "max_chunk_words": 0,
        "min_chunk_words": None,
        "videos": []
    }

    print(f"Found {len(transcript_files)} transcript files.\n")

    for index, transcript_file in enumerate(transcript_files, start=1):

        try:
            with open(transcript_file, "r", encoding="utf-8") as file:
                transcript_data = json.load(file)

            chunks = chunking_service.create_chunks(transcript_data)

            video_id = transcript_data["video_id"]

            output_path = CHUNK_DIR / f"{video_id}_chunks.json"

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(chunks, file, indent=4, ensure_ascii=False)

            word_counts = [
                chunk["word_count"]
                for chunk in chunks
            ]

            if not chunks:
                raise ValueError("No chunks were generated.")

            video_total_words = sum(word_counts)

            report["successful"] += 1
            report["total_chunks"] += len(chunks)
            report["total_words"] += video_total_words
            report["max_chunk_words"] = max(
                report["max_chunk_words"],
                max(word_counts)
            )

            current_min = min(word_counts)

            if report["min_chunk_words"] is None:
                report["min_chunk_words"] = current_min
            else:
                report["min_chunk_words"] = min(
                    report["min_chunk_words"],
                    current_min
                )

            report["videos"].append({
                "video_id": video_id,
                "transcript_file": transcript_file.name,
                "total_chunks": len(chunks),
                "total_words": video_total_words,
                "min_chunk_words": min(word_counts),
                "max_chunk_words": max(word_counts),
                "output_file": output_path.name,
                "status": "success"
            })

            print(
                f"[{index}/{len(transcript_files)}] "
                f"SUCCESS: {video_id} | "
                f"{len(chunks)} chunks"
            )

        except Exception as error:

            report["failed"] += 1

            report["videos"].append({
                "transcript_file": transcript_file.name,
                "status": "failed",
                "error": f"{type(error).__name__}: {error}"
            })

            print(
                f"[{index}/{len(transcript_files)}] "
                f"FAILED: {transcript_file.name} | {error}"
            )

    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\n========== CHUNKING SUMMARY ==========")
    print("Total transcripts:", report["total_transcripts"])
    print("Successful:", report["successful"])
    print("Failed:", report["failed"])
    print("Total chunks:", report["total_chunks"])
    print("Total words:", report["total_words"])
    print("Minimum chunk words:", report["min_chunk_words"])
    print("Maximum chunk words:", report["max_chunk_words"])
    print("Report saved to:", REPORT_PATH)


if __name__ == "__main__":
    main()
