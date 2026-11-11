
import os
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client.models import PayloadSchemaType

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "learnvault_knowledge_base"
)


class SearchService:

    def __init__(self):
        print("Loading embedding model...")

        self.model = SentenceTransformer(MODEL_NAME)

        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            port=443,
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=60,
            prefer_grpc=False
        )
        self.client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="playlist_id",
            field_schema=PayloadSchemaType.KEYWORD,
            wait=True
        )

    def search(
        self,
        query: str,
        playlist_id: str,
        limit: int = 5
    ):

        query_vector = self.model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

        playlist_filter = Filter(
            must=[
                FieldCondition(
                    key="playlist_id",
                    match=MatchValue(value=playlist_id)
                )
            ]
        )

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=playlist_filter,
            limit=limit,
            with_payload=True
        ).points

        return [
            {
                "score": result.score,
                "video_id": result.payload.get("video_id"),
                "chunk_id": result.payload.get("chunk_id"),
                "start_time": result.payload.get("start_time"),
                "end_time": result.payload.get("end_time"),
                "text": result.payload.get("text")
            }
            for result in results
            if result.score >= 0.50
        ]

    def close(self):
        self.client.close()
