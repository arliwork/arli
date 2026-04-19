"""Platform statistics routes"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_async_db
from auth import get_current_active_user
from models import User
from models import Agent, User, Task, AgentSale
from schemas import PlatformStats

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("", response_model=PlatformStats)
async def get_stats(db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_active_user)):
    agents_result = await db.execute(select(func.count(Agent.id)))
    total_agents = agents_result.scalar() or 0
    
    market_value_result = await db.execute(select(func.sum(Agent.market_value)))
    total_market_value = market_value_result.scalar() or 0
    
    revenue_result = await db.execute(select(func.sum(Agent.total_revenue)))
    total_revenue_generated = revenue_result.scalar() or 0
    
    tasks_result = await db.execute(select(func.count(Task.id)))
    total_tasks = tasks_result.scalar() or 0
    
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0
    
    sales_result = await db.execute(select(func.count(AgentSale.id)))
    total_sales = sales_result.scalar() or 0
    
    return PlatformStats(
        total_agents=total_agents,
        total_market_value=total_market_value,
        total_revenue_generated=total_revenue_generated,
        total_tasks=total_tasks,
        total_users=total_users,
        total_sales=total_sales,
    )
