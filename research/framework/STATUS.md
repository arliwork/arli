# ARLI Research Framework — Build Status

**Built:** April 23, 2026  
**Status:** PRODUCTION READY  
**Next Run:** Daily at 06:00 UTC (cron job: `arli-research-daily`)

---

## What Was Built

### 1. Configuration (`config.yaml`)
- 5 research domains with priorities, refresh intervals, key questions
- Source discovery via DuckDuckGo + trusted domains
- Extraction pipeline config (jina, firecrawl, direct HTTP, Camoufox)
- Saturation threshold: 85%

### 2. Domain Definitions (`domains/`)
| Domain | Priority | Refresh | Key Output |
|--------|----------|---------|------------|
| Regulatory | P1 | 24h | Licensing paths, compliance costs |
| Business Model | P1 | 24h | Pricing tiers, unit economics |
| Market Landscape | P2 | 48h | Competitor profiles, TAM/SAM/SOM |
| Customers | P2 | 48h | ICPs, procurement maps |
| Technology | P3 | 72h | Architecture decisions, vendor comparisons |

### 3. Orchestrator (`pipelines/orchestrator.py`)
- **Discover**: DuckDuckGo search + trusted sources
- **Fetch**: Direct HTTP → jina.ai → Camoufox → Playwright
- **Extract**: Pattern-based claim extraction with confidence scoring
- **Cluster**: Keyword-based theme grouping
- **Saturate**: Auto-stop at 85% claim redundancy
- **Report**: Markdown with executive summary, findings, themes, gaps

### 4. Data-Room Sync (`pipelines/sync_to_dataroom.py`)
- Auto-copies latest 10 reports to `../data-room/research/`
- Generates `index.md` for navigation

### 5. Automation (`run.sh` + cron)
- Master script: runs all domains + syncs
- Cron: Daily at 06:00 UTC
- Logs to `/tmp/arli-research.log`

---

## File Structure

```
framework/
├── config.yaml
├── README.md
├── STATUS.md
├── run.sh                    ← Master run script
├── domains/
│   ├── regulatory.md
│   ├── market_landscape.md
│   ├── technology.md
│   ├── customers.md
│   └── business_model.md
├── pipelines/
│   ├── orchestrator.py       ← Core engine
│   └── sync_to_dataroom.py   ← Data-room integration
├── templates/                ← (ready for custom templates)
└── outputs/                  ← Generated reports
```

---

## How to Run Manually

```bash
cd /home/paperclip/arli/research/framework
source ../prediction-markets-autoresearch/venv/bin/activate

# Single domain, quick test
python pipelines/orchestrator.py --domain regulatory --cycles 1

# All domains, full run
python pipelines/orchestrator.py --domain all --cycles 2

# Or use the master script
./run.sh
```

---

## What Eddy's Answers Would Add (When They Arrive)

| Question | Framework Handles Now | Eddy Can Refine |
|----------|----------------------|-----------------|
| Exact pricing tiers | Benchmarked from expert networks | His target ACV |
| Geographic priority | All 5 jurisdictions tracked | His preference |
| Tech stack | Oracle/vendor comparison | His ICP preference |
| Customer segments | Hedge fund, family office, crypto firm | His specific targets |
| Partnership model | B2B subscription + transaction fee | His actual deals |

**We do NOT need to wait for Eddy. The framework runs autonomously and his answers will refine outputs, not block them.**

---

## Next Actions

1. ✅ Install missing deps: `pip install pyyaml`
2. ✅ Run first test cycle: `python pipelines/orchestrator.py --domain regulatory`
3. ✅ Review report in `outputs/`
4. ✅ Verify cron job: `hermes cron list`
5. ⬜ When Eddy responds: update `config.yaml` key_questions with his answers
6. ⬜ When HKSTP application starts: add `hkstp.md` domain
