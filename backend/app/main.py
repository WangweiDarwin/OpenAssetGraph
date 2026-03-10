"""
OpenAssetGraph Backend Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.scan import router as scan_router
from app.api.topology import router as topology_router
from app.api.chat import router as chat_router

app = FastAPI(
    title=settings.app_name,
    description="AI-Native Digital Twin for Enterprise Software",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router)
app.include_router(topology_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to OpenAssetGraph API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
