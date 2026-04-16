"""
Bot Bridge for Telegram/Discord integration with ARLI agents
This module creates simple bot wrappers that connect messaging platforms to ARLI agents
"""
import os
import asyncio
import aiohttp
from typing import Dict, Optional, Any

API_BASE = os.getenv("APP_URL", "http://localhost:8000")


class ARLIBotBridge:
    """Bridge between messaging platforms and ARLI API"""

    def __init__(self, api_base: str = API_BASE):
        self.api_base = api_base
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def login_or_register(self, email: str, password: str) -> Optional[str]:
        """Get auth token for a platform user"""
        session = await self._get_session()
        
        # Try login first
        async with session.post(
            f"{self.api_base}/auth/login",
            json={"email": email, "password": password},
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("access_token")
        
        # Register if login fails
        async with session.post(
            f"{self.api_base}/auth/register",
            json={"email": email, "password": password, "name": email.split("@")[0]},
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("access_token")
        
        return None

    async def get_or_create_agent(self, token: str, role: str = "backend-dev") -> Optional[str]:
        """Get user's first agent or create one"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.api_base}/agents/my",
            headers={"Authorization": f"Bearer {token}"},
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                items = data.get("items", [])
                if items:
                    return items[0]["agent_id"]
        
        # Create default agent
        async with session.post(
            f"{self.api_base}/agents",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": f"{role.title()} Agent",
                "role": role,
                "capabilities": ["general", "coding"],
            },
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("agent_id")
        
        return None

    async def send_task_to_agent(self, token: str, agent_id: str, task: str) -> Dict[str, Any]:
        """Send a task to an agent via the execute-task endpoint"""
        session = await self._get_session()
        
        async with session.post(
            f"{self.api_base}/orchestration/execute-task",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "role": "backend-dev",
                "description": task,
            },
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            return {"success": False, "error": f"HTTP {resp.status}"}

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


# Telegram Bot Runner
async def run_telegram_bot():
    """Run a Telegram bot that bridges to ARLI"""
    token = os.getenv("ARLI_TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("[BotBridge] ARLI_TELEGRAM_BOT_TOKEN not set. Skipping Telegram bot.")
        return
    
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    except ImportError:
        print("[BotBridge] python-telegram-bot not installed. Run: pip install python-telegram-bot")
        return
    
    bridge = ARLIBotBridge()
    
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 Welcome to ARLI!\n\n"
            "I'm your AI company assistant. Send me any task and I'll delegate it to your team of agents.\n\n"
            "Examples:\n"
            "• 'Build a login page'\n"
            "• 'Research competitors'\n"
            "• 'Write a marketing email'"
        )
    
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat_id = update.effective_chat.id
        text = update.message.text
        
        # Derive credentials from Telegram user ID
        email = f"tg_{user.id}@arli.bot"
        password = f"tg_password_{user.id}"
        
        await update.message.chat.send_action(action="typing")
        
        auth_token = await bridge.login_or_register(email, password)
        if not auth_token:
            await update.message.reply_text("❌ Failed to authenticate. Please try again later.")
            return
        
        agent_id = await bridge.get_or_create_agent(auth_token)
        if not agent_id:
            await update.message.reply_text("❌ Failed to create agent. Please try again later.")
            return
        
        result = await bridge.send_task_to_agent(auth_token, agent_id, text)
        
        if result.get("success"):
            output = result.get("output", "Task completed.")
            model = result.get("model_used", "unknown")
            credits = result.get("credits_used", 0)
            response = f"✅ *Task completed*\n\n{output[:2000]}"
            if len(output) > 2000:
                response += "\n\n...(truncated)"
            response += f"\n\n_Model: {model} | Credits: {credits:.2f}_"
        else:
            error = result.get("error", "Unknown error")
            response = f"❌ *Task failed*\n\n{error}"
        
        await update.message.reply_text(response, parse_mode="Markdown")
    
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("[BotBridge] Starting Telegram bot...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Keep running
    while True:
        await asyncio.sleep(60)


# Discord Bot Runner
async def run_discord_bot():
    """Run a Discord bot that bridges to ARLI"""
    token = os.getenv("ARLI_DISCORD_BOT_TOKEN", "")
    if not token:
        print("[BotBridge] ARLI_DISCORD_BOT_TOKEN not set. Skipping Discord bot.")
        return
    
    try:
        import discord
        from discord.ext import commands
    except ImportError:
        print("[BotBridge] discord.py not installed. Run: pip install discord.py")
        return
    
    bridge = ARLIBotBridge()
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!arli ", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"[BotBridge] Discord bot logged in as {bot.user}")
    
    @bot.command(name="task")
    async def task_cmd(ctx: commands.Context, *, task_text: str):
        user = ctx.author
        email = f"dc_{user.id}@arli.bot"
        password = f"dc_password_{user.id}"
        
        async with ctx.typing():
            auth_token = await bridge.login_or_register(email, password)
            if not auth_token:
                await ctx.reply("❌ Failed to authenticate.")
                return
            
            agent_id = await bridge.get_or_create_agent(auth_token)
            if not agent_id:
                await ctx.reply("❌ Failed to create agent.")
                return
            
            result = await bridge.send_task_to_agent(auth_token, agent_id, task_text)
        
        if result.get("success"):
            output = result.get("output", "Task completed.")[:1900]
            model = result.get("model_used", "unknown")
            credits = result.get("credits_used", 0)
            await ctx.reply(f"✅ **Task completed**\n\n{output}\n\n*Model: {model} | Credits: {credits:.2f}*")
        else:
            error = result.get("error", "Unknown error")
            await ctx.reply(f"❌ **Task failed**\n\n{error}")
    
    @bot.command(name="agent")
    async def agent_cmd(ctx: commands.Context):
        await ctx.reply(
            "🤖 **ARLI Agent Bridge**\n\n"
            "Use `!arli task <description>` to send a task to your AI agent.\n\n"
            "Examples:\n"
            "• `!arli task Build a login API with JWT`\n"
            "• `!arli task Research top 3 competitors in fintech`\n"
            "• `!arli task Write a welcome email for new users`"
        )
    
    print("[BotBridge] Starting Discord bot...")
    await bot.start(token)


async def main():
    """Run all configured bot bridges"""
    await asyncio.gather(
        run_telegram_bot(),
        run_discord_bot(),
        return_exceptions=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
