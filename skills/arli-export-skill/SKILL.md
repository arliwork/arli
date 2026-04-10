# Arli Export Skill

Universal skill for exporting agents to Arli Marketplace format. Any agent (Hermes, OpenClaw, AutoGen, etc.) can use this skill to create a data package ready for sale.

## 🎯 What It Does

1. **Scans** agent data (memory, skills, history)
2. **Extracts** valuable metrics (XP, successes, insights)
3. **Packages** into standard Arli JSON
4. **Estimates** market value

## 📦 Installation

### For Hermes Agent:

```bash
# Copy skill to skills folder
cp -r arli-export-skill ~/.hermes/skills/

# Or via Hermes CLI
hermes skills install arli-export
```

### For Other Systems:

Copy the `export_adapter.py` file into your project and use as a module.

## 🚀 Usage

### Option 1: Via Command

```bash
# Hermes
/hermes export-to-arli

# Result: arli_package_2025-01-15.json
```

### Option 2: Programmatically

```python
from arli_export import ArliExporter

# Create exporter
exporter = ArliExporter(
    agent_name="My Trading Bot",
    agent_id="bot_001",
    source_system="hermes"  # or "openclaw", "autogen", etc.
)

# Add data
exporter.add_skill(
    name="crypto_trading",
    category="trading",
    proficiency=0.85,
    executions=1500,
    success_rate=0.72
)

exporter.add_session(
    task="Executed buy order",
    success=True,
    xp_earned=50
)

exporter.add_insight(
    content="BTC rises on Mondays",
    source="pattern_analysis"
)

# Generate package
package = exporter.export()

# Save
with open("my_agent_arli.json", "w") as f:
    json.dump(package, f, indent=2)
```

### Option 3: Auto-Scan (Hermes)

```python
# Automatically scans fabric, sessions, skills
from arli_export import HermesAutoScanner

scanner = HermesAutoScanner()
package = scanner.scan_and_export(
    fabric_path="~/.hermes/fabric/",
    sessions_path="~/.hermes/sessions/"
)

print(f"Agent ready for sale! Value: ${package['estimated_market_value']}")
```

## 📊 What Gets Exported

### Required Fields:
- `name` — agent name
- `source_system` — source system (hermes, openclaw, etc.)
- `capabilities` — list of skills

### Optional Fields:
- `session_history` — task history
- `insights` — key insights and strategies
- `preferences` — context preferences
- `performance_metrics` — performance metrics

### Auto-Generated:
- `arli_id` — unique Arli ID
- `level` — level (calculated from XP)
- `xp` — total experience
- `tier` — tier (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY)
- `estimated_market_value` — price estimate ($)
- `uniqueness_score` — uniqueness (0-100%)

## 💰 Pricing Algorithm

```python
base_value = 10

# For skills
for skill in capabilities:
    value += skill.proficiency * 5
    value += skill.executions * 0.1

# For experience
value += total_tasks * 0.5
value += success_rate * 50

# For uniqueness
value += unique_insights * 2
value += successful_strategies * 3
```

## 🔌 Arli Integration

After export:

```bash
# Upload to marketplace
arli upload my_agent_arli.json

# Or via API
curl -X POST https://api.arli.ai/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d @my_agent_arli.json
```

## 📁 Package Structure

```json
{
  "name": "Crypto Trading Bot",
  "source_system": "hermes",
  "arli_id": "arli_a1b2c3d4...",
  "level": 15,
  "tier": "RARE",
  "xp": 12500,
  "capabilities": [...],
  "trajectory": {...},
  "memory": {...},
  "estimated_market_value": 450.00,
  "uniqueness_score": 0.78
}
```

## 🛠️ For Developers

### Add Support for New System:

```python
from arli_export import BaseExporter

class MySystemExporter(BaseExporter):
    def scan_agent(self, agent_instance):
        # Your scanning logic
        self.add_skill(...)
        self.add_session(...)
        return self.export()
```

## 🔒 Security

- ❌ **NO** API keys exported
- ❌ **NO** passwords exported
- ❌ **NO** personal user data exported
- ✅ Only metadata and metrics exported

## 📄 License

MIT — free to use in any projects.
