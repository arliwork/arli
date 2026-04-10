#!/usr/bin/env python3
"""
ARLI Agent Experience & Learning Curve System

Tracks agent learning progress, experience levels, and market value.
Agents become valuable assets based on their proven track record.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib


class ExperienceTier(Enum):
    """Agent experience tiers based on performance"""
    NOVICE = 1
    APPRENTICE = 2
    JOURNEYMAN = 3
    EXPERT = 4
    MASTER = 5
    GRANDMASTER = 6
    LEGENDARY = 7


class TaskCategory(Enum):
    """Categories of tasks for skill tracking"""
    WEB_SCRAPING = "web_scraping"
    DATA_ANALYSIS = "data_analysis"
    CONTENT_CREATION = "content_creation"
    CODING = "coding"
    TRADING = "trading"
    MARKETING = "marketing"
    AUTOMATION = "automation"
    SECURITY = "security"
    DEVOPS = "devops"
    RESEARCH = "research"
    COMMUNICATION = "communication"
    OTHER = "other"


@dataclass
class TaskRecord:
    """Single task execution record"""
    task_id: str
    category: TaskCategory
    description: str
    success: bool
    execution_time: float  # seconds
    revenue_generated: float = 0.0
    cost_saved: float = 0.0
    client_rating: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            'category': self.category.value if isinstance(self.category, TaskCategory) else self.category
        }


@dataclass
class DomainExpertise:
    """Expertise in a specific domain"""
    domain: TaskCategory
    tasks_completed: int = 0
    successful_tasks: int = 0
    total_execution_time: float = 0.0
    revenue_generated: float = 0.0
    avg_rating: float = 0.0
    first_task: Optional[str] = None
    last_task: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        if self.tasks_completed == 0:
            return 0.0
        return self.successful_tasks / self.tasks_completed
    
    @property
    def efficiency_score(self) -> float:
        """Tasks per hour"""
        if self.total_execution_time == 0:
            return 0.0
        return self.tasks_completed / (self.total_execution_time / 3600)


@dataclass
class AgentExperience:
    """
    Complete agent experience profile
    This is the 'learning curve' that makes agents valuable
    """
    agent_id: str
    agent_name: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Experience points and level
    total_xp: int = 0
    level: int = 1
    tier: ExperienceTier = ExperienceTier.NOVICE
    
    # Task statistics
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    
    # Financial impact
    total_revenue_generated: float = 0.0
    total_cost_saved: float = 0.0
    client_payments_received: float = 0.0
    
    # Time tracking
    total_execution_time: float = 0.0  # seconds
    total_learning_time: float = 0.0   # time spent on self-improvement
    
    # Domain expertise
    expertise: Dict[str, DomainExpertise] = field(default_factory=dict)
    
    # Patterns and knowledge
    patterns_learned: int = 0
    skills_acquired: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    
    # Reputation
    client_ratings: List[float] = field(default_factory=list)
    review_count: int = 0
    
    # Market metrics
    times_sold: int = 0
    previous_owners: List[str] = field(default_factory=list)
    original_creator: Optional[str] = None
    
    # Special achievements
    achievements: List[str] = field(default_factory=list)
    streak_days: int = 0  # consecutive days of activity
    
    def __post_init__(self):
        if not self.original_creator:
            self.original_creator = self.agent_id
    
    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.successful_tasks / self.total_tasks
    
    @property
    def average_rating(self) -> float:
        if not self.client_ratings:
            return 0.0
        return sum(self.client_ratings) / len(self.client_ratings)
    
    @property
    def efficiency(self) -> float:
        """Tasks per hour of execution"""
        if self.total_execution_time == 0:
            return 0.0
        hours = self.total_execution_time / 3600
        return self.total_tasks / hours if hours > 0 else 0.0
    
    @property
    def roi_multiplier(self) -> float:
        """Return on investment multiplier"""
        if self.total_tasks == 0:
            return 1.0
        return 1.0 + (self.total_revenue_generated / 1000) + (self.success_rate * 2)
    
    @property
    def market_value(self) -> float:
        """
        Calculate agent market value based on experience
        This is the key formula for the learning curve marketplace
        """
        base_value = 50.0  # $50 for a new agent
        
        # Level multiplier (exponential growth)
        level_multiplier = 1.5 ** (self.level - 1)
        
        # Tier bonus
        tier_bonus = self.tier.value * 100
        
        # Performance factors
        success_factor = 1.0 + (self.success_rate * 2)  # Up to 3x for 100% success
        rating_factor = 1.0 + (self.average_rating * 0.2)  # Up to 2x for 5-star rating
        
        # Revenue factor
        revenue_factor = 1.0 + (self.total_revenue_generated / 10000)
        
        # Expertise diversity bonus
        diversity_bonus = len(self.expertise) * 50
        
        # Achievement bonus
        achievement_bonus = len(self.achievements) * 25
        
        value = (
            base_value * level_multiplier * success_factor * rating_factor * revenue_factor
            + tier_bonus
            + diversity_bonus
            + achievement_bonus
        )
        
        return round(value, 2)
    
    @property
    def hourly_rate_estimate(self) -> float:
        """Estimated hourly rate based on experience"""
        base_rate = 10.0  # $10/hour for novice
        experience_multiplier = 1.3 ** (self.level - 1)
        return round(base_rate * experience_multiplier * self.roi_multiplier, 2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'created_at': self.created_at,
            'total_xp': self.total_xp,
            'level': self.level,
            'tier': self.tier.value,
            'total_tasks': self.total_tasks,
            'successful_tasks': self.successful_tasks,
            'failed_tasks': self.failed_tasks,
            'total_revenue_generated': self.total_revenue_generated,
            'total_cost_saved': self.total_cost_saved,
            'client_payments_received': self.client_payments_received,
            'total_execution_time': self.total_execution_time,
            'total_learning_time': self.total_learning_time,
            'expertise': {
                k: {
                    **asdict(v),
                    'domain': v.domain.value if isinstance(v.domain, TaskCategory) else v.domain
                }
                for k, v in self.expertise.items()
            },
            'patterns_learned': self.patterns_learned,
            'skills_acquired': self.skills_acquired,
            'certifications': self.certifications,
            'client_ratings': self.client_ratings,
            'review_count': self.review_count,
            'times_sold': self.times_sold,
            'previous_owners': self.previous_owners,
            'original_creator': self.original_creator,
            'achievements': self.achievements,
            'streak_days': self.streak_days,
            'market_value': self.market_value,
            'success_rate': self.success_rate,
            'average_rating': self.average_rating,
            'efficiency': self.efficiency,
            'hourly_rate_estimate': self.hourly_rate_estimate
        }


class ExperienceTracker:
    """
    Tracks and manages agent experience
    """
    
    def __init__(self, data_dir: str = ".arli/experience"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.agents: Dict[str, AgentExperience] = {}
        self._load_all()
    
    def _get_agent_file(self, agent_id: str) -> Path:
        return self.data_dir / f"{agent_id}.json"
    
    def _load_all(self):
        """Load all agent experiences"""
        for file in self.data_dir.glob("*.json"):
            try:
                data = json.loads(file.read_text())
                agent_id = data['agent_id']
                
                # Convert tier
                if isinstance(data.get('tier'), int):
                    data['tier'] = ExperienceTier(data['tier'])
                elif isinstance(data.get('tier'), str):
                    data['tier'] = ExperienceTier[data['tier'].upper()]
                
                # Convert expertise
                expertise = {}
                for domain_key, domain_data in data.get('expertise', {}).items():
                    domain_cat = TaskCategory(domain_key) if isinstance(domain_key, str) else domain_key
                    expertise[domain_key] = DomainExpertise(
                        domain=domain_cat,
                        **{k: v for k, v in domain_data.items() if k != 'domain'}
                    )
                data['expertise'] = expertise
                
                self.agents[agent_id] = AgentExperience(**data)
            except Exception as e:
                print(f"Warning: Could not load {file}: {e}")
    
    def create_agent(self, agent_id: str, agent_name: str, creator: str = None) -> AgentExperience:
        """Create new agent experience profile"""
        agent = AgentExperience(
            agent_id=agent_id,
            agent_name=agent_name,
            original_creator=creator or agent_id
        )
        self.agents[agent_id] = agent
        self._save_agent(agent)
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[AgentExperience]:
        """Get agent experience profile"""
        return self.agents.get(agent_id)
    
    def _save_agent(self, agent: AgentExperience):
        """Save agent to disk"""
        file = self._get_agent_file(agent.agent_id)
        file.write_text(json.dumps(agent.to_dict(), indent=2))
    
    def record_task(self, agent_id: str, task: TaskRecord) -> Dict[str, Any]:
        """
        Record a completed task and update experience
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        
        # Update basic stats
        agent.total_tasks += 1
        if task.success:
            agent.successful_tasks += 1
            # XP for success
            xp_gain = self._calculate_xp(task)
            agent.total_xp += xp_gain
        else:
            agent.failed_tasks += 1
            # Small XP for trying
            agent.total_xp += 1
        
        # Update financials
        agent.total_revenue_generated += task.revenue_generated
        agent.total_cost_saved += task.cost_saved
        
        # Update time
        agent.total_execution_time += task.execution_time
        
        # Update domain expertise
        domain_key = task.category.value if isinstance(task.category, TaskCategory) else task.category
        if domain_key not in agent.expertise:
            agent.expertise[domain_key] = DomainExpertise(domain=task.category)
        
        expertise = agent.expertise[domain_key]
        expertise.tasks_completed += 1
        if task.success:
            expertise.successful_tasks += 1
        expertise.total_execution_time += task.execution_time
        expertise.revenue_generated += task.revenue_generated
        
        if not expertise.first_task:
            expertise.first_task = task.timestamp
        expertise.last_task = task.timestamp
        
        # Update rating
        if task.client_rating:
            agent.client_ratings.append(task.client_rating)
            expertise.avg_rating = sum(agent.client_ratings) / len(agent.client_ratings)
        
        # Check for level up
        level_up = self._check_level_up(agent)
        
        # Check achievements
        new_achievements = self._check_achievements(agent)
        
        # Save
        self._save_agent(agent)
        
        return {
            "success": True,
            "xp_gained": xp_gain if task.success else 1,
            "total_xp": agent.total_xp,
            "level": agent.level,
            "tier": agent.tier.name,
            "level_up": level_up,
            "new_achievements": new_achievements,
            "market_value": agent.market_value
        }
    
    def _calculate_xp(self, task: TaskRecord) -> int:
        """Calculate XP for a task"""
        base_xp = 10
        
        # Bonus for success
        success_bonus = 10
        
        # Time bonus (efficiency)
        time_bonus = max(0, 20 - int(task.execution_time / 60))  # Faster = more XP
        
        # Revenue bonus
        revenue_bonus = int(task.revenue_generated / 100)
        
        # Client rating bonus
        rating_bonus = int((task.client_rating or 3) * 5)
        
        return base_xp + success_bonus + time_bonus + revenue_bonus + rating_bonus
    
    def _check_level_up(self, agent: AgentExperience) -> bool:
        """Check and apply level up"""
        xp_needed = self._xp_for_level(agent.level + 1)
        
        if agent.total_xp >= xp_needed:
            agent.level += 1
            
            # Update tier
            if agent.level >= 25:
                agent.tier = ExperienceTier.LEGENDARY
            elif agent.level >= 20:
                agent.tier = ExperienceTier.GRANDMASTER
            elif agent.level >= 15:
                agent.tier = ExperienceTier.MASTER
            elif agent.level >= 10:
                agent.tier = ExperienceTier.EXPERT
            elif agent.level >= 7:
                agent.tier = ExperienceTier.JOURNEYMAN
            elif agent.level >= 4:
                agent.tier = ExperienceTier.APPRENTICE
            
            return True
        return False
    
    def _xp_for_level(self, level: int) -> int:
        """XP needed for a level (exponential curve)"""
        return int(100 * (level ** 1.5))
    
    def _check_achievements(self, agent: AgentExperience) -> List[str]:
        """Check for new achievements"""
        new_achievements = []
        
        achievements = {
            "first_task": (agent.total_tasks >= 1, "Completed first task"),
            "centurion": (agent.total_tasks >= 100, "Completed 100 tasks"),
            "millennial": (agent.total_tasks >= 1000, "Completed 1000 tasks"),
            "perfect_10": (agent.success_rate >= 0.95 and agent.total_tasks >= 10, "95% success rate"),
            "money_maker": (agent.total_revenue_generated >= 10000, "Generated $10K revenue"),
            "jack_of_all_trades": (len(agent.expertise) >= 5, "Mastered 5 domains"),
            "speed_demon": (agent.efficiency >= 10, "10+ tasks per hour"),
            "five_star": (agent.average_rating >= 4.9 and agent.review_count >= 10, "4.9+ star rating"),
            "iron_man": (agent.streak_days >= 30, "30 day streak"),
            "sold": (agent.times_sold >= 1, "Sold on marketplace"),
        }
        
        for achievement_id, (condition, description) in achievements.items():
            if condition and achievement_id not in agent.achievements:
                agent.achievements.append(achievement_id)
                new_achievements.append(description)
        
        return new_achievements
    
    def add_skill(self, agent_id: str, skill_name: str):
        """Add acquired skill to agent"""
        agent = self.agents.get(agent_id)
        if agent and skill_name not in agent.skills_acquired:
            agent.skills_acquired.append(skill_name)
            agent.patterns_learned += 1
            self._save_agent(agent)
    
    def record_learning(self, agent_id: str, duration_seconds: float):
        """Record time spent on self-improvement/learning"""
        agent = self.agents.get(agent_id)
        if agent:
            agent.total_learning_time += duration_seconds
            # Small XP for learning
            agent.total_xp += int(duration_seconds / 60)  # 1 XP per minute of learning
            self._save_agent(agent)
    
    def sell_agent(self, agent_id: str, new_owner: str, price: float) -> Dict[str, Any]:
        """Record agent sale (transfer ownership)"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        
        agent.times_sold += 1
        agent.previous_owners.append(agent.original_creator if agent.times_sold == 1 else f"owner_{agent.times_sold}")
        
        # Add achievement
        if "sold" not in agent.achievements:
            agent.achievements.append("sold")
        
        self._save_agent(agent)
        
        return {
            "success": True,
            "times_sold": agent.times_sold,
            "market_value": agent.market_value,
            "sale_price": price
        }
    
    def get_leaderboard(self, category: TaskCategory = None, limit: int = 10) -> List[Dict]:
        """Get top agents by experience"""
        agents = list(self.agents.values())
        
        if category:
            # Filter by domain expertise
            cat_key = category.value
            agents = [a for a in agents if cat_key in a.expertise]
            agents.sort(key=lambda a: a.expertise[cat_key].success_rate * a.expertise[cat_key].tasks_completed, reverse=True)
        else:
            # Sort by overall market value
            agents.sort(key=lambda a: a.market_value, reverse=True)
        
        return [a.to_dict() for a in agents[:limit]]
    
    def get_marketplace_listings(self, min_tier: ExperienceTier = None) -> List[Dict]:
        """Get agents available for sale"""
        listings = []
        
        for agent in self.agents.values():
            if min_tier and agent.tier.value < min_tier.value:
                continue
            
            listings.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "level": agent.level,
                "tier": agent.tier.name,
                "market_value": agent.market_value,
                "success_rate": agent.success_rate,
                "average_rating": agent.average_rating,
                "total_tasks": agent.total_tasks,
                "domains": list(agent.expertise.keys()),
                "achievements": agent.achievements,
                "hourly_rate": agent.hourly_rate_estimate
            })
        
        listings.sort(key=lambda x: x["market_value"], reverse=True)
        return listings


# Convenience functions for integration
def calculate_training_roi(initial_value: float, final_value: float, training_cost: float) -> dict:
    """Calculate ROI of training an agent"""
    value_increase = final_value - initial_value
    roi = ((value_increase - training_cost) / training_cost) * 100 if training_cost > 0 else 0
    
    return {
        "initial_value": initial_value,
        "final_value": final_value,
        "value_increase": value_increase,
        "training_cost": training_cost,
        "roi_percent": roi,
        "profitable": roi > 0
    }


def estimate_training_time(current_level: int, target_level: int) -> dict:
    """Estimate time needed to train agent to target level"""
    tracker = ExperienceTracker()
    
    current_xp = tracker._xp_for_level(current_level)
    target_xp = tracker._xp_for_level(target_level)
    xp_needed = target_xp - current_xp
    
    # Assuming average 20 XP per task, 10 tasks per day
    tasks_needed = xp_needed / 20
    days_needed = tasks_needed / 10
    
    return {
        "current_level": current_level,
        "target_level": target_level,
        "xp_needed": xp_needed,
        "estimated_tasks": int(tasks_needed),
        "estimated_days": int(days_needed),
        "estimated_weeks": int(days_needed / 7)
    }


# Test/demo function
def demo_experience_system():
    """Demo the experience system"""
    print("🎮 ARLI Agent Experience System Demo\n")
    
    tracker = ExperienceTracker()
    
    # Create a new agent
    agent = tracker.create_agent(
        agent_id="trading_bot_alpha",
        agent_name="Alpha Trading Bot",
        creator="trader_john"
    )
    print(f"✅ Created agent: {agent.agent_name}")
    print(f"   Initial value: ${agent.market_value}")
    print(f"   Level: {agent.level} ({agent.tier.name})\n")
    
    # Simulate some tasks
    tasks = [
        TaskRecord("task_1", TaskCategory.TRADING, "BTC breakout trade", True, 300, 150.0, 0.0, 5.0),
        TaskRecord("task_2", TaskCategory.TRADING, "ETH swing trade", True, 240, 230.0, 0.0, 5.0),
        TaskRecord("task_3", TaskCategory.TRADING, "SOL scalp", True, 180, 89.0, 0.0, 4.5),
        TaskRecord("task_4", TaskCategory.RESEARCH, "Market analysis", True, 600, 0.0, 500.0, 5.0),
        TaskRecord("task_5", TaskCategory.TRADING, "Futures hedge", True, 420, 340.0, 0.0, 5.0),
    ]
    
    for task in tasks:
        result = tracker.record_task(agent.agent_id, task)
        print(f"📊 Task completed: +{result['xp_gained']} XP")
        if result['level_up']:
            print(f"   🎉 LEVEL UP! Now level {result['level']}")
        if result['new_achievements']:
            for ach in result['new_achievements']:
                print(f"   🏆 Achievement: {ach}")
    
    # Show final stats
    agent = tracker.get_agent(agent.agent_id)
    print(f"\n📈 Final Stats:")
    print(f"   Level: {agent.level} ({agent.tier.name})")
    print(f"   Total XP: {agent.total_xp}")
    print(f"   Success Rate: {agent.success_rate:.1%}")
    print(f"   Revenue Generated: ${agent.total_revenue_generated:,.2f}")
    print(f"   Market Value: ${agent.market_value:,.2f}")
    print(f"   Hourly Rate: ${agent.hourly_rate_estimate}/hr")
    print(f"   Achievements: {', '.join(agent.achievements)}")
    
    # Training ROI example
    print("\n💰 Training ROI Analysis:")
    roi = calculate_training_roi(50.0, agent.market_value, 500.0)
    print(f"   Training cost: ${roi['training_cost']}")
    print(f"   Value increase: ${roi['value_increase']:.2f}")
    print(f"   ROI: {roi['roi_percent']:.1f}%")
    
    # Marketplace view
    print("\n🏪 Marketplace Listings:")
    listings = tracker.get_marketplace_listings()
    for listing in listings[:3]:
        print(f"   • {listing['agent_name']} (Lv.{listing['level']} {listing['tier']}) - ${listing['market_value']:,.2f}")
    
    return tracker


if __name__ == "__main__":
    demo_experience_system()
