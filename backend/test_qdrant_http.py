import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

url = os.getenv("QDRANT_URL").rstrip("/")
api_key = os.getenv("QDRANT_API_KEY")

headers = {
    "api-key": api_key
}

print("Testing Qdrant REST API...")

try:
    response = httpx.get(
        f"{url}/collections",
        headers=headers,
        timeout=30
    )

    print("Status Code:", response.status_code)
    print("Response:", response.text[:1000])

except httpx.RequestError as error:
    print("Connection Error:", error)