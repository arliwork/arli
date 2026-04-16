"""Scheduled workflow routes for cron automation"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone
import uuid

from dependencies import get_async_db
from auth import get_current_active_user
from models import ScheduledWorkflow, User

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.post("/schedules")
async def create_schedule(
    data: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a scheduled workflow"""
    schedule = ScheduledWorkflow(
        schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
        name=data.get("name", "Scheduled Workflow"),
        description=data.get("description"),
        schedule=data.get("schedule", "daily"),
        pipeline_type=data.get("pipeline_type", "plan-feature"),
        context=data.get("context", {}),
        owner_id=current_user.id,
        is_active=data.get("is_active", True),
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return {
        "success": True,
        "schedule_id": schedule.schedule_id,
        "name": schedule.name,
        "schedule": schedule.schedule,
        "pipeline_type": schedule.pipeline_type,
        "is_active": schedule.is_active,
    }


@router.get("/schedules")
async def list_schedules(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """List user's scheduled workflows"""
    result = await db.execute(
        select(ScheduledWorkflow)
        .where(ScheduledWorkflow.owner_id == current_user.id)
        .order_by(ScheduledWorkflow.created_at.desc())
    )
    items = result.scalars().all()
    return {
        "schedules": [
            {
                "schedule_id": s.schedule_id,
                "name": s.name,
                "schedule": s.schedule,
                "pipeline_type": s.pipeline_type,
                "is_active": s.is_active,
                "last_run_at": s.last_run_at.isoformat() if s.last_run_at else None,
                "next_run_at": s.next_run_at.isoformat() if s.next_run_at else None,
                "run_count": s.run_count,
            }
            for s in items
        ]
    }


@router.patch("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: str,
    data: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a scheduled workflow"""
    result = await db.execute(
        select(ScheduledWorkflow)
        .where(ScheduledWorkflow.schedule_id == schedule_id, ScheduledWorkflow.owner_id == current_user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if "name" in data:
        schedule.name = data["name"]
    if "schedule" in data:
        schedule.schedule = data["schedule"]
    if "is_active" in data:
        schedule.is_active = data["is_active"]
    if "context" in data:
        schedule.context = data["context"]

    await db.commit()
    return {"success": True, "schedule_id": schedule.schedule_id}


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a scheduled workflow"""
    result = await db.execute(
        select(ScheduledWorkflow)
        .where(ScheduledWorkflow.schedule_id == schedule_id, ScheduledWorkflow.owner_id == current_user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await db.delete(schedule)
    await db.commit()
    return {"success": True}
