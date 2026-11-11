import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase URL or API key is missing")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)