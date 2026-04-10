#!/usr/bin/env python3
"""
ARLI API Server
FastAPI backend for skills marketplace and experience tracking
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add routes
sys.path.insert(0, os.path.dirname(__file__))
from routes.skills_real import router as skills_router
from routes.experience import router as experience_router
from routes.live_tasks import router as tasks_router

app = FastAPI(
    title="ARLI API",
    description="ARLI Platform API - Skills, Experience & Live Tasks",
    version="1.0.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(skills_router)
app.include_router(experience_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {
        "message": "ARLI API Server",
        "version": "1.0.0",
        "features": ["skills", "experience", "live-tasks"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
