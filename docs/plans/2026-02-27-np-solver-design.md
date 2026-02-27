# NP-Solver Design — 2026-02-27

## Goal

Autonomous GA + SPIN verification loop that solves NP-hard problems (starting with TSP), formally verifies solutions via the SPIN model checker, and self-tunes until gap < 5% AND SPIN verification passes.

## Architecture

**Blackboard pattern.** `blackboard.json` is the single source of truth. All agents read/write only through `agents/blackboard.py`. No direct inter-agent communication.

**Target path:** `np-solver/` inside the current git repo.

## Agent Pipeline (per iteration)

```
ProblemReader → GASolver → PromelaGenerator → SPINVerifier → FeedbackAgent → TestRunner → Orchestrator
```

## Components

| Component | File | Responsibility |
|-----------|------|----------------|
| Blackboard | `agents/blackboard.py` | Nested get/set/update/increment on `blackboard.json` |
| GA Solver | `strategies/ga_tsp.py` | DEAP TSP: ordered crossover, shuffle mutation, tournament selection |
| Promela Generator | `models/promela_gen.py` | Hamiltonian cycle verification model (assignment-in-init, no array literals) |
| SPIN Runner | `verification/spin_runner.py` | spin -a → gcc → ./pan → parse errors → clean up artifacts |
| Feedback Agent | `agents/feedback.py` | Fitness = (pass_rate×100) + 1/(gap+0.01) + log(coverage+1); adaptive param tuning |
| Orchestrator | `agents/orchestrator.py` | Main loop (max 100 iterations); emits promise on success |

## Termination

`<promise>GAP_LT_5_PERCENT_VERIFIED</promise>` when:
- `gap < 0.05` (best_cost within 5% of optimal)
- `pass_rate >= 0.95`
- All pytest tests in `tests/test_np_solver.py` pass

Hard abort at 100 iterations → exit(1).

## Adaptive Tuning Rules

| Condition | Action |
|-----------|--------|
| pass_rate < 0.5 | pop_size × 1.2 |
| gap > 0.1 | gens += 50 |
| stagnant_count > 5 | mutpb += 0.05 (cap 0.3) |

## Key Correctness Fixes

- All Python package dirs have `__init__.py`
- Promela array init uses individual assignments in `init` block (no `byte tour[N] = {...}`)
- SPIN artifacts (`pan.c`, `pan`, `pan.h`, `pan.b`, `pan.m`, `pan.t`) cleaned up after each run
- `mutpb` capped at 0.3
- `gens` increased additively (+50), not multiplicatively

## Problem Instance (TSP)

- Coords: `[[0,0],[3,1],[1,4],[5,2],[2,5],[4,3]]` (6 cities)
- Optimal: 14.8
- Initial GA params: pop_size=100, gens=200, mutpb=0.1, cxpb=0.7
