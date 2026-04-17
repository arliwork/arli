"""Webhook routes for external integrations"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_async_db
from services.telegram_service import TelegramService
from services.discord_service import DiscordService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    """Receive updates from Telegram Bot"""
    update = await request.json()
    service = TelegramService()
    result = await service.process_update(db, update)
    return result


@router.post("/discord")
async def discord_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    """Receive interactions and messages from Discord"""
    payload = await request.json()
    service = DiscordService()
    result = await service.process_interaction(db, payload)
    return result
