#!/usr/bin/env python3
"""
OpenClaw → Arli Export (Ultra-Simple Version)
Just copy this file next to your agent and use!
"""

import json
import hashlib

class ArliExport:
    """
    Simplified exporter for OpenClaw agents
    
    Usage:
        exp = ArliExport("My Bot", "bot_001")
        exp.skill("trading", level=0.8, uses=150)
        exp.task(success=True)
        exp.save()  # Creates arli_My_Bot.json
    """
    
    def __init__(self, agent_name: str, agent_id: str):
        self.name = agent_name
        self.id = agent_id
        
        # Generate Arli ID
        hash_str = hashlib.md5(f"openclaw:{agent_id}".encode()).hexdigest()[:16]
        
        self.data = {
            "name": agent_name,
            "source_system": "openclaw",
            "original_id": agent_id,
            "arli_id": f"arli_{hash_str}",
            "level": 1,
            "xp": 0,
            "tier": "COMMON",
            "capabilities": [],
            "trajectory": {
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "xp_gained": 0
            },
            "memory": {
                "key_insights": [],
                "successful_strategies": []
            },
            "estimated_market_value": 10.0,
            "uniqueness_score": 0.3,
            "created_at": "2025-01-15T10:00:00Z"
        }
    
    def skill(self, name: str, level: float = 0.5, uses: int = 0):
        """Add a skill
        
        Args:
            name: Skill name
            level: Proficiency level (0.0 - 1.0)
            uses: How many times it was used
        """
        self.data["capabilities"].append({
            "name": name,
            "category": "general",
            "proficiency": level,
            "execution_count": uses,
            "success_rate": 0.7
        })
        self.data["xp"] += int(uses * 0.5) + 10
        self._update()
        return self
    
    def task(self, success: bool = True, description: str = ""):
        """Add a completed task
        
        Args:
            success: Whether it was successful
            description: Task description (optional)
        """
        self.data["trajectory"]["total_tasks"] += 1
        if success:
            self.data["trajectory"]["successful_tasks"] += 1
            self.data["xp"] += 50
        else:
            self.data["trajectory"]["failed_tasks"] += 1
            self.data["xp"] += 10
        
        if description:
            self.data["memory"]["key_insights"].append(description)
        
        self._update()
        return self
    
    def insight(self, text: str):
        """Add an insight/strategy"""
        self.data["memory"]["successful_strategies"].append(text)
        self._update()
        return self
    
    def _update(self):
        """Recalculate level and value"""
        # Recalculate level
        xp = self.data["xp"]
        level = 1
        needed = 100
        while xp >= needed:
            xp -= needed
            level += 1
            needed = int(needed * 1.2)
        self.data["level"] = min(level, 100)
        
        # Determine tier
        if level >= 80:
            self.data["tier"] = "LEGENDARY"
        elif level >= 60:
            self.data["tier"] = "EPIC"
        elif level >= 40:
            self.data["tier"] = "RARE"
        elif level >= 20:
            self.data["tier"] = "UNCOMMON"
        
        # Recalculate value
        value = 10.0
        for cap in self.data["capabilities"]:
            value += cap["proficiency"] * 5
            value += cap["execution_count"] * 0.1
        value += self.data["trajectory"]["total_tasks"] * 0.5
        
        # For uniqueness
        value += len(self.data["memory"]["key_insights"]) * 2
        value += len(self.data["memory"]["successful_strategies"]) * 3
        
        self.data["estimated_market_value"] = round(value, 2)
        self.data["uniqueness_score"] = min(0.3 + len(self.data["capabilities"]) * 0.1, 1.0)
    
    def save(self, filename: str = None) -> str:
        """Save to JSON file
        
        Returns:
            Path to created file
        """
        if filename is None:
            safe_name = self.name.replace(" ", "_").replace("/", "_")
            filename = f"arli_{safe_name}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Arli export created: {filename}")
        print(f"📊 Level: {self.data['level']} ({self.data['tier']})")
        print(f"💰 Market value: ${self.data['estimated_market_value']}")
        print(f"🦄 Uniqueness: {self.data['uniqueness_score']:.0%}")
        
        return filename
    
    def preview(self):
        """Show preview without saving"""
        print("\n" + "="*50)
        print(f"📦 {self.name}")
        print("="*50)
        print(f"Level: {self.data['level']} ({self.data['tier']})")
        print(f"XP: {self.data['xp']}")
        print(f"Skills: {len(self.data['capabilities'])}")
        for cap in self.data['capabilities'][:3]:
            print(f"  • {cap['name']}: {cap['proficiency']:.0%}")
        print(f"Tasks: {self.data['trajectory']['total_tasks']}")
        print(f"Value: ${self.data['estimated_market_value']}")
        print("="*50)
        return self


# ===== USAGE EXAMPLE =====
if __name__ == "__main__":
    print("🚀 OpenClaw → Arli Export Demo\n")
    
    # Create export
    exp = ArliExport("Trading Bot Pro", "claw_trader_v3")
    
    # Add skills
    exp.skill("BTC Trading", level=0.85, uses=1200)
    exp.skill("ETH Analysis", level=0.78, uses=890)
    exp.skill("Risk Management", level=0.92, uses=1500)
    
    # Add tasks
    exp.task(True, "Bought BTC at support")
    exp.task(True, "Sold ETH at resistance")
    exp.task(True, "DCA position opened")
    exp.task(False, "Stop loss hit")
    exp.task(True, "Swing trade profit +5%")
    
    # Add insights
    exp.insight("BTC pumps after funding turns negative")
    exp.insight("ETH follows BTC with 2-3h delay")
    
    # Preview
    exp.preview()
    
    # Save
    exp.save()
    
    print("\n📤 Upload to Arli:")
    print("   curl -X POST https://api.arli.ai/agents -d @arli_Trading_Bot_Pro.json")


# ===== AGENT INTEGRATION =====
"""
PASTE THIS INTO YOUR OPENCLAW AGENT:

1. Copy the ArliExport class above

2. Add method to your agent:

    def export_to_arli(self):
        exp = ArliExport(self.name, self.id)
        
        # Add your modules as skills
        for module in self.modules:
            exp.skill(
                name=module.name,
                level=getattr(module, 'efficiency', 0.5),
                uses=getattr(module, 'executions', 0)
            )
        
        # Add history as tasks
        for log in self.execution_log[-50:]:
            exp.task(
                success=log.get('success', True),
                description=log.get('task', '')
            )
        
        return exp.save()  # Done!

3. Use:
    agent = MyOpenClawAgent()
    # ... agent working ...
    agent.export_to_arli()  # Ready!
"""
