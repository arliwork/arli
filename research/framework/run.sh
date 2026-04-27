#!/bin/bash
# ARLI Research Framework — Master Run Script
# Runs all domains, generates reports, syncs to data-room

LOG_FILE="/tmp/arli-research.log"

# Create log file BEFORE set -e so we always have output
touch "$LOG_FILE"
exec > >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

set -e

cd "$(dirname "$0")"
VENV="../prediction-markets-autoresearch/venv/bin/activate"

if [ -f "$VENV" ]; then
    source "$VENV"
fi

echo "=== ARLI Research Framework ==="
echo "Started: $(date -u +%Y-%m-%d_%H:%M:%S)"

# Run all domains with 2 cycles each
python pipelines/orchestrator.py --domain all --cycles 2

# Sync to data-room
python pipelines/sync_to_dataroom.py

echo "Completed: $(date -u +%Y-%m-%d_%H:%M:%S)"
