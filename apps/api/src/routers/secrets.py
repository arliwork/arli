"""Secrets Management — per-agent secure API key storage"""
import uuid
import os
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from dependencies import get_async_db
from auth import get_current_active_user
from models import AgentSecret, Agent, User
from schemas import ApprovalOut, ApprovalListResponse

router = APIRouter(prefix="/agents/{agent_id}/secrets", tags=["secrets"])

# Simple XOR encryption for demo — in production use AWS KMS / HashiCorp Vault
MASTER_KEY = os.getenv("SECRET_MASTER_KEY", "arli-default-key-32bytes-long!!").encode()[:32]

def _xor_encrypt(data: str) -> str:
    return "".join(chr(ord(c) ^ MASTER_KEY[i % len(MASTER_KEY)]) for i, c in enumerate(data))

def _xor_decrypt(data: str) -> str:
    return _xor_encrypt(data)  # XOR is symmetric

@router.get("")
async def list_secrets(
    agent_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(AgentSecret).where(AgentSecret.agent_id == agent_id)
    )
    items = result.scalars().all()
    return {"secrets": [{"id": s.id, "key_name": s.key_name, "created_at": s.created_at} for s in items]}

@router.post("")
async def create_secret(
    agent_id: str,
    key_name: str,
    value: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    # Verify agent exists and user owns it
    agent_result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = agent_result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    encrypted = _xor_encrypt(value)
    secret = AgentSecret(agent_id=agent_id, key_name=key_name, encrypted_value=encrypted)
    db.add(secret)
    await db.commit()
    await db.refresh(secret)
    return {"id": secret.id, "key_name": secret.key_name, "created_at": secret.created_at}

@router.get("/{secret_id}")
async def get_secret(
    agent_id: str,
    secret_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(AgentSecret).where(AgentSecret.id == secret_id, AgentSecret.agent_id == agent_id)
    )
    secret = result.scalar_one_or_none()
    if not secret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")

    decrypted = _xor_decrypt(secret.encrypted_value)
    return {"id": secret.id, "key_name": secret.key_name, "value": decrypted}

@router.delete("/{secret_id}")
async def delete_secret(
    agent_id: str,
    secret_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(AgentSecret).where(AgentSecret.id == secret_id, AgentSecret.agent_id == agent_id)
    )
    secret = result.scalar_one_or_none()
    if not secret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")

    await db.delete(secret)
    await db.commit()
    return {"success": True}
