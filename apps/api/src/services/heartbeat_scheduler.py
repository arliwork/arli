"""Heartbeat Scheduler — runs all active agents on a schedule"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from models import Agent
from services.agent_executor import AgentExecutor


async def run_all_heartbeats():
    """Run one heartbeat cycle for all active agents."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Agent)
            .where(Agent.status.in_(["idle", "active"]))
            .where(Agent.role != "system")
        )
        agents = result.scalars().all()

        executor = AgentExecutor(db)
        results = []

        for agent in agents:
            try:
                outcome = await executor.heartbeat(agent.agent_id)
                results.append({"agent_id": agent.agent_id, "name": agent.name, "outcome": outcome})
            except Exception as e:
                results.append({"agent_id": agent.agent_id, "name": agent.name, "error": str(e)})

        return {"run_at": datetime.now(timezone.utc).isoformat(), "agents_processed": len(agents), "results": results}


async def heartbeat_loop(interval_seconds: int = 300):
    """Background loop that runs heartbeats continuously."""
    while True:
        try:
            result = await run_all_heartbeats()
            print(f"[Heartbeat] Processed {result['agents_processed']} agents at {result['run_at']}")
        except Exception as e:
            print(f"[Heartbeat] Error: {e}")
        await asyncio.sleep(interval_seconds)
