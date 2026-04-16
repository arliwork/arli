"""Credit management service for ARLI"""
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import User


class CreditService:
    """Manages user credits for LLM and compute usage"""

    TIER_LIMITS = {
        "free": Decimal("500"),
        "plus": Decimal("4000"),
        "pro": Decimal("20000"),
        "enterprise": Decimal("999999999"),
    }

    @staticmethod
    async def deduct_credits(db: AsyncSession, user_id: str, amount: float, reason: str = "") -> Dict[str, Any]:
        """Deduct credits from user balance"""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"success": False, "error": "User not found"}

        amount_dec = Decimal(str(amount))
        if user.credits_balance < amount_dec:
            return {
                "success": False,
                "error": "Insufficient credits",
                "balance": float(user.credits_balance),
                "required": float(amount_dec),
            }

        user.credits_balance -= amount_dec
        user.credits_spent += amount_dec
        await db.commit()

        return {
            "success": True,
            "deducted": float(amount_dec),
            "balance": float(user.credits_balance),
            "reason": reason,
        }

    @staticmethod
    async def add_credits(db: AsyncSession, user_id: str, amount: float, reason: str = "") -> Dict[str, Any]:
        """Add credits to user balance"""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"success": False, "error": "User not found"}

        amount_dec = Decimal(str(amount))
        user.credits_balance += amount_dec
        await db.commit()

        return {
            "success": True,
            "added": float(amount_dec),
            "balance": float(user.credits_balance),
            "reason": reason,
        }

    @staticmethod
    async def get_balance(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Get user credit balance and tier info"""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"success": False, "error": "User not found"}

        tier_limit = CreditService.TIER_LIMITS.get(user.subscription_tier, Decimal("500"))
        return {
            "success": True,
            "balance": float(user.credits_balance),
            "spent": float(user.credits_spent),
            "tier": user.subscription_tier,
            "tier_limit": float(tier_limit),
        }

    @staticmethod
    async def set_tier(db: AsyncSession, user_id: str, tier: str) -> Dict[str, Any]:
        """Update user subscription tier"""
        if tier not in CreditService.TIER_LIMITS:
            return {"success": False, "error": f"Invalid tier. Choose from: {list(CreditService.TIER_LIMITS.keys())}"}

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"success": False, "error": "User not found"}

        user.subscription_tier = tier
        await db.commit()
        return {"success": True, "tier": tier}
