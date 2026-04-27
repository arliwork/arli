"""
Sync research outputs to data-room for investor access.

Usage:
    python pipelines/sync_to_dataroom.py
"""

import shutil
from datetime import datetime, timezone
from pathlib import Path

FRAMEWORK_DIR = Path(__file__).parent.parent
OUTPUT_DIR = FRAMEWORK_DIR / "outputs"
DATAROOM_DIR = Path("/home/paperclip/arli/research/landing-premium/data-room")
RESEARCH_DIR = DATAROOM_DIR / "research_library"

def sync():
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    # Copy latest reports
    reports = sorted(OUTPUT_DIR.glob("report_*.md"))
    if not reports:
        print("No reports to sync")
        return

    for report in reports[-10:]:  # Last 10 reports
        dest = RESEARCH_DIR / report.name
        shutil.copy2(report, dest)
        print(f"Synced: {dest}")

    # Update index
    index = RESEARCH_DIR / "index.md"
    lines = ["# Research Library", "", f"Last updated: {datetime.now(timezone.utc).isoformat()}", "", "## Reports", ""]
    for report in sorted(RESEARCH_DIR.glob("report_*.md"), reverse=True):
        lines.append(f"- [{report.stem}]({report.name})")
    index.write_text("\n".join(lines), encoding="utf-8")
    print(f"Updated: {index}")

if __name__ == "__main__":
    sync()
