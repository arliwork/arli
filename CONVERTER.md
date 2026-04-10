# Universal Agent Converter

Converts agents from any system to Arli universal format.

## 🎯 What It Does

1. **Extracts** valuable data from agents of any system
2. **Analyzes** learning curve and experience
3. **Packages** into universal format
4. **Estimates** market value

## 📦 Supported Systems

| System | Status | Conversion Quality |
|--------|--------|-------------------|
| Hermes | ✅ Ready | High |
| OpenClaw | ✅ Ready | Medium |
| AutoGen | 🚧 Planned | - |
| LangChain | 🚧 Planned | - |
| Custom | 🚧 Planned | - |

## 🚀 Usage

### CLI

```bash
# Convert single agent
python tools/convert_agent.py my_agent.json

# Save result
python tools/convert_agent.py my_agent.json -o converted.json

# JSON format
python tools/convert_agent.py my_agent.json -f json

# Import to Arli
python tools/convert_agent.py my_agent.json --import-to-arli
```

### API

```bash
# Convert via API
curl -X POST http://localhost:8000/convert/agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_data": { ... }
  }'
```

### Python

```python
from agent_converter import AgentConverter

converter = AgentConverter()
package = converter.convert(my_agent_data)

print(f"Level: {package.level}")
print(f"Value: ${package.estimated_market_value}")
print(f"Capabilities: {len(package.capabilities)}")
```

## 📊 What Gets Extracted

### Capabilities
- Name and category
- Proficiency level (0-100%)
- Execution count
- Success rate
- Average execution time

### Learning Trajectory
- Total task count
- Successful/failed tasks
- XP earned
- Level history
- Acquired skills
- Behavioral patterns

### Memory
- Key insights
- Successful strategies
- Preferred tools
- Failure patterns
- Context preferences

## 💰 Value Estimation

Pricing algorithm considers:
- Agent level and experience
- Skill quantity and quality
- Insight uniqueness
- Task completion success rate
- Skill combination rarity

## 🔌 Adding New Adapter

```python
from agent_converter import BaseAgentAdapter

class MySystemAdapter(BaseAgentAdapter):
    def __init__(self):
        super().__init__("mysystem")
    
    def can_parse(self, agent_data):
        # Check if this is our format
        return "mysystem_id" in agent_data
    
    def parse_capabilities(self, agent_data):
        # Extract capabilities
        return [...]
    
    def parse_trajectory(self, agent_data):
        # Extract trajectory
        return LearningTrajectory(...)
    
    def parse_memory(self, agent_data):
        # Extract memory
        return AgentMemory(...)

# Register
converter.register_adapter(MySystemAdapter())
```

## 📁 Output Format

```json
{
  "name": "My Trading Agent",
  "source_system": "hermes",
  "arli_id": "arli_a1b2c3d4...",
  "level": 15,
  "tier": "RARE",
  "xp": 2450,
  "capabilities": [
    {
      "name": "binance_trading",
      "category": "trading",
      "proficiency": 0.85,
      "execution_count": 342,
      "success_rate": 0.78
    }
  ],
  "trajectory": {
    "total_tasks": 500,
    "successful_tasks": 390,
    "xp_gained": 2450
  },
  "memory": {
    "key_insights": ["Market trends..."],
    "preferred_tools": ["binance_api", "ta_lib"],
    "successful_strategies": ["Buy on dip..."]
  },
  "estimated_market_value": 245.50,
  "uniqueness_score": 0.73
}
```
