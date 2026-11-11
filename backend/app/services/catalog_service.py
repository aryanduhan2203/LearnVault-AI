
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


class CatalogService:

    def get_playlists(self):
        playlist_dir = DATA_DIR / "playlists"

        playlists = []

        for file_path in playlist_dir.glob("*.json"):
            with file_path.open("r", encoding="utf-8") as file:
                playlist = json.load(file)

            playlists.append({
                "playlist_id": playlist["playlist_id"],
                "playlist_title": playlist["playlist_title"],
                "total_videos": playlist["total_videos"]
            })

        return playlists

    def get_playlist_videos(self, playlist_id: str):
        if not playlist_id or Path(playlist_id).name != playlist_id:
            raise ValueError("Invalid playlist ID")

        file_path = DATA_DIR / "playlists" / f"{playlist_id}.json"

        if not file_path.is_file():
            return None

        with file_path.open("r", encoding="utf-8") as file:
            playlist = json.load(file)

        return {
            "playlist_id": playlist["playlist_id"],
            "playlist_title": playlist["playlist_title"],
            "total_videos": playlist["total_videos"],
            "videos": playlist["videos"]
        }

    def get_video_transcript(self, video_id: str):
        if not video_id or Path(video_id).name != video_id:
            raise ValueError("Invalid video ID")

        file_path = DATA_DIR / "transcripts" / f"{video_id}.json"

        if not file_path.is_file():
            return None

        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
