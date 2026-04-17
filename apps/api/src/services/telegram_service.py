"""Telegram integration for ARLI agents"""
import os
import json
from typing import Optional, Dict, Any
import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Agent, Task, User
from services.credit_service import CreditService

TELEGRAM_API = "https://api.telegram.org/bot"


class TelegramService:
    """Bridge between Telegram and ARLI agents"""

    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.client = httpx.AsyncClient(timeout=30)

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """Send a message to a Telegram chat"""
        if not self.bot_token:
            return {"success": False, "error": "TELEGRAM_BOT_TOKEN not configured"}

        url = f"{TELEGRAM_API}{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        try:
            response = await self.client.post(url, json=payload)
            data = response.json()
            if data.get("ok"):
                return {"success": True, "message_id": data["result"]["message_id"]}
            return {"success": False, "error": data.get("description", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_update(self, db: AsyncSession, update: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Telegram update"""
        message = update.get("message") or update.get("edited_message")
        if not message:
            return {"success": False, "error": "No message in update"}

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "").strip()
        from_user = message.get("from", {})
        username = from_user.get("username", f"user_{from_user.get('id', 'unknown')}")

        if not text:
            return {"success": False, "error": "Empty message"}

        # Handle /start
        if text == "/start":
            welcome = (
                "*Welcome to ARLI* 🤖\n\n"
                "I'm your autonomous AI agent bridge.\n\n"
                "*Commands:*\n"
                "- Send any message \u2192 I'll create a task for my AI team\n"
                "- `/agents` \u2192 List your active agents\n"
                "- `/status` \u2192 Check platform status\n"
                "- `/balance` \u2192 Check your credit balance"
            )
            await self.send_message(chat_id, welcome)
            return {"success": True, "handled": "welcome"}

        # Handle /agents
        if text == "/agents":
            result = await db.execute(select(Agent).limit(10))
            agents = result.scalars().all()
            if not agents:
                await self.send_message(chat_id, "No agents found. Create one at https://arli.ai/templates")
                return {"success": True, "handled": "agents"}
            msg = "*Your Agents:*\n\n" + "\n".join([
                f"• *{a.name}* ({a.role}) \u2014 Lv.{a.level}"
                for a in agents
            ])
            await self.send_message(chat_id, msg)
            return {"success": True, "handled": "agents"}

        # Handle /status
        if text == "/status":
            from services.orchestration_service import get_orchestrator
            orchestrator = get_orchestrator()
            status = orchestrator.get_status()
            msg = (
                f"*ARLI Status* 📊\n\n"
                f"Agents: {status['agents_total']}\n"
                f"Active: {status['agents_active']}\n"
                f"Pending tasks: {status['tasks_pending']}\n"
                f"In progress: {status['tasks_in_progress']}\n"
                f"Completed: {status['tasks_completed']}"
            )
            await self.send_message(chat_id, msg)
            return {"success": True, "handled": "status"}

        # Handle /balance
        if text == "/balance":
            # Try to find user by telegram username mapping (simplified)
            msg = "Use /dashboard at https://arli.ai/billing to view your full credit balance."
            await self.send_message(chat_id, msg)
            return {"success": True, "handled": "balance"}

        # Default: create a task from the message
        task_id = f"tg_{chat_id}_{message.get('message_id', '0')}"
        task = Task(
            task_id=task_id,
            description=text,
            category="general",
            status="pending",
            source="telegram",
            source_metadata={"chat_id": chat_id, "username": username, "update": update},
        )
        db.add(task)
        await db.commit()

        # Queue the task for execution
        from worker import celery_app
        celery_app.send_task("worker.process_task", args=[task_id])

        confirm_msg = (
            f"📋 *Task Created*\n\n"
            f"_{text[:200]}_\n\n"
            f"Task ID: `{task_id}`\n"
            f"Status: queued for execution\n\n"
            f"I'll notify you when it's done!"
        )
        await self.send_message(chat_id, confirm_msg)

        return {
            "success": True,
            "task_id": task_id,
            "chat_id": chat_id,
        }

    async def notify_task_complete(self, chat_id: int, task: Task) -> Dict[str, Any]:
        """Notify user in Telegram that a task is complete"""
        result_data = task.result_data or {}
        output = result_data.get("output", "Task completed.")
        credits_used = result_data.get("credits_used", 0)

        msg = (
            f"✅ *Task Complete*\n\n"
            f"*Task:* {task.description[:150]}\n\n"
            f"*Result:*\n_{output[:800]}_\n\n"
        )
        if credits_used:
            msg += f"_Credits used: {credits_used:.2f}_"

        return await self.send_message(chat_id, msg)
