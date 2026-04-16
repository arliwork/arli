"""Skills marketplace routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from dependencies import get_async_db
from auth import get_current_active_user
from models import Skill, User
from schemas import SkillCreate, SkillOut

router = APIRouter(prefix="/skills", tags=["skills"])

@router.post("", response_model=SkillOut)
async def create_skill(
    data: SkillCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    skill = Skill(
        skill_id=data.skill_id,
        name=data.name,
        description=data.description,
        category=data.category,
        price=data.price,
        author_id=current_user.id,
        code_package_url=data.code_package_url,
        version=data.version,
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return SkillOut.model_validate(skill)

@router.get("", response_model=List[SkillOut])
async def list_skills(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(Skill).where(Skill.is_published == True)
    if category:
        stmt = stmt.where(Skill.category == category)
    if search:
        stmt = stmt.where(Skill.name.ilike(f"%{search}%"))
    if min_price is not None:
        stmt = stmt.where(Skill.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Skill.price <= max_price)
    
    result = await db.execute(stmt.order_by(Skill.created_at.desc()).offset(offset).limit(limit))
    items = result.scalars().all()
    return [SkillOut.model_validate(s) for s in items]

@router.get("/{skill_id}", response_model=SkillOut)
async def get_skill(skill_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Skill).where(Skill.skill_id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return SkillOut.model_validate(skill)

@router.post("/{skill_id}/purchase", response_model=dict)
async def purchase_skill(
    skill_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Skill).where(Skill.skill_id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    skill.downloads += 1
    await db.commit()
    return {"success": True, "skill_id": skill.skill_id, "price": float(skill.price)}
