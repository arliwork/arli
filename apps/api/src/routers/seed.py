"""Seed / welcome data for new users"""
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_async_db
from auth import get_current_active_user
from models import Agent, Task, ActivityLog, User

router = APIRouter(prefix="/seed", tags=["seed"])


def _agent_id():
    return f"agent_{uuid.uuid4().hex[:8]}"


def _task_id():
    return f"task_{uuid.uuid4().hex[:8]}"


@router.post("/welcome")
async def seed_welcome(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create welcome demo data for a new user"""
    user_id = current_user.id
    now = datetime.utcnow()

    # 1. Create starter agents
    ceo = Agent(
        agent_id=_agent_id(),
        name="Alpha CEO",
        role="ceo",
        description="Strategic executive agent. Sets vision, approves major initiatives, and allocates budget across departments.",
        owner_id=user_id,
        creator_id=user_id,
        level=5,
        tier="EXPERT",
        total_tasks=12,
        successful_tasks=11,
        total_revenue=5200,
        market_value=2500,
        capabilities=["strategy", "planning", "budgeting", "leadership"],
        status="active",
    )
    sales = Agent(
        agent_id=_agent_id(),
        name="Sales Hunter",
        role="sales",
        description="Outbound sales agent. Prospects leads, runs demos, and closes deals autonomously.",
        owner_id=user_id,
        creator_id=user_id,
        level=3,
        tier="JOURNEYMAN",
        total_tasks=24,
        successful_tasks=20,
        total_revenue=8400,
        market_value=1200,
        capabilities=["outreach", "demo", "negotiation", "crm"],
        status="active",
    )
    dev = Agent(
        agent_id=_agent_id(),
        name="Code Weaver",
        role="developer",
        description="Full-stack development agent. Builds features, fixes bugs, and deploys to production.",
        owner_id=user_id,
        creator_id=user_id,
        level=4,
        tier="EXPERT",
        total_tasks=18,
        successful_tasks=17,
        total_revenue=3600,
        market_value=1800,
        capabilities=["frontend", "backend", "devops", "testing"],
        status="idle",
    )

    db.add_all([ceo, sales, dev])
    await db.flush()  # Get IDs assigned

    # 2. Create tasks
    tasks = [
        Task(
            task_id=_task_id(),
            agent_id=ceo.id,
            category="strategy",
            description="Q2 roadmap planning and resource allocation",
            status="completed",
            success=True,
            revenue_generated=1200,
            execution_time_seconds=180,
            completed_at=now - timedelta(hours=2),
        ),
        Task(
            task_id=_task_id(),
            agent_id=sales.id,
            category="sales",
            description="Closed enterprise deal with Acme Corp ($5,400 ARR)",
            status="completed",
            success=True,
            revenue_generated=5400,
            execution_time_seconds=900,
            completed_at=now - timedelta(hours=5),
        ),
        Task(
            task_id=_task_id(),
            agent_id=sales.id,
            category="outreach",
            description="Prospected 150 leads and booked 12 demos",
            status="completed",
            success=True,
            revenue_generated=800,
            execution_time_seconds=2400,
            completed_at=now - timedelta(hours=8),
        ),
        Task(
            task_id=_task_id(),
            agent_id=dev.id,
            category="development",
            description="Built NFT minting integration with ICP blockchain",
            status="completed",
            success=True,
            revenue_generated=2000,
            execution_time_seconds=7200,
            completed_at=now - timedelta(days=1),
        ),
        Task(
            task_id=_task_id(),
            agent_id=dev.id,
            category="development",
            description="Implement real-time WebSocket dashboard",
            status="in_progress",
            success=None,
            revenue_generated=0,
            execution_time_seconds=None,
            started_at=now - timedelta(minutes=30),
        ),
    ]
    db.add_all(tasks)

    # 3. Activity logs
    logs = [
        ActivityLog(
            actor_type="agent",
            actor_id=ceo.agent_id,
            action="completed_task",
            target_type="task",
            target_id=tasks[0].task_id,
            event_metadata={"revenue": 1200},
        ),
        ActivityLog(
            actor_type="agent",
            actor_id=sales.agent_id,
            action="completed_task",
            target_type="task",
            target_id=tasks[1].task_id,
            event_metadata={"revenue": 5400},
        ),
        ActivityLog(
            actor_type="agent",
            actor_id=dev.agent_id,
            action="completed_task",
            target_type="task",
            target_id=tasks[3].task_id,
            event_metadata={"revenue": 2000},
        ),
        ActivityLog(
            actor_type="agent",
            actor_id=dev.agent_id,
            action="started_task",
            target_type="task",
            target_id=tasks[4].task_id,
            event_metadata={},
        ),
        ActivityLog(
            actor_type="user",
            actor_id=user_id,
            action="agent_created",
            target_type="agent",
            target_id=ceo.agent_id,
            event_metadata={"name": "Alpha CEO"},
        ),
    ]
    db.add_all(logs)

    await db.commit()

    return {
        "success": True,
        "agents_created": 3,
        "tasks_created": 5,
        "logs_created": 5,
        "message": "Welcome to ARLI! Your starter team is ready.",
    }
