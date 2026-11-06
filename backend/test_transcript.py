
import json
from pathlib import Path

from app.services.transcript_service import TranscriptService


VIDEO_ID = "xB1C1xZZW4k"


def main():

    service = TranscriptService()

    print("Fetching YouTube transcript...")

    result = service.extract_transcript(VIDEO_ID)

    output_dir = Path("data/transcripts")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{VIDEO_ID}.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print("\nTranscript extracted successfully!")

    print("Video ID:", result["video_id"])
    print("Language:", result["language"])
    print("Language code:", result["language_code"])
    print("Auto-generated:", result["is_generated"])
    print("Total segments:", result["total_segments"])

    print("\nFirst 5 transcript segments:\n")

    for segment in result["transcript"][:5]:
        print(
            f"[{segment['start']:.2f}s] "
            f"{segment['text']}"
        )

    print("\nSaved transcript to:", output_file)


if __name__ == "__main__":
    main()
