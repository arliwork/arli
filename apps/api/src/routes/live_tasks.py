"""
Live Tasks API - Real task execution system
Connects agents to real task execution with XP tracking
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'agents'))

from agent_experience import ExperienceTracker, TaskRecord, TaskCategory

router = APIRouter(prefix="/tasks", tags=["live-tasks"])

# Initialize tracker
tracker = ExperienceTracker()

# Task queue
task_queue: List[Dict] = []
running_tasks: Dict[str, Dict] = {}
task_results: Dict[str, Any] = {}

# Task handlers registry
task_handlers: Dict[str, Callable] = {}

class TaskRequest(BaseModel):
    agent_id: str
    category: str
    description: str
    parameters: Dict[str, Any] = {}
    priority: int = 1  # 1-5, higher = more important

class TaskResponse(BaseModel):
    task_id: str
    agent_id: str
    status: str  # queued, running, completed, failed
    result: Optional[Dict] = None
    xp_gained: Optional[int] = None

class TaskResult(BaseModel):
    success: bool
    output: str
    revenue_generated: float = 0.0
    execution_time: float = 0.0
    metadata: Dict[str, Any] = {}

def register_task_handler(category: str, handler: Callable):
    """Register a handler for a task category"""
    task_handlers[category] = handler

# Task Handlers

async def handle_content_creation(params: Dict) -> TaskResult:
    """Generate content using GPT or templates"""
    start_time = datetime.now()
    
    try:
        # Simulate content generation
        content_type = params.get('type', 'blog')
        topic = params.get('topic', 'general')
        
        # In real implementation, call GPT-4 API here
        output = f"Generated {content_type} about {topic}"
        
        # Calculate revenue (example: $0.10 per word)
        word_count = len(output.split())
        revenue = word_count * 0.10
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return TaskResult(
            success=True,
            output=output,
            revenue_generated=revenue,
            execution_time=execution_time,
            metadata={"word_count": word_count, "type": content_type}
        )
    except Exception as e:
        return TaskResult(
            success=False,
            output=str(e),
            execution_time=(datetime.now() - start_time).total_seconds()
        )

async def handle_trading_task(params: Dict) -> TaskResult:
    """Execute trading strategy"""
    start_time = datetime.now()
    
    try:
        # Simulate trading (in real: connect to exchange API)
        symbol = params.get('symbol', 'BTC')
        action = params.get('action', 'hold')
        
        # Mock profit calculation
        import random
        profit = random.uniform(-100, 500) if action != 'hold' else 0
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return TaskResult(
            success=profit > 0,
            output=f"{action.upper()} {symbol}: ${profit:.2f}",
            revenue_generated=max(0, profit),
            execution_time=execution_time,
            metadata={"symbol": symbol, "action": action, "pnl": profit}
        )
    except Exception as e:
        return TaskResult(
            success=False,
            output=str(e),
            execution_time=(datetime.now() - start_time).total_seconds()
        )

async def handle_research_task(params: Dict) -> TaskResult:
    """Perform research task"""
    start_time = datetime.now()
    
    try:
        query = params.get('query', '')
        
        # Simulate research (in real: web search + analysis)
        # For now, return mock results
        findings = f"Research findings for: {query}"
        
        # Revenue from research (example: hourly rate)
        execution_time = (datetime.now() - start_time).total_seconds()
        revenue = (execution_time / 3600) * 50  # $50/hr
        
        return TaskResult(
            success=True,
            output=findings,
            revenue_generated=revenue,
            execution_time=execution_time,
            metadata={"sources": 5, "findings": len(findings)}
        )
    except Exception as e:
        return TaskResult(
            success=False,
            output=str(e),
            execution_time=(datetime.now() - start_time).total_seconds()
        )

async def handle_data_analysis(params: Dict) -> TaskResult:
    """Analyze data"""
    start_time = datetime.now()
    
    try:
        dataset = params.get('dataset', '')
        
        # Simulate analysis
        insights = f"Analyzed {dataset}: Found 3 key patterns"
        
        execution_time = (datetime.now() - start_time).total_seconds()
        revenue = (execution_time / 3600) * 75  # $75/hr
        
        return TaskResult(
            success=True,
            output=insights,
            revenue_generated=revenue,
            execution_time=execution_time,
            metadata={"rows_analyzed": 10000, "patterns_found": 3}
        )
    except Exception as e:
        return TaskResult(
            success=False,
            output=str(e),
            execution_time=(datetime.now() - start_time).total_seconds()
        )

# Register handlers
register_task_handler("content_creation", handle_content_creation)
register_task_handler("trading", handle_trading_task)
register_task_handler("research", handle_research_task)
register_task_handler("data_analysis", handle_data_analysis)

# API Endpoints

@router.post("/submit", response_model=TaskResponse)
async def submit_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Submit a new task for execution"""
    task_id = f"task_{datetime.now().timestamp()}_{request.agent_id}"
    
    task = {
        "task_id": task_id,
        "agent_id": request.agent_id,
        "category": request.category,
        "description": request.description,
        "parameters": request.parameters,
        "priority": request.priority,
        "status": "queued",
        "created_at": datetime.now().isoformat()
    }
    
    # Add to queue
    task_queue.append(task)
    task_queue.sort(key=lambda x: x["priority"], reverse=True)
    
    # Start processing in background
    background_tasks.add_task(process_task, task_id)
    
    return TaskResponse(
        task_id=task_id,
        agent_id=request.agent_id,
        status="queued"
    )

@router.get("/{task_id}/status")
async def get_task_status(task_id: str):
    """Get task status and result"""
    # Check if completed
    if task_id in task_results:
        result = task_results[task_id]
        return TaskResponse(
            task_id=task_id,
            agent_id=result.get("agent_id"),
            status="completed" if result.get("success") else "failed",
            result=result,
            xp_gained=result.get("xp_gained")
        )
    
    # Check if running
    if task_id in running_tasks:
        return TaskResponse(
            task_id=task_id,
            agent_id=running_tasks[task_id]["agent_id"],
            status="running"
        )
    
    # Check if queued
    for task in task_queue:
        if task["task_id"] == task_id:
            return TaskResponse(
                task_id=task_id,
                agent_id=task["agent_id"],
                status="queued"
            )
    
    raise HTTPException(status_code=404, detail="Task not found")

@router.get("/agent/{agent_id}/history")
async def get_agent_task_history(agent_id: str, limit: int = 10):
    """Get task history for an agent"""
    # Get from experience tracker
    agent = tracker.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Return recent tasks (in real: fetch from DB)
    return {
        "agent_id": agent_id,
        "total_tasks": agent.total_tasks,
        "recent_tasks": []  # TODO: fetch from storage
    }

@router.get("/queue")
async def get_queue_status():
    """Get current task queue status"""
    return {
        "queued": len(task_queue),
        "running": len(running_tasks),
        "completed": len(task_results),
        "queue": [t["task_id"] for t in task_queue[:5]]  # Show first 5
    }

async def process_task(task_id: str):
    """Process a task"""
    # Find task in queue
    task = None
    for t in task_queue:
        if t["task_id"] == task_id:
            task = t
            break
    
    if not task:
        return
    
    # Remove from queue, add to running
    task_queue.remove(task)
    running_tasks[task_id] = task
    task["status"] = "running"
    task["started_at"] = datetime.now().isoformat()
    
    try:
        # Get handler
        category = task["category"]
        handler = task_handlers.get(category)
        
        if not handler:
            raise Exception(f"No handler for category: {category}")
        
        # Execute task
        result = await handler(task["parameters"])
        
        # Record in experience system
        agent_id = task["agent_id"]
        
        try:
            cat_enum = TaskCategory(category)
        except:
            cat_enum = TaskCategory.OTHER
        
        exp_task = TaskRecord(
            task_id=task_id,
            category=cat_enum,
            description=task["description"],
            success=result.success,
            execution_time=result.execution_time,
            revenue_generated=result.revenue_generated,
            client_rating=5.0 if result.success else None
        )
        
        xp_result = tracker.record_task(agent_id, exp_task)
        
        # Store result
        task_results[task_id] = {
            "task_id": task_id,
            "agent_id": agent_id,
            "success": result.success,
            "output": result.output,
            "revenue": result.revenue_generated,
            "execution_time": result.execution_time,
            "xp_gained": xp_result.get("xp_gained", 0),
            "metadata": result.metadata,
            "completed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        task_results[task_id] = {
            "task_id": task_id,
            "agent_id": task["agent_id"],
            "success": False,
            "output": str(e),
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        }
    finally:
        # Remove from running
        if task_id in running_tasks:
            del running_tasks[task_id]

@router.post("/batch")
async def submit_batch_tasks(requests: List[TaskRequest], background_tasks: BackgroundTasks):
    """Submit multiple tasks"""
    results = []
    for request in requests:
        result = await submit_task(request, background_tasks)
        results.append(result)
    return results

# Webhook for external task completion
@router.post("/webhook/complete/{task_id}")
async def webhook_task_complete(task_id: str, result: TaskResult):
    """External systems can call this to complete tasks"""
    if task_id in running_tasks:
        task = running_tasks[task_id]
        
        # Record in experience
        agent_id = task["agent_id"]
        category = task["category"]
        
        try:
            cat_enum = TaskCategory(category)
        except:
            cat_enum = TaskCategory.OTHER
        
        exp_task = TaskRecord(
            task_id=task_id,
            category=cat_enum,
            description=task["description"],
            success=result.success,
            execution_time=result.execution_time,
            revenue_generated=result.revenue_generated,
            client_rating=5.0 if result.success else None
        )
        
        xp_result = tracker.record_task(agent_id, exp_task)
        
        task_results[task_id] = {
            "task_id": task_id,
            "agent_id": agent_id,
            "success": result.success,
            "output": result.output,
            "revenue": result.revenue_generated,
            "xp_gained": xp_result.get("xp_gained", 0),
            "metadata": result.metadata
        }
        
        del running_tasks[task_id]
        
        return {"success": True}
    
    raise HTTPException(status_code=404, detail="Task not found or not running")
