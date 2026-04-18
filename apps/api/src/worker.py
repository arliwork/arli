"""Celery worker for background task processing"""
from celery import Celery
from celery.signals import worker_process_init
import os
import asyncio
from datetime import datetime, timezone
import math
import sys
from pathlib import Path

from config import settings

redis_url = settings.REDIS_URL

celery_app = Celery(
    "arli_worker",
    broker=redis_url,
    backend=redis_url,
    include=["worker"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "run-scheduled-workflows": {
            "task": "worker.run_scheduled_workflows",
            "schedule": 60.0,  # Check every minute
        },
        "run-agent-heartbeats": {
            "task": "worker.run_agent_heartbeats",
            "schedule": 300.0,  # Every 5 minutes
        },
    },
)

# Database and models initialized lazily per worker process
db_session = None
llm_client = None

@worker_process_init.connect
def init_worker(**kwargs):
    global db_session, llm_client
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models import Base
    from services.llm_client import get_llm_client
    
    sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(sync_db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    Base.metadata.create_all(bind=engine)
    
    llm_client = get_llm_client()

@celery_app.task(bind=True, max_retries=3)
def process_task(self, task_id: str):
    """Process a task in background"""
    from models import Task, Agent
    
    task = db_session.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    task.status = "running"
    task.started_at = datetime.now(timezone.utc)
    db_session.commit()
    
    try:
        # Run async task execution in sync celery context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(execute_real_task(task))
        loop.close()
        
        task.status = "completed" if result.get("success") else "failed"
        task.success = result.get("success")
        task.result_data = result
        task.completed_at = datetime.now(timezone.utc)
        
        if result.get("success") and task.agent_id:
            update_agent_xp(db_session, task.agent_id, task)
            # Deduct credits for LLM usage
            credits_used = result.get("credits_used", 0)
            if credits_used:
                deduct_credits_sync(task.agent_id, credits_used)
        
        db_session.commit()
        return result
        
    except Exception as exc:
        db_session.rollback()
        task.status = "failed"
        task.error_message = str(exc)
        task.completed_at = datetime.now(timezone.utc)
        db_session.commit()
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

async def execute_real_task(task: Task) -> dict:
    """Execute task using LLM client and real tools"""
    import json
    
    category = task.category.lower()
    
    # Coding tasks
    if category in ("coding", "development", "backend", "frontend"):
        lang = "python" if "backend" in category or "coding" in category else "typescript"
        messages = [
            {"role": "system", "content": f"You are an expert {lang} developer. Write clean, production-ready code with comments."},
            {"role": "user", "content": f"Write {lang} code for: {task.description}"},
        ]
        result = await llm_client.generate(messages=messages, task_type="coding", max_tokens=4000)
        return {
            "success": True,
            "output": result.content,
            "credits_used": result.credits_used,
            "model_used": result.model,
            "metadata": {"category": category, "language": lang},
        }
    
    # Research tasks
    elif category in ("research", "analysis"):
        result = await llm_client.generate(
            messages=[
                {"role": "system", "content": "You are a research analyst. Provide concise, actionable insights."},
                {"role": "user", "content": f"Research and summarize: {task.description}"}
            ],
            task_type="reasoning",
            max_tokens=3000,
        )
        return {
            "success": True,
            "output": result.content,
            "credits_used": result.credits_used,
            "model_used": result.model,
            "metadata": {"category": category},
        }
    
    # Content tasks
    elif category in ("content_creation", "content"):
        result = await llm_client.generate(
            messages=[
                {"role": "system", "content": "You are a professional content writer."},
                {"role": "user", "content": task.description}
            ],
            task_type="default",
            max_tokens=3000,
        )
        word_count = len(result.content.split())
        return {
            "success": True,
            "output": result.content,
            "credits_used": result.credits_used,
            "model_used": result.model,
            "metadata": {"category": category, "word_count": word_count},
        }
    
    # Planning/Strategy tasks
    elif category in ("planning", "strategy"):
        messages = [
            {"role": "system", "content": "You are a strategic planner. Break down complex objectives into clear, actionable steps."},
            {"role": "user", "content": task.description},
        ]
        result = await llm_client.generate(messages=messages, task_type="reasoning", max_tokens=2000)
        return {
            "success": True,
            "output": result.content,
            "credits_used": result.credits_used,
            "model_used": result.model,
            "metadata": {"category": category},
        }
    
    # Trading tasks
    elif category in ("trading",):
        return {
            "success": True,
            "output": "Trading signal generated",
            "metadata": {"category": category, "note": "Connect exchange API for live trading"},
        }
    
    # Generic tasks
    else:
        result = await llm_client.generate(
            messages=[{"role": "user", "content": task.description}],
            task_type="default",
        )
        return {
            "success": True,
            "output": result.content,
            "credits_used": result.credits_used,
            "model_used": result.model,
            "metadata": {"category": category},
        }

def update_agent_xp(db, agent_id: str, task: Task):
    """Update agent XP after successful task"""
    from models import Agent
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return
    
    base_xp = 10
    success_bonus = 10 if task.success else 0
    time_bonus = max(0, 20 - int((task.execution_time_seconds or 0) / 60))
    revenue_bonus = int(float(task.revenue_generated or 0) / 100)
    rating_bonus = (task.client_rating or 3) * 5
    
    xp_gain = base_xp + success_bonus + time_bonus + revenue_bonus + rating_bonus
    
    agent.total_xp += xp_gain
    agent.total_tasks += 1
    if task.success:
        agent.successful_tasks += 1
    
    # Check level up
    new_level = int((agent.total_xp / 100) ** (2/3)) + 1
    if new_level > agent.level:
        agent.level = new_level
        agent.tier = get_tier(new_level)
    
    agent.market_value = calculate_market_value(agent)
    agent.updated_at = datetime.now(timezone.utc)
    db.commit()

def get_tier(level: int) -> str:
    if level >= 25: return "LEGENDARY"
    if level >= 20: return "GRANDMASTER"
    if level >= 15: return "MASTER"
    if level >= 10: return "EXPERT"
    if level >= 7: return "JOURNEYMAN"
    if level >= 4: return "APPRENTICE"
    return "NOVICE"

def calculate_market_value(agent) -> float:
    base = 50.0
    level_mult = 1.5 ** (agent.level - 1)
    success_rate = agent.successful_tasks / max(agent.total_tasks, 1)
    success_factor = 1.0 + success_rate * 2.0
    return base * level_mult * success_factor + (agent.level * 100)

def deduct_credits_sync(agent_id: str, amount: float):
    """Deduct credits from agent owner's balance synchronously"""
    from decimal import Decimal
    from models import Agent, User
    
    agent = db_session.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return
    
    user = db_session.query(User).filter(User.id == agent.owner_id).first()
    if not user:
        return
    
    amount_dec = Decimal(str(amount))
    if user.credits_balance >= amount_dec:
        user.credits_balance -= amount_dec
        user.credits_spent += amount_dec
        db_session.commit()
    else:
        db_session.rollback()

@celery_app.task
def run_scheduled_workflows():
    """Check and run due scheduled workflows"""
    from models import ScheduledWorkflow
    from services.orchestration_service import get_orchestrator
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import asyncio
    
    sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(sync_db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        now = datetime.now(timezone.utc)
        schedules = db.query(ScheduledWorkflow).filter(
            ScheduledWorkflow.is_active == True
        ).all()
        
        orchestrator = get_orchestrator()
        
        for sched in schedules:
            # Simple schedule parsing
            should_run = False
            if sched.schedule in ("hourly", "every hour"):
                should_run = sched.last_run_at is None or (now - sched.last_run_at).total_seconds() >= 3600
            elif sched.schedule in ("daily", "every day"):
                should_run = sched.last_run_at is None or (now - sched.last_run_at).total_seconds() >= 86400
            elif sched.schedule in ("weekly",):
                should_run = sched.last_run_at is None or (now - sched.last_run_at).total_seconds() >= 604800
            else:
                # Default to hourly if unrecognized
                should_run = sched.last_run_at is None or (now - sched.last_run_at).total_seconds() >= 3600
            
            if should_run:
                # Create and run workflow
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
                from sqlalchemy.orm import sessionmaker
                
                async_engine = create_async_engine(settings.DATABASE_URL)
                async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
                
                async def run_sched():
                    async with async_session() as async_db:
                        workflow = await orchestrator.create_workflow(
                            db=async_db,
                            name=sched.name,
                            description=sched.description or f"Scheduled: {sched.name}",
                            pipeline_type=sched.pipeline_type,
                            context=sched.context,
                        )
                        result = await orchestrator.run_full_workflow(async_db, workflow.workflow_id)
                        
                        sched.last_run_at = datetime.now(timezone.utc)
                        sched.run_count += 1
                        # Update next_run_at roughly
                        if sched.schedule in ("hourly", "every hour"):
                            sched.next_run_at = datetime.now(timezone.utc).replace(second=0, microsecond=0)
                        elif sched.schedule in ("daily", "every day"):
                            sched.next_run_at = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                        
                        await async_db.commit()
                        return result
                
                try:
                    result = loop.run_until_complete(run_sched())
                    print(f"[Scheduler] Ran {sched.schedule_id}: {result['steps_executed']} steps")
                except Exception as e:
                    print(f"[Scheduler] Failed {sched.schedule_id}: {e}")
                finally:
                    loop.close()
                    async_engine.dispose()
        
        db.commit()
    finally:
        db.close()

@celery_app.task
def run_agent_heartbeats():
    """Run heartbeat cycle for all active agents every 5 minutes."""
    import asyncio
    from services.heartbeat_scheduler import run_all_heartbeats

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(run_all_heartbeats())
        print(f"[Heartbeat] Processed {result['agents_processed']} agents at {result['run_at']}")
    except Exception as e:
        print(f"[Heartbeat] Error: {e}")
    finally:
        loop.close()
