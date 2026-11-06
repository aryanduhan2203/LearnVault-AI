
from youtube_transcript_api import YouTubeTranscriptApi


class TranscriptService:

    def __init__(self):
        self.youtube_api = YouTubeTranscriptApi()

    def extract_transcript(self, video_id: str):

        try:
            transcript = self.youtube_api.fetch(
                video_id,
                languages=["en"]
            )

            segments = transcript.to_raw_data()

            result = {
                "video_id": video_id,
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "total_segments": len(segments),
                "transcript": segments
            }

            return result

        except Exception as e:
            raise RuntimeError(
                f"Transcript extraction failed: {type(e).__name__}: {e}"
            ) from e
