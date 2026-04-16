"""Pydantic schemas for API requests/responses"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    principal: Optional[str] = None
    wallet_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# Agent schemas
class AgentCreate(BaseModel):
    name: str
    role: str = "worker"
    description: Optional[str] = None
    capabilities: Optional[List[str]] = Field(default_factory=list)

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    is_listed: Optional[bool] = None
    listing_price: Optional[Decimal] = None
    status: Optional[str] = None

class AgentOut(BaseModel):
    id: str
    agent_id: str
    name: str
    role: str
    description: Optional[str]
    level: int
    tier: str
    total_xp: int
    total_tasks: int
    successful_tasks: int
    total_revenue: Decimal
    market_value: Decimal
    hourly_rate: Decimal
    is_listed: bool
    listing_price: Optional[Decimal]
    nft_token_id: Optional[str]
    capabilities: List[str]
    status: str
    created_at: datetime
    owner_id: str
    creator_id: str
    
    class Config:
        from_attributes = True

class AgentListResponse(BaseModel):
    items: List[AgentOut]
    total: int

# Task schemas
class TaskCreate(BaseModel):
    task_id: str
    category: str
    description: str
    assigned_role: Optional[str] = None
    workflow_id: Optional[str] = None

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    success: Optional[bool] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_seconds: Optional[int] = None
    revenue_generated: Optional[Decimal] = None
    client_rating: Optional[int] = None

class TaskOut(BaseModel):
    id: str
    task_id: str
    agent_id: Optional[str]
    workflow_id: Optional[str]
    category: str
    description: str
    assigned_role: Optional[str]
    status: str
    success: Optional[bool]
    execution_time_seconds: Optional[int]
    revenue_generated: Decimal
    client_rating: Optional[int]
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Workflow schemas
class WorkflowCreate(BaseModel):
    workflow_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    total_steps: int = 0
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class WorkflowUpdate(BaseModel):
    status: Optional[str] = None
    current_step: Optional[int] = None
    context: Optional[Dict[str, Any]] = None
    result_summary: Optional[str] = None

class WorkflowOut(BaseModel):
    id: str
    workflow_id: str
    name: str
    description: Optional[str]
    status: str
    current_step: int
    total_steps: int
    context: Dict[str, Any]
    result_summary: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    tasks: List[TaskOut] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

# Marketplace schemas
class SkillCreate(BaseModel):
    skill_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Decimal
    code_package_url: Optional[str] = None
    version: Optional[str] = "1.0.0"

class SkillOut(BaseModel):
    id: str
    skill_id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    price: Decimal
    author_id: str
    version: str
    downloads: int
    rating: Optional[Decimal]
    review_count: int
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PurchaseAgentRequest(BaseModel):
    buyer_id: str

class PurchaseResponse(BaseModel):
    success: bool
    price: Decimal
    platform_fee: Decimal
    creator_royalty: Decimal
    seller_receives: Decimal

# Stats schemas
class PlatformStats(BaseModel):
    total_agents: int
    total_market_value: Optional[Decimal]
    total_revenue_generated: Optional[Decimal]
    total_tasks: int
    total_users: int
    total_sales: int
