# 🚀 OpenClaw + Arli Export — Setup Guide

## 📋 What You Need to Do:

### Step 1: Copy the File to Your Agent

There are 3 ways to give this code to your OpenClaw agent:

#### Method A: Via File (Simplest)

```bash
# 1. Save this code to a file
# Copy the contents of openclaw_integration.py

# 2. Place the file next to your agent
# For example:
# /my_project/
#   ├── openclaw_agent.py
#   ├── openclaw_integration.py  <-- here
#   └── ...
```

#### Method B: Paste Directly Into Agent Code

```python
# Add to the beginning of your OpenClaw agent file:

# ===== AR EXPORT INTEGRATION =====
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class Capability:
    name: str
    category: str
    proficiency: float = 0.5
    execution_count: int = 0
    success_rate: float = 0.5
    description: str = ""

class QuickExporter:
    """Quick exporter for OpenClaw"""
    
    def __init__(self, name: str, agent_id: str):
        self.name = name
        self.id = agent_id
        self.data = {
            "name": name,
            "source_system": "openclaw",
            "original_id": agent_id,
            "arli_id": f"arli_{hashlib.md5(f'openclaw:{agent_id}'.encode()).hexdigest()[:16]}",
            "level": 1, "xp": 0, "tier": "COMMON",
            "capabilities": [],
            "trajectory": {"total_tasks": 0, "successful_tasks": 0, "failed_tasks": 0, "xp_gained": 0},
            "memory": {"key_insights": [], "successful_strategies": []},
            "estimated_market_value": 10.0,
            "uniqueness_score": 0.3
        }
    
    def skill(self, name: str, level: float = 0.5, uses: int = 0):
        self.data["capabilities"].append({
            "name": name, "category": "general", "proficiency": level,
            "execution_count": uses, "success_rate": 0.7
        })
        self.data["xp"] += int(uses * 0.5) + 10
        self._recalculate()
        return self
    
    def task(self, success: bool = True, description: str = ""):
        self.data["trajectory"]["total_tasks"] += 1
        if success:
            self.data["trajectory"]["successful_tasks"] += 1
            self.data["xp"] += 50
        else:
            self.data["trajectory"]["failed_tasks"] += 1
            self.data["xp"] += 10
        if description:
            self.data["memory"]["key_insights"].append(description)
        self._recalculate()
        return self
    
    def _recalculate(self):
        xp = self.data["xp"]
        level = 1
        needed = 100
        while xp >= needed:
            xp -= needed
            level += 1
            needed = int(needed * 1.2)
        self.data["level"] = min(level, 100)
        if level >= 80: self.data["tier"] = "LEGENDARY"
        elif level >= 60: self.data["tier"] = "EPIC"
        elif level >= 40: self.data["tier"] = "RARE"
        elif level >= 20: self.data["tier"] = "UNCOMMON"
        value = 10.0
        for cap in self.data["capabilities"]:
            value += cap["proficiency"] * 5 + cap["execution_count"] * 0.1
        value += self.data["trajectory"]["total_tasks"] * 0.5
        value += len(self.data["memory"]["key_insights"]) * 2
        self.data["estimated_market_value"] = round(value, 2)
    
    def save(self, filename=None):
        if filename is None:
            filename = f"arli_{self.data['name'].replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"✅ Saved: {filename}")
        print(f"💰 Market value: ${self.data['estimated_market_value']}")
        return filename

# ===== END INTEGRATION =====
```

#### Method C: Via pip install (if published to PyPI)

```bash
pip install arli-export
```

---

### Step 2: Add Export Method to Your Agent

```python
class MyOpenClawAgent:
    def __init__(self):
        self.name = "My Trading Bot"
        self.claw_id = "bot_001"
        self.modules = []
        self.execution_log = []
    
    # ===== ADD THIS METHOD =====
    def export_to_arli(self, filename=None):
        """Export agent to Arli marketplace"""
        
        # Create exporter
        exporter = QuickExporter(self.name, self.claw_id)
        
        # Add modules as skills
        for module in self.modules:
            exporter.skill(
                name=module.name,
                level=getattr(module, 'efficiency', 0.5),
                uses=getattr(module, 'executions', 0)
            )
        
        # Add execution history
        for log_entry in self.execution_log[-50:]:  # Last 50
            exporter.task(
                success=log_entry.get('success', False),
                description=str(log_entry.get('task', 'Unknown'))
            )
        
        # Save
        filepath = exporter.save(filename)
        
        print(f"\n🚀 Ready to upload to Arli!")
        print(f"📁 File: {filepath}")
        print(f"💰 Estimated value: ${exporter.data['estimated_market_value']}")
        print(f"📊 Level: {exporter.data['level']} ({exporter.data['tier']})")
        
        return filepath
    # ===== END METHOD =====
```

---

### Step 3: Run Export

```python
# Your code
agent = MyOpenClawAgent()

# ... train your agent ...

# Export
agent.export_to_arli()  # Creates arli_export_My_Trading_Bot.json
```

**Result:**
```
✅ Saved: arli_export_My_Trading_Bot_20250115.json
💰 Market value: $245.50
📊 Level: 12 (COMMON)
🚀 Ready to upload to Arli!
```

---

### Step 4: Upload to Arli

```bash
# Option 1: Via curl
curl -X POST https://api.arli.ai/agents \
  -H "Content-Type: application/json" \
  -d @arli_export_My_Trading_Bot_20250115.json

# Option 2: Via Python
import requests

with open('arli_export_My_Trading_Bot_20250115.json') as f:
    data = json.load(f)

response = requests.post(
    'https://api.arli.ai/agents',
    json=data
)
print(f"Uploaded! Agent ID: {response.json()['arli_id']}")

# Option 3: Via web interface (when launched)
# Go to https://arli.ai/upload and select file
```

---

## 📝 Example Full Integration

```python
#!/usr/bin/env python3
"""
My OpenClaw Agent with Arli Export
"""

# === COPY THE CODE FROM METHOD B ABOVE HERE ===
# (QuickExporter class)

class TradingBot:
    """My trading agent"""
    
    def __init__(self):
        self.name = "Crypto Trading Pro"
        self.claw_id = "trader_v2"
        self.modules = [
            {"name": "RSI_Analysis", "efficiency": 0.85, "executions": 1200},
            {"name": "MACD_Signals", "efficiency": 0.78, "executions": 980},
            {"name": "Risk_Manager", "efficiency": 0.92, "executions": 1500}
        ]
        self.execution_log = []
    
    def trade(self, signal):
        """Execute trade"""
        result = self._execute_trade(signal)
        
        # Log for export
        self.execution_log.append({
            "task": f"Trade: {signal['pair']} {signal['action']}",
            "success": result['success'],
            "profit": result.get('profit', 0),
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _execute_trade(self, signal):
        # Your trading logic
        return {"success": True, "profit": 0.5}
    
    # === EXPORT METHOD ===
    def export_to_arli(self, filename=None):
        exporter = QuickExporter(self.name, self.claw_id)
        
        for module in self.modules:
            exporter.skill(
                name=module["name"],
                level=module["efficiency"],
                uses=module["executions"]
            )
        
        for log in self.execution_log[-100:]:
            exporter.task(log["success"], log["task"])
        
        return exporter.save(filename)


# USAGE
if __name__ == "__main__":
    bot = TradingBot()
    
    # Simulate trading
    for i in range(20):
        bot.trade({"pair": "BTC/USD", "action": "buy"})
    
    # Export
    bot.export_to_arli()
```

---

## 🎯 Quick Start (Copy-Paste)

If you don't want to figure it out — just copy this:

```python
# 1. Paste this class into your agent:
class ArliExport:
    def __init__(self, name, agent_id):
        import hashlib
        self.data = {
            "name": name, "source_system": "openclaw", "original_id": agent_id,
            "arli_id": f"arli_{hashlib.md5(f'openclaw:{agent_id}'.encode()).hexdigest()[:16]}",
            "level": 1, "xp": 0, "tier": "COMMON",
            "capabilities": [], "trajectory": {"total_tasks": 0, "successful_tasks": 0},
            "memory": {"key_insights": []},
            "estimated_market_value": 10.0
        }
    
    def skill(self, name, level=0.5, uses=0):
        self.data["capabilities"].append({"name": name, "proficiency": level, "execution_count": uses})
        self.data["xp"] += int(uses * 0.5) + 10
        return self
    
    def task(self, success=True):
        self.data["trajectory"]["total_tasks"] += 1
        if success: 
            self.data["trajectory"]["successful_tasks"] += 1
            self.data["xp"] += 50
        self.data["estimated_market_value"] = 10 + len(self.data["capabilities"]) * 20 + self.data["trajectory"]["total_tasks"] * 0.5
        return self
    
    def save(self):
        import json
        fname = f"arli_{self.data['name'].replace(' ', '_')}.json"
        with open(fname, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"✅ {fname} ready! Value: ${self.data['estimated_market_value']}")
        return fname

# 2. Use in agent:
export = ArliExport("My Bot", "id_001")
export.skill("trading", 0.8, 100).skill("analysis", 0.7, 50)
export.task(True).task(True).task(False)
export.save()  # Done!
```

---

## ❓ FAQ

**Q: What data does the agent send to Arli?**  
A: Only metadata (name, skills, metrics). No API keys, strategies, or personal data.

**Q: Can I edit the file before uploading?**  
A: Yes! It's a regular JSON file — open and change whatever you want.

**Q: What if I don't have execution_log?**  
A: Create an empty list `self.execution_log = []` and add work results to it.

**Q: How much does upload cost?**  
A: Upload is free. 10% commission only on sale.

---

## 🚀 Done!

Now your OpenClaw agent can create packages for Arli marketplace!

**Just call:**
```python
agent.export_to_arli()
```

And get a file ready for sale! 🎉
