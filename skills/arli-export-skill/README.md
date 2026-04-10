# 🚀 Arli Export Skill

Universal tool for exporting any AI agent to Arli Marketplace format.

## ⚡ Quick Start

```bash
# Installation
pip install arli-export

# Or copy files
wget https://arli.ai/skills/export_adapter.py
```

## 📦 Supported Systems

- ✅ **Hermes** — full auto-integration
- ✅ **OpenClaw** — via SDK
- ✅ **AutoGen** — via Python API
- ✅ **LangChain** — via callbacks
- ✅ **LlamaIndex** — via metadata
- ✅ **Custom** — manual export

## 🎯 Usage

### 1. For Hermes (Auto-Scan)

```bash
# In Hermes CLI
/export-to-arli

# Result: arli_export_Hermes_Agent_20250115.json
```

### 2. For Any System (Python)

```python
from arli_export import ArliExporter

# Create exporter
exporter = ArliExporter(
    agent_name="My Trading Bot",
    agent_id="bot_001",
    source_system="openclaw"
)

# Add data
exporter.add_capability(
    name="crypto_trading",
    category="trading",
    proficiency=0.85,
    execution_count=1500,
    success_rate=0.72
)

exporter.add_session(
    task="Executed buy order",
    success=True,
    xp_earned=50
)

# Export
package = exporter.export()  # dict
filepath = exporter.save()   # saves to JSON

print(f"Ready for Arli! Value: ${package['estimated_market_value']}")
```

### 3. CLI

```bash
# Export with auto-scanning
python export_adapter.py --name "My Agent" --id "001" --hermes

# Or manual
python export_adapter.py --name "My Agent" --id "001" --system custom
```

## 📊 What Gets Exported

| Data | Description | Result |
|------|-------------|--------|
| `capabilities` | Skills and abilities | Mastery level, usage count |
| `sessions` | Task history | XP, success/failure |
| `insights` | Insights and strategies | Agent's unique knowledge |
| `preferences` | Preferences | Work context |

**Auto-generated:**
- `level` — agent level (1-100)
- `xp` — total experience
- `tier` — tier (COMMON → LEGENDARY)
- `estimated_market_value` — price estimate ($)
- `uniqueness_score` — uniqueness (%)

## 💰 Pricing Algorithm

```
Base value: $10
+ For skills: proficiency × $5
+ For experience: executions × $0.10
+ For success: success_rate × $50
+ For insights: count × $2
= Final value
```

## 🔌 System Integrations

### OpenClaw

```python
# In OpenClaw agent code
from arli_export import ArliExporter

class MyClawAgent:
    def export_to_arli(self):
        exporter = ArliExporter(
            agent_name=self.name,
            agent_id=self.claw_id,
            source_system="openclaw"
        )
        
        # Add modules as capabilities
        for module in self.modules:
            exporter.add_capability(
                name=module.name,
                category=module.type,
                proficiency=module.efficiency,
                execution_count=module.executions
            )
        
        return exporter.save()  # ready to sell!
```

### AutoGen

```python
from arli_export import ArliExporter

# After session
def on_session_end(agent, sessions):
    exporter = ArliExporter(
        agent_name=agent.name,
        agent_id=str(agent.id),
        source_system="autogen"
    )
    
    for s in sessions:
        exporter.add_session(
            task=s.task,
            success=s.success,
            xp_earned=s.xp
        )
    
    exporter.save()
```

### LangChain

```python
from langchain.callbacks.base import BaseCallbackHandler
from arli_export import ArliExporter

class ArliExportCallback(BaseCallbackHandler):
    def __init__(self, agent_name, agent_id):
        self.exporter = ArliExporter(
            agent_name=agent_name,
            agent_id=agent_id,
            source_system="langchain"
        )
    
    def on_tool_end(self, tool_name, output, **kwargs):
        self.exporter.add_capability(
            name=tool_name,
            category="tool",
            proficiency=0.8
        )
    
    def on_chain_end(self, outputs, **kwargs):
        self.exporter.save()
```

## 📤 Upload to Arli

```bash
# Via CLI
arli upload my_agent.json

# Via API
curl -X POST https://api.arli.ai/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d @my_agent.json

# Via Python
import requests

with open('my_agent.json') as f:
    package = json.load(f)

response = requests.post(
    'https://api.arli.ai/agents',
    json=package,
    headers={'Authorization': 'Bearer TOKEN'}
)
```

## 🔒 Security

- ❌ **NO** API keys exported
- ❌ **NO** passwords exported
- ❌ **NO** personal data exported
- ✅ Only metadata and metrics

## 📄 Output File Format

```json
{
  "name": "Crypto Trading Bot",
  "source_system": "openclaw",
  "arli_id": "arli_a1b2c3d4...",
  "level": 15,
  "tier": "RARE",
  "xp": 12500,
  "capabilities": [...],
  "trajectory": {
    "total_tasks": 500,
    "successful_tasks": 390,
    "xp_gained": 12500
  },
  "memory": {
    "key_insights": [...],
    "successful_strategies": [...]
  },
  "estimated_market_value": 450.00,
  "uniqueness_score": 0.78
}
```

## 🤝 Support

- 📖 Docs: https://docs.arli.ai/export
- 💬 Discord: https://discord.gg/arli
- 🐛 Issues: https://github.com/arliwork/arli/issues

## 📜 License

MIT — free to use in any project.
