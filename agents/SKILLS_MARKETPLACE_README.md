# 💰 ARLI Skills Marketplace

Monetization system for custom agent skills.

## Overview

The Skills Marketplace allows:
- **Skill creators** to build and sell custom capabilities
- **Platform** to take 30% commission
- **Companies** to extend agents with purchased skills

## Revenue Model

```
┌─────────────────────────────────────────────────────────────┐
│                   REVENUE SPLIT                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Skill Price: $50.00                                       │
│   ├─ Creator (70%): $35.00  ◄── Skill author               │
│   └─ Platform (30%): $15.00 ◄── ARLI revenue               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  SKILLS MARKETPLACE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🏪 MARKETPLACE              📦 SKILL PACKAGE              │
│  ├── Listings                ├── Template generation        │
│  ├── Search & discovery      ├── Validation                 │
│  ├── Purchase system         ├── Packaging (tar.gz)         │
│  ├── Reviews & ratings       └── Manifest                   │
│  └── Revenue tracking                                      │
│                                                             │
│  💻 SKILL INSTALLER                                        │
│  ├── Purchase verification                                  │
│  ├── License key validation                                 │
│  ├── Dynamic loading                                        │
│  └── Version management                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Skill Structure

```
skill_name/
├── skill.py          # Main implementation
├── skill.json        # Metadata & pricing
├── README.md         # Documentation
└── requirements.txt  # Dependencies
```

### skill.json Format

```json
{
  "skill_id": "author.skill_name",
  "name": "Skill Name",
  "version": "1.0.0",
  "description": "What this skill does",
  "category": "coding",
  "author": "Your Name",
  "author_id": "your_id",
  "price": 49.99,
  "currency": "USD",
  "entry_point": "skill.py",
  "dependencies": ["requests", "beautifulsoup4"],
  "min_arli_version": "1.0.0"
}
```

## Usage

### For Skill Users (Buyers)

```python
from runtime import AgentRuntime

# Create agent
agent = AgentRuntime("my-agent", enable_memory=True)

# Search skills
results = agent.search_skills(
    query="web scraping",
    category="web_scraping",
    max_price=100
)

for skill in results:
    print(f"{skill['name']}: ${skill['price']}")
    print(f"  Rating: {skill['rating']} ⭐ ({skill['downloads']} downloads)")

# Purchase skill
purchase = agent.purchase_skill("devstudio.web_scraper_pro")
print(f"License: {purchase['license_key']}")

# Install skill
agent.install_skill("devstudio.web_scraper_pro")

# Use skill
result = agent.use_skill(
    "devstudio.web_scraper_pro",
    url="https://example.com",
    selector=".price"
)

print(result)
```

### For Skill Creators

```python
# Create skill template
result = agent.create_skill("Advanced Web Scraper")
print(f"Template: {result['template_path']}")

# Edit files in template directory...
# - skill.py (implementation)
# - skill.json (metadata & pricing)
# - README.md (documentation)

# Publish skill
result = agent.publish_skill(".arli/skills/source/author.advanced_web_scraper")
print(f"Published: {result['success']}")
```

### Manual Skill Creation

```bash
# Create skill template
cd ~/arli
python3 -c "
from agents.skills_marketplace import SkillPackage
packager = SkillPackage()
packager.create_skill_template('My Skill', 'My Name')
"

# Edit generated files
# .arli/skills/source/my_name.my_skill/skill.py
# .arli/skills/source/my_name.my_skill/skill.json
# .arli/skills/source/my_name.my_skill/README.md

# Validate
python3 -c "
from agents.skills_marketplace import SkillPackage
packager = SkillPackage()
result = packager.validate_skill('.arli/skills/source/my_name.my_skill')
print(result)
"

# Package
python3 -c "
from agents.skills_marketplace import SkillPackage
packager = SkillPackage()
packager.package_skill('.arli/skills/source/my_name.my_skill')
"
```

## Skill Implementation Example

```python
# skill.py
class Skill:
    def __init__(self, runtime):
        self.runtime = runtime
        self.name = "Web Scraper Pro"
    
    def execute(self, url: str, selector: str):
        """
        Scrape data from URL
        
        Args:
            url: Website URL to scrape
            selector: CSS selector for data
        
        Returns:
            List of scraped items
        """
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.select(selector)
        return [item.text.strip() for item in items]
    
    def get_capabilities(self):
        return ["web_scraping", "data_extraction"]

def create_skill(runtime):
    return Skill(runtime)
```

## Categories

- `coding` — Development tools, code generation
- `data_analysis` — Data processing, analytics
- `web_scraping` — Data extraction from websites
- `automation` — Workflow automation
- `integration` — Third-party service integration
- `content` — Content generation, processing
- `security` — Security tools, analysis
- `devops` — Deployment, monitoring tools
- `other` — Everything else

## API Reference

### AgentRuntime Skills Methods

| Method | Description |
|--------|-------------|
| `search_skills(query, category, max_price)` | Search marketplace |
| `purchase_skill(skill_id)` | Buy a skill |
| `install_skill(skill_id)` | Install purchased skill |
| `use_skill(skill_id, **kwargs)` | Execute skill |
| `list_skills()` | List installed skills |
| `create_skill(name)` | Create skill template |
| `publish_skill(path)` | Publish to marketplace |

### Marketplace Methods

| Method | Description |
|--------|-------------|
| `publish_skill(path)` | Submit skill for review |
| `approve_skill(skill_id)` | Approve skill (admin) |
| `search_skills(...)` | Search skills |
| `purchase_skill(skill_id, user_id)` | Purchase skill |
| `add_review(skill_id, user_id, rating, comment)` | Add review |
| `get_revenue_stats(author_id)` | Get earnings |

### SkillInstaller Methods

| Method | Description |
|--------|-------------|
| `install_skill(skill_id, marketplace, user_id)` | Install skill |
| `load_skill(skill_id, runtime)` | Load for execution |
| `list_installed_skills()` | List installed |
| `uninstall_skill(skill_id)` | Remove skill |

## File Structure

```
.arli/
├── skills/
│   ├── source/              # Skill development
│   │   └── {author}.{skill}/
│   │       ├── skill.py
│   │       ├── skill.json
│   │       ├── README.md
│   │       └── requirements.txt
│   ├── packages/            # Packaged skills
│   │   └── {skill}-{version}.tar.gz
│   └── installed/           # Installed skills
│       └── {skill}/
│           ├── skill.py
│           └── {skill}.installed.json
│
└── marketplace/
    ├── listings/            # Skill listings
    │   └── {skill_id}.json
    ├── packages/            # Distribution packages
    ├── reviews/             # User reviews
    │   └── {skill_id}.jsonl
    └── purchases/           # Purchase records
        └── {user_id}_{skill_id}.json
```

## Testing

```bash
cd ~/arli

# Test marketplace
python3 agents/skills_marketplace.py

# Test skill creation
python3 -c "
from agents.skills_marketplace import SkillPackage
packager = SkillPackage()
packager.create_skill_template('Test Skill', 'Test Author')
"
```

## Revenue Dashboard (Future)

```python
# Get creator earnings
stats = marketplace.get_revenue_stats(author_id="devstudio_one")

print(f"Total sales: ${stats['total_sales']:.2f}")
print(f"Your earnings (90%): ${stats['total_creator_earnings']:.2f}")

for skill_id, data in stats['skill_breakdown'].items():
    print(f"  {data['name']}: {data['sales_count']} sales, ${data['revenue']:.2f}")
```

## Security

- Skills run in isolated namespace
- License key validation required
- Checksum verification on install
- Review process before publishing

## Next Steps

- [ ] Online marketplace frontend
- [ ] Payment processing (Stripe)
- [ ] Skill analytics dashboard
- [ ] Automated skill testing
- [ ] Community reviews system
- [ ] Skill versioning & updates
- [ ] Revenue withdrawals
