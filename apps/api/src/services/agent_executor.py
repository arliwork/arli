"""Agent Executor — the brain that makes agents actually work"""
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Agent, Task, TaskComment, Approval, ActivityLog, AgentSecret
from services.llm_client import get_llm_client
from routers.activity import log_event


class AgentExecutor:
    """Executes a single agent heartbeat: check context, decide, act."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = get_llm_client()

    async def heartbeat(self, agent_id: str) -> dict:
        """Run one heartbeat cycle for an agent."""
        result = await self.db.execute(select(Agent).where(Agent.agent_id == agent_id))
        agent = result.scalar_one_or_none()
        if not agent:
            return {"error": "Agent not found"}

        # Skip if paused or terminated
        if agent.status in ("paused", "terminated"):
            return {"status": "skipped", "reason": f"Agent is {agent.status}"}

        # Check budget
        if agent.monthly_budget > 0 and agent.budget_spent >= agent.monthly_budget:
            agent.status = "paused"
            await self.db.commit()
            return {"status": "paused", "reason": "Budget exceeded"}

        # Gather context
        context = await self._build_context(agent)

        # Make decision via LLM
        decision = await self._decide(agent, context)

        # Execute decision
        outcome = await self._execute_decision(agent, decision)

        # Log activity
        await log_event(
            self.db,
            actor_type="agent",
            actor_id=agent.agent_id,
            actor_name=agent.name,
            event_type="agent_heartbeat",
            event_description=f"{agent.name} executed: {decision.get('action', 'idle')}",
            company_id=agent.company_id,
            metadata={"decision": decision, "outcome": outcome},
        )

        return {"status": "ok", "decision": decision, "outcome": outcome}

    async def _build_context(self, agent: Agent) -> dict:
        """Build the agent's situational awareness."""
        # Pending tasks assigned to this agent
        task_result = await self.db.execute(
            select(Task)
            .where(Task.agent_id == agent.id, Task.status.in_(["pending", "in_progress"]))
            .order_by(Task.created_at.desc())
            .limit(10)
        )
        pending_tasks = task_result.scalars().all()

        # Recent comments on agent's tasks
        comments_result = await self.db.execute(
            select(TaskComment)
            .where(TaskComment.author_id != agent.agent_id)
            .order_by(TaskComment.created_at.desc())
            .limit(10)
        )
        recent_messages = comments_result.scalars().all()

        # Subordinates (if manager)
        subordinates = agent.subordinates or []

        return {
            "agent_name": agent.name,
            "role": agent.role,
            "level": agent.level,
            "tier": agent.tier,
            "status": agent.status,
            "budget_remaining": float(agent.monthly_budget or 0) - float(agent.budget_spent or 0),
            "pending_tasks": [
                {"task_id": t.task_id, "description": t.description, "status": t.status}
                for t in pending_tasks
            ],
            "recent_messages": [
                {"from": c.author_name, "content": c.content}
                for c in recent_messages
            ],
            "subordinate_count": len(subordinates),
            "total_xp": agent.total_xp,
        }

    async def _decide(self, agent: Agent, context: dict) -> dict:
        """Ask the LLM what the agent should do next."""
        role_prompts = {
            "ceo": "You are the CEO of an AI company. Your job is to set strategy, delegate work, and ensure goals are met.",
            "cto": "You are the CTO. Your job is to oversee technical architecture, code quality, and engineering tasks.",
            "developer": "You are a software developer. Your job is to write code, debug, and build features.",
            "analyst": "You are a research analyst. Your job is to gather information, analyze data, and produce insights.",
            "trader": "You are a trading analyst. Your job is to analyze markets and generate trading signals.",
        }
        system_msg = role_prompts.get(agent.role.lower(), "You are an AI worker agent.")

        prompt = f"""{system_msg}

Your current context:
{json.dumps(context, indent=2)}

Based on your context, decide your next action. Respond with a JSON object:
{{
  "action": "pick_task" | "delegate" | "request_approval" | "send_message" | "idle",
  "reasoning": "why you chose this",
  "target_task_id": "if picking a task",
  "message_to": "agent_id if sending message",
  "message_content": "content if sending message",
  "approval_type": "hire_agent | ceo_strategy | budget_override",
  "approval_title": "title if requesting approval",
  "approval_description": "description if requesting approval"
}}
"""

        try:
            response = await self.llm.generate(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                task_type="reasoning",
                max_tokens=2000,
                agent_id=agent.agent_id,
                db=self.db,
            )
            # Try to parse JSON from response
            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            return {"action": "idle", "reasoning": f"Decision error: {e}"}

    async def _execute_decision(self, agent: Agent, decision: dict) -> dict:
        action = decision.get("action", "idle")

        if action == "pick_task":
            return await self._execute_task(agent, decision.get("target_task_id"))

        elif action == "delegate" and agent.subordinates:
            return await self._delegate_task(agent, decision)

        elif action == "request_approval":
            return await self._request_approval(agent, decision)

        elif action == "send_message":
            return await self._send_message(agent, decision)

        return {"action": "idle", "result": "No action taken"}

    async def _execute_task(self, agent: Agent, task_id: Optional[str]) -> dict:
        """Execute a task via LLM based on its description."""
        if not task_id:
            return {"error": "No task_id provided"}

        result = await self.db.execute(select(Task).where(Task.task_id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return {"error": "Task not found"}

        task.status = "in_progress"
        task.started_at = datetime.now(timezone.utc)
        await self.db.commit()

        # Execute based on task type
        category = (task.assigned_role or "generic").lower()
        prompt = task.description or "Complete your assigned work."

        try:
            response = await self.llm.generate(
                messages=[
                    {"role": "system", "content": f"You are {agent.name}, a {agent.role}. Complete the task professionally."},
                    {"role": "user", "content": prompt},
                ],
                task_type="default",
                max_tokens=2000,
                agent_id=agent.agent_id,
                db=self.db,
            )

            task.status = "completed"
            task.completed_at = datetime.now(timezone.utc)
            task.result_data = {"output": response.content, "credits_used": response.credits_used}
            task.success = True
            await self.db.commit()

            # Add comment with result
            comment = TaskComment(
                task_id=task_id,
                author_type="agent",
                author_id=agent.agent_id,
                author_name=agent.name,
                content=f"Task completed. Result:\n\n{response.content[:2000]}",
            )
            self.db.add(comment)
            await self.db.commit()

            return {"task_id": task_id, "status": "completed", "output_preview": response.content[:200]}

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            await self.db.commit()
            return {"task_id": task_id, "status": "failed", "error": str(e)}

    async def _delegate_task(self, agent: Agent, decision: dict) -> dict:
        """Assign a task to a subordinate."""
        if not agent.subordinates:
            return {"error": "No subordinates"}

        subordinate = agent.subordinates[0]
        # Create a new task for subordinate
        new_task = Task(
            task_id=f"task_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{subordinate.agent_id}",
            description=decision.get("approval_description", "Delegated work from manager"),
            assigned_role=subordinate.role,
            agent_id=subordinate.id,
            status="pending",
        )
        self.db.add(new_task)
        await self.db.commit()

        return {"delegated_to": subordinate.agent_id, "task_id": new_task.task_id}

    async def _request_approval(self, agent: Agent, decision: dict) -> dict:
        """Create an approval request."""
        approval = Approval(
            approval_id=f"aprv_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            company_id=agent.company_id,
            approval_type=decision.get("approval_type", "hire_agent"),
            title=decision.get("approval_title", "Approval Request"),
            description=decision.get("approval_description", ""),
            requested_by_agent_id=agent.id,
            payload=decision,
        )
        self.db.add(approval)
        await self.db.commit()

        return {"approval_id": approval.approval_id, "status": "pending"}

    async def _send_message(self, agent: Agent, decision: dict) -> dict:
        """Send a message to another agent via task comments on their active tasks."""
        target_id = decision.get("message_to")
        content = decision.get("message_content", "")
        if not target_id or not content:
            return {"error": "Missing message target or content"}

        # Find a recent task of the target agent and comment on it
        result = await self.db.execute(
            select(Task).where(Task.agent_id == target_id).order_by(Task.created_at.desc()).limit(1)
        )
        target_task = result.scalar_one_or_none()

        if target_task:
            comment = TaskComment(
                task_id=target_task.task_id,
                author_type="agent",
                author_id=agent.agent_id,
                author_name=agent.name,
                content=f"[Message from {agent.name}]: {content}",
            )
            self.db.add(comment)
            await self.db.commit()
            return {"sent_to": target_id, "via_task": target_task.task_id}

        return {"error": "No active task found for target agent"}
