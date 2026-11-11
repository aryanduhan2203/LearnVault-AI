import os
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient

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

info = client.get_collection(COLLECTION_NAME)

print("Collection:", COLLECTION_NAME)
print("Stored vectors:", info.points_count)
print("Vector configuration:", info.config.params.vectors)

print("\nFetching sample points...")

points, _ = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=3,
    with_payload=True,
    with_vectors=False
)

for point in points:
    print("\nPoint ID:", point.id)
    print("Payload:", point.payload)

if info.points_count == 2830:
    print("\nVerification successful!")
else:
    print("\nWarning: Expected 2830 vectors.")

client.close()