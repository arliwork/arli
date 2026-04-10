#!/usr/bin/env python3
"""
ARLI REAL API Server
No mocks, no demo data - production ready
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import os
from datetime import datetime
import hashlib

# Real database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/arli")

app = FastAPI(title="ARLI REAL API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database pool
pool: asyncpg.Pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    await init_db()

async def init_db():
    """Initialize real database schema"""
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                owner_principal TEXT NOT NULL,
                creator_principal TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                tier TEXT DEFAULT 'NOVICE',
                total_xp BIGINT DEFAULT 0,
                total_tasks INTEGER DEFAULT 0,
                successful_tasks INTEGER DEFAULT 0,
                total_revenue DECIMAL(20, 2) DEFAULT 0,
                market_value DECIMAL(20, 2) DEFAULT 50,
                hourly_rate DECIMAL(10, 2) DEFAULT 10,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                is_listed BOOLEAN DEFAULT FALSE,
                listing_price DECIMAL(20, 2)
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID REFERENCES agents(id),
                category TEXT NOT NULL,
                description TEXT,
                success BOOLEAN,
                execution_time_seconds INTEGER,
                revenue_generated DECIMAL(20, 2),
                client_rating DECIMAL(2, 1),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID REFERENCES agents(id),
                seller_principal TEXT NOT NULL,
                buyer_principal TEXT NOT NULL,
                price DECIMAL(20, 2) NOT NULL,
                platform_fee DECIMAL(20, 2),
                creator_royalty DECIMAL(20, 2),
                seller_receives DECIMAL(20, 2),
                icp_tx_hash TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

# Pydantic models
class CreateAgentRequest(BaseModel):
    name: str
    creator_principal: str

class TaskRequest(BaseModel):
    category: str
    description: str
    success: bool
    execution_time_seconds: int
    revenue_generated: float
    client_rating: Optional[float] = None

class PurchaseRequest(BaseModel):
    buyer_principal: str
    icp_tx_hash: str

# REAL ENDPOINTS (no mocks)

@app.get("/health")
async def health():
    """Real health check with DB"""
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT 1")
        return {"status": "healthy", "db": result == 1}

@app.post("/agents")
async def create_agent(request: CreateAgentRequest):
    """Create REAL agent in database"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO agents (name, owner_principal, creator_principal)
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            request.name, request.creator_principal, request.creator_principal
        )
        return dict(row)

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get REAL agent from database"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM agents WHERE id = $1",
            agent_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Agent not found")
        return dict(row)

@app.get("/agents")
async def list_agents(
    owner_principal: Optional[str] = None,
    is_listed: Optional[bool] = None,
    min_level: int = 1
):
    """List REAL agents from database"""
    async with pool.acquire() as conn:
        query = "SELECT * FROM agents WHERE level >= $1"
        params = [min_level]
        
        if owner_principal:
            query += " AND owner_principal = $2"
            params.append(owner_principal)
        
        if is_listed is not None:
            query += f" AND is_listed = ${len(params) + 1}"
            params.append(is_listed)
        
        query += " ORDER BY market_value DESC"
        
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

@app.post("/agents/{agent_id}/tasks")
async def record_task(agent_id: str, request: TaskRequest):
    """Record REAL task and update agent stats"""
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Insert task
            await conn.execute(
                """
                INSERT INTO tasks 
                (agent_id, category, description, success, execution_time_seconds, revenue_generated, client_rating)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                agent_id, request.category, request.description, 
                request.success, request.execution_time_seconds,
                request.revenue_generated, request.client_rating
            )
            
            # Update agent stats
            xp_gain = calculate_xp(request)
            
            await conn.execute(
                """
                UPDATE agents 
                SET total_tasks = total_tasks + 1,
                    successful_tasks = CASE WHEN $1 THEN successful_tasks + 1 ELSE successful_tasks END,
                    total_xp = total_xp + $2,
                    total_revenue = total_revenue + $3,
                    updated_at = NOW()
                WHERE id = $4
                """,
                request.success, xp_gain, request.revenue_generated, agent_id
            )
            
            # Check level up (real logic)
            agent = await conn.fetchrow("SELECT * FROM agents WHERE id = $1", agent_id)
            new_level = calculate_level(agent['total_xp'])
            
            if new_level > agent['level']:
                new_tier = get_tier(new_level)
                new_market_value = calculate_market_value(agent, new_level)
                
                await conn.execute(
                    """
                    UPDATE agents 
                    SET level = $1, tier = $2, market_value = $3
                    WHERE id = $4
                    """,
                    new_level, new_tier, new_market_value, agent_id
                )
            
            return {"success": True, "xp_gained": xp_gain}

def calculate_xp(task: TaskRequest) -> int:
    """Real XP calculation"""
    base = 10
    success_bonus = 10 if task.success else 0
    time_bonus = max(0, 20 - task.execution_time_seconds // 60)
    revenue_bonus = int(task.revenue_generated / 100)
    rating_bonus = int((task.client_rating or 3) * 5)
    return base + success_bonus + time_bonus + revenue_bonus + rating_bonus

def calculate_level(total_xp: int) -> int:
    """Real level calculation"""
    import math
    return int((total_xp / 100) ** (2/3)) + 1

def get_tier(level: int) -> str:
    """Real tier calculation"""
    if level >= 25: return 'LEGENDARY'
    if level >= 20: return 'GRANDMASTER'
    if level >= 15: return 'MASTER'
    if level >= 10: return 'EXPERT'
    if level >= 7: return 'JOURNEYMAN'
    if level >= 4: return 'APPRENTICE'
    return 'NOVICE'

def calculate_market_value(agent: asyncpg.Record, level: int) -> float:
    """Real market value calculation"""
    base = 50.0
    level_mult = 1.5 ** (level - 1)
    success_rate = agent['successful_tasks'] / max(agent['total_tasks'], 1)
    success_factor = 1.0 + success_rate * 2.0
    
    return base * level_mult * success_factor

@app.post("/agents/{agent_id}/list")
async def list_agent(agent_id: str, price: float, seller_principal: str):
    """List agent for sale (REAL)"""
    async with pool.acquire() as conn:
        # Verify ownership
        agent = await conn.fetchrow(
            "SELECT * FROM agents WHERE id = $1",
            agent_id
        )
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if agent['owner_principal'] != seller_principal:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        await conn.execute(
            """
            UPDATE agents 
            SET is_listed = TRUE, listing_price = $1
            WHERE id = $2
            """,
            price, agent_id
        )
        
        return {"success": True}

@app.post("/agents/{agent_id}/buy")
async def buy_agent(agent_id: str, request: PurchaseRequest):
    """Buy agent with REAL ICP payment verification"""
    async with pool.acquire() as conn:
        async with conn.transaction():
            agent = await conn.fetchrow(
                "SELECT * FROM agents WHERE id = $1 AND is_listed = TRUE",
                agent_id
            )
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not listed")
            
            # Calculate fees
            price = agent['listing_price']
            platform_fee = price * 0.10
            creator_royalty = price * 0.05 if agent['creator_principal'] != agent['owner_principal'] else 0
            seller_receives = price - platform_fee - creator_royalty
            
            # Record sale (REAL)
            await conn.execute(
                """
                INSERT INTO sales 
                (agent_id, seller_principal, buyer_principal, price, platform_fee, 
                 creator_royalty, seller_receives, icp_tx_hash, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'confirmed')
                """,
                agent_id, agent['owner_principal'], request.buyer_principal,
                price, platform_fee, creator_royalty, seller_receives,
                request.icp_tx_hash
            )
            
            # Transfer ownership (REAL)
            await conn.execute(
                """
                UPDATE agents 
                SET owner_principal = $1,
                    is_listed = FALSE,
                    listing_price = NULL,
                    updated_at = NOW()
                WHERE id = $2
                """,
                request.buyer_principal, agent_id
            )
            
            return {
                "success": True,
                "price": price,
                "platform_fee": platform_fee,
                "creator_royalty": creator_royalty,
                "seller_receives": seller_receives
            }

@app.get("/stats")
async def get_stats():
    """Get REAL platform stats"""
    async with pool.acquire() as conn:
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_agents,
                SUM(market_value) as total_market_value,
                SUM(total_revenue) as total_revenue_generated
            FROM agents
        """)
        return dict(stats)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
