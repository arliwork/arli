"""
Marketplace Upload API
Handles agent uploads to Arli Marketplace
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import hashlib
import uuid
from pathlib import Path

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

# Storage path
MARKETPLACE_DIR = Path("/home/paperclip/arli/data/marketplace")
MARKETPLACE_DIR.mkdir(parents=True, exist_ok=True)


class AgentUploadRequest(BaseModel):
    """Agent upload request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    seller_wallet: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class AgentUploadResponse(BaseModel):
    """Agent upload response"""
    success: bool
    agent_id: Optional[str] = None
    listing_url: Optional[str] = None
    message: str
    estimated_value: Optional[float] = None


class AgentListing(BaseModel):
    """Agent listing in marketplace"""
    id: str
    name: str
    description: Optional[str]
    level: int
    tier: str
    xp: int
    price: float
    currency: str
    seller: str
    capabilities: List[Dict[str, Any]]
    tags: List[str]
    created_at: str
    status: str = "active"


@router.post("/upload", response_model=AgentUploadResponse)
async def upload_agent(
    file: UploadFile = File(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    seller_wallet: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """
    Upload agent to marketplace
    
    - **file**: Agent JSON file (from export)
    - **price**: Sale price in USD
    - **description**: Optional listing description
    - **seller_wallet**: Seller's ICP wallet address
    - **tags**: Comma-separated tags
    """
    try:
        # Read and validate JSON
        content = await file.read()
        agent_data = json.loads(content)
        
        # Validate required fields
        required = ["name", "arli_id", "level", "capabilities"]
        for field in required:
            if field not in agent_data:
                return AgentUploadResponse(
                    success=False,
                    message=f"Missing required field: {field}"
                )
        
        # Generate listing ID
        listing_id = f"list_{uuid.uuid4().hex[:12]}"
        
        # Parse tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else []
        
        # Create listing
        listing = {
            "id": listing_id,
            "agent_data": agent_data,
            "name": agent_data["name"],
            "description": description or agent_data.get("description", ""),
            "level": agent_data.get("level", 1),
            "tier": agent_data.get("tier", "COMMON"),
            "xp": agent_data.get("xp", 0),
            "price": price,
            "currency": "USD",
            "estimated_value": agent_data.get("estimated_market_value", 10.0),
            "seller": seller_wallet or "anonymous",
            "capabilities": agent_data.get("capabilities", []),
            "tags": tag_list,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "views": 0,
            "sales": 0
        }
        
        # Save listing
        listing_path = MARKETPLACE_DIR / f"{listing_id}.json"
        with open(listing_path, 'w') as f:
            json.dump(listing, f, indent=2)
        
        # Save to catalog
        catalog_path = MARKETPLACE_DIR / "catalog.json"
        catalog = []
        if catalog_path.exists():
            with open(catalog_path, 'r') as f:
                catalog = json.load(f)
        
        catalog.append({
            "id": listing_id,
            "name": listing["name"],
            "price": price,
            "tier": listing["tier"],
            "level": listing["level"],
            "tags": tag_list,
            "created_at": listing["created_at"]
        })
        
        with open(catalog_path, 'w') as f:
            json.dump(catalog, f, indent=2)
        
        return AgentUploadResponse(
            success=True,
            agent_id=listing_id,
            listing_url=f"/marketplace/agent/{listing_id}",
            message="Agent successfully listed on marketplace",
            estimated_value=listing["estimated_value"]
        )
        
    except json.JSONDecodeError:
        return AgentUploadResponse(
            success=False,
            message="Invalid JSON file"
        )
    except Exception as e:
        return AgentUploadResponse(
            success=False,
            message=f"Upload failed: {str(e)}"
        )


@router.post("/upload/bundle")
async def upload_bundle(
    file: UploadFile = File(...),
    bundle_price: float = Form(...),
    seller_wallet: Optional[str] = Form(None)
):
    """Upload multiple agents as a bundle"""
    try:
        content = await file.read()
        bundle_data = json.loads(content)
        
        if "agents" not in bundle_data:
            return {"success": False, "message": "Invalid bundle format"}
        
        bundle_id = f"bundle_{uuid.uuid4().hex[:12]}"
        
        listing = {
            "id": bundle_id,
            "type": "bundle",
            "name": bundle_data.get("name", "Agent Bundle"),
            "agent_count": len(bundle_data["agents"]),
            "agents": bundle_data["agents"],
            "price": bundle_price,
            "currency": "USD",
            "seller": seller_wallet or "anonymous",
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        # Save bundle
        bundle_path = MARKETPLACE_DIR / f"{bundle_id}.json"
        with open(bundle_path, 'w') as f:
            json.dump(listing, f, indent=2)
        
        return {
            "success": True,
            "bundle_id": bundle_id,
            "listing_url": f"/marketplace/bundle/{bundle_id}",
            "message": f"Bundle with {listing['agent_count']} agents listed",
            "total_value": sum(a.get("estimated_market_value", 0) for a in bundle_data["agents"])
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/agents", response_model=List[AgentListing])
async def list_agents(
    tier: Optional[str] = None,
    min_level: Optional[int] = None,
    max_price: Optional[float] = None,
    tag: Optional[str] = None,
    sort_by: str = "created_at"
):
    """List all marketplace agents with filters"""
    listings = []
    
    for listing_file in MARKETPLACE_DIR.glob("list_*.json"):
        try:
            with open(listing_file, 'r') as f:
                data = json.load(f)
            
            if data.get("status") != "active":
                continue
            
            # Apply filters
            if tier and data.get("tier") != tier.upper():
                continue
            if min_level and data.get("level", 0) < min_level:
                continue
            if max_price and data.get("price", 0) > max_price:
                continue
            if tag and tag not in data.get("tags", []):
                continue
            
            listings.append(AgentListing(
                id=data["id"],
                name=data["name"],
                description=data.get("description"),
                level=data["level"],
                tier=data["tier"],
                xp=data.get("xp", 0),
                price=data["price"],
                currency=data.get("currency", "USD"),
                seller=data["seller"],
                capabilities=data.get("capabilities", []),
                tags=data.get("tags", []),
                created_at=data["created_at"]
            ))
            
        except Exception:
            continue
    
    # Sort
    if sort_by == "price":
        listings.sort(key=lambda x: x.price)
    elif sort_by == "level":
        listings.sort(key=lambda x: x.level, reverse=True)
    else:
        listings.sort(key=lambda x: x.created_at, reverse=True)
    
    return listings


@router.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    """Get single agent details"""
    listing_path = MARKETPLACE_DIR / f"{agent_id}.json"
    
    if not listing_path.exists():
        raise HTTPException(status_code=404, detail="Agent not found")
    
    with open(listing_path, 'r') as f:
        data = json.load(f)
    
    # Increment views
    data["views"] = data.get("views", 0) + 1
    with open(listing_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return data


@router.post("/agent/{agent_id}/purchase")
async def purchase_agent(agent_id: str, buyer_wallet: str = Form(...)):
    """Purchase an agent"""
    listing_path = MARKETPLACE_DIR / f"{agent_id}.json"
    
    if not listing_path.exists():
        raise HTTPException(status_code=404, detail="Agent not found")
    
    with open(listing_path, 'r') as f:
        data = json.load(f)
    
    if data["status"] != "active":
        raise HTTPException(status_code=400, detail="Agent not available")
    
    # Record purchase
    data["sales"] = data.get("sales", 0) + 1
    data["last_purchase"] = datetime.utcnow().isoformat()
    
    with open(listing_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return {
        "success": True,
        "message": "Purchase recorded",
        "agent": data["name"],
        "price": data["price"],
        "transaction_id": f"tx_{uuid.uuid4().hex[:16]}"
    }


@router.get("/stats")
async def marketplace_stats():
    """Get marketplace statistics"""
    total_agents = 0
    total_value = 0
    tier_counts = {}
    
    for listing_file in MARKETPLACE_DIR.glob("list_*.json"):
        try:
            with open(listing_file, 'r') as f:
                data = json.load(f)
            
            if data.get("status") == "active":
                total_agents += 1
                total_value += data.get("price", 0)
                tier = data.get("tier", "COMMON")
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
                
        except Exception:
            continue
    
    return {
        "total_agents": total_agents,
        "total_value_usd": round(total_value, 2),
        "tier_distribution": tier_counts,
        "agents_by_tier": tier_counts
    }
