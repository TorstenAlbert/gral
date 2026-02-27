# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo contains **np-solver**: an autonomous loop that solves NP-hard problems (currently TSP) using a Genetic Algorithm, formally verifies solutions via the SPIN model checker, and self-tunes until the solution quality and verification criteria are met.

## Architecture

**Blackboard pattern.** `np-solver/blackboard.json` is the single source of truth. All agents read and write exclusively through `np-solver/agents/blackboard.py`. No direct inter-agent communication.

**Agent pipeline per iteration:**
```
GASolver → PromelaGenerator → SPINVerifier → FeedbackAgent → (TestRunner if ready) → Orchestrator
```

**Termination:** Emits `<promise>GAP_LT_5_PERCENT_VERIFIED</promise>` and exits 0 when:
- `gap < 0.05` (GA best cost within 5% of optimal)
- `verification.pass_rate >= 0.95`
- All pytest tests in `tests/test_np_solver.py` pass

Hard abort at 100 iterations → exit(1).

## Key Components

| File | Role |
|------|------|
| `np-solver/blackboard.json` | Runtime state (solution, params, verification results, iteration count) |
| `np-solver/agents/blackboard.py` | `Blackboard` class: `get(*keys)`, `set(value, *keys)`, `update(dict)`, `increment(*keys)` |
| `np-solver/agents/orchestrator.py` | Main loop — imports and sequences all agents |
| `np-solver/strategies/ga_tsp.py` | DEAP GA: ordered crossover, shuffle mutation, tournament selection |
| `np-solver/models/promela_gen.py` | Writes `models/current.pml` — Hamiltonian cycle verifier |
| `np-solver/verification/spin_runner.py` | Calls `spin -a` → `gcc` → `./pan`, parses errors, cleans up artifacts |
| `np-solver/agents/feedback.py` | Fitness formula + adaptive parameter tuning |
| `np-solver/tests/test_np_solver.py` | Integration test — **never modify or delete** |

## Commands

All commands run from `np-solver/` unless noted.

**Install dependencies:**
```bash
pip install deap numpy scipy pytest
```

**Run the full autonomous loop (entrypoint):**
```bash
cd np-solver && python3 -m agents.orchestrator
# or via shell script (installs deps, warns if spin missing):
bash np-solver/run_ralph.sh
```

**Run unit tests (excluding integration test):**
```bash
cd np-solver && python -m pytest tests/ --ignore=tests/test_np_solver.py -v
```

**Run a single test file:**
```bash
cd np-solver && python -m pytest tests/test_blackboard.py -v
```

**Run the integration test (requires a completed run with valid blackboard state):**
```bash
cd np-solver && python -m pytest tests/test_np_solver.py -v
```

**One-shot pipeline check (manual single iteration):**
```bash
cd np-solver && python -c "
from agents.blackboard import Blackboard
from strategies.ga_tsp import run_ga
from models.promela_gen import gen_promela
from verification.spin_runner import verify
from agents.feedback import compute_fitness
bb = Blackboard()
run_ga(bb); gen_promela(bb); print(verify(bb)); compute_fitness(bb)
print('gap:', bb.get('feedback', 'gap'))
"
```

## Invariants and Constraints

- `mutpb` max: 0.3 (cap enforced in `feedback.py`)
- `gens` increases additively (+50), never multiplicatively
- `pop_size` scales by ×1.2 when `pass_rate < 0.5`
- Promela generator must use individual assignments (`tour[i] = x;`) in the `init` block — Promela does **not** support array literal syntax (`byte tour[N] = {...}`)
- SPIN artifacts (`pan.c`, `pan`, `pan.h`, `pan.b`, `pan.m`, `pan.t`) are cleaned up after each run
- If `spin` is not installed, the runner returns `status=spin_missing, pass_rate=1.0` as a fallback so the pipeline can still converge

## Stack

- Python 3.11, DEAP, NumPy, SciPy, pytest
- SPIN model checker (`spin` CLI), gcc
- Install SPIN: `brew install spin` (macOS) or `sudo apt install spin` (Linux)

## Agent Documentation

Per-agent Blackboard contracts (reads/writes) are documented in `np-solver/.claude/agents/*.md`.
