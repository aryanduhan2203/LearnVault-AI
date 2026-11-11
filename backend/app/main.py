
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.rag_schema import ChatRequest, ChatResponse
from app.services.rag_service import RAGService
from app.services.catalog_service import CatalogService


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing LearnVault AI services...")

    rag_service = RAGService()
    catalog_service = CatalogService()

    app.state.rag_service = rag_service
    app.state.catalog_service = catalog_service

    print("LearnVault AI services initialized successfully.")

    yield

    print("Closing LearnVault AI services...")
    rag_service.close()


app = FastAPI(
    title="LearnVault AI",
    description="AI-powered learning and revision assistant",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to LearnVault AI",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LearnVault AI Backend"
    }


@app.get("/api/playlists")
def get_playlists(request: Request):
    catalog = request.app.state.catalog_service
    return catalog.get_playlists()


@app.get("/api/playlists/{playlist_id}/videos")
def get_playlist_videos(playlist_id: str, request: Request):
    catalog = request.app.state.catalog_service

    try:
        result = catalog.get_playlist_videos(playlist_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid playlist ID")

    if result is None:
        raise HTTPException(status_code=404, detail="Playlist not found")

    return result


@app.get("/api/videos/{video_id}/transcript")
def get_video_transcript(video_id: str, request: Request):
    catalog = request.app.state.catalog_service

    try:
        result = catalog.get_video_transcript(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID")

    if result is None:
        raise HTTPException(status_code=404, detail="Transcript not found")

    return result


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, http_request: Request):
    try:
        rag_service = http_request.app.state.rag_service

        result = rag_service.generate_answer(
            query=request.question,
            playlist_id=request.playlist_id,
            limit=request.limit
        )

        return ChatResponse(**result)

    except Exception as e:
        print(f"Chat API error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the answer."
        )
