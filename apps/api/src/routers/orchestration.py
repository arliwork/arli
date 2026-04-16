import uuid
"""Autonomous company orchestration routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from dependencies import get_async_db
from auth import get_current_active_user
from models import Workflow, User
from schemas import WorkflowCreate, WorkflowOut, WorkflowUpdate
from services.orchestration_service import get_orchestrator, OrchestrationService, WORKFLOW_PIPELINES

router = APIRouter(prefix="/orchestration", tags=["orchestration"])

@router.post("/workflows", response_model=WorkflowOut)
async def create_workflow(
    data: WorkflowCreate,
    pipeline_type: str = "plan-feature",
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if pipeline_type not in WORKFLOW_PIPELINES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown pipeline type. Available: {list(WORKFLOW_PIPELINES.keys())}"
        )
    
    orchestrator = get_orchestrator()
    workflow = await orchestrator.create_workflow(
        db=db,
        name=data.name,
        description=data.description or f"Autonomous workflow: {data.name}",
        pipeline_type=pipeline_type,
        context=data.context,
        workflow_id=data.workflow_id,
    )
    return WorkflowOut.model_validate(workflow)

@router.get("/workflows", response_model=list[WorkflowOut])
async def list_workflows(
    status: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    stmt = select(Workflow)
    if status:
        stmt = stmt.where(Workflow.status == status)
    result = await db.execute(stmt.order_by(Workflow.created_at.desc()))
    items = result.scalars().all()
    return [WorkflowOut.model_validate(w) for w in items]

@router.get("/workflows/{workflow_id}", response_model=WorkflowOut)
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return WorkflowOut.model_validate(workflow)

@router.post("/workflows/{workflow_id}/step")
async def execute_step(
    workflow_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    orchestrator = get_orchestrator()
    result = await orchestrator.execute_workflow_step(db, workflow_id)
    return result

@router.post("/workflows/{workflow_id}/run")
async def run_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    orchestrator = get_orchestrator()
    result = await orchestrator.run_full_workflow(db, workflow_id)
    return result

@router.get("/pipelines")
async def list_pipelines():
    return {
        "pipelines": {
            key: [{"role": role, "description": desc} for role, desc in steps]
            for key, steps in WORKFLOW_PIPELINES.items()
        }
    }
