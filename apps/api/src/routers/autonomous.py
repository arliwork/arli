"""Autonomous Agent Router — heartbeat, strategy, demo scenarios"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from dependencies import get_async_db
from auth import get_current_active_user
from models import User, Agent, Company, Task
from services.agent_executor import AgentExecutor
from services.heartbeat_scheduler import run_all_heartbeats
from services.ceo_strategy import CEOStrategyService

router = APIRouter(prefix="/autonomous", tags=["autonomous"])

@router.post("/heartbeat/{agent_id}")
async def trigger_agent_heartbeat(
    agent_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Manually trigger a heartbeat for a specific agent."""
    executor = AgentExecutor(db)
    result = await executor.heartbeat(agent_id)
    return result

@router.post("/heartbeat-all")
async def trigger_all_heartbeats(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Manually trigger heartbeats for all active agents."""
    result = await run_all_heartbeats()
    return result

@router.post("/strategy/generate")
async def generate_ceo_strategy(
    company_id: str,
    ceo_agent_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """CEO generates a strategic plan for approval."""
    service = CEOStrategyService(db)
    result = await service.generate_strategy(company_id, ceo_agent_id)
    return result

@router.post("/strategy/execute")
async def execute_approved_strategy(
    approval_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Execute an approved strategy — decompose into tasks."""
    service = CEOStrategyService(db)
    result = await service.execute_approved_strategy(approval_id)
    return result

@router.post("/demo/create-company")
async def demo_create_company(
    goal: str,
    company_name: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """General Demo: Create an AI Company from any goal with dynamic team assembly."""
    import uuid
    from services.llm_client import get_llm_client

    llm = get_llm_client()

    # Use LLM to determine optimal team composition based on goal
    team_prompt = f"""Given this business goal: "{goal}"

Determine the optimal AI team composition. Respond with JSON only:
{{
  "company_name": "Creative name for the company",
  "description": "One sentence description",
  "team": [
    {{"role": "ceo", "name": "Name", "description": "What they do", "level": 5}},
    {{"role": "developer", "name": "Name", "description": "What they do", "level": 3}},
    {{"role": "analyst", "name": "Name", "description": "What they do", "level": 3}}
  ],
  "initial_task": "First task for the CEO"
}}

Pick 3-4 roles that best fit the goal. Available roles: ceo, cto, developer, analyst, trader, marketer, designer, researcher."""

    try:
        response = await llm.generate(
            messages=[
                {"role": "system", "content": "You are a startup architect."},
                {"role": "user", "content": team_prompt},
            ],
            task_type="reasoning",
            max_tokens=2000,
        )
        text = response.content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        plan = json.loads(text)
    except Exception:
        # Fallback plan
        plan = {
            "company_name": company_name or "AI Venture",
            "description": f"AI company focused on: {goal}",
            "team": [
                {"role": "ceo", "name": "Chief Executive", "description": "Strategic leader", "level": 5},
                {"role": "developer", "name": "Lead Developer", "description": "Builds the product", "level": 3},
                {"role": "analyst", "name": "Research Analyst", "description": "Gathers insights", "level": 3},
            ],
            "initial_task": f"Create a strategy to achieve: {goal}",
        }

    # 1. Create Company
    comp = Company(
        company_id=f"comp_{uuid.uuid4().hex[:6]}",
        name=plan["company_name"],
        description=plan.get("description", ""),
        goal=goal,
        owner_id=current_user.id,
        monthly_budget=500,
    )
    db.add(comp)
    await db.commit()
    await db.refresh(comp)

    created_agents = []
    ceo_agent = None

    # 2. Create agents from plan
    for member in plan.get("team", []):
        agent = Agent(
            agent_id=f"agent_{uuid.uuid4().hex[:6]}",
            name=member["name"],
            role=member["role"],
            description=member.get("description", ""),
            owner_id=current_user.id,
            creator_id=current_user.id,
            company_id=comp.id,
            manager_id=None,  # Will link after CEO created
            level=member.get("level", 3),
            tier="EXPERT" if member.get("level", 3) >= 5 else "ADVANCED",
            monthly_budget=100 if member["role"] == "ceo" else 50,
            status="idle",
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        created_agents.append(agent)
        if member["role"] == "ceo":
            ceo_agent = agent

    # 3. Link subordinates to CEO
    if ceo_agent:
        for agent in created_agents:
            if agent.id != ceo_agent.id:
                agent.manager_id = ceo_agent.id
        await db.commit()

    # 4. Initial task for CEO
    if ceo_agent:
        task = Task(
            task_id=f"task_{uuid.uuid4().hex[:6]}",
            description=plan.get("initial_task", f"Create a strategy to achieve: {goal}"),
            category="strategy",
            assigned_role="ceo",
            agent_id=ceo_agent.id,
            status="pending",
        )
        db.add(task)
        await db.commit()

    return {
        "success": True,
        "company_id": comp.company_id,
        "company_name": comp.name,
        "goal": goal,
        "ceo_id": ceo_agent.agent_id if ceo_agent else None,
        "team": [{"agent_id": a.agent_id, "name": a.name, "role": a.role} for a in created_agents],
        "message": f"{comp.name} is ready! The CEO will analyze the goal and propose a strategy. Check /approvals to review and approve.",
    }

@router.post("/demo/run-cycle")
async def demo_run_cycle(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Run one full heartbeat cycle for the demo."""
    result = await run_all_heartbeats()
    return result
