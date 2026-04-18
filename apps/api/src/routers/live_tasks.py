"""Live task execution with real-time updates and retry logic"""
import uuid
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Callable
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_async_db
from auth import get_current_active_user
from models import Task, Agent, User
from schemas import TaskOut

router = APIRouter(prefix="/live-tasks", tags=["live-tasks"])

# ─── In-memory state (use Redis in production) ──────────────────────
_task_queue: asyncio.Queue = asyncio.Queue()
_running_tasks: Dict[str, dict] = {}
_task_results: Dict[str, dict] = {}
_task_handlers: Dict[str, Callable] = {}
_websocket_clients: List[WebSocket] = []

# ─── Schemas ────────────────────────────────────────────────────────

class LiveTaskSubmit(BaseModel):
    agent_id: str
    category: str
    description: str
    parameters: Dict[str, Any] = {}
    priority: int = 1

class LiveTaskResponse(BaseModel):
    task_id: str
    agent_id: str
    status: str
    result: Optional[Dict] = None
    xp_gained: Optional[int] = None
    created_at: str

class TaskQueueStatus(BaseModel):
    queued: int
    running: int
    completed: int

# ─── Task Handlers ──────────────────────────────────────────────────

async def _handle_coding(params: dict) -> dict:
    """Execute coding task via LLM"""
    from services.llm_client import get_llm_client
    client = get_llm_client()
    lang = params.get("language", "python")
    prompt = params.get("prompt", params.get("description", "Write code"))
    result = await client.generate(
        messages=[
            {"role": "system", "content": f"You are an expert {lang} developer."},
            {"role": "user", "content": prompt},
        ],
        task_type="coding",
        max_tokens=4000,
    )
    return {"success": True, "output": result.content, "credits_used": result.credits_used}

async def _handle_research(params: dict) -> dict:
    """Execute research task"""
    from services.llm_client import get_llm_client
    client = get_llm_client()
    query = params.get("query", params.get("description", "Research topic"))
    result = await client.generate(
        messages=[
            {"role": "system", "content": "You are a research analyst."},
            {"role": "user", "content": f"Research and summarize: {query}"},
        ],
        task_type="reasoning",
        max_tokens=2000,
    )
    return {"success": True, "output": result.content, "credits_used": result.credits_used}

async def _handle_content(params: dict) -> dict:
    """Execute content creation task"""
    from services.llm_client import get_llm_client
    client = get_llm_client()
    topic = params.get("topic", params.get("description", "Create content"))
    result = await client.generate(
        messages=[
            {"role": "system", "content": "You are a professional content writer."},
            {"role": "user", "content": topic},
        ],
        task_type="default",
        max_tokens=3000,
    )
    word_count = len(result.content.split())
    return {"success": True, "output": result.content, "word_count": word_count, "credits_used": result.credits_used}

async def _handle_trading(params: dict) -> dict:
    """Trading signal generation (mock until exchange API connected)"""
    import random
    symbol = params.get("symbol", "BTC")
    action = params.get("action", "analyze")
    signal = random.choice(["BUY", "SELL", "HOLD"])
    confidence = random.uniform(0.6, 0.95)
    return {
        "success": True,
        "output": f"Signal for {symbol}: {signal} (confidence: {confidence:.0%})",
        "metadata": {"symbol": symbol, "signal": signal, "confidence": confidence},
    }

# Register handlers
_task_handlers["coding"] = _handle_coding
_task_handlers["development"] = _handle_coding
_task_handlers["backend"] = _handle_coding
_task_handlers["frontend"] = _handle_coding
_task_handlers["research"] = _handle_research
_task_handlers["analysis"] = _handle_research
_task_handlers["content"] = _handle_content
_task_handlers["content_creation"] = _handle_content
_task_handlers["trading"] = _handle_trading

# ─── Helpers ────────────────────────────────────────────────────────

async def _broadcast_status(task_id: str, status: str, data: dict = None):
    """Broadcast task status to all connected WebSocket clients"""
    payload = {"task_id": task_id, "status": status, "data": data or {}}
    dead = []
    for ws in _websocket_clients:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in _websocket_clients:
            _websocket_clients.remove(ws)

async def _execute_with_retry(handler: Callable, params: dict, max_retries: int = 2) -> dict:
    """Execute handler with exponential backoff retry"""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await handler(params)
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait = 2 ** attempt
                await asyncio.sleep(wait)
    return {"success": False, "output": str(last_error), "error": str(last_error)}

# ─── Background Worker ──────────────────────────────────────────────

async def _process_task(task_id: str, task: dict, db: AsyncSession):
    """Process a single task with full lifecycle"""
    _running_tasks[task_id] = task
    task["status"] = "running"
    task["started_at"] = datetime.now(timezone.utc).isoformat()
    await _broadcast_status(task_id, "running")

    category = task.get("category", "generic").lower()
    handler = _task_handlers.get(category, _task_handlers.get("research"))

    # Execute with retry
    result = await _execute_with_retry(handler, task.get("parameters", {}))

    # Update agent XP if successful
    agent_id = task.get("agent_id")
    if result.get("success") and agent_id:
        try:
            res = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
            agent = res.scalar_one_or_none()
            if agent:
                agent.total_tasks += 1
                if result.get("success"):
                    agent.successful_tasks += 1
                xp_gain = 10 + (result.get("metadata", {}).get("word_count", 0) // 100)
                agent.total_xp += xp_gain
                result["xp_gained"] = xp_gain
                await db.commit()
        except Exception:
            pass

    # Store result
    result["task_id"] = task_id
    result["agent_id"] = agent_id
    result["completed_at"] = datetime.now(timezone.utc).isoformat()
    _task_results[task_id] = result

    # Cleanup
    if task_id in _running_tasks:
        del _running_tasks[task_id]

    status = "completed" if result.get("success") else "failed"
    await _broadcast_status(task_id, status, result)

# ─── API Endpoints ──────────────────────────────────────────────────

@router.post("/submit", response_model=LiveTaskResponse)
async def submit_task(
    data: LiveTaskSubmit,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    task_id = f"lt_{uuid.uuid4().hex[:8]}"
    task = {
        "task_id": task_id,
        "agent_id": data.agent_id,
        "category": data.category,
        "description": data.description,
        "parameters": data.parameters,
        "priority": data.priority,
        "status": "queued",
        "user_id": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await _task_queue.put((data.priority, task_id, task))

    # Start background processor if not already running
    asyncio.create_task(_process_task(task_id, task, db))

    return LiveTaskResponse(
        task_id=task_id,
        agent_id=data.agent_id,
        status="queued",
        created_at=task["created_at"],
    )

@router.get("/{task_id}/status")
async def get_task_status(task_id: str):
    if task_id in _task_results:
        r = _task_results[task_id]
        return LiveTaskResponse(
            task_id=task_id,
            agent_id=r.get("agent_id"),
            status="completed" if r.get("success") else "failed",
            result=r,
            xp_gained=r.get("xp_gained"),
            created_at=r.get("completed_at", ""),
        )
    if task_id in _running_tasks:
        t = _running_tasks[task_id]
        return LiveTaskResponse(
            task_id=task_id,
            agent_id=t.get("agent_id"),
            status="running",
            created_at=t.get("created_at", ""),
        )
    raise HTTPException(status_code=404, detail="Task not found")

@router.get("/queue", response_model=TaskQueueStatus)
async def queue_status():
    return TaskQueueStatus(
        queued=_task_queue.qsize(),
        running=len(_running_tasks),
        completed=len(_task_results),
    )

@router.post("/batch")
async def submit_batch(
    tasks: List[LiveTaskSubmit],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    results = []
    for t in tasks:
        result = await submit_task(t, None, db, current_user)
        results.append(result)
    return results

@router.get("/agent/{agent_id}/history")
async def agent_history(agent_id: str, db: AsyncSession = Depends(get_async_db)):
    res = await db.execute(
        select(Task)
        .where(Task.agent_id == agent_id)
        .order_by(Task.created_at.desc())
        .limit(20)
    )
    items = res.scalars().all()
    return {"agent_id": agent_id, "total": len(items), "tasks": [TaskOut.model_validate(t) for t in items]}

# ─── WebSocket ──────────────────────────────────────────────────────

@router.websocket("/ws")
async def task_websocket(websocket: WebSocket):
    await websocket.accept()
    _websocket_clients.append(websocket)
    try:
        while True:
            # Keep connection alive, optionally handle client messages
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        if websocket in _websocket_clients:
            _websocket_clients.remove(websocket)
