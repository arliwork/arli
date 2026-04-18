"""Autonomous Agent Router — heartbeat, strategy, demo scenarios"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from dependencies import get_async_db
from auth import get_current_active_user
from models import User, Agent, Company, Task
from services.agent_executor import AgentExecutor
from services.heartbeat_scheduler import run_all_heartbeats
from services.ceo_strategy import CEOStrategyService

router = APIRouter(prefix="/autonomous", tags=["autonomous"])

@router.post("/heartbeat/{agent_id}")
async def trigger_agent_heartbeat(
    agent_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Manually trigger a heartbeat for a specific agent."""
    executor = AgentExecutor(db)
    result = await executor.heartbeat(agent_id)
    return result

@router.post("/heartbeat-all")
async def trigger_all_heartbeats(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Manually trigger heartbeats for all active agents."""
    result = await run_all_heartbeats()
    return result

@router.post("/strategy/generate")
async def generate_ceo_strategy(
    company_id: str,
    ceo_agent_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """CEO generates a strategic plan for approval."""
    service = CEOStrategyService(db)
    result = await service.generate_strategy(company_id, ceo_agent_id)
    return result

@router.post("/strategy/execute")
async def execute_approved_strategy(
    approval_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Execute an approved strategy — decompose into tasks."""
    service = CEOStrategyService(db)
    result = await service.execute_approved_strategy(approval_id)
    return result

@router.post("/demo/setup-alpha-fund")
async def demo_setup_alpha_fund(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Production Demo: Set up 'Alpha Fund' company with CEO + analysts."""
    import uuid
    from datetime import datetime, timezone
    from models import Company, Agent, Task
    from sqlalchemy import select

    # 1. Create Company
    company = Company(
        company_id=f"comp_{uuid.uuid4().hex[:6]}",
        name="Alpha Fund",
        description="AI-powered quantitative research fund",
        goal="Analyze crypto and equity markets to generate alpha signals with 60%+ confidence",
        owner_id=current_user.id,
        monthly_budget=500,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)

    # 2. Create CEO Agent
    ceo = Agent(
        agent_id=f"agent_{uuid.uuid4().hex[:6]}",
        name="Alpha CEO",
        role="ceo",
        description="Strategic leader of Alpha Fund. Sets research direction and delegates analysis tasks.",
        owner_id=current_user.id,
        creator_id=current_user.id,
        company_id=company.id,
        level=5,
        tier="EXPERT",
        monthly_budget=100,
        status="idle",
    )
    db.add(ceo)
    await db.commit()
    await db.refresh(ceo)

    # 3. Create Analyst 1
    analyst1 = Agent(
        agent_id=f"agent_{uuid.uuid4().hex[:6]}",
        name="Crypto Analyst",
        role="analyst",
        description="Specializes in on-chain analysis, DeFi protocols, and crypto market sentiment.",
        owner_id=current_user.id,
        creator_id=current_user.id,
        company_id=company.id,
        manager_id=ceo.id,
        level=3,
        tier="ADVANCED",
        monthly_budget=50,
        status="idle",
    )
    db.add(analyst1)

    # 4. Create Analyst 2
    analyst2 = Agent(
        agent_id=f"agent_{uuid.uuid4().hex[:6]}",
        name="Equity Analyst",
        role="analyst",
        description="Focuses on equities, macro trends, and earnings analysis.",
        owner_id=current_user.id,
        creator_id=current_user.id,
        company_id=company.id,
        manager_id=ceo.id,
        level=3,
        tier="ADVANCED",
        monthly_budget=50,
        status="idle",
    )
    db.add(analyst2)
    await db.commit()

    # 5. Initial task for CEO
    strategy_task = Task(
        task_id=f"task_{uuid.uuid4().hex[:6]}",
        description="Create a comprehensive market research strategy for Q2 2026 covering crypto and equity markets",
        assigned_role="ceo",
        agent_id=ceo.id,
        status="pending",
    )
    db.add(strategy_task)
    await db.commit()

    return {
        "success": True,
        "demo": "Alpha Fund",
        "company_id": company.company_id,
        "ceo_id": ceo.agent_id,
        "analysts": [analyst1.agent_id, analyst2.agent_id],
        "message": "Alpha Fund is ready! The CEO will propose a strategy. Check /approvals to review it.",
    }

@router.post("/demo/run-cycle")
async def demo_run_cycle(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Run one full heartbeat cycle for the demo."""
    result = await run_all_heartbeats()
    return result
