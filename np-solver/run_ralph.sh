#\!/bin/bash
set -e
echo "=== NP-Solver Ralph Loop ==="
pip install -q deap numpy pytest scipy
which spin || { echo "SPIN nicht gefunden\! Installiere mit: sudo apt install spin"; exit 1; }
python -m agents.orchestrator
