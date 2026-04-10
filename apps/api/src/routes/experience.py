"""
Experience System API Routes
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'agents'))

from agent_experience import (
    ExperienceTracker, TaskRecord, TaskCategory, 
    calculate_training_roi, estimate_training_time
)

router = APIRouter(prefix="/experience", tags=["experience"])

# Initialize tracker
tracker = ExperienceTracker()

class CreateAgentRequest(BaseModel):
    agent_name: str
    creator_id: str

class TaskRequest(BaseModel):
    category: str
    description: str
    success: bool
    execution_time: float = 3600
    revenue_generated: float = 0.0
    client_rating: Optional[float] = None

class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
    level: int
    tier: str
    total_xp: int
    success_rate: float
    market_value: float
    hourly_rate: float
    total_revenue: float
    achievements: List[str]

@router.post("/agents/create")
async def create_agent(request: CreateAgentRequest):
    """Create new agent with experience tracking"""
    import hashlib
    import time
    
    agent_id = f"agent_{hashlib.md5(f'{request.agent_name}{time.time()}'.encode()).hexdigest()[:8]}"
    
    agent = tracker.create_agent(
        agent_id=agent_id,
        agent_name=request.agent_name,
        creator=request.creator_id
    )
    
    return {
        "success": True,
        "agent_id": agent_id,
        "agent_name": agent.agent_name,
        "initial_value": agent.market_value,
        "level": agent.level
    }

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent experience profile"""
    agent = tracker.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent.to_dict()

@router.post("/agents/{agent_id}/tasks")
async def record_task(agent_id: str, request: TaskRequest):
    """Record a completed task"""
    agent = tracker.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        category = TaskCategory(request.category)
    except ValueError:
        category = TaskCategory.OTHER
    
    task = TaskRecord(
        task_id=f"task_{int(os.times().system * 1000)}",
        category=category,
        description=request.description,
        success=request.success,
        execution_time=request.execution_time,
        revenue_generated=request.revenue_generated,
        client_rating=request.client_rating
    )
    
    result = tracker.record_task(agent_id, task)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "success": True,
        "xp_gained": result["xp_gained"],
        "total_xp": result["total_xp"],
        "level": result["level"],
        "tier": result["tier"],
        "level_up": result["level_up"],
        "new_achievements": result["new_achievements"],
        "market_value": result["market_value"]
    }

@router.get("/agents/{agent_id}/value-report")
async def get_value_report(agent_id: str):
    """Get agent value analysis"""
    agent = tracker.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    initial_value = 50.0
    training_cost = agent.total_execution_time * 0.01
    
    roi = calculate_training_roi(initial_value, agent.market_value, training_cost)
    next_level = estimate_training_time(agent.level, agent.level + 1)
    
    return {
        "agent_id": agent.agent_id,
        "agent_name": agent.agent_name,
        "current_value": agent.market_value,
        "initial_value": initial_value,
        "value_growth": agent.market_value - initial_value,
        "growth_percent": ((agent.market_value - initial_value) / initial_value) * 100,
        "training_cost": training_cost,
        "roi_percent": roi["roi_percent"],
        "total_revenue": agent.total_revenue_generated,
        "hourly_rate": agent.hourly_rate_estimate,
        "next_level": next_level
    }

@router.get("/marketplace")
async def get_marketplace_listings(
    min_level: int = Query(1, ge=1),
    category: Optional[str] = None,
    limit: int = Query(20, le=100)
):
    """Get agents available for purchase"""
    listings = []
    
    for agent_id, agent in tracker.agents.items():
        if agent.level < min_level:
            continue
        
        if category and category not in agent.expertise:
            continue
        
        listings.append({
            "agent_id": agent_id,
            "agent_name": agent.agent_name,
            "level": agent.level,
            "tier": agent.tier.name,
            "market_value": agent.market_value,
            "success_rate": agent.success_rate,
            "average_rating": agent.average_rating,
            "total_tasks": agent.total_tasks,
            "total_revenue": agent.total_revenue_generated,
            "domains": list(agent.expertise.keys()),
            "achievements": agent.achievements,
            "hourly_rate": agent.hourly_rate_estimate,
            "creator": agent.original_creator,
            "times_sold": agent.times_sold
        })
    
    listings.sort(key=lambda x: x["market_value"], reverse=True)
    return listings[:limit]

@router.get("/leaderboard")
async def get_leaderboard(category: Optional[str] = None, limit: int = 10):
    """Get top agents by experience"""
    cat_enum = None
    if category:
        try:
            cat_enum = TaskCategory(category)
        except ValueError:
            pass
    
    leaderboard = tracker.get_leaderboard(category=cat_enum, limit=limit)
    return leaderboard

@router.get("/stats/global")
async def get_global_stats():
    """Get global marketplace stats"""
    total_agents = len(tracker.agents)
    total_value = sum(a.market_value for a in tracker.agents.values())
    total_revenue = sum(a.total_revenue_generated for a in tracker.agents.values())
    
    tier_counts = {}
    for agent in tracker.agents.values():
        tier = agent.tier.name
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    return {
        "total_agents": total_agents,
        "total_market_value": total_value,
        "total_revenue_generated": total_revenue,
        "average_agent_value": total_value / total_agents if total_agents > 0 else 0,
        "tier_distribution": tier_counts
    }
