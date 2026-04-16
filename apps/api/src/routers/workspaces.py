"""Agent workspace routes for visual collaboration"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any

from dependencies import get_async_db
from auth import get_current_active_user
from models import Agent, Task, User
from services.browser_service import BrowserService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("/agents/{agent_id}")
async def get_agent_workspace(
    agent_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get workspace state for an agent"""
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get recent tasks
    tasks_result = await db.execute(
        select(Task)
        .where(Task.agent_id == agent.id)
        .order_by(Task.created_at.desc())
        .limit(20)
    )
    tasks = tasks_result.scalars().all()

    return {
        "agent": {
            "id": agent.id,
            "agent_id": agent.agent_id,
            "name": agent.name,
            "role": agent.role,
            "status": agent.status,
            "level": agent.level,
        },
        "tasks": [
            {
                "id": t.task_id,
                "description": t.description,
                "status": t.status,
                "success": t.success,
                "result_data": t.result_data,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tasks
        ],
    }


@router.post("/agents/{agent_id}/browser/navigate")
async def browser_navigate_action(
    agent_id: str,
    url: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent or agent.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    browser = BrowserService()
    action_result = await browser.navigate(url)
    return {
        "success": action_result.success,
        "url": action_result.url,
        "error": action_result.error,
    }


@router.post("/agents/{agent_id}/browser/snapshot")
async def browser_snapshot_action(
    agent_id: str,
    full: bool = False,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent or agent.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    browser = BrowserService()
    action_result = await browser.get_page_content(full=full)
    return {
        "success": action_result.success,
        "url": action_result.url,
        "content": action_result.content,
        "error": action_result.error,
    }


@router.post("/agents/{agent_id}/terminal")
async def agent_terminal(
    agent_id: str,
    command: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Execute a terminal command on behalf of an agent"""
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent or agent.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Import runtime and execute safely
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "agents"))
    from runtime import AgentRuntime

    runtime = AgentRuntime(agent_id=agent.agent_id, workspace=".")
    output = runtime.execute_shell(command)
    return {
        "success": output.get("success", False),
        "stdout": output.get("stdout", "")[:5000],
        "stderr": output.get("stderr", "")[:5000],
        "returncode": output.get("returncode", -1),
    }


@router.post("/agents/{agent_id}/files/read")
async def read_agent_file(
    agent_id: str,
    path: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent or agent.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "agents"))
    from runtime import AgentRuntime

    runtime = AgentRuntime(agent_id=agent.agent_id, workspace=".")
    output = runtime.read_file(path)
    return output


@router.post("/agents/{agent_id}/files/write")
async def write_agent_file(
    agent_id: str,
    path: str,
    content: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent or agent.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "agents"))
    from runtime import AgentRuntime

    runtime = AgentRuntime(agent_id=agent.agent_id, workspace=".")
    output = runtime.write_file(path, content)
    return output
