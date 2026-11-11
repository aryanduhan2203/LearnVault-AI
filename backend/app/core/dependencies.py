from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import get_current_user, security
from app.db.client import get_user_supabase_client


def get_authenticated_db(
    current_user=Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_client = get_user_supabase_client(
        credentials.credentials
    )

    return {
        "user": current_user,
        "db": user_client
    }
