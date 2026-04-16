"""SQLAlchemy ORM models for ARLI production database"""
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, ForeignKey, Text, JSON, select
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    principal = Column(String(255), unique=True, nullable=True)
    wallet_address = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    # Credit system
    credits_balance = Column(Numeric(18, 4), default=500)  # Free tier starts with 500
    credits_spent = Column(Numeric(18, 4), default=0)
    subscription_tier = Column(String(50), default="free")  # free, plus, pro, enterprise
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    agents = relationship("Agent", back_populates="owner", foreign_keys="Agent.owner_id", lazy="selectin")
    created_agents = relationship("Agent", back_populates="creator", foreign_keys="Agent.creator_id", lazy="selectin")
    skills = relationship("Skill", back_populates="author", lazy="selectin")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False, default="worker")
    description = Column(Text, nullable=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    level = Column(Integer, default=1)
    tier = Column(String(50), default="NOVICE")
    total_xp = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    total_revenue = Column(Numeric(18, 2), default=0)
    market_value = Column(Numeric(18, 2), default=50)
    hourly_rate = Column(Numeric(18, 2), default=10)
    is_listed = Column(Boolean, default=False)
    listing_price = Column(Numeric(18, 2), nullable=True)
    nft_token_id = Column(String(255), nullable=True)
    capabilities = Column(JSON, default=list)
    status = Column(String(50), default="idle")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    owner = relationship("User", back_populates="agents", foreign_keys=[owner_id], lazy="selectin")
    creator = relationship("User", back_populates="created_agents", foreign_keys=[creator_id], lazy="selectin")
    expertise = relationship("AgentExpertise", back_populates="agent", lazy="selectin", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="agent", lazy="selectin", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="agent", lazy="selectin", cascade="all, delete-orphan")

class AgentExpertise(Base):
    __tablename__ = "agent_expertise"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(100), nullable=False)
    tasks_completed = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    total_revenue = Column(Numeric(18, 2), default=0)
    avg_rating = Column(Numeric(3, 2), nullable=True)
    
    agent = relationship("Agent", back_populates="expertise")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    agent_id = Column(String, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="pending")
    success = Column(Boolean, nullable=True)
    execution_time_seconds = Column(Integer, nullable=True)
    revenue_generated = Column(Numeric(18, 2), default=0)
    client_rating = Column(Integer, nullable=True)
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    assigned_role = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    agent = relationship("Agent", back_populates="tasks")
    workflow = relationship("Workflow", back_populates="tasks")

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    context = Column(JSON, default=dict)
    result_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    tasks = relationship("Task", back_populates="workflow", lazy="selectin")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    skill_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    price = Column(Numeric(18, 2), nullable=False, default=0)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    code_package_url = Column(String(500), nullable=True)
    version = Column(String(50), default="1.0.0")
    downloads = Column(Integer, default=0)
    rating = Column(Numeric(3, 2), nullable=True)
    review_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    author = relationship("User", back_populates="skills", lazy="selectin")

class AgentSale(Base):
    __tablename__ = "agent_sales"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    seller_id = Column(String, ForeignKey("users.id"), nullable=False)
    buyer_id = Column(String, ForeignKey("users.id"), nullable=False)
    price = Column(Numeric(18, 2), nullable=False)
    platform_fee = Column(Numeric(18, 2), nullable=False)
    creator_royalty = Column(Numeric(18, 2), default=0)
    seller_receives = Column(Numeric(18, 2), nullable=False)
    sale_type = Column(String(50), default="direct")
    tx_hash = Column(String(255), nullable=True)
    status = Column(String(50), default="confirmed")
    sold_at = Column(DateTime(timezone=True), server_default=func.now())

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    achievement_type = Column(String(100), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    agent = relationship("Agent", back_populates="achievements")

class ScheduledWorkflow(Base):
    __tablename__ = "scheduled_workflows"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    schedule_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # Cron expression or interval like "daily", "hourly", "0 9 * * *"
    schedule = Column(String(100), nullable=False)
    pipeline_type = Column(String(100), nullable=False)
    context = Column(JSON, default=dict)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    run_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", lazy="selectin")
