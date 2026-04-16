"""Task management routes"""
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone

from dependencies import get_async_db
from auth import get_current_active_user
from models import Task, Agent, User
from schemas import TaskCreate, TaskUpdate, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=TaskOut)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    task = Task(
        task_id=data.task_id or f"task_{uuid.uuid4().hex[:8]}",
        category=data.category,
        description=data.description,
        assigned_role=data.assigned_role,
        workflow_id=data.workflow_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskOut.model_validate(task)

@router.get("", response_model=List[TaskOut])
async def list_tasks(
    status: Optional[str] = None,
    category: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(Task)
    if status:
        stmt = stmt.where(Task.status == status)
    if category:
        stmt = stmt.where(Task.category == category)
    if agent_id:
        stmt = stmt.where(Task.agent_id == agent_id)
    
    result = await db.execute(stmt.order_by(Task.created_at.desc()).offset(offset).limit(limit))
    items = result.scalars().all()
    return [TaskOut.model_validate(t) for t in items]

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Task).where(Task.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskOut.model_validate(task)

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Task).where(Task.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(task, key, value)
    
    if data.status == "running" and not task.started_at:
        task.started_at = datetime.now(timezone.utc)
    if data.status in ("completed", "failed") and not task.completed_at:
        task.completed_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(task)
    return TaskOut.model_validate(task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Task).where(Task.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await db.delete(task)
    await db.commit()
    return None
