# ARLI Research Framework v1.0

Autonomous research system for Truth Meter Limited. Collects, structures, and synthesizes intelligence across 5 research domains.

## Architecture

```
framework/
├── config.yaml           # Master configuration
├── domains/              # Domain definitions
│   ├── regulatory.md
│   ├── market_landscape.md
│   ├── technology.md
│   ├── customers.md
│   └── business_model.md
├── pipelines/
│   └── orchestrator.py   # Main research engine
├── templates/            # Report templates
└── outputs/              # Generated reports
```

## Quick Start

```bash
cd /home/paperclip/arli/research/framework
source ../prediction-markets-autoresearch/venv/bin/activate

# Run single domain
python pipelines/orchestrator.py --domain regulatory --cycles 3

# Run all domains
python pipelines/orchestrator.py --domain all --cycles 2

# Output goes to outputs/report_{domain}_{timestamp}.md
```

## Research Domains

| Domain | Priority | Refresh | Focus |
|--------|----------|---------|-------|
| **Regulatory** | P1 | 24h | SFC, MAS, VARA, CFTC licensing paths |
| **Business Model** | P1 | 24h | Pricing, unit economics, partnerships |
| **Market Landscape** | P2 | 48h | Competitors, TAM/SAM/SOM, positioning |
| **Customers** | P2 | 48h | ICPs, procurement, pain points |
| **Technology** | P3 | 72h | Oracles, infrastructure, security |

## How It Works

1. **Discover**: Search DuckDuckGo + trusted sources for URLs
2. **Fetch**: Direct HTTP → jina.ai fallback → Camoufox → Playwright
3. **Extract**: Pattern-based claim extraction with confidence scoring
4. **Cluster**: Keyword-based theme clustering
5. **Saturate**: Stop when >85% claims are redundant
6. **Report**: Markdown output with findings, themes, gaps, sources

## Integration with Data Room

Reports auto-copy to `../data-room/research/` for investor access:

```bash
# Add to cron for daily refresh
cronjob create --schedule "0 6 * * *" --prompt "Run ARLI research framework"
```

## Saturation Logic

The system tracks claim similarity across cycles. When >85% of new claims match existing ones, research stops for that domain. This prevents infinite loops and ensures efficient resource use.

## Output Format

Each report includes:
- **Executive Summary** — Top-level synthesis
- **Key Findings** — Ranked claims with confidence scores
- **Themes** — Auto-clustered by keyword (regulation, market, tech, business)
- **Research Gaps** — Unanswered questions from config
- **Sources** — Full URL list with fetched content archived

## Next Steps

1. Install dependencies: `pip install pyyaml duckduckgo-search requests beautifulsoup4`
2. Run first cycle: `python pipelines/orchestrator.py --domain regulatory`
3. Review output in `outputs/`
4. Schedule daily runs via cron
