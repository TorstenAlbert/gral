# NP-Solver Claude Code Conventions

## Stack
- Python 3.11, DEAP, NumPy, SciPy, pytest, subprocess
- SPIN model checker (CLI: `spin`), gcc

## Rules
- `blackboard.json` is the single source of truth. ALL reads/writes go through `agents/blackboard.py`.
- Tests in `tests/test_np_solver.py` must NEVER be modified or deleted.
- The promise `GAP_LT_5_PERCENT_VERIFIED` is only emitted when ALL pytest tests pass AND `verification.pass_rate >= 0.95`.
- Budget guard: abort after 100 iterations.
- Agent execution order: ProblemReader → GASolver → PromelaGenerator → SPINVerifier → FeedbackAgent → TestRunner → Orchestrator

## Adaptive Tuning Caps
- `mutpb` max: 0.3
- `gens` increment: +50 additive (not multiplicative)
