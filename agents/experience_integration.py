#!/usr/bin/env python3
"""
Integration of Agent Experience System with ARLI Runtime and Marketplace

This connects the learning curve system with:
- AgentRuntime (track experience during task execution)
- Skills Marketplace (sell trained agents)
- Memory System (patterns become skills)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from agent_experience import (
    ExperienceTracker, AgentExperience, TaskRecord, 
    TaskCategory, ExperienceTier, calculate_training_roi, estimate_training_time
)
from skills_marketplace import Marketplace, SkillMetadata, SkillCategory as SkillCat


class ExperienceMarketplace:
    """
    Marketplace for trained/experienced agents
    Unlike skills marketplace (sells code), this sells AGENTS with proven track records
    """
    
    def __init__(
        self,
        experience_tracker: ExperienceTracker,
        skills_marketplace: Marketplace
    ):
        self.experience = experience_tracker
        self.skills_marketplace = skills_marketplace
        
        # Commission structure (platform takes 10%)
        self.platform_fee_percent = 0.10
        self.creator_royalty_percent = 0.05  # Original creator gets 5% forever
    
    def list_agent_for_sale(
        self,
        agent_id: str,
        seller_id: str,
        asking_price: Optional[float] = None,
        description: str = None
    ) -> Dict[str, Any]:
        """
        List an experienced agent for sale
        """
        agent = self.experience.get_agent(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        
        # Use calculated market value if no asking price
        price = asking_price or agent.market_value
        
        # Calculate fees
        platform_fee = price * self.platform_fee_percent
        
        # Creator royalty (if not original creator selling)
        creator_royalty = 0
        if seller_id != agent.original_creator:
            creator_royalty = price * self.creator_royalty_percent
        
        seller_proceeds = price - platform_fee - creator_royalty
        
        listing = {
            "listing_id": f"agent_{agent_id}_{int(datetime.now().timestamp())}",
            "agent_id": agent_id,
            "agent_name": agent.agent_name,
            "seller_id": seller_id,
            "asking_price": price,
            "platform_fee": platform_fee,
            "creator_royalty": creator_royalty,
            "seller_proceeds": seller_proceeds,
            "agent_stats": {
                "level": agent.level,
                "tier": agent.tier.name,
                "success_rate": agent.success_rate,
                "total_tasks": agent.total_tasks,
                "revenue_generated": agent.total_revenue_generated,
                "domains": list(agent.expertise.keys()),
                "achievements": agent.achievements
            },
            "description": description or self._generate_description(agent),
            "listed_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        return listing
    
    def _generate_description(self, agent: AgentExperience) -> str:
        """Auto-generate listing description based on agent stats"""
        parts = [
            f"Level {agent.level} {agent.tier.name} Agent",
            f"Success Rate: {agent.success_rate:.1%}",
            f"Completed {agent.total_tasks} tasks",
            f"Generated ${agent.total_revenue_generated:,.2f} in revenue",
        ]
        
        if agent.expertise:
            top_domain = max(agent.expertise.items(), key=lambda x: x[1].tasks_completed)
            parts.append(f"Specialist in {top_domain[0]} ({top_domain[1].tasks_completed} tasks)")
        
        return " | ".join(parts)
    
    def buy_agent(self, listing: Dict, buyer_id: str) -> Dict[str, Any]:
        """
        Purchase an agent (transfer ownership)
        """
        agent_id = listing["agent_id"]
        
        # Record the sale in experience tracker
        result = self.experience.sell_agent(
            agent_id=agent_id,
            new_owner=buyer_id,
            price=listing["asking_price"]
        )
        
        if "error" in result:
            return result
        
        # Also add to skills marketplace as a "trained agent" product
        skill_listing = self._create_agent_skill_package(agent_id, listing)
        
        return {
            "success": True,
            "purchase": result,
            "skill_package": skill_listing,
            "transfer": {
                "agent_id": agent_id,
                "new_owner": buyer_id,
                "previous_owners": self.experience.get_agent(agent_id).previous_owners,
                "sale_price": listing["asking_price"]
            }
        }
    
    def _create_agent_skill_package(self, agent_id: str, listing: Dict) -> Dict:
        """Create a skill package representing the trained agent"""
        agent = self.experience.get_agent(agent_id)
        
        # Create a skill that represents this trained agent
        skill_metadata = SkillMetadata(
            skill_id=f"trained_agent.{agent_id}",
            name=f"Trained Agent: {agent.agent_name}",
            version=f"{agent.level}.0.0",
            description=listing.get("description", f"Pre-trained agent with {agent.total_tasks} tasks completed"),
            category=SkillCat.AUTOMATION,
            author=listing["seller_id"],
            author_id=listing["seller_id"],
            price=listing["asking_price"]
        )
        
        return {
            "skill_id": skill_metadata.skill_id,
            "name": skill_metadata.name,
            "price": skill_metadata.price,
            "agent_stats": listing["agent_stats"]
        }
    
    def find_agents_by_expertise(
        self,
        domain: TaskCategory,
        min_level: int = 1,
        min_success_rate: float = 0.8
    ) -> List[Dict]:
        """Find agents for hire by expertise"""
        results = []
        
        for agent_id, agent in self.experience.agents.items():
            domain_key = domain.value
            
            # Check if agent has expertise in this domain
            if domain_key not in agent.expertise:
                continue
            
            expertise = agent.expertise[domain_key]
            
            # Filter by requirements
            if agent.level < min_level:
                continue
            if expertise.success_rate < min_success_rate:
                continue
            
            results.append({
                "agent_id": agent_id,
                "agent_name": agent.agent_name,
                "level": agent.level,
                "tier": agent.tier.name,
                "domain_expertise": {
                    "tasks": expertise.tasks_completed,
                    "success_rate": expertise.success_rate,
                    "revenue": expertise.revenue_generated
                },
                "market_value": agent.market_value,
                "hourly_rate": agent.hourly_rate_estimate,
                "available": True  # Could check if currently engaged
            })
        
        # Sort by domain success rate
        results.sort(
            key=lambda x: x["domain_expertise"]["success_rate"] * x["level"],
            reverse=True
        )
        
        return results
    
    def compare_agents(self, agent_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple agents side by side"""
        agents = []
        
        for agent_id in agent_ids:
            agent = self.experience.get_agent(agent_id)
            if agent:
                agents.append(agent.to_dict())
        
        if len(agents) < 2:
            return {"error": "Need at least 2 agents to compare"}
        
        # Calculate best in each category
        categories = {
            "market_value": max(agents, key=lambda x: x["market_value"]),
            "success_rate": max(agents, key=lambda x: x["success_rate"]),
            "efficiency": max(agents, key=lambda x: x["efficiency"]),
            "revenue": max(agents, key=lambda x: x["total_revenue_generated"]),
        }
        
        return {
            "agents": agents,
            "winners": {k: v["agent_name"] for k, v in categories.items()},
            "recommendation": self._generate_recommendation(agents)
        }
    
    def _generate_recommendation(self, agents: List[Dict]) -> str:
        """Generate a recommendation based on comparison"""
        if not agents:
            return "No agents to compare"
        
        # Find best value (market value / asking price ratio)
        best_value = min(agents, key=lambda x: x["market_value"] / max(x.get("level", 1), 1))
        
        # Find most reliable
        most_reliable = max(agents, key=lambda x: x["success_rate"])
        
        # Find highest earner
        top_earner = max(agents, key=lambda x: x["total_revenue_generated"])
        
        return (
            f"For best value: {best_value['agent_name']} | "
            f"For reliability: {most_reliable['agent_name']} | "
            f"For revenue: {top_earner['agent_name']}"
        )


class ExperienceEnhancedRuntime:
    """
    Enhanced runtime that automatically tracks experience
    """
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.experience_tracker = ExperienceTracker()
        
        # Get or create agent profile
        self.agent = self.experience_tracker.get_agent(agent_id)
        if not self.agent:
            self.agent = self.experience_tracker.create_agent(agent_id, agent_name)
    
    async def execute_task(
        self,
        task_category: TaskCategory,
        task_description: str,
        execution_func,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a task with automatic experience tracking
        """
        import time
        start_time = time.time()
        
        try:
            # Execute the actual task
            result = await execution_func(*args, **kwargs) if hasattr(execution_func, '__await__') else execution_func(*args, **kwargs)
            success = True
            
            # Extract metrics from result
            revenue = result.get("revenue_generated", 0.0) if isinstance(result, dict) else 0.0
            rating = result.get("client_rating", None) if isinstance(result, dict) else None
            
        except Exception as e:
            success = False
            revenue = 0.0
            rating = None
            result = {"error": str(e)}
        
        execution_time = time.time() - start_time
        
        # Create task record
        task = TaskRecord(
            task_id=f"task_{int(time.time() * 1000)}",
            category=task_category,
            description=task_description,
            success=success,
            execution_time=execution_time,
            revenue_generated=revenue,
            client_rating=rating
        )
        
        # Record experience
        xp_result = self.experience_tracker.record_task(self.agent_id, task)
        
        return {
            "task_result": result,
            "success": success,
            "experience": xp_result,
            "agent_stats": self.agent.to_dict()
        }
    
    def get_value_report(self) -> Dict[str, Any]:
        """Generate a value report for this agent"""
        agent = self.agent
        
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.agent_name,
            "created_at": agent.created_at,
            "age_days": (datetime.now() - datetime.fromisoformat(agent.created_at)).days if agent.created_at else 0,
            "current_value": agent.market_value,
            "value_growth": agent.market_value - 50.0,  # From base $50
            "performance": {
                "success_rate": agent.success_rate,
                "efficiency": agent.efficiency,
                "total_revenue": agent.total_revenue_generated
            },
            "training_investment_roi": calculate_training_roi(
                initial_value=50.0,
                final_value=agent.market_value,
                training_cost=agent.total_execution_time * 0.01  # Assume $0.01 per second
            ),
            "next_level": estimate_training_time(agent.level, agent.level + 1)
        }


def demo_experience_marketplace():
    """Demo the full experience + marketplace integration"""
    print("🚀 ARLI Experience Marketplace Demo\n")
    
    # Initialize systems
    exp_tracker = ExperienceTracker()
    skills_market = Marketplace()
    exp_market = ExperienceMarketplace(exp_tracker, skills_market)
    
    # Create a trained agent
    print("1️⃣ Creating and training an agent...")
    agent = exp_tracker.create_agent(
        agent_id="seo_expert_v1",
        agent_name="SEO Expert Pro",
        creator="agency_alpha"
    )
    
    # Simulate training period
    tasks = [
        (TaskCategory.CONTENT_CREATION, "Blog optimization", True, 1800, 500.0, 5.0),
        (TaskCategory.RESEARCH, "Keyword analysis", True, 3600, 0.0, 5.0),
        (TaskCategory.CONTENT_CREATION, "Meta tags optimization", True, 900, 200.0, 4.5),
        (TaskCategory.MARKETING, "Link building campaign", True, 7200, 1200.0, 5.0),
        (TaskCategory.CONTENT_CREATION, "Content strategy", True, 5400, 800.0, 5.0),
    ]
    
    for i, (category, desc, success, time_spent, revenue, rating) in enumerate(tasks, 1):
        from datetime import datetime
        task = TaskRecord(
            task_id=f"train_{i}",
            category=category,
            description=desc,
            success=success,
            execution_time=time_spent,
            revenue_generated=revenue,
            client_rating=rating
        )
        result = exp_tracker.record_task(agent.agent_id, task)
        print(f"   Task {i}: +{result['xp_gained']} XP")
    
    print(f"\n2️⃣ Training complete!")
    print(f"   Level: {agent.level}")
    print(f"   Success Rate: {agent.success_rate:.1%}")
    print(f"   Market Value: ${agent.market_value:,.2f}")
    
    # List for sale
    print(f"\n3️⃣ Listing agent on marketplace...")
    listing = exp_market.list_agent_for_sale(
        agent_id=agent.agent_id,
        seller_id="agency_alpha",
        asking_price=agent.market_value
    )
    
    print(f"   Listed at: ${listing['asking_price']:,.2f}")
    print(f"   Platform fee (10%): ${listing['platform_fee']:.2f}")
    print(f"   Seller receives: ${listing['seller_proceeds']:,.2f}")
    
    # Simulate purchase
    print(f"\n4️⃣ Simulating purchase by 'company_beta'...")
    purchase = exp_market.buy_agent(listing, "company_beta")
    
    print(f"   ✅ Purchase complete!")
    print(f"   New owner: company_beta")
    print(f"   Times sold: {purchase['purchase']['times_sold']}")
    
    # Show trained agent as skill
    print(f"\n5️⃣ Trained agent as skill package:")
    print(f"   Skill ID: {purchase['skill_package']['skill_id']}")
    print(f"   Price: ${purchase['skill_package']['price']}")
    
    # ROI Analysis
    print(f"\n6️⃣ Investment Analysis:")
    roi = calculate_training_roi(50.0, agent.market_value, 1000.0)
    print(f"   Training investment: ${roi['training_cost']:,.2f}")
    print(f"   Final value: ${roi['final_value']:,.2f}")
    print(f"   ROI: {roi['roi_percent']:+.1f}%")
    
    print(f"\n💡 Key Insight:")
    print(f"   This agent generated ${agent.total_revenue_generated:,.2f} in value")
    print(f"   AND can be sold for ${agent.market_value:,.2f}")
    print(f"   Total return: ${agent.total_revenue_generated + agent.market_value:,.2f}")
    
    return exp_market


if __name__ == "__main__":
    demo_experience_marketplace()
