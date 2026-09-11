#!/usr/bin/env bash
# Regenerates the pydoc HTML docs into docs/pydoc/.
# Run from the project root, after `pip install -e .`.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p docs/pydoc
cd docs/pydoc
python3 -m pydoc -w weatherstats weatherstats.data_loader weatherstats.stats weatherstats.report
echo "Docs written to docs/pydoc/ -- open docs/pydoc/index.html"
