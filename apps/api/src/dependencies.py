"""FastAPI dependencies"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal, get_db
from auth import get_current_active_user
from models import User

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
