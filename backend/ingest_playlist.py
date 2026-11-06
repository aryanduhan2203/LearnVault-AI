
import json
import time
from pathlib import Path

from app.services.transcript_service import TranscriptService


PLAYLIST_FILE = Path(
    "data/playlists/PLui3EUkuMTPgZcV0QhQrOcwMPcBCcd_Q1.json"
)

TRANSCRIPT_DIR = Path("data/transcripts")
REPORT_FILE = Path("data/transcript_ingestion_report.json")


def main():

    with open(PLAYLIST_FILE, "r", encoding="utf-8") as file:
        playlist = json.load(file)

    videos = playlist["videos"]

    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    service = TranscriptService()

    successful = []
    failed = []
    skipped = []

    total = len(videos)

    print(f"Starting ingestion for {total} videos\n")

    for index, video in enumerate(videos, start=1):

        video_id = video["video_id"]
        title = video["title"]

        output_file = TRANSCRIPT_DIR / f"{video_id}.json"

        print(f"[{index}/{total}] Processing: {title}")

        if output_file.exists():
            print("Already processed. Skipping.\n")
            skipped.append(video_id)
            continue

        try:

            result = service.extract_transcript(video_id)

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(
                    result,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            successful.append({
                "video_id": video_id,
                "title": title,
                "segments": result["total_segments"],
                "language": result["language"],
                "is_generated": result["is_generated"]
            })

            print(
                f"Success! Segments: {result['total_segments']}"
            )

        except Exception as e:

            failed.append({
                "video_id": video_id,
                "title": title,
                "error": str(e)
            })

            print(f"Failed: {e}")

        print()

        time.sleep(0.5)

    report = {
        "playlist_id": playlist["playlist_id"],
        "playlist_title": playlist["playlist_title"],
        "total_videos": total,
        "successful": len(successful),
        "failed": len(failed),
        "skipped": len(skipped),
        "successful_videos": successful,
        "failed_videos": failed,
        "skipped_video_ids": skipped
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========== INGESTION SUMMARY ==========")
    print("Total videos:", total)
    print("Successful:", len(successful))
    print("Failed:", len(failed))
    print("Skipped:", len(skipped))
    print("Report saved:", REPORT_FILE)


if __name__ == "__main__":
    main()
