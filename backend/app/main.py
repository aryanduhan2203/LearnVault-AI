
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from app.core.security import get_current_user
from app.core.dependencies import get_authenticated_db

from app.services.playlist_import_service import PlaylistImportService
from app.schemas.rag_schema import ChatRequest, ChatResponse
from app.services.rag_service import RAGService
from app.services.catalog_service import CatalogService
from app.schemas.playlist_schema import PlaylistImportRequest
from app.api.auth import router as auth_router

def process_import_and_update_status(
    service,
    catalog,
    db,
    playlist_id: str,
    playlist_url: str
):
    service.process_import(playlist_id, playlist_url)

    job = service.get_job_status(playlist_id)
    status = job["status"]

    update_data = {
        "status": status
    }

    if status == "ready":
        metadata = catalog.get_playlist_videos(playlist_id)

        if metadata:
            update_data["title"] = metadata["playlist_title"]

    db.table("playlists").update(
        update_data
    ).eq(
        "youtube_playlist_id", playlist_id
    ).execute()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing LearnVault AI services...")

    rag_service = RAGService()
    catalog_service = CatalogService()
    playlist_import_service = PlaylistImportService(
    embedding_model=rag_service.search_service.model,
    qdrant_client=rag_service.search_service.client
)
    app.state.rag_service = rag_service
    app.state.catalog_service = catalog_service
    app.state.playlist_import_service = playlist_import_service

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
app.include_router(auth_router)
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
def get_playlists(
    auth=Depends(get_authenticated_db),
    request: Request = None
):
    catalog = request.app.state.catalog_service

    response = (
        auth["db"]
        .table("playlists")
        .select("youtube_playlist_id,title,status")
        .execute()
    )

    playlists = []

    for playlist in response.data:
        metadata = catalog.get_playlist_videos(
            playlist["youtube_playlist_id"]
        )

        playlists.append({
            "playlist_id": playlist["youtube_playlist_id"],
            "playlist_title": playlist["title"],
            "total_videos": metadata["total_videos"] if metadata else 0,
            "status": playlist["status"]
        })

    return playlists

@app.post("/api/playlists/import", status_code=202)
def import_playlist(
    payload: PlaylistImportRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    auth=Depends(get_authenticated_db)
):
    service = request.app.state.playlist_import_service
    catalog = request.app.state.catalog_service

    try:
        result = service.start_import(payload.playlist_url)
        playlist_id = result["playlist_id"]

        metadata = catalog.get_playlist_videos(playlist_id)

        title = (
            metadata["playlist_title"]
            if metadata
            else playlist_id
        )

        status = (
            "ready"
            if result["status"] == "already_imported"
            else "importing"
        )

        auth["db"].table("playlists").upsert(
            {
                "user_id": auth["user"].id,
                "youtube_playlist_id": playlist_id,
                "title": title,
                "status": status
            },
            on_conflict="user_id,youtube_playlist_id"
        ).execute()

        if result["status"] == "queued":
            background_tasks.add_task(
            process_import_and_update_status,
            service,
            catalog,
            auth["db"],
            playlist_id,
            payload.playlist_url
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@app.get("/api/playlists/{playlist_id}/status")
def get_playlist_import_status(
    playlist_id: str,
    request: Request,
    auth=Depends(get_authenticated_db)
):
    db = auth["db"]

    ownership = (
        db.table("playlists")
        .select("status")
        .eq("youtube_playlist_id", playlist_id)
        .execute()
    )

    if not ownership.data:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found"
        )

    service = request.app.state.playlist_import_service
    catalog = request.app.state.catalog_service

    job_status = service.get_job_status(playlist_id)
    current_status = ownership.data[0]["status"]

    if job_status.get("status") in ["ready", "failed"]:
        current_status = job_status["status"]

        update_data = {
            "status": current_status
        }

        if current_status == "ready":
            metadata = catalog.get_playlist_videos(playlist_id)

            if metadata:
                update_data["title"] = metadata["playlist_title"]

        db.table("playlists").update(
            update_data
        ).eq(
            "youtube_playlist_id", playlist_id
        ).execute()

    return {
        **job_status,
        "status": current_status
    }

@app.get("/api/playlists/{playlist_id}/videos")
def get_playlist_videos(
    playlist_id: str,
    request: Request,
    auth=Depends(get_authenticated_db)
):
    ownership = (
        auth["db"]
        .table("playlists")
        .select("id")
        .eq("youtube_playlist_id", playlist_id)
        .execute()
    )

    if not ownership.data:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found"
        )

    catalog = request.app.state.catalog_service

    try:
        result = catalog.get_playlist_videos(playlist_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid playlist ID"
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found"
        )

    return result


@app.get("/api/videos/{video_id}/transcript")
def get_video_transcript(
    video_id: str,
    request: Request,
    playlist_id: str,
    auth=Depends(get_authenticated_db)
):
    ownership = (
        auth["db"]
        .table("playlists")
        .select("id")
        .eq("youtube_playlist_id", playlist_id)
        .execute()
    )

    if not ownership.data:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found"
        )

    catalog = request.app.state.catalog_service

    playlist = catalog.get_playlist_videos(playlist_id)

    if playlist is None:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found"
        )

    video_exists = any(
        video["video_id"] == video_id
        for video in playlist["videos"]
    )

    if not video_exists:
        raise HTTPException(
            status_code=404,
            detail="Video not found in this playlist"
        )

    try:
        result = catalog.get_video_transcript(video_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid video ID"
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found"
        )

    return result


@app.post("/api/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    http_request: Request,
    auth=Depends(get_authenticated_db)
):
    ownership = (
        auth["db"]
        .table("playlists")
        .select("id")
        .eq("youtube_playlist_id", payload.playlist_id)
        .execute()
    )

    if not ownership.data:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found"
        )

    try:
        rag_service = http_request.app.state.rag_service

        result = rag_service.generate_answer(
            query=payload.question,
            playlist_id=payload.playlist_id,
            limit=payload.limit
        )

        return ChatResponse(**result)

    except Exception as e:
        print(f"Chat API error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the answer."
        )

    
@app.get("/api/auth/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }



