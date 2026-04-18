"""NFT routes for agent NFT gallery and management"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from dependencies import get_async_db
from auth import get_current_active_user
from models import Agent, User
from schemas import AgentOut, AgentListResponse

router = APIRouter(prefix="/nfts", tags=["nfts"])

@router.get("", response_model=AgentListResponse)
async def list_nft_agents(
    tier: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    """List all agents that have been minted as NFTs"""
    stmt = select(Agent).where(Agent.nft_token_id.isnot(None))
    if tier:
        stmt = stmt.where(Agent.tier == tier)
    if search:
        stmt = stmt.where(Agent.name.ilike(f"%{search}%"))

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar()

    result = await db.execute(stmt.order_by(Agent.market_value.desc()).offset(offset).limit(limit))
    items = result.scalars().all()
    return AgentListResponse(items=[AgentOut.model_validate(a) for a in items], total=total)

@router.get("/my", response_model=AgentListResponse)
async def my_nft_agents(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """List NFTs owned by current user"""
    result = await db.execute(
        select(Agent)
        .where(Agent.owner_id == current_user.id)
        .where(Agent.nft_token_id.isnot(None))
        .order_by(Agent.created_at.desc())
    )
    items = result.scalars().all()
    return AgentListResponse(items=[AgentOut.model_validate(a) for a in items], total=len(items))

@router.get("/{agent_id}", response_model=AgentOut)
async def get_nft_agent(agent_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get a specific agent NFT by agent_id"""
    result = await db.execute(
        select(Agent).where(Agent.agent_id == agent_id).where(Agent.nft_token_id.isnot(None))
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFT agent not found")
    return AgentOut.model_validate(agent)

@router.post("/{agent_id}/transfer")
async def transfer_nft_agent(
    agent_id: str,
    to_principal: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Transfer NFT ownership to another principal"""
    result = await db.execute(
        select(Agent).where(Agent.agent_id == agent_id).where(Agent.nft_token_id.isnot(None))
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NFT agent not found")
    if agent.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")

    # Call ICP canister to transfer NFT
    try:
        from icp_integration import icp_client
        success = await icp_client.transfer_nft(
            token_id=agent.nft_token_id,
            from_principal=current_user.principal or str(current_user.id),
            to_principal=to_principal,
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transfer failed")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # Update local DB ownership
    # TODO: Resolve new owner user from principal, or mark as transferred
    agent.nft_token_id = None  # Clear until new owner claims
    await db.commit()
    await db.refresh(agent)
    return {"success": True, "message": "NFT transferred", "agent_id": agent_id}
