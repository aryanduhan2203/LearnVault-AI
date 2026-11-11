
from pydantic import BaseModel, Field
from typing import List


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Question asked by the student"
    )
    playlist_id: str = Field(
        ...,
        min_length=1,
        description="Selected YouTube playlist ID"
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of transcript chunks to retrieve"
    )


class SourceResponse(BaseModel):
    video_id: str
    chunk_id: int
    start_time: float
    end_time: float
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceResponse]
