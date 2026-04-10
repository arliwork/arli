"""
Arli Marketplace Server
Real marketplace backend for agents
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime
import os

app = FastAPI(title="Arli Marketplace", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with PostgreSQL in production)
agents_db: Dict[str, Dict] = {}
sales_db: List[Dict] = []


class AgentListing(BaseModel):
    arli_id: str
    name: str
    source_system: str
    level: int
    tier: str
    xp: int
    estimated_market_value: float
    capabilities: List[Dict]
    description: Optional[str] = ""
    seller_id: Optional[str] = "anonymous"
    price: Optional[float] = None
    status: str = "active"  # active, sold, withdrawn


class PurchaseRequest(BaseModel):
    buyer_id: str
    payment_method: str = "icp"  # icp, stripe, crypto


@app.get("/")
def root():
    return {
        "name": "Arli Marketplace",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "list_agents": "GET /agents",
            "upload_agent": "POST /agents/upload",
            "buy_agent": "POST /agents/{id}/buy",
            "search": "GET /agents/search?q=query"
        }
    }


@app.get("/agents")
def list_agents(
    tier: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    source_system: Optional[str] = None,
    sort_by: str = "price"  # price, level, date
):
    """List all available agents"""
    agents = [a for a in agents_db.values() if a["status"] == "active"]
    
    # Filters
    if tier:
        agents = [a for a in agents if a["tier"] == tier.upper()]
    if source_system:
        agents = [a for a in agents if a["source_system"] == source_system]
    if min_price:
        agents = [a for a in agents if a.get("price", 0) >= min_price]
    if max_price:
        agents = [a for a in agents if a.get("price", 0) <= max_price]
    
    # Sorting
    if sort_by == "price":
        agents.sort(key=lambda x: x.get("price", 0))
    elif sort_by == "level":
        agents.sort(key=lambda x: x["level"], reverse=True)
    elif sort_by == "date":
        agents.sort(key=lambda x: x.get("listed_at", ""), reverse=True)
    
    return {
        "total": len(agents),
        "agents": agents
    }


@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    """Get single agent details"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    
    # Add calculated fields
    agent["market_stats"] = {
        "views": agent.get("views", 0),
        "favorites": agent.get("favorites", 0),
        "times_sold": agent.get("times_sold", 0)
    }
    
    return agent


@app.post("/agents/upload")
async def upload_agent(file: UploadFile = File(...)):
    """Upload new agent to marketplace"""
    try:
        content = await file.read()
        agent_data = json.loads(content)
        
        # Validate required fields
        required = ["name", "arli_id", "level", "capabilities"]
        for field in required:
            if field not in agent_data:
                raise HTTPException(status_code=400, detail=f"Missing field: {field}")
        
        # Add metadata
        agent_data["listing_id"] = str(uuid.uuid4())
        agent_data["listed_at"] = datetime.utcnow().isoformat()
        agent_data["status"] = "active"
        agent_data["seller_id"] = agent_data.get("seller_id", "anonymous")
        
        # Set price if not provided
        if "price" not in agent_data or not agent_data["price"]:
            agent_data["price"] = agent_data.get("estimated_market_value", 10.0)
        
        # Store
        agents_db[agent_data["arli_id"]] = agent_data
        
        return {
            "success": True,
            "listing_id": agent_data["listing_id"],
            "arli_id": agent_data["arli_id"],
            "name": agent_data["name"],
            "price": agent_data["price"],
            "url": f"/agents/{agent_data['arli_id']}"
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/upload/json")
def upload_agent_json(agent_data: Dict[Any, Any]):
    """Upload agent via JSON body"""
    try:
        # Validate
        required = ["name", "arli_id", "level", "capabilities"]
        for field in required:
            if field not in agent_data:
                raise HTTPException(status_code=400, detail=f"Missing field: {field}")
        
        # Add metadata
        agent_data["listing_id"] = str(uuid.uuid4())
        agent_data["listed_at"] = datetime.utcnow().isoformat()
        agent_data["status"] = "active"
        
        # Set price
        if "price" not in agent_data or not agent_data["price"]:
            agent_data["price"] = agent_data.get("estimated_market_value", 10.0)
        
        # Store
        agents_db[agent_data["arli_id"]] = agent_data
        
        return {
            "success": True,
            "listing_id": agent_data["listing_id"],
            "arli_id": agent_data["arli_id"],
            "price": agent_data["price"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/{agent_id}/buy")
def buy_agent(agent_id: str, request: PurchaseRequest):
    """Purchase an agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    
    if agent["status"] != "active":
        raise HTTPException(status_code=400, detail="Agent not available")
    
    # Create sale record
    sale = {
        "sale_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "agent_name": agent["name"],
        "seller_id": agent["seller_id"],
        "buyer_id": request.buyer_id,
        "price": agent["price"],
        "payment_method": request.payment_method,
        "sold_at": datetime.utcnow().isoformat(),
        "platform_fee": agent["price"] * 0.10,  # 10% fee
        "seller_revenue": agent["price"] * 0.90  # 90% to seller
    }
    
    sales_db.append(sale)
    
    # Update agent status
    agent["status"] = "sold"
    agent["times_sold"] = agent.get("times_sold", 0) + 1
    agent["last_sold_at"] = sale["sold_at"]
    agent["last_sold_price"] = sale["price"]
    
    return {
        "success": True,
        "sale_id": sale["sale_id"],
        "agent_id": agent_id,
        "price": sale["price"],
        "fee": sale["platform_fee"],
        "download_url": f"/agents/{agent_id}/download"
    }


@app.get("/agents/search")
def search_agents(q: str):
    """Search agents by name, category, or capability"""
    results = []
    q = q.lower()
    
    for agent in agents_db.values():
        # Search in name
        if q in agent["name"].lower():
            results.append(agent)
            continue
        
        # Search in capabilities
        for cap in agent.get("capabilities", []):
            if q in cap.get("name", "").lower() or q in cap.get("category", "").lower():
                results.append(agent)
                break
    
    return {
        "query": q,
        "total": len(results),
        "agents": results
    }


@app.get("/stats")
def marketplace_stats():
    """Get marketplace statistics"""
    active_agents = [a for a in agents_db.values() if a["status"] == "active"]
    
    total_value = sum(a.get("price", 0) for a in active_agents)
    
    tier_counts = {}
    for agent in active_agents:
        tier = agent.get("tier", "COMMON")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    return {
        "total_agents": len(agents_db),
        "active_listings": len(active_agents),
        "total_sales": len(sales_db),
        "total_volume": sum(s["price"] for s in sales_db),
        "platform_revenue": sum(s["platform_fee"] for s in sales_db),
        "average_price": total_value / len(active_agents) if active_agents else 0,
        "tier_distribution": tier_counts
    }


@app.get("/my-agents/{seller_id}")
def my_agents(seller_id: str):
    """Get all agents by seller"""
    my_listings = [a for a in agents_db.values() if a.get("seller_id") == seller_id]
    
    return {
        "seller_id": seller_id,
        "total_listings": len(my_listings),
        "active": len([a for a in my_listings if a["status"] == "active"]),
        "sold": len([a for a in my_listings if a["status"] == "sold"]),
        "agents": my_listings
    }


# Load existing agents on startup
def load_sample_agents():
    """Load sample agents for demo"""
    sample_agents = [
        {
            "arli_id": "arli_sample_001",
            "name": "Crypto Trading Pro",
            "source_system": "openclaw",
            "level": 15,
            "tier": "UNCOMMON",
            "xp": 3200,
            "price": 299.99,
            "capabilities": [
                {"name": "btc_trading", "proficiency": 0.92},
                {"name": "risk_management", "proficiency": 0.88}
            ],
            "seller_id": "trader_joe",
            "status": "active",
            "listed_at": datetime.utcnow().isoformat()
        }
    ]
    
    for agent in sample_agents:
        agents_db[agent["arli_id"]] = agent


if __name__ == "__main__":
    import uvicorn
    load_sample_agents()
    uvicorn.run(app, host="0.0.0.0", port=8002)
