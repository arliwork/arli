"""Companies routes for frontend compatibility"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from dependencies import get_async_db
from auth import get_current_active_user
from models import Agent, Task, Workflow, User

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("")
async def list_companies(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return user's agents as 'companies' for dashboard compatibility"""
    result = await db.execute(
        select(Agent).where(Agent.owner_id == current_user.id)
    )
    agents = result.scalars().all()
    
    companies = []
    for agent in agents:
        task_count = await db.execute(
            select(func.count(Task.id)).where(Task.agent_id == agent.id)
        )
        tc = task_count.scalar()
        
        companies.append({
            "id": agent.id,
            "name": agent.name,
            "slug": agent.agent_id,
            "status": "ACTIVE" if agent.status != "idle" else "PAUSED",
            "credits": 1000,
            "totalRevenue": float(agent.total_revenue or 0),
            "_count": {
                "agents": 1,
                "tickets": tc or 0,
            }
        })
    
    return {"companies": companies}
