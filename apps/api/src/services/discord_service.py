"""Discord integration for ARLI agents"""
import os
from typing import Optional, Dict, Any
import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Agent, Task

DISCORD_API = "https://discord.com/api/v10"


class DiscordService:
    """Bridge between Discord and ARLI agents"""

    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("DISCORD_BOT_TOKEN", "")
        self.client = httpx.AsyncClient(timeout=30)

    async def send_message(self, channel_id: str, content: str) -> Dict[str, Any]:
        """Send a message to a Discord channel"""
        if not self.bot_token:
            return {"success": False, "error": "DISCORD_BOT_TOKEN not configured"}

        url = f"{DISCORD_API}/channels/{channel_id}/messages"
        try:
            response = await self.client.post(
                url,
                json={"content": content},
                headers={"Authorization": f"Bot {self.bot_token}"},
            )
            if response.status_code == 200:
                return {"success": True, "message_id": response.json().get("id")}
            return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_interaction(self, db: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Discord interaction or message"""
        # Handle slash commands / interactions
        if payload.get("type") in (2, 3):  # 2 = slash command, 3 = component interaction
            return await self._handle_interaction(db, payload)

        # Handle regular messages (requires Message Content intent)
        if "content" in payload:
            return await self._handle_message(db, payload)

        return {"success": False, "error": "Unknown payload type"}

    async def _handle_interaction(self, db: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload.get("data", {})
        command_name = data.get("name", "")
        channel_id = payload.get("channel", {}).get("id") if "channel" in payload else payload.get("channel_id")

        if command_name == "agents":
            result = await db.execute(select(Agent).limit(10))
            agents = result.scalars().all()
            if not agents:
                content = "No agents found. Create one at https://arli.ai/templates"
            else:
                content = "**Your Agents:**\n" + "\n".join([
                    f"• **{a.name}** ({a.role}) \u2014 Lv.{a.level}"
                    for a in agents
                ])
            await self.send_message(channel_id, content)
            return {"success": True, "handled": "agents"}

        if command_name == "status":
            from services.orchestration_service import get_orchestrator
            status = get_orchestrator().get_status()
            content = (
                f"**ARLI Status** 📊\n"
                f"Agents: {status['agents_total']} | Active: {status['agents_active']}\n"
                f"Tasks: {status['tasks_pending']} pending, {status['tasks_in_progress']} running, {status['tasks_completed']} done"
            )
            await self.send_message(channel_id, content)
            return {"success": True, "handled": "status"}

        if command_name == "task":
            options = {opt["name"]: opt["value"] for opt in data.get("options", [])}
            description = options.get("description", "")
            if not description:
                await self.send_message(channel_id, "Please provide a task description.")
                return {"success": True, "handled": "task"}

            task_id = f"discord_{channel_id}_{payload.get('id', '0')}"
            task = Task(
                task_id=task_id,
                description=description,
                category="general",
                status="pending",
                source="discord",
                source_metadata={"channel_id": channel_id, "interaction_id": payload.get("id")},
            )
            db.add(task)
            await db.commit()

            from worker import celery_app
            celery_app.send_task("worker.process_task", args=[task_id])

            await self.send_message(
                channel_id,
                f"📋 **Task Created**\n_{description[:200]}_\nTask ID: `{task_id}`"
            )
            return {"success": True, "task_id": task_id}

        return {"success": False, "error": f"Unknown command: {command_name}"}

    async def _handle_message(self, db: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
        content = payload.get("content", "").strip()
        channel_id = payload.get("channel_id")
        author = payload.get("author", {})

        # Ignore bot messages
        if author.get("bot"):
            return {"success": False, "error": "Bot message ignored"}

        # Simple prefix commands
        if content.startswith("!arli "):
            description = content[len("!arli "):].strip()
            task_id = f"discord_{channel_id}_{payload.get('id', '0')}"
            task = Task(
                task_id=task_id,
                description=description,
                category="general",
                status="pending",
                source="discord",
                source_metadata={"channel_id": channel_id, "author": author},
            )
            db.add(task)
            await db.commit()

            from worker import celery_app
            celery_app.send_task("worker.process_task", args=[task_id])

            await self.send_message(channel_id, f"📋 Task queued: `{task_id}`")
            return {"success": True, "task_id": task_id}

        return {"success": False, "error": "Message not handled"}
