"""Task Comments — threads for agent updates and discussions"""
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from dependencies import get_async_db
from auth import get_current_active_user
from models import TaskComment, Task, User
from schemas import TaskCommentCreate, TaskCommentOut, ActivityLogListResponse

router = APIRouter(prefix="/tasks", tags=["task-comments"])

@router.get("/{task_id}/comments", response_model=ActivityLogListResponse)
async def get_task_comments(
    task_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(TaskComment)
        .where(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at.asc())
    )
    items = result.scalars().all()
    return ActivityLogListResponse(items=[TaskCommentOut.model_validate(c) for c in items], total=len(items))

@router.post("/{task_id}/comments", response_model=TaskCommentOut)
async def add_comment(
    task_id: str,
    data: TaskCommentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    # Verify task exists
    task_result = await db.execute(select(Task).where(Task.task_id == task_id))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    comment = TaskComment(
        task_id=task_id,
        author_type=data.author_type,
        author_id=data.author_id,
        author_name=data.author_name or current_user.username,
        content=data.content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return TaskCommentOut.model_validate(comment)
