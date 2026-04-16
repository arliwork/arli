"""Agent management and marketplace routes"""
import uuid
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from decimal import Decimal

from dependencies import get_async_db
from auth import get_current_active_user
from models import Agent, User, AgentSale, Achievement
from schemas import AgentCreate, AgentUpdate, AgentOut, AgentListResponse, PurchaseAgentRequest, PurchaseResponse

router = APIRouter(prefix="/agents", tags=["agents"])

def generate_agent_id():
    return f"agent_{uuid.uuid4().hex[:8]}"

@router.post("", response_model=AgentOut)
async def create_agent(
    data: AgentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    agent = Agent(
        agent_id=generate_agent_id(),
        name=data.name,
        role=data.role,
        description=data.description,
        capabilities=data.capabilities or [],
        owner_id=current_user.id,
        creator_id=current_user.id,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return AgentOut.model_validate(agent)

@router.get("", response_model=AgentListResponse)
async def list_agents(
    is_listed: Optional[bool] = None,
    min_level: int = Query(1, ge=1),
    search: Optional[str] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(Agent).where(Agent.level >= min_level)
    if is_listed is not None:
        stmt = stmt.where(Agent.is_listed == is_listed)
    if search:
        stmt = stmt.where(Agent.name.ilike(f"%{search}%"))
    
    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar()
    
    result = await db.execute(stmt.order_by(Agent.market_value.desc()).offset(offset).limit(limit))
    items = result.scalars().all()
    return AgentListResponse(items=[AgentOut.model_validate(a) for a in items], total=total)

@router.get("/my", response_model=AgentListResponse)
async def my_agents(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.owner_id == current_user.id).order_by(Agent.created_at.desc()))
    items = result.scalars().all()
    return AgentListResponse(items=[AgentOut.model_validate(a) for a in items], total=len(items))

@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return AgentOut.model_validate(agent)

@router.patch("/{agent_id}", response_model=AgentOut)
async def update_agent(
    agent_id: str,
    data: AgentUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if agent.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(agent, key, value)
    
    await db.commit()
    await db.refresh(agent)
    return AgentOut.model_validate(agent)

@router.post("/{agent_id}/list", response_model=AgentOut)
async def list_agent_for_sale(
    agent_id: str,
    price: Decimal,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if agent.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    agent.is_listed = True
    agent.listing_price = price
    await db.commit()
    await db.refresh(agent)
    return AgentOut.model_validate(agent)

@router.post("/{agent_id}/buy", response_model=PurchaseResponse)
async def buy_agent(
    agent_id: str,
    data: PurchaseAgentRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id, Agent.is_listed == True))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not listed")
    if agent.owner_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot buy your own agent")
    
    price = agent.listing_price or Decimal("0")
    platform_fee = price * Decimal("0.10")
    creator_royalty = price * Decimal("0.05") if agent.creator_id != agent.owner_id else Decimal("0")
    seller_receives = price - platform_fee - creator_royalty
    
    sale = AgentSale(
        agent_id=agent.id,
        seller_id=agent.owner_id,
        buyer_id=current_user.id,
        price=price,
        platform_fee=platform_fee,
        creator_royalty=creator_royalty,
        seller_receives=seller_receives,
    )
    db.add(sale)
    
    agent.owner_id = current_user.id
    agent.is_listed = False
    agent.listing_price = None
    
    await db.commit()
    return PurchaseResponse(
        success=True,
        price=price,
        platform_fee=platform_fee,
        creator_royalty=creator_royalty,
        seller_receives=seller_receives,
    )

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if agent.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    await db.delete(agent)
    await db.commit()
    return None
