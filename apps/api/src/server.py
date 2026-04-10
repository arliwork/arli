#!/usr/bin/env python3
"""
ARLI API Server - Production
FastAPI with PostgreSQL backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="ARLI API",
    description="ARLI Platform Production API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import models and create tables
from models import Base, engine
Base.metadata.create_all(bind=engine)

# Include routers
from routes.agents_real import router as agents_router
from routes.live_tasks import router as tasks_router

app.include_router(agents_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {
        "message": "ARLI Production API",
        "version": "1.0.0",
        "status": "production",
        "database": "postgresql"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    uvicorn.run(app, host="0.0.0.0", port=8000)
