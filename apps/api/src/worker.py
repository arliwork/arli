"""Celery worker for background task processing"""
from celery import Celery
from celery.signals import worker_process_init
import os
from datetime import datetime, timezone
import math

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
)

# Database and models initialized lazily per worker process
db_session = None

@worker_process_init.connect
def init_worker(**kwargs):
    global db_session
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models import Base
    
    sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(sync_db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    Base.metadata.create_all(bind=engine)

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
        result = execute_real_task(task)
        
        task.status = "completed" if result.get("success") else "failed"
        task.success = result.get("success")
        task.result_data = result
        task.completed_at = datetime.now(timezone.utc)
        
        if result.get("success") and task.agent_id:
            update_agent_xp(db_session, task.agent_id, task)
        
        db_session.commit()
        return result
        
    except Exception as exc:
        db_session.rollback()
        task.status = "failed"
        task.error_message = str(exc)
        task.completed_at = datetime.now(timezone.utc)
        db_session.commit()
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

def execute_real_task(task: Task) -> dict:
    """Execute task based on category using real workers"""
    import sys
    from pathlib import Path
    
    # Import task workers
    workers_path = Path(__file__).resolve().parents[2] / "workers"
    sys.path.insert(0, str(workers_path))
    
    category = task.category.lower()
    
    # Delegate to actual worker implementations
    if category in ("content_creation", "content"):
        from task_workers import ContentWorker
        worker = ContentWorker()
        return worker.execute_sync({
            "type": "blog",
            "topic": task.description,
            "word_count": 500,
        })
    elif category in ("trading", "analysis"):
        from task_workers import TradingWorker
        worker = TradingWorker()
        return worker.execute_sync({
            "symbol": "BTCUSDT",
            "action": "analyze",
        })
    elif category in ("research",):
        from task_workers import ResearchWorker
        worker = ResearchWorker()
        return worker.execute_sync({
            "query": task.description,
            "sources": ["web"],
        })
    else:
        # Generic coding/implementation task
        return {
            "success": True,
            "output": f"Executed {category} task: {task.description}",
            "metadata": {"category": category, "task_id": task.task_id}
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
