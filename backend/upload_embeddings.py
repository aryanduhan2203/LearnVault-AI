import os
import json
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    port=443,
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=60,
    prefer_grpc=False
)

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "learnvault_knowledge_base"
)

DATA_DIR = BASE_DIR / "data" / "embeddings"

embeddings = np.load(DATA_DIR / "embeddings.npy")

with open(DATA_DIR / "chunk_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

if len(embeddings) != len(metadata):
    raise ValueError("Embedding and metadata counts do not match!")

if embeddings.shape[1] != 384:
    raise ValueError("Incorrect embedding dimensions!")

print("Total embeddings:", len(embeddings))

BATCH_SIZE = 100

for start in range(0, len(embeddings), BATCH_SIZE):
    end = min(start + BATCH_SIZE, len(embeddings))

    points = [
        PointStruct(
            id=i,
            vector=embeddings[i].tolist(),
            payload=metadata[i]
        )
        for i in range(start, end)
    ]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )

    print(f"Uploaded {end}/{len(embeddings)}")

print("All embeddings uploaded successfully!")

client.close()