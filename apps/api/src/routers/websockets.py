"""Real-time WebSocket endpoints for dashboard and live updates"""
import asyncio
import json
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_async_db
from auth import get_current_active_user
from models import Agent, Task, User, AgentSale

router = APIRouter(prefix="/ws", tags=["websockets"])

# ─── Client management ──────────────────────────────────────────────
_dashboard_clients: List[WebSocket] = []

async def _broadcast_dashboard(db: AsyncSession):
    """Broadcast dashboard stats to all connected clients"""
    while True:
        try:
            # Fetch stats
            agents_result = await db.execute(select(func.count(Agent.id)))
            total_agents = agents_result.scalar() or 0
            
            market_value_result = await db.execute(select(func.sum(Agent.market_value)))
            total_market_value = float(market_value_result.scalar() or 0)
            
            revenue_result = await db.execute(select(func.sum(Agent.total_revenue)))
            total_revenue = float(revenue_result.scalar() or 0)
            
            tasks_result = await db.execute(select(func.count(Task.id)))
            total_tasks = tasks_result.scalar() or 0
            
            users_result = await db.execute(select(func.count(User.id)))
            total_users = users_result.scalar() or 0
            
            # Count active agents
            active_result = await db.execute(
                select(func.count(Agent.id)).where(Agent.status == "active")
            )
            active_agents = active_result.scalar() or 0
            
            payload = {
                "type": "dashboard_stats",
                "data": {
                    "total_agents": total_agents,
                    "active_agents": active_agents,
                    "total_market_value": total_market_value,
                    "total_revenue": total_revenue,
                    "total_tasks": total_tasks,
                    "total_users": total_users,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            }
            
            # Send to all connected clients
            disconnected = []
            for ws in _dashboard_clients:
                try:
                    await ws.send_json(payload)
                except Exception:
                    disconnected.append(ws)
            
            # Clean up disconnected clients
            for ws in disconnected:
                if ws in _dashboard_clients:
                    _dashboard_clients.remove(ws)
                    
        except Exception as e:
            print(f"Dashboard broadcast error: {e}")
        
        await asyncio.sleep(5)  # Update every 5 seconds

@router.websocket("/dashboard")
async def dashboard_websocket(websocket: WebSocket, db: AsyncSession = Depends(get_async_db)):
    await websocket.accept()
    _dashboard_clients.append(websocket)
    
    # Start broadcaster if this is the first client
    if len(_dashboard_clients) == 1:
        asyncio.create_task(_broadcast_dashboard(db))
    
    try:
        # Send initial stats immediately
        agents_result = await db.execute(select(func.count(Agent.id)))
        total_agents = agents_result.scalar() or 0
        
        market_value_result = await db.execute(select(func.sum(Agent.market_value)))
        total_market_value = float(market_value_result.scalar() or 0)
        
        revenue_result = await db.execute(select(func.sum(Agent.total_revenue)))
        total_revenue = float(revenue_result.scalar() or 0)
        
        tasks_result = await db.execute(select(func.count(Task.id)))
        total_tasks = tasks_result.scalar() or 0
        
        await websocket.send_json({
            "type": "dashboard_stats",
            "data": {
                "total_agents": total_agents,
                "total_market_value": total_market_value,
                "total_revenue": total_revenue,
                "total_tasks": total_tasks,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        })
        
        # Keep connection alive
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        if websocket in _dashboard_clients:
            _dashboard_clients.remove(websocket)
