
class ChunkingService:

    def __init__(self, chunk_size=150, overlap=30):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def create_chunks(self, transcript_data):

        segments = transcript_data["transcript"]

        chunks = []
        current_segments = []
        current_words = 0

        def save_chunk(segment_group):

            if not segment_group:
                return

            text = " ".join(
                segment["text"].strip()
                for segment in segment_group
            ).strip()

            if not text:
                return

            start_time = segment_group[0]["start"]

            last_segment = segment_group[-1]

            end_time = (
                last_segment["start"] +
                last_segment["duration"]
            )

            chunks.append({
                "chunk_id": len(chunks),
                "video_id": transcript_data["video_id"],
                "text": text,
                "start_time": round(start_time, 2),
                "end_time": round(end_time, 2),
                "word_count": len(text.split())
            })

        for segment in segments:

            segment_words = len(segment["text"].split())

            if (
                current_segments
                and current_words + segment_words > self.chunk_size
            ):

                save_chunk(current_segments)

                overlap_segments = []
                overlap_words = 0

                for old_segment in reversed(current_segments):

                    words = len(old_segment["text"].split())

                    if overlap_words + words > self.overlap:
                        break

                    overlap_segments.insert(0, old_segment)
                    overlap_words += words

                current_segments = overlap_segments
                current_words = overlap_words

            current_segments.append(segment)
            current_words += segment_words

        save_chunk(current_segments)

        return chunks
