from fastapi import FastAPI
from app.core.config import settings
from app.api.webhook import router as webhook_router

app = FastAPI(title="VertexRabbit", version="0.1.0")

app.include_router(webhook_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "VertexRabbit is running 🐰"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
