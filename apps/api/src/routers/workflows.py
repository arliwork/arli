"""Workflow orchestration routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone

from dependencies import get_async_db
from auth import get_current_active_user
from models import Workflow, Task, User
from schemas import WorkflowCreate, WorkflowUpdate, WorkflowOut

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("", response_model=WorkflowOut)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    wf = Workflow(
        workflow_id=data.workflow_id,
        name=data.name,
        description=data.description,
        total_steps=data.total_steps,
        context=data.context or {},
    )
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return WorkflowOut.model_validate(wf)

@router.get("", response_model=List[WorkflowOut])
async def list_workflows(
    status: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(Workflow)
    if status:
        stmt = stmt.where(Workflow.status == status)
    result = await db.execute(stmt.order_by(Workflow.created_at.desc()).limit(limit))
    items = result.scalars().all()
    return [WorkflowOut.model_validate(w) for w in items]

@router.get("/{workflow_id}", response_model=WorkflowOut)
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return WorkflowOut.model_validate(wf)

@router.patch("/{workflow_id}", response_model=WorkflowOut)
async def update_workflow(
    workflow_id: str,
    data: WorkflowUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(wf, key, value)
    
    if data.status == "running" and not wf.started_at:
        wf.started_at = datetime.now(timezone.utc)
    if data.status in ("completed", "failed") and not wf.completed_at:
        wf.completed_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(wf)
    return WorkflowOut.model_validate(wf)

@router.post("/{workflow_id}/execute", response_model=WorkflowOut)
async def execute_workflow_step(
    workflow_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    
    # Advance workflow step
    if wf.current_step < wf.total_steps:
        wf.current_step += 1
        if wf.current_step == wf.total_steps:
            wf.status = "completed"
            wf.completed_at = datetime.now(timezone.utc)
        elif wf.status == "pending":
            wf.status = "running"
            wf.started_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(wf)
    return WorkflowOut.model_validate(wf)
