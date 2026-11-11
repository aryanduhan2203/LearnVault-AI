import os
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

# Configuration
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "learnvault_knowledge_base"
)

# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# Connect to Qdrant
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    port=443,
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=60,
    prefer_grpc=False
)

# User query
query = "What is the difference between SQL and NoSQL databases?"

# Generate query embedding
query_vector = model.encode(
    query,
    normalize_embeddings=True
).tolist()

# Search Qdrant
results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=5,
    with_payload=True
).points

# Display results
print("\nUser Query:", query)
print("\nTop 5 Relevant Chunks:\n")

for i, result in enumerate(results, 1):
    payload = result.payload

    print(f"Result {i}")
    print("Similarity Score:", round(result.score, 4))
    print("Video ID:", payload.get("video_id"))
    print("Timestamp:", payload.get("start_time"), "-", payload.get("end_time"))
    print("Text:", payload.get("text"))
    print("-" * 80)

client.close()