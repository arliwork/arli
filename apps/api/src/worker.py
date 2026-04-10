"""
Celery worker for background task processing
"""
from celery import Celery
import os
from sqlalchemy.orm import Session
from models import SessionLocal, Task, Agent
import openai
import anthropic

# Celery app
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('arli_worker', broker=redis_url, backend=redis_url)

# API clients
openai.api_key = os.getenv('OPENAI_API_KEY')
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

@celery_app.task(bind=True, max_retries=3)
def process_task(self, task_id: str):
    """Process a task in background"""
    db = SessionLocal()
    
    try:
        # Get task from DB
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update status
        task.status = 'running'
        db.commit()
        
        # Execute based on category
        result = execute_task(task)
        
        # Update task
        task.status = 'completed' if result['success'] else 'failed'
        task.success = result['success']
        task.result_data = result
        task.completed_at = datetime.now()
        
        # Update agent XP if successful
        if result['success']:
            update_agent_xp(db, task.agent_id, task)
        
        db.commit()
        
        return result
        
    except Exception as exc:
        db.rollback()
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
    finally:
        db.close()

def execute_task(task: Task) -> dict:
    """Execute task based on category"""
    category = task.category.lower()
    
    if category == 'content_creation':
        return execute_content_task(task)
    elif category == 'trading':
        return execute_trading_task(task)
    elif category == 'research':
        return execute_research_task(task)
    elif category == 'coding':
        return execute_coding_task(task)
    else:
        return {"success": False, "error": "Unknown category"}

def execute_content_task(task: Task) -> dict:
    """Generate content using GPT-4"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional content writer."},
                {"role": "user", "content": task.description}
            ],
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        word_count = len(content.split())
        
        return {
            "success": True,
            "output": content,
            "metadata": {
                "word_count": word_count,
                "model": "gpt-4",
                "tokens_used": response.usage.total_tokens
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_trading_task(task: Task) -> dict:
    """Execute trading strategy (placeholder for real exchange API)"""
    # TODO: Connect to real exchange API (Binance, Coinbase, etc.)
    return {
        "success": True,
        "output": "Trading signal generated",
        "metadata": {"note": "Real exchange integration required"}
    }

def execute_research_task(task: Task) -> dict:
    """Perform research"""
    try:
        response = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": f"Research and summarize: {task.description}"}
            ]
        )
        
        return {
            "success": True,
            "output": response.content[0].text,
            "metadata": {"model": "claude-3-opus"}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_coding_task(task: Task) -> dict:
    """Generate code"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert programmer."},
                {"role": "user", "content": task.description}
            ],
            max_tokens=3000
        )
        
        return {
            "success": True,
            "output": response.choices[0].message.content,
            "metadata": {"model": "gpt-4"}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_agent_xp(db: Session, agent_id: str, task: Task):
    """Update agent XP after successful task"""
    from datetime import datetime
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return
    
    # Calculate XP
    base_xp = 10
    success_bonus = 10 if task.success else 0
    time_bonus = max(0, 20 - int(task.execution_time_seconds / 60)) if task.execution_time_seconds else 0
    revenue_bonus = int(float(task.revenue_generated) / 100) if task.revenue_generated else 0
    rating_bonus = (task.client_rating or 3) * 5
    
    xp_gain = base_xp + success_bonus + time_bonus + revenue_bonus + rating_bonus
    
    agent.total_xp += xp_gain
    
    # Check level up
    import math
    xp_needed = int(100 * math.pow(agent.level + 1, 1.5))
    
    if agent.total_xp >= xp_needed:
        agent.level += 1
        # Update tier logic here
    
    # Recalculate market value
    agent.market_value = calculate_market_value(agent)
    
    db.commit()

def calculate_market_value(agent: Agent) -> float:
    """Calculate agent market value"""
    import math
    base = 50.0
    level_mult = math.pow(1.5, agent.level - 1)
    
    success_rate = agent.successful_tasks / agent.total_tasks if agent.total_tasks > 0 else 0
    success_factor = 1.0 + (success_rate * 2)
    
    return base * level_mult * success_factor + (agent.level * 100)

if __name__ == '__main__':
    from datetime import datetime
    celery_app.start()
