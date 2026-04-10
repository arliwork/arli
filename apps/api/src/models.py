"""
SQLAlchemy models for ARLI production database
"""
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Numeric, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://arli:password@localhost:5432/arli_prod')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    principal = Column(String(255), unique=True)
    wallet_address = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    agents = relationship("Agent", back_populates="owner", foreign_keys="Agent.owner_id")
    created_agents = relationship("Agent", back_populates="creator", foreign_keys="Agent.creator_id")

class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    owner_id = Column(String, ForeignKey('users.id'))
    creator_id = Column(String, ForeignKey('users.id'))
    level = Column(Integer, default=1)
    tier = Column(String(50), default='NOVICE')
    total_xp = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    total_revenue = Column(Numeric(18, 2), default=0)
    market_value = Column(Numeric(18, 2), default=50)
    hourly_rate = Column(Numeric(18, 2), default=10)
    is_listed = Column(Boolean, default=False)
    listing_price = Column(Numeric(18, 2))
    nft_token_id = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="agents", foreign_keys=[owner_id])
    creator = relationship("User", back_populates="created_agents", foreign_keys=[creator_id])
    expertise = relationship("AgentExpertise", back_populates="agent")
    tasks = relationship("Task", back_populates="agent")
    achievements = relationship("Achievement", back_populates="agent")

class AgentExpertise(Base):
    __tablename__ = 'agent_expertise'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey('agents.id'))
    domain = Column(String(100), nullable=False)
    tasks_completed = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    total_revenue = Column(Numeric(18, 2), default=0)
    avg_rating = Column(Numeric(3, 2))
    
    agent = relationship("Agent", back_populates="expertise")

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True)
    task_id = Column(String(255), unique=True, nullable=False)
    agent_id = Column(String, ForeignKey('agents.id'))
    category = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='pending')
    success = Column(Boolean)
    execution_time_seconds = Column(Integer)
    revenue_generated = Column(Numeric(18, 2), default=0)
    client_rating = Column(Integer)
    result_data = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    agent = relationship("Agent", back_populates="tasks")

class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(String, primary_key=True)
    skill_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    price = Column(Numeric(18, 2), nullable=False)
    author_id = Column(String, ForeignKey('users.id'))
    code_package_url = Column(String(500))
    version = Column(String(50), default='1.0.0')
    downloads = Column(Integer, default=0)
    rating = Column(Numeric(3, 2))
    review_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class AgentSale(Base):
    __tablename__ = 'agent_sales'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey('agents.id'))
    seller_id = Column(String, ForeignKey('users.id'))
    buyer_id = Column(String, ForeignKey('users.id'))
    price = Column(Numeric(18, 2))
    platform_fee = Column(Numeric(18, 2))
    creator_royalty = Column(Numeric(18, 2))
    seller_receives = Column(Numeric(18, 2))
    sale_type = Column(String(50))
    tx_hash = Column(String(255))
    sold_at = Column(DateTime, server_default=func.now())

class Achievement(Base):
    __tablename__ = 'achievements'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey('agents.id'))
    achievement_type = Column(String(100), nullable=False)
    unlocked_at = Column(DateTime, server_default=func.now())
    
    agent = relationship("Agent", back_populates="achievements")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
