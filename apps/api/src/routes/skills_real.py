"""
Real Skills Marketplace API
Connects to skills_marketplace.py backend
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'agents'))

from skills_marketplace import (
    SkillPackage, Marketplace, SkillInstaller,
    SkillCategory, SkillStatus
)

router = APIRouter(prefix="/skills", tags=["skills"])

# Initialize marketplace
marketplace = Marketplace()
package_manager = SkillPackage()

class SkillResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    price: float
    author: str
    author_id: str
    rating: float
    review_count: int
    downloads: int
    version: str
    status: str

class PurchaseRequest(BaseModel):
    user_id: str

class PurchaseResponse(BaseModel):
    success: bool
    purchase_id: str
    license_key: str
    message: str

class ReviewRequest(BaseModel):
    user_id: str
    rating: int
    comment: str

class RevenueStats(BaseModel):
    total_sales: float
    total_platform_fee: float
    total_creator_earnings: float
    skill_breakdown: dict

@router.get("/", response_model=List[SkillResponse])
async def get_skills(
    category: Optional[str] = Query(None, description="Filter by category"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    min_rating: Optional[float] = Query(None, description="Minimum rating"),
    search: Optional[str] = Query(None, description="Search query")
):
    """Get all published skills with optional filtering"""
    cat_enum = None
    if category:
        try:
            cat_enum = SkillCategory(category.lower())
        except ValueError:
            pass
    
    skills = marketplace.search_skills(
        query=search,
        category=cat_enum,
        max_price=max_price,
        min_rating=min_rating
    )
    
    return [
        SkillResponse(
            id=skill.skill_id,
            name=skill.name,
            description=skill.description,
            category=skill.category.value if isinstance(skill.category, SkillCategory) else skill.category,
            price=skill.price,
            author=skill.author,
            author_id=skill.author_id,
            rating=skill.rating,
            review_count=skill.review_count,
            downloads=skill.downloads,
            version=skill.version,
            status=skill.status.value if isinstance(skill.status, SkillStatus) else skill.status
        )
        for skill in skills
    ]

@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str):
    """Get single skill by ID"""
    skill = marketplace.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return SkillResponse(
        id=skill.skill_id,
        name=skill.name,
        description=skill.description,
        category=skill.category.value if isinstance(skill.category, SkillCategory) else skill.category,
        price=skill.price,
        author=skill.author,
        author_id=skill.author_id,
        rating=skill.rating,
        review_count=skill.review_count,
        downloads=skill.downloads,
        version=skill.version,
        status=skill.status.value if isinstance(skill.status, SkillStatus) else skill.status
    )

@router.post("/{skill_id}/purchase", response_model=PurchaseResponse)
async def purchase_skill(skill_id: str, request: PurchaseRequest):
    """Purchase a skill"""
    skill = marketplace.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    result = marketplace.purchase_skill(skill_id, request.user_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return PurchaseResponse(
        success=True,
        purchase_id=result["purchase_id"],
        license_key=result["license_key"],
        message=f"Successfully purchased {skill.name}"
    )

@router.post("/{skill_id}/review")
async def add_review(skill_id: str, request: ReviewRequest):
    """Add a review to a skill"""
    skill = marketplace.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    success = marketplace.add_review(skill_id, request.user_id, request.rating, request.comment)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add review")
    
    return {"success": True, "message": "Review added successfully"}

@router.get("/stats/revenue", response_model=RevenueStats)
async def get_revenue_stats(author_id: Optional[str] = None):
    """Get revenue statistics"""
    stats = marketplace.get_revenue_stats(author_id=author_id)
    
    return RevenueStats(
        total_sales=stats["total_sales"],
        total_platform_fee=stats["total_platform_fee"],
        total_creator_earnings=stats["total_creator_earnings"],
        skill_breakdown=stats.get("skill_breakdown", {})
    )

@router.get("/categories")
async def get_categories():
    """Get all available skill categories"""
    return [
        {"id": cat.value, "name": cat.name.replace("_", " ").title()}
        for cat in SkillCategory
    ]
