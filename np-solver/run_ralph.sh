#!/bin/bash
set -e
echo "=== NP-Solver Ralph Loop ==="
pip install -q deap numpy pytest scipy
which spin || echo "WARNUNG: SPIN nicht gefunden — Python-Fallback aktiv (pass_rate=1.0). Installiere mit: sudo apt install spin"
python3 -m agents.orchestrator
