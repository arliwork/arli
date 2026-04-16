"""Credit management routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_async_db
from auth import get_current_active_user
from models import User
from services.credit_service import CreditService

router = APIRouter(prefix="/credits", tags=["credits"])


@router.get("/balance")
async def get_balance(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current credit balance and tier info"""
    return await CreditService.get_balance(db, current_user.id)


@router.post("/deduct")
async def deduct_credits(
    amount: float,
    reason: str = "",
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Deduct credits from user balance"""
    result = await CreditService.deduct_credits(db, current_user.id, amount, reason)
    if not result["success"]:
        raise HTTPException(status_code=402, detail=result["error"])
    return result


@router.post("/add")
async def add_credits(
    amount: float,
    reason: str = "",
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add credits to user balance"""
    result = await CreditService.add_credits(db, current_user.id, amount, reason)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.patch("/tier")
async def set_tier(
    tier: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update subscription tier"""
    result = await CreditService.set_tier(db, current_user.id, tier)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
