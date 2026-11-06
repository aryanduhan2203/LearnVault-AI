
from fastapi import FastAPI

app = FastAPI(
    title="LearnVault AI",
    description="AI-powered learning and revision assistant",
    version="1.0.0"
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
