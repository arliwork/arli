"""Approvals system — governance layer for AI companies"""
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone

from dependencies import get_async_db
from auth import get_current_active_user
from models import Approval, Agent, User, Company
from schemas import ApprovalCreate, ApprovalUpdate, ApprovalOut, ApprovalListResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])

def generate_approval_id():
    return f"aprv_{uuid.uuid4().hex[:8]}"

@router.post("", response_model=ApprovalOut)
async def create_approval(
    data: ApprovalCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    approval = Approval(
        approval_id=generate_approval_id(),
        company_id=data.company_id,
        approval_type=data.approval_type,
        title=data.title,
        description=data.description,
        payload=data.payload or {},
        requested_by_agent_id=data.requested_by_agent_id,
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    return ApprovalOut.model_validate(approval)

@router.get("", response_model=ApprovalListResponse)
async def list_approvals(
    status: Optional[str] = None,
    approval_type: Optional[str] = None,
    company_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    stmt = select(Approval)
    if status:
        stmt = stmt.where(Approval.status == status)
    if approval_type:
        stmt = stmt.where(Approval.approval_type == approval_type)
    if company_id:
        stmt = stmt.where(Approval.company_id == company_id)

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar()

    result = await db.execute(stmt.order_by(Approval.created_at.desc()).offset(offset).limit(limit))
    items = result.scalars().all()
    return ApprovalListResponse(items=[ApprovalOut.model_validate(a) for a in items], total=total)

@router.get("/pending", response_model=ApprovalListResponse)
async def pending_approvals(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Approval)
        .where(Approval.status.in_(["pending", "revision_requested"]))
        .order_by(Approval.created_at.desc())
    )
    items = result.scalars().all()
    return ApprovalListResponse(items=[ApprovalOut.model_validate(a) for a in items], total=len(items))

@router.get("/{approval_id}", response_model=ApprovalOut)
async def get_approval(approval_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Approval).where(Approval.approval_id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    return ApprovalOut.model_validate(approval)

@router.post("/{approval_id}/approve", response_model=ApprovalOut)
async def approve_request(
    approval_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Approval).where(Approval.approval_id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    if approval.status not in ("pending", "revision_requested"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval already decided")

    approval.status = "approved"
    approval.approved_by_user_id = current_user.id
    approval.decided_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(approval)
    return ApprovalOut.model_validate(approval)

@router.post("/{approval_id}/reject", response_model=ApprovalOut)
async def reject_request(
    approval_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Approval).where(Approval.approval_id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    if approval.status not in ("pending", "revision_requested"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval already decided")

    approval.status = "rejected"
    approval.approved_by_user_id = current_user.id
    approval.rejection_reason = reason
    approval.decided_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(approval)
    return ApprovalOut.model_validate(approval)

@router.post("/{approval_id}/request-revision", response_model=ApprovalOut)
async def request_revision(
    approval_id: str,
    feedback: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Approval).where(Approval.approval_id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only request revision on pending approvals")

    approval.status = "revision_requested"
    approval.rejection_reason = feedback
    await db.commit()
    await db.refresh(approval)
    return ApprovalOut.model_validate(approval)

# Board Override — human can override any agent decision
@router.post("/board-override/{agent_id}")
async def board_override(
    agent_id: str,
    action: str,  # pause, resume, fire, reassign
    reason: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    if action == "pause":
        agent.status = "paused"
    elif action == "resume":
        agent.status = "idle"
    elif action == "fire":
        agent.status = "terminated"
    elif action == "reassign":
        # Payload would contain new_manager_id
        pass

    await db.commit()
    await db.refresh(agent)
    return {"success": True, "agent_id": agent_id, "action": action, "reason": reason}
