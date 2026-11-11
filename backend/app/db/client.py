from supabase import create_client
from supabase.lib.client_options import SyncClientOptions

from app.database import SUPABASE_URL, SUPABASE_KEY


def get_user_supabase_client(access_token: str):
    options = SyncClientOptions(
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        auto_refresh_token=False,
        persist_session=False
    )

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=options
    )