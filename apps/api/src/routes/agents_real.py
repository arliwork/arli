"""
Real Agent API - Production ready with PostgreSQL
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from models import get_db, Agent, AgentExpertise, Task, Achievement, User

router = APIRouter(prefix="/agents", tags=["agents"])

# Schemas
class AgentCreate(BaseModel):
    name: str
    owner_id: str

class TaskCreate(BaseModel):
    category: str
    description: str
    success: bool
    execution_time: int = 3600
    revenue: float = 0.0
    rating: Optional[int] = None

class AgentResponse(BaseModel):
    id: str
    agent_id: str
    name: str
    level: int
    tier: str
    total_xp: int
    success_rate: float
    market_value: float
    total_revenue: float
    is_listed: bool
    listing_price: Optional[float]
    
    class Config:
        from_attributes = True

# Endpoints

@router.post("/create", response_model=AgentResponse)
def create_agent(data: AgentCreate, db: Session = Depends(get_db)):
    """Create new agent in database"""
    agent_uuid = str(uuid.uuid4())
    agent_id = f"agent_{datetime.now().timestamp()}"
    
    agent = Agent(
        id=agent_uuid,
        agent_id=agent_id,
        name=data.name,
        owner_id=data.owner_id,
        creator_id=data.owner_id,
        level=1,
        tier='NOVICE',
        market_value=50.0
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return agent

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent by ID"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/owner/{owner_id}", response_model=List[AgentResponse])
def get_owner_agents(owner_id: str, db: Session = Depends(get_db)):
    """Get all agents owned by user"""
    agents = db.query(Agent).filter(Agent.owner_id == owner_id).all()
    return agents

@router.get("/marketplace/listings", response_model=List[AgentResponse])
def get_marketplace_listings(
    min_level: int = 1,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get listed agents for marketplace"""
    query = db.query(Agent).filter(Agent.is_listed == True, Agent.level >= min_level)
    
    if max_price:
        query = query.filter(Agent.listing_price <= max_price)
    
    agents = query.order_by(Agent.market_value.desc()).all()
    return agents

@router.post("/{agent_id}/tasks")
def record_task(agent_id: str, task_data: TaskCreate, db: Session = Depends(get_db)):
    """Record completed task and update agent XP"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Create task record
    task = Task(
        id=str(uuid.uuid4()),
        task_id=f"task_{datetime.now().timestamp()}",
        agent_id=agent.id,
        category=task_data.category,
        description=task_data.description,
        status='completed',
        success=task_data.success,
        execution_time_seconds=task_data.execution_time,
        revenue_generated=task_data.revenue,
        client_rating=task_data.rating,
        completed_at=datetime.now()
    )
    db.add(task)
    
    # Update agent stats
    agent.total_tasks += 1
    if task_data.success:
        agent.successful_tasks += 1
        # Calculate XP
        xp_gain = calculate_xp(task_data)
        agent.total_xp += xp_gain
    
    agent.total_revenue += task_data.revenue
    
    # Update or create expertise
    expertise = db.query(AgentExpertise).filter(
        AgentExpertise.agent_id == agent.id,
        AgentExpertise.domain == task_data.category
    ).first()
    
    if not expertise:
        expertise = AgentExpertise(
            id=str(uuid.uuid4()),
            agent_id=agent.id,
            domain=task_data.category,
            tasks_completed=0,
            successful_tasks=0
        )
        db.add(expertise)
    
    expertise.tasks_completed += 1
    if task_data.success:
        expertise.successful_tasks += 1
    expertise.total_revenue += task_data.revenue
    
    # Check level up
    check_and_apply_level_up(agent)
    
    # Recalculate market value
    agent.market_value = calculate_market_value(agent)
    agent.hourly_rate = calculate_hourly_rate(agent)
    
    db.commit()
    
    return {
        "success": True,
        "xp_gained": xp_gain if task_data.success else 1,
        "total_xp": agent.total_xp,
        "level": agent.level,
        "market_value": float(agent.market_value)
    }

def calculate_xp(task_data: TaskCreate) -> int:
    """Calculate XP for task completion"""
    base = 10
    success_bonus = 10
    time_bonus = max(0, 20 - int(task_data.execution_time / 60))
    revenue_bonus = int(task_data.revenue / 100)
    rating_bonus = (task_data.rating or 3) * 5
    return base + success_bonus + time_bonus + revenue_bonus + rating_bonus

def check_and_apply_level_up(agent: Agent):
    """Check if agent should level up"""
    import math
    xp_needed = int(100 * math.pow(agent.level + 1, 1.5))
    
    if agent.total_xp >= xp_needed:
        agent.level += 1
        
        # Update tier
        tiers = [
            (1, 3, 'NOVICE'),
            (4, 6, 'APPRENTICE'),
            (7, 9, 'JOURNEYMAN'),
            (10, 14, 'EXPERT'),
            (15, 19, 'MASTER'),
            (20, 24, 'GRANDMASTER'),
            (25, 999, 'LEGENDARY')
        ]
        
        for min_lv, max_lv, tier_name in tiers:
            if min_lv <= agent.level <= max_lv:
                agent.tier = tier_name
                break

def calculate_market_value(agent: Agent) -> float:
    """Calculate agent market value"""
    import math
    base = 50.0
    level_mult = math.pow(1.5, agent.level - 1)
    
    success_rate = agent.successful_tasks / agent.total_tasks if agent.total_tasks > 0 else 0
    success_factor = 1.0 + (success_rate * 2)
    
    tier_bonus = agent.level * 100
    
    return base * level_mult * success_factor + tier_bonus

def calculate_hourly_rate(agent: Agent) -> float:
    """Calculate estimated hourly rate"""
    import math
    base = 10.0
    mult = math.pow(1.3, agent.level - 1)
    return base * mult

@router.post("/{agent_id}/list")
def list_agent(agent_id: str, price: float, db: Session = Depends(get_db)):
    """List agent for sale"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.is_listed = True
    agent.listing_price = price
    db.commit()
    
    return {"success": True, "listing_price": price}

@router.post("/{agent_id}/buy")
def buy_agent(agent_id: str, buyer_id: str, db: Session = Depends(get_db)):
    """Buy agent (transfer ownership)"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if not agent.is_listed:
        raise HTTPException(status_code=400, detail="Agent not listed for sale")
    
    # Record sale
    sale = AgentSale(
        id=str(uuid.uuid4()),
        agent_id=agent.id,
        seller_id=agent.owner_id,
        buyer_id=buyer_id,
        price=agent.listing_price,
        platform_fee=agent.listing_price * 0.10,
        creator_royalty=agent.listing_price * 0.05,
        seller_receives=agent.listing_price * 0.85
    )
    db.add(sale)
    
    # Transfer ownership
    agent.owner_id = buyer_id
    agent.is_listed = False
    agent.listing_price = None
    
    db.commit()
    
    return {"success": True, "new_owner": buyer_id}

@router.get("/stats/global")
def get_global_stats(db: Session = Depends(get_db)):
    """Get global marketplace stats"""
    from sqlalchemy import func
    
    total_agents = db.query(func.count(Agent.id)).scalar()
    total_value = db.query(func.sum(Agent.market_value)).scalar() or 0
    total_revenue = db.query(func.sum(Agent.total_revenue)).scalar() or 0
    listed_count = db.query(func.count(Agent.id)).filter(Agent.is_listed == True).scalar()
    
    return {
        "total_agents": total_agents,
        "total_market_value": float(total_value),
        "total_revenue_generated": float(total_revenue),
        "agents_listed": listed_count
    }
