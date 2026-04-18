"""CEO Strategy — generates company strategy and decomposes into tasks"""
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Agent, Company, Approval, Task
from services.llm_client import get_llm_client
from routers.activity import log_event


class CEOStrategyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = get_llm_client()

    async def generate_strategy(self, company_id: str, ceo_agent_id: str) -> dict:
        """CEO generates a strategic plan for the company."""
        company_result = await self.db.execute(select(Company).where(Company.company_id == company_id))
        company = company_result.scalar_one_or_none()
        if not company:
            return {"error": "Company not found"}

        ceo_result = await self.db.execute(select(Agent).where(Agent.agent_id == ceo_agent_id))
        ceo = ceo_result.scalar_one_or_none()
        if not ceo:
            return {"error": "CEO agent not found"}

        prompt = f"""You are {ceo.name}, CEO of {company.name}.

Company Goal: {company.goal or "Grow the company and generate revenue."}
Company Budget: ${company.monthly_budget} per month

Your task: Create a strategic plan. Respond with JSON:
{{
  "strategy_summary": "One-paragraph strategy overview",
  "key_objectives": ["objective 1", "objective 2", "objective 3"],
  "recommended_team": [
    {{"role": "developer", "reason": "why needed", "budget": 100}},
    {{"role": "analyst", "reason": "why needed", "budget": 80}}
  ],
  "phases": [
    {{
      "phase_name": "Phase 1: Setup",
      "duration_days": 7,
      "tasks": ["task description 1", "task description 2"]
    }}
  ],
  "success_metrics": ["metric 1", "metric 2"]
}}
"""

        response = await self.llm.generate(
            messages=[
                {"role": "system", "content": "You are a strategic CEO. Think step by step."},
                {"role": "user", "content": prompt},
            ],
            task_type="reasoning",
            max_tokens=4000,
            agent_id=ceo_agent_id,
            db=self.db,
        )

        # Parse strategy
        text = response.content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        try:
            strategy = json.loads(text)
        except Exception:
            strategy = {
                "strategy_summary": text[:500],
                "key_objectives": [],
                "recommended_team": [],
                "phases": [],
                "success_metrics": [],
                "raw": text,
            }

        # Create approval request for the strategy
        approval = Approval(
            approval_id=f"aprv_{uuid.uuid4().hex[:8]}",
            company_id=company_id,
            approval_type="ceo_strategy",
            title=f"CEO Strategy: {company.name}",
            description=strategy.get("strategy_summary", "Strategy proposal")[:500],
            requested_by_agent_id=ceo.id,
            payload={"strategy": strategy, "company_id": company_id},
        )
        self.db.add(approval)
        await self.db.commit()

        # Log
        await log_event(
            self.db,
            actor_type="agent",
            actor_id=ceo.agent_id,
            actor_name=ceo.name,
            event_type="ceo_strategy_created",
            event_description=f"{ceo.name} created a strategy for {company.name}",
            company_id=company_id,
            metadata={"approval_id": approval.approval_id},
        )

        return {
            "success": True,
            "approval_id": approval.approval_id,
            "strategy": strategy,
            "status": "pending_approval",
        }

    async def execute_approved_strategy(self, approval_id: str) -> dict:
        """After strategy is approved, decompose into tasks and assign."""
        approval_result = await self.db.execute(select(Approval).where(Approval.approval_id == approval_id))
        approval = approval_result.scalar_one_or_none()
        if not approval or approval.status != "approved":
            return {"error": "Strategy not approved yet"}

        strategy = approval.payload.get("strategy", {})
        company_id = approval.company_id
        ceo_id = approval.requested_by_agent_id

        # Find CEO agent
        ceo_result = await self.db.execute(select(Agent).where(Agent.id == ceo_id))
        ceo = ceo_result.scalar_one_or_none()
        if not ceo:
            return {"error": "CEO not found"}

        created_tasks = []

        # Create tasks from phases
        for phase in strategy.get("phases", []):
            for task_desc in phase.get("tasks", []):
                task = Task(
                    task_id=f"task_{uuid.uuid4().hex[:8]}",
                    description=task_desc,
                    assigned_role=ceo.role,
                    agent_id=ceo.id,
                    status="pending",
                )
                self.db.add(task)
                created_tasks.append(task_desc)

        await self.db.commit()

        # Log
        await log_event(
            self.db,
            actor_type="system",
            actor_id="system",
            actor_name="System",
            event_type="strategy_executed",
            event_description=f"Strategy {approval_id} approved and decomposed into {len(created_tasks)} tasks",
            company_id=company_id,
            metadata={"task_count": len(created_tasks)},
        )

        return {
            "success": True,
            "tasks_created": len(created_tasks),
            "task_descriptions": created_tasks,
        }
