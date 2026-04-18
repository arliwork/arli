"""Activity Log — audit trail for all company events"""
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from dependencies import get_async_db
from auth import get_current_active_user
from models import ActivityLog, User
from schemas import ActivityLogCreate, ActivityLogOut, ActivityLogListResponse

router = APIRouter(prefix="/activity", tags=["activity"])

def generate_activity_id():
    return f"act_{uuid.uuid4().hex[:8]}"

async def log_event(
    db: AsyncSession,
    actor_type: str,
    actor_id: str,
    actor_name: str,
    event_type: str,
    event_description: str,
    company_id: Optional[str] = None,
    metadata: dict = None,
):
    """Helper to log an activity event"""
    log = ActivityLog(
        company_id=company_id,
        actor_type=actor_type,
        actor_id=actor_id,
        actor_name=actor_name,
        event_type=event_type,
        event_description=event_description,
        metadata=metadata or {},
    )
    db.add(log)
    await db.commit()
    return log

@router.get("", response_model=ActivityLogListResponse)
async def list_activity(
    company_id: Optional[str] = None,
    event_type: Optional[str] = None,
    actor_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    stmt = select(ActivityLog)
    if company_id:
        stmt = stmt.where(ActivityLog.company_id == company_id)
    if event_type:
        stmt = stmt.where(ActivityLog.event_type == event_type)
    if actor_type:
        stmt = stmt.where(ActivityLog.actor_type == actor_type)

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar()

    result = await db.execute(stmt.order_by(ActivityLog.created_at.desc()).offset(offset).limit(limit))
    items = result.scalars().all()
    return ActivityLogListResponse(items=[ActivityLogOut.model_validate(a) for a in items], total=total)

@router.get("/stats")
async def activity_stats(
    company_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get activity breakdown by event type"""
    stmt = select(ActivityLog.event_type, func.count(ActivityLog.id))
    if company_id:
        stmt = stmt.where(ActivityLog.company_id == company_id)
    stmt = stmt.group_by(ActivityLog.event_type)

    result = await db.execute(stmt)
    breakdown = {row[0]: row[1] for row in result.all()}

    # Recent activity count
    recent_stmt = select(func.count(ActivityLog.id))
    if company_id:
        recent_stmt = recent_stmt.where(ActivityLog.company_id == company_id)
    recent_result = await db.execute(recent_stmt)
    total = recent_result.scalar()

    return {"total": total, "breakdown": breakdown}
