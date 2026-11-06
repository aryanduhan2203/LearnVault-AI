
import json
from pathlib import Path

from app.services.youtube_service import YouTubeService


PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLui3EUkuMTPgZcV0QhQrOcwMPcBCcd_Q1"


def main():

    service = YouTubeService()

    print("Extracting YouTube playlist metadata...")

    result = service.extract_playlist(PLAYLIST_URL)

    output_dir = Path("data/playlists")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{result['playlist_id']}.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print("\nPlaylist extracted successfully!")

    print("Playlist ID:", result["playlist_id"])
    print("Playlist title:", result["playlist_title"])
    print("Total videos:", result["total_videos"])

    print("\nFirst 5 videos:\n")

    for video in result["videos"][:5]:
        print(video["video_id"], "-", video["title"])

    print("\nSaved to:", output_file)


if __name__ == "__main__":
    main()
