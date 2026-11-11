from pydantic import BaseModel, Field


class PlaylistImportRequest(BaseModel):
    playlist_url: str = Field(
        min_length=10,
        max_length=2048
    )