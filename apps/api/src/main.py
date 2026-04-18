"""ARLI Production FastAPI Backend"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import engine, Base
import models  # noqa: F401 — registers tables with Base.metadata
from routers import auth, agents, tasks, marketplace, orchestration, stats, companies, workspaces, scheduler, credits, webhooks, nfts, live_tasks, approvals, activity, task_comments, secrets, autonomous

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="ARLI API",
    description="Production backend for Autonomous Research & Linked Intelligence",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

# Include routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(tasks.router)
app.include_router(marketplace.router)
app.include_router(orchestration.router)
app.include_router(stats.router)
app.include_router(companies.router)
app.include_router(workspaces.router)
app.include_router(scheduler.router)
app.include_router(credits.router)
app.include_router(webhooks.router)
app.include_router(nfts.router)
app.include_router(live_tasks.router)
app.include_router(approvals.router)
app.include_router(activity.router)
app.include_router(task_comments.router)
app.include_router(secrets.router)
app.include_router(autonomous.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
