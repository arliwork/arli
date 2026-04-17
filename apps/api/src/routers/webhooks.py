"""Webhook routes for external integrations"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_async_db
from services.telegram_service import TelegramService

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
