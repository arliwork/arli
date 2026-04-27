"""
ARLI Research Framework Orchestrator
Production-grade autonomous research system.

Usage:
    cd /home/paperclip/arli/research/framework
    source ../prediction-markets-autoresearch/venv/bin/activate
    python pipelines/orchestrator.py [--domain regulatory] [--cycles 3]
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "prediction-markets-autoresearch"))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FRAMEWORK_DIR = Path(__file__).parent.parent
CONFIG_PATH = FRAMEWORK_DIR / "config.yaml"
OUTPUT_DIR = FRAMEWORK_DIR / "outputs"
SOURCES_DIR = FRAMEWORK_DIR / "sources"
DOMAINS_DIR = FRAMEWORK_DIR / "domains"

# Ensure dirs exist
OUTPUT_DIR.mkdir(exist_ok=True)
SOURCES_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

class Logger:
    def __init__(self, name: str):
        self.name = name
        self.start = time.time()

    def _fmt(self, level: str, msg: str) -> str:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        elapsed = time.time() - self.start
        return f"[{ts}] [{level}] [{self.name}] [{elapsed:.1f}s] {msg}"

    def info(self, msg: str):
        print(self._fmt("INFO", msg), flush=True)

    def warn(self, msg: str):
        print(self._fmt("WARN", msg), flush=True)

    def error(self, msg: str):
        print(self._fmt("ERROR", msg), flush=True)

# ---------------------------------------------------------------------------
# Config Loader
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Load framework configuration."""
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

# ---------------------------------------------------------------------------
# Source Fetcher (Minimal — uses direct HTTP + jina.ai fallback)
# ---------------------------------------------------------------------------

class SourceFetcher:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.session = self._init_session()

    def _init_session(self):
        import requests
        s = requests.Session()
        s.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        return s

    def fetch(self, url: str, timeout: int = 15) -> Optional[str]:
        """Fetch URL content with fallback chain."""
        # 1. Try direct HTTP
        try:
            r = self.session.get(url, timeout=timeout, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 500:
                self.logger.info(f"FETCH_OK_DIRECT {url}")
                return r.text
        except Exception as e:
            self.logger.warn(f"FETCH_FAIL_DIRECT {url}: {e}")

        # 2. Try jina.ai summarizer
        try:
            jina_url = f"https://r.jina.ai/http://{urllib.parse.urlparse(url).netloc}{urllib.parse.urlparse(url).path}"
            r = self.session.get(jina_url, timeout=timeout)
            if r.status_code == 200 and len(r.text) > 200:
                self.logger.info(f"FETCH_OK_JINA {url}")
                return r.text
        except Exception as e:
            self.logger.warn(f"FETCH_FAIL_JINA {url}: {e}")

        return None

# ---------------------------------------------------------------------------
# Claim Extractor
# ---------------------------------------------------------------------------

class ClaimExtractor:
    """Extract structured claims from raw text with HTML cleanup and quality filtering."""

    CLAIM_PATTERNS = [
        re.compile(r'([A-Z][^.]{10,150}\b(?:is|are|will|can|has|have|had|does|do|did)\b[^.]{5,200}\.)'),
        re.compile(r'(According to [^,]+, [^.]{20,300}\.)'),
        re.compile(r'([^\n]{20,200}(?:reported|announced|stated|confirmed|revealed|found|discovered)[^\n]{10,200}\.)'),
    ]

    # HTML / metadata artifacts to reject
    _HTML_JUNK_RE = re.compile(r'<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<[^>]+>|\{[^}]+\}|\[\d+\]|[a-zA-Z0-9_-]+\.js["\']?|static/chunks/|_next/static/|\\u[0-9a-fA-F]{4}|\|[^|]+\|[^|]+\|')
    _META_PREFIXES = {"share", "expertise", "jurisdiction", "publication", "guide", "sponsored", "advertisement", "download", "image", "photo", "figure", "by press room", "table of contents"}
    _CONTINUATION_WORDS = {"moreover", "however", "therefore", "furthermore", "additionally", "also", "thus", "hence", "consequently", "nevertheless", "nonetheless", "meanwhile", "subsequently", "accordingly", "notably", "interestingly", "importantly", "specifically", "particularly", "indeed", "similarly", "conversely", "alternatively", "otherwise", "instead", "besides", "finally", "lastly"}

    # Domain-specific subject-matter gates
    _DOMAIN_SUBJECT_TERMS = {
        'regulatory': re.compile(
            r'\b(prediction market|gambling|gaming|sfc|dicj|hkjc|aml|kyc|fatf|regulation|regulatory|compliance|'
            r'licens|derivative|event contract|virtual asset|crypto|hedging|treasury|sandbox|concessionaire|'
            r'penalty|fine|prosecution|illegal|enforcement|betting|wagering|gaming revenue|ggr|junket|'
            r'prediction|forecast|outcome|contract|market maker|oracle|settlement|clearing|'
            r'mas|vara|asic|cftc|sec|fsc|fsa|austrac|ukgc|gambling commission|'
            r'betting duty|gaming tax|capital requirement|base capital|application fee|'
            r'vasp|va trading|virtual asset service|travel rule|enforcement action|cease and desist)',
            re.IGNORECASE
        ),
        'customers': re.compile(
            r'\b(hedge fund|institutional|retail|customer|user|adoption|willingness to pay|'
            r'client|investor|trader|family office|asset manager|pension fund|'
            r'vendor selection|due diligence|onboarding|kyc|'
            r'b2b|enterprise|corporate treasury|risk management|'
            r'prediction market|event contract|derivative|betting|trading|'
            r'liquidity provider|market maker|counterparty)',
            re.IGNORECASE
        ),
        'market_landscape': re.compile(
            r'\b(market size|tam|sam|som|competitor|landscape|polymarket|kalshi|betfair|'
            r'volume|revenue|valuation|funding|market share|growth rate|'
            r'prediction market|event contract|derivative|forecast|outcome|'
            r'platform|exchange|trading venue|liquidity|user base|'
            r'industry report|sector analysis|market research|'
            r'billion|million|trillion|usd|eur|gbp|hkd|sgd)',
            re.IGNORECASE
        ),
        'business_model': re.compile(
            r'\b(revenue|fee|pricing|unit economics|ltv|cac|break-even|funding|'
            r'subscription|transaction fee|spread|commission|take rate|'
            r'monetization|business model|pricing tier|acv|arr|mrr|'
            r'profit margin|gross margin|operating cost|burn rate|'
            r'prediction market|event contract|platform|exchange)',
            re.IGNORECASE
        ),
        'technology': re.compile(
            r'\b(blockchain|oracle|smart contract|icp|settlement|latency|api|'
            r'infrastructure|architecture|protocol|consensus|layer|'
            r'web3|defi|on-chain|off-chain|cross-chain|interoperability|'
            r'zero knowledge|zk|rollup|sidechain|bridge|'
            r'prediction market|event contract|derivative|'
            r'trading engine|matching engine|order book|amm|'
            r'security|audit|bug bounty|exploit|hack)',
            re.IGNORECASE
        ),
    }

    # Fallback general gate
    _SUBJECT_TERMS = re.compile(
        r'\b(prediction market|gambling|gaming|sfc|dicj|hkjc|aml|kyc|fatf|regulation|regulatory|compliance|'
        r'licens|derivative|event contract|virtual asset|crypto|hedging|treasury|sandbox|concessionaire|'
        r'penalty|fine|prosecution|illegal|enforcement|betting|wagering|gaming revenue|ggr|junket|'
        r'prediction|forecast|outcome|contract|market maker|oracle|settlement|clearing|'
        r'mas|vara|asic|cftc|sec|fsc|fsa|austrac|ukgc|gambling commission|'
        r'betting duty|gaming tax|capital requirement|base capital|application fee)',
        re.IGNORECASE
    )

    def __init__(self, logger: Logger):
        self.logger = logger

    def _clean_html(self, text: str) -> str:
        """Strip HTML tags, script chunks, JSON-like artifacts, and HTML entities."""
        # Remove script/style blocks and tags
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove JS chunks, static paths, unicode escapes
        text = re.sub(r'[a-zA-Z0-9_-]+\.js["\']?', ' ', text)
        text = re.sub(r'static/chunks/[^\s"\']+', ' ', text)
        text = re.sub(r'_next/static/[^\s"\']+', ' ', text)
        text = re.sub(r'\\u[0-9a-fA-F]{4}', ' ', text)
        text = re.sub(r'\{[^}]+\}', ' ', text)
        text = re.sub(r'\[\d+\]', ' ', text)
        # Remove table-row artifacts with pipes
        text = re.sub(r'\|[^|]+\|[^|]+\|', ' ', text)
        # Remove Wikipedia [ edit ] markers
        text = re.sub(r'\[\s*edit\s*\]', ' ', text, flags=re.IGNORECASE)
        # Decode HTML entities (&rsquo; &#91; &nbsp; etc.)
        import html as _html
        text = _html.unescape(text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _is_junk(self, text: str) -> bool:
        """Reject sentences that are HTML artifacts, metadata, or continuation fragments."""
        # HTML junk ratio
        if self._HTML_JUNK_RE.search(text):
            # If more than 30% of chars are inside tags/scripts, reject
            junk_chars = sum(len(m.group(0)) for m in self._HTML_JUNK_RE.finditer(text))
            if junk_chars / max(len(text), 1) > 0.3:
                return True
        # Pipe/table artifacts
        if text.count("|") >= 3:
            return True
        # Uppercase ratio (header fragments)
        upper_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if upper_ratio > 0.35 and len(text) < 120:
            return True
        # Metadata prefixes
        first_word = text.split()[0].lower().rstrip(",;:'\"") if text.split() else ""
        if first_word in self._META_PREFIXES:
            return True
        # Continuation words (dangling adverbs)
        if first_word in self._CONTINUATION_WORDS:
            return True
        # Paywall / subscription fragments
        paywall_phrases = [
            "only users who have a paid subscription",
            "become an insider and start reading",
            "have an account? log in",
            "subscribe to continue reading",
            "premium content",
            "exclusive to subscribers",
            "sign in to read",
            "continue reading this article",
        ]
        text_lower = text.lower()
        for phrase in paywall_phrases:
            if phrase in text_lower:
                return True
        # Too short after cleaning
        if len(text) < 30:
            return True
        return False

    def _has_subject_matter(self, text: str, domain: str = "") -> bool:
        """Require at least one domain-specific subject-matter term for relevance."""
        # Use domain-specific gate if available
        domain_key = domain.lower().replace(" ", "_").replace("-", "_")
        # DEBUG: log domain matching
        if domain_key in self._DOMAIN_SUBJECT_TERMS:
            result = bool(self._DOMAIN_SUBJECT_TERMS[domain_key].search(text))
            if not result:
                # Log first 80 chars of rejected text for debugging
                pass  # silently reject
            return result
        # Fallback to general gate
        return bool(self._SUBJECT_TERMS.search(text))

    def extract(self, text: str, source_url: str, domain: str = "") -> List[dict]:
        """Extract claims from text with full quality pipeline."""
        # Step 1: Clean HTML artifacts
        text = self._clean_html(text)

        claims = []
        seen = set()

        for pattern in self.CLAIM_PATTERNS:
            for match in pattern.finditer(text):
                claim_text = match.group(1).strip()

                # Step 2: Deduplicate
                key = re.sub(r'\s+', ' ', claim_text.lower()[:80])
                if key in seen or len(claim_text) < 30:
                    continue
                seen.add(key)

                # Step 3: Junk filter (HTML artifacts, metadata, continuation words)
                if self._is_junk(claim_text):
                    continue

                # Step 4: Subject-matter gate (domain-specific)
                if not self._has_subject_matter(claim_text, domain):
                    continue

                # Step 5: Confidence heuristic
                confidence = 0.7
                if any(x in claim_text.lower() for x in ['according to', 'reported', 'stated']):
                    confidence = 0.85
                if any(x in claim_text.lower() for x in ['may', 'might', 'could', 'possibly']):
                    confidence = 0.55

                claims.append({
                    "text": claim_text,
                    "source": source_url,
                    "confidence": round(confidence, 2),
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                })

        self.logger.info(f"EXTRACTED {len(claims)} claims from {source_url[:60]}...")
        return claims

# ---------------------------------------------------------------------------
# Saturation Checker
# ---------------------------------------------------------------------------

class SaturationChecker:
    """Check if research has reached saturation."""

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.claim_history: List[str] = []

    def check(self, new_claims: List[dict]) -> float:
        """Return saturation score (0-1). Higher = more saturated."""
        if not new_claims:
            return 1.0

        new_texts = [c["text"].lower()[:100] for c in new_claims]

        if not self.claim_history:
            self.claim_history.extend(new_texts)
            return 0.0

        # Count how many new claims are similar to existing
        similar = 0
        for new_text in new_texts:
            for hist_text in self.claim_history[-200:]:  # Compare against last 200
                if self._similarity(new_text, hist_text) > 0.7:
                    similar += 1
                    break

        saturation = similar / len(new_texts) if new_texts else 1.0
        self.claim_history.extend(new_texts)
        return saturation

    def _similarity(self, a: str, b: str) -> float:
        """Simple Jaccard similarity."""
        set_a = set(a.split())
        set_b = set(b.split())
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union else 0.0

# ---------------------------------------------------------------------------
# Research Cycle
# ---------------------------------------------------------------------------

class ResearchCycle:
    """Run one research cycle for a domain."""

    def __init__(self, domain_name: str, domain_config: dict, logger: Logger):
        self.domain_name = domain_name
        self.config = domain_config
        self.logger = logger
        self.fetcher = SourceFetcher(logger)
        self.extractor = ClaimExtractor(logger)
        self.saturation = SaturationChecker()
        self.claims: List[dict] = []
        self.sources: List[dict] = []

    def run(self, max_sources: int = 20, depth: int = 2) -> dict:
        """Execute research cycle."""
        self.logger.info(f"Starting cycle for domain: {self.domain_name}")

        # Phase 1: Search for sources
        queries = self.config.get("search_queries", [])
        urls = self._discover_urls(queries, max_sources)

        # Phase 2: Fetch and extract
        for i, url in enumerate(urls):
            self.logger.info(f"Fetching [{i+1}/{len(urls)}] {url[:80]}...")
            content = self.fetcher.fetch(url)
            if not content:
                continue

            # Save raw source
            source_id = self._source_id(url)
            source_path = SOURCES_DIR / f"{self.domain_name}_{source_id}.html"
            source_path.write_text(content, encoding="utf-8")

            self.sources.append({
                "url": url,
                "path": str(source_path),
                "size": len(content),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

            # Extract claims
            claims = self.extractor.extract(content, url, self.domain_name)
            self.claims.extend(claims)

            # Check saturation
            if claims:
                sat = self.saturation.check(claims)
                self.logger.info(f"Saturation: {sat:.2%}")
                if sat > 0.85 and i > 5:
                    self.logger.info("Saturation threshold reached, stopping early")
                    break

        # Phase 3: Generate report
        report = self._generate_report()
        return report

    def _discover_urls(self, queries: List[str], max_results: int) -> List[str]:
        """Discover URLs via search with domain authority pre-sorting."""
        urls = set()
        scored_results = []  # (authority_score, url)

        # Domain authority patterns (Fix Pattern 15)
        PRIMARY_DOMAINS = {
            'gov.hk', 'info.gov.hk', 'fso.gov.hk', 'hkma.gov.hk', 'sfc.hk',
            'gov.mo', 'dicj.gov.mo', 'mof.gov.mo',
            'mas.gov.sg', 'mof.gov.sg', 'abs.gov.sg',
            'cftc.gov', 'sec.gov', 'treasury.gov', 'fincen.gov',
            'fca.org.uk', 'gamblingcommission.gov.uk', 'gov.uk',
            'europa.eu', 'ec.europa.eu', 'esma.europa.eu',
            'asic.gov.au', 'austrac.gov.au',
            'fsa.go.jp', 'fsca.kr', 'uae.gov.ae', 'dfsa.ae',
        }
        SECONDARY_DOMAINS = {
            'reuters.com', 'bloomberg.com', 'ft.com', 'wsj.com', 'cnbc.com',
            'scmp.com', 'nikkei.com', 'channelnewsasia.com',
            'dlapiper.com', 'cliffordchance.com', 'bakermckenzie.com',
            'harneys.com', 'maples.com', 'walkersglobal.com',
            'harvard.edu', 'ox.ac.uk', 'cam.ac.uk', 'nber.org',
            'hkex.com.hk', 'sgx.com', 'lseg.com', 'nasdaq.com',
            'fortune.com', 'economist.com', 'forbes.com',
        }

        def score_domain(url: str) -> float:
            domain = urllib.parse.urlparse(url).netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            if any(domain == d or domain.endswith('.' + d) for d in PRIMARY_DOMAINS):
                return 3.0
            if any(domain == d or domain.endswith('.' + d) for d in SECONDARY_DOMAINS):
                return 2.0
            return 0.0

        # Try ddgs (DuckDuckGo) if available
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                for query in queries:
                    if len(urls) >= max_results:
                        break
                    self.logger.info(f"Searching: {query[:80]}...")
                    results = ddgs.text(query, max_results=10)
                    for r in results:
                        url = r.get("href", "")
                        if url and self._is_valid_url(url) and url not in urls:
                            scored_results.append((score_domain(url), url))
                            urls.add(url)
                        if len(urls) >= max_results:
                            break
        except ImportError:
            self.logger.warn("ddgs not available, using fallback")

        # Sort by authority score descending so high-credibility sources are fetched first
        scored_results.sort(key=lambda x: x[0], reverse=True)
        sorted_urls = [url for _, url in scored_results]

        # Fallback: trusted sources
        if len(sorted_urls) < 5:
            for domain in self.config.get("trusted_sources", []):
                url = f"https://{domain}"
                if url not in urls:
                    sorted_urls.append(url)

        return sorted_urls[:max_results]

    def _is_valid_url(self, url: str) -> bool:
        """Filter out bad URLs."""
        if not url.startswith("http"):
            return False
        blacklist = {"facebook.com", "twitter.com", "x.com", "youtube.com", "linkedin.com"}
        return not any(b in url.lower() for b in blacklist)

    def _source_id(self, url: str) -> str:
        """Generate safe source ID."""
        clean = re.sub(r'[^a-zA-Z0-9]', '_', url[:80])
        return f"{clean}_{int(time.time())}"

    def _generate_report(self) -> dict:
        """Generate structured report."""
        # Sort claims by confidence
        top_claims = sorted(self.claims, key=lambda x: x["confidence"], reverse=True)[:50]

        # Group by theme (simple keyword clustering)
        themes = self._cluster_themes(self.claims)

        report = {
            "meta": {
                "domain": self.domain_name,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "sources_count": len(self.sources),
                "claims_count": len(self.claims),
                "saturation": self.saturation.check([]) if not self.claims else 0.0,
            },
            "executive_summary": self._generate_summary(top_claims, themes),
            "key_findings": top_claims[:20],
            "themes": themes,
            "sources": self.sources,
            "gaps": self._identify_gaps(),
        }

        return report

    def _cluster_themes(self, claims: List[dict]) -> Dict[str, List[str]]:
        """Simple keyword-based theme clustering."""
        themes = {}
        keywords = {
            "regulation": ["regulation", "license", "compliance", "sfc", "sec", "mas", "vara"],
            "market": ["market", "trading", "volume", "price", "demand"],
            "technology": ["blockchain", "oracle", "smart contract", "infrastructure"],
            "business": ["revenue", "pricing", "subscription", "partnership", "customer"],
        }

        for claim in claims:
            text = claim["text"].lower()
            for theme, words in keywords.items():
                if any(w in text for w in words):
                    if theme not in themes:
                        themes[theme] = []
                    themes[theme].append(claim["text"])

        return {k: v[:10] for k, v in themes.items()}

    def _generate_summary(self, claims: List[dict], themes: Dict[str, List[str]]) -> str:
        """Generate executive summary with geo-coherent sentence extraction."""
        lines = [
            f"# Research Report: {self.domain_name.title()}",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
            f"**Sources:** {len(self.sources)} | **Claims:** {len(self.claims)}  ",
            "",
            "## Executive Summary",
            "",
        ]

        if claims:
            lines.append(f"Analysis of {len(self.sources)} sources identified {len(self.claims)} distinct claims. "
                        f"Top themes: {', '.join(themes.keys()) if themes else 'general'}.")
            lines.append("")
            lines.append("### Top Findings")
            # Geo-coherent extraction: pick top claim per jurisdiction theme
            seen_jurs = set()
            for claim in claims:
                text_lower = claim['text'].lower()
                jur = None
                for candidate in ['hong kong', 'macau', 'singapore', 'dubai', 'uae', 'japan', 'south korea', 'australia', 'uk', 'eu']:
                    if candidate in text_lower:
                        jur = candidate
                        break
                if jur and jur not in seen_jurs:
                    seen_jurs.add(jur)
                    lines.append(f"- **{claim['confidence']}** — {claim['text']}")
                elif not jur and len([l for l in lines if l.startswith('- **')]) < 5:
                    lines.append(f"- **{claim['confidence']}** — {claim['text']}")
                if len([l for l in lines if l.startswith('- **')]) >= 5:
                    break
        else:
            lines.append("No claims extracted in this cycle.")

        return "\n".join(lines)

    def _identify_gaps(self) -> List[str]:
        """Identify research gaps with word-boundary matching for short terms."""
        gaps = []
        questions = self.config.get("key_questions", [])
        claim_texts = " ".join(c["text"].lower() for c in self.claims)

        for question in questions:
            # Word-boundary matching: short terms (≤4 chars) use \b to avoid
            # substring false positives like 'mas' matching 'mass-metallicity'
            key_terms = [w for w in question.lower().split() if len(w) > 3]
            matches = 0
            for term in key_terms:
                if len(term) <= 4:
                    # Use word boundary for short acronyms
                    if re.search(r'\b' + re.escape(term) + r'\b', claim_texts):
                        matches += 1
                else:
                    if term in claim_texts:
                        matches += 1
            if matches < 2:
                gaps.append(question)

        return gaps[:5]

# ---------------------------------------------------------------------------
# Report Writer
# ---------------------------------------------------------------------------

class ReportWriter:
    """Write reports to disk."""

    def write(self, report: dict, output_dir: Path):
        """Write report as markdown."""
        domain = report["meta"]["domain"]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
        filename = f"report_{domain}_{timestamp}.md"
        filepath = output_dir / filename

        lines = [
            report["executive_summary"],
            "",
            "---",
            "",
            "## Key Findings",
            "",
        ]

        for claim in report["key_findings"]:
            lines.append(f"- **{claim['confidence']}** — {claim['text']}")
            lines.append(f"  Source: {claim['source'][:80]}...")
            lines.append("")

        if report["themes"]:
            lines.append("---")
            lines.append("")
            lines.append("## Themes")
            lines.append("")
            for theme, items in report["themes"].items():
                lines.append(f"### {theme.title()}")
                for item in items[:5]:
                    lines.append(f"- {item}")
                lines.append("")

        if report["gaps"]:
            lines.append("---")
            lines.append("")
            lines.append("## Research Gaps")
            lines.append("")
            for gap in report["gaps"]:
                lines.append(f"- [ ] {gap}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## Sources")
        lines.append("")
        for src in report["sources"]:
            lines.append(f"- [{src['url'][:60]}...]({src['url']}) — {src['size']} chars")

        filepath.write_text("\n".join(lines), encoding="utf-8")
        return filepath

# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ARLI Research Framework")
    parser.add_argument("--domain", default="all", help="Domain to research (or 'all')")
    parser.add_argument("--cycles", type=int, default=1, help="Number of cycles per domain")
    parser.add_argument("--output", default=str(OUTPUT_DIR), help="Output directory")
    args = parser.parse_args()

    logger = Logger("orchestrator")
    config = load_config()
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    domains_config = config.get("domains", {})

    if args.domain != "all":
        if args.domain not in domains_config:
            logger.error(f"Unknown domain: {args.domain}")
            sys.exit(1)
        domains = {args.domain: domains_config[args.domain]}
    else:
        # Sort by priority
        domains = dict(sorted(
            domains_config.items(),
            key=lambda x: x[1].get("priority", 99)
        ))

    logger.info(f"Starting research for {len(domains)} domain(s)")

    all_reports = []
    for domain_name, domain_config in domains.items():
        for cycle in range(args.cycles):
            cycle_logger = Logger(f"{domain_name}.cycle{cycle+1}")
            cycle_runner = ResearchCycle(domain_name, domain_config, cycle_logger)
            report = cycle_runner.run(
                max_sources=config.get("cycles", {}).get("max_sources_per_cycle", 20),
                depth=config.get("cycles", {}).get("default_depth", 2),
            )
            all_reports.append(report)

            # Write report
            writer = ReportWriter()
            filepath = writer.write(report, output_dir)
            cycle_logger.info(f"Report written: {filepath}")

    logger.info(f"Research complete. {len(all_reports)} reports generated in {output_dir}")

if __name__ == "__main__":
    main()
