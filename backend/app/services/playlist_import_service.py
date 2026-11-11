import json
import time
import uuid

from pathlib import Path
from urllib.parse import urlparse, parse_qs

from app.services.youtube_service import YouTubeService
from app.services.transcript_service import TranscriptService
from app.services.chunking_service import ChunkingService
from app.services.search_service import COLLECTION_NAME

from qdrant_client.models import PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

PLAYLIST_DIR = DATA_DIR / "playlists"
TRANSCRIPT_DIR = DATA_DIR / "transcripts"
CHUNK_DIR = DATA_DIR / "chunks"



class PlaylistImportService:

    def __init__(self, embedding_model, qdrant_client):

        self.embedding_model = embedding_model
        self.qdrant_client = qdrant_client

        self.youtube_service = YouTubeService()
        self.transcript_service = TranscriptService()
        self.chunking_service = ChunkingService()

        self.jobs = {}

    
    def extract_playlist_id(self, playlist_url: str):

        parsed_url = urlparse(playlist_url.strip())

        allowed_hosts = {
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com"
        }

        if parsed_url.scheme not in ["https", "http"]:
            raise ValueError("Invalid YouTube URL")

        if parsed_url.hostname not in allowed_hosts:
            raise ValueError("Invalid YouTube URL")

        if parsed_url.path not in ["/playlist", "/watch"]:
            raise ValueError("Invalid YouTube playlist URL")

        query_params = parse_qs(parsed_url.query)
        playlist_ids = query_params.get("list")

        if not playlist_ids or not playlist_ids[0]:
            raise ValueError("URL does not contain a playlist ID")

        playlist_id = playlist_ids[0]

        if len(playlist_id) > 100:
            raise ValueError("Invalid playlist ID")

        return playlist_id
    
    def is_playlist_imported(self, playlist_id: str):

        playlist_file = PLAYLIST_DIR / f"{playlist_id}.json"

        if not playlist_file.exists():
            return False

        with playlist_file.open("r", encoding="utf-8") as file:
            playlist = json.load(file)

        return playlist.get("playlist_id") == playlist_id
    
    def get_job_status(self, playlist_id: str):

        return self.jobs.get(
            playlist_id,
            {
                "playlist_id": playlist_id,
                "status": "not_found",
                "message": "No import job found."
            }
        )
    
    def start_import(self, playlist_url: str):

        playlist_id = self.extract_playlist_id(playlist_url)

        if self.is_playlist_imported(playlist_id):
            return {
                "playlist_id": playlist_id,
                "status": "already_imported",
                "message": "This playlist has already been imported."
            }

        existing_job = self.jobs.get(playlist_id)

        if existing_job and existing_job["status"] not in ["failed"]:
            return {
                "playlist_id": playlist_id,
                "status": existing_job["status"],
                "message": "This playlist is already being processed."
            }

        self.jobs[playlist_id] = {
            "playlist_id": playlist_id,
            "status": "queued",
            "message": "Playlist import has been queued."
        }

        return {
            "playlist_id": playlist_id,
            "status": "queued",
            "message": "Playlist import has been queued."
        }
    
    def extract_and_chunk_playlist(self, playlist_id: str, playlist_url: str):

        self.jobs[playlist_id].update({
            "status": "fetching_videos",
            "message": "Fetching playlist information..."
        })

        playlist = self.youtube_service.extract_playlist(playlist_url)

        if playlist["playlist_id"] != playlist_id:
            raise ValueError("Playlist ID mismatch")

        videos = playlist["videos"]

        if not videos:
            raise ValueError("No videos found in this playlist")

        self.jobs[playlist_id].update({
            "status": "extracting_transcripts",
            "message": f"Extracting transcripts from {len(videos)} videos...",
            "total_videos": len(videos),
            "processed_videos": 0
        })

        TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

        playlist_chunk_dir = CHUNK_DIR / playlist_id
        playlist_chunk_dir.mkdir(parents=True, exist_ok=True)

        all_chunks = []
        failed_videos = []

        for index, video in enumerate(videos, start=1):

            video_id = video["video_id"]
            transcript_file = TRANSCRIPT_DIR / f"{video_id}.json"

            try:
                if transcript_file.exists():
                    with transcript_file.open("r", encoding="utf-8") as file:
                        transcript = json.load(file)
                else:
                    transcript = self.transcript_service.extract_transcript(video_id)

                    with transcript_file.open("w", encoding="utf-8") as file:
                        json.dump(transcript, file, indent=4, ensure_ascii=False)

                chunks = self.chunking_service.create_chunks(transcript)

                for chunk in chunks:
                    chunk["playlist_id"] = playlist_id

                all_chunks.extend(chunks)

                print(f"[{index}/{len(videos)}] Processed: {video['title']}")

            except Exception as error:
                failed_videos.append({
                    "video_id": video_id,
                    "title": video.get("title"),
                    "error": str(error)
                })

                print(f"[{index}/{len(videos)}] Failed: {video_id} - {error}")

            self.jobs[playlist_id]["processed_videos"] = index

            time.sleep(0.5)

        if not all_chunks:
            raise ValueError("No transcripts could be processed successfully")

        chunk_file = playlist_chunk_dir / "chunks.json"

        with chunk_file.open("w", encoding="utf-8") as file:
            json.dump(all_chunks, file, indent=4, ensure_ascii=False)

        self.jobs[playlist_id].update({
            "total_chunks": len(all_chunks),
            "failed_videos": failed_videos
        })

        return playlist, all_chunks
    
    def generate_playlist_embeddings(self, playlist_id: str, chunks: list):

        self.jobs[playlist_id].update({
            "status": "generating_embeddings",
            "message": "Generating embeddings..."
        })

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.embedding_model.encode(
            texts,
            batch_size=16,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        if len(embeddings) != len(chunks):
            raise ValueError("Embedding and chunk counts do not match")

        if embeddings.shape[1] != 384:
            raise ValueError("Incorrect embedding dimensions")

        self.jobs[playlist_id].update({
            "total_embeddings": len(embeddings),
            "message": f"Generated {len(embeddings)} embeddings."
        })

        return embeddings
    
    def upload_playlist_embeddings(self, playlist_id: str, chunks: list, embeddings):

        self.jobs[playlist_id].update({
            "status": "indexing",
            "message": "Uploading embeddings to Qdrant..."
        })

        if len(chunks) != len(embeddings):
            raise ValueError("Chunk and embedding counts do not match")

        batch_size = 100
        total = len(chunks)

        for start in range(0, total, batch_size):

            end = min(start + batch_size, total)

            points = []

            for index in range(start, end):

                chunk = chunks[index]

                point_id = str(uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"learnvault:{playlist_id}:{chunk['video_id']}:{chunk['chunk_id']}"
                ))

                points.append(
                    PointStruct(
                        id=point_id,
                        vector=embeddings[index].tolist(),
                        payload=chunk
                    )
                )

            self.qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
                wait=True
            )

            self.jobs[playlist_id]["indexed_chunks"] = end

            print(f"Uploaded {end}/{total} chunks")

        return total

    def cleanup_playlist_vectors(self, playlist_id: str):

        self.qdrant_client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="playlist_id",
                        match=MatchValue(value=playlist_id)
                    )
                ]
            ),
            wait=True
        )
        print(f"Cleaned up previous vectors for playlist: {playlist_id}")
    def process_import(self, playlist_id: str, playlist_url: str):

        try:
            playlist, chunks = self.extract_and_chunk_playlist(
                playlist_id,
                playlist_url
            )

            embeddings = self.generate_playlist_embeddings(
                playlist_id,
                chunks
            )

            total_indexed = self.upload_playlist_embeddings(
                playlist_id,
                chunks,
                embeddings
            )

            playlist_file = PLAYLIST_DIR / f"{playlist_id}.json"
            PLAYLIST_DIR.mkdir(parents=True, exist_ok=True)

            with playlist_file.open("w", encoding="utf-8") as file:
                json.dump(
                    playlist,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            failed_count = len(
                self.jobs[playlist_id].get("failed_videos", [])
            )

            self.jobs[playlist_id].update({
                "status": "ready",
                "message": (
                    f"Playlist imported successfully. "
                    f"{failed_count} videos could not be processed."
                    if failed_count > 0
                    else "Playlist imported successfully."
                ),
                "total_chunks": len(chunks),
                "indexed_chunks": total_indexed,
                "failed_video_count": failed_count
            })

        except Exception as error:

            self.jobs[playlist_id].update({
                "status": "failed",
                "message": str(error)
            })

            print(f"Playlist import failed: {error}")









