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
    timeout=30,
    prefer_grpc=False
)

print("Testing Qdrant Python client...")

try:
    collections = client.get_collections()

    print("Connected successfully!")
    print("Existing collections:")

    for collection in collections.collections:
        print("-", collection.name)

except Exception as e:
    print("Error:", repr(e))

finally:
    client.close()