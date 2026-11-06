
import yt_dlp


class YouTubeService:

    def extract_playlist(self, playlist_url: str):

        options = {
            "extract_flat": "in_playlist",
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:

                info = ydl.extract_info(
                    playlist_url,
                    download=False
                )

                if not info:
                    raise ValueError("Unable to extract playlist")

                videos = []

                for entry in info.get("entries", []):

                    if not entry:
                        continue

                    video_id = entry.get("id")

                    if not video_id:
                        continue

                    videos.append({
                        "video_id": video_id,
                        "title": entry.get("title"),
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })

                return {
                    "playlist_id": info.get("id"),
                    "playlist_title": info.get("title"),
                    "total_videos": len(videos),
                    "videos": videos
                }

        except Exception as e:
            raise RuntimeError(
                f"Playlist extraction failed: {type(e).__name__}: {e}"
            ) from e
