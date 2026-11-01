#!/bin/sh
# Runs every check of the model and the Knesset 27 site:
#   1. pytest (seat allocation of every election, sector model invariants, box linking);
#   2. scripts/check_panels_site.py (browser: no errors or overflow, JS calculator seats
#      equal the Python model for every panel, majorities, committee file import).
# Usage: sh scripts/check_all.sh [screenshot_dir]
set -e
cd "$(dirname "$0")/.."
python -m pytest -q tests
PYTHONPATH=src python scripts/check_panels_site.py "${1:-${TMPDIR:-/tmp}/panels_shots}" | grep -v "JS vs Python 0"
