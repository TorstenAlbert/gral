# 🧬 NP-Solver — Formally Verified Metaheuristic Optimization

> A self-correcting pipeline that solves NP-hard combinatorial optimization problems using Genetic Algorithms, Iterated Local Search, and SPIN/Promela formal verification — orchestrated through a blackboard architecture with an autonomous feedback loop.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![SPIN Model Checker](https://img.shields.io/badge/SPIN-model%20checker-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Results](#key-results)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
  - [Phase 0 — Setup](#phase-0--setup)
  - [Phase 1 — Iteration Loop](#phase-1--iteration-loop)
  - [Diagnosis Decision Tree](#diagnosis-decision-tree)
  - [Escalation Ladder](#escalation-ladder)
- [Core Components](#core-components)
  - [Blackboard](#blackboard)
  - [GA + Local Search Solver](#ga--local-search-solver)
  - [SPIN Verification](#spin-verification)
  - [Feedback Agent](#feedback-agent)
  - [Orchestrator](#orchestrator)
- [Distance Convention (Critical)](#distance-convention-critical)
- [Configuration](#configuration)
- [Algorithmic Toolkit](#algorithmic-toolkit)
- [Optimization Guide](#optimization-guide)
- [Extending to Other Problems](#extending-to-other-problems)
- [Hard Rules](#hard-rules)
- [Troubleshooting](#troubleshooting)
- [Benchmarks](#benchmarks)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

NP-Solver is a pipeline that combines **metaheuristic search** with **formal verification** to solve NP-hard problems — starting with the Travelling Salesman Problem (TSP). It does not just find solutions; it **proves properties** about them using the SPIN model checker.

The system is designed to run autonomously via a feedback loop (the "Ralph Loop"): it solves, verifies, diagnoses failures, patches parameters, and iterates until a formally verified solution meeting the quality threshold is found.

**What makes it different from a plain GA/TSP solver:**

| Feature | Plain GA | NP-Solver |
|---------|----------|-----------|
| Finds good tours | ✅ | ✅ |
| Proves tour validity (Hamiltonian cycle) | ❌ | ✅ via SPIN |
| Verifies claimed cost matches actual cost | ❌ | ✅ via SPIN |
| Self-tunes parameters on failure | ❌ | ✅ via feedback agent |
| Autonomous iteration with diagnosis | ❌ | ✅ via orchestrator |
| Emits formal promise on success | ❌ | ✅ `GAP_LT_5_PERCENT_VERIFIED` |

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                                 │
│                  (agents/orchestrator.py)                            │
│                                                                     │
│   ┌──────────┐    ┌──────────────┐    ┌───────────────────────┐     │
│   │  GA +    │───▶│  BLACKBOARD  │───▶│   SPIN VERIFICATION   │     │
│   │  ILS     │    │  (JSON)      │    │   (Promela model)     │     │
│   │  Solver  │    │              │◀───│                       │     │
│   └──────────┘    │  • problem   │    └───────────────────────┘     │
│        ▲          │  • best_cost │              │                   │
│        │          │  • best_tour │              ▼                   │
│        │          │  • gap       │    ┌───────────────────────┐     │
│        │          │  • params    │    │   FEEDBACK AGENT      │     │
│        └──────────│  • promise   │◀───│   (gap analysis,      │     │
│                   │              │    │    param tuning)       │     │
│                   └──────────────┘    └───────────────────────┘     │
│                                                                     │
│   Repeat until promise == "GAP_LT_5_PERCENT_VERIFIED"              │
└───────────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. **Solver** (GA + ILS) writes `best_solution` and `best_cost` to the blackboard
2. **Promela generator** encodes the candidate tour as a SPIN model
3. **SPIN runner** compiles and verifies the model (permutation check + cost check)
4. **Feedback agent** reads verification results, computes gap vs. known optimal, tunes parameters
5. **Orchestrator** checks for the success promise; if not met, loops back to step 1

---

## Key Results

| Instance | Cities | Optimal | Found | Gap | Iterations | SPIN Status |
|----------|--------|---------|-------|-----|------------|-------------|
| eil51 | 51 | 426 | 426 | 0.00% | 1 | ✅ PASS |

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.10+ | Runtime |
| **SPIN** | 6.5+ | Model checking / formal verification |
| **GCC** | Any recent | Compiling SPIN-generated verifiers (`pan.c`) |
| **pip** | Latest | Python package management |

**Verify installation:**

```bash
python3 --version        # Python 3.10+
which spin               # /usr/bin/spin or similar
which gcc                # /usr/bin/gcc
```

### Installing SPIN

- **macOS:** `brew install spin`
- **Ubuntu/Debian:** `apt-get install spin`
- **From source:** [spinroot.com](https://spinroot.com/spin/whatispin.html)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/np-solver.git
cd np-solver

# Install Python dependencies
pip install -r requirements.txt

# Verify everything compiles
python3 -m py_compile agents/orchestrator.py
python3 -m py_compile strategies/ga_tsp.py
python3 -m py_compile models/promela_gen.py
python3 -m py_compile verification/spin_runner.py
python3 -m py_compile agents/feedback.py

# Run tests
pytest tests/ -v
```

### Python Dependencies

```
deap>=1.4          # Genetic algorithm framework
pytest>=7.0        # Testing
```

---

## Project Structure

```
np-solver/
├── agents/
│   ├── orchestrator.py       # Main loop: solver → verify → feedback → repeat
│   └── feedback.py           # Gap analysis, parameter tuning, stagnation detection
├── strategies/
│   └── ga_tsp.py             # GA + 2-opt + Or-opt + ILS + double-bridge solver
├── models/
│   └── promela_gen.py        # Generates Promela models from candidate tours
├── verification/
│   └── spin_runner.py        # Compiles and runs SPIN verification
├── tests/
│   └── test_np_solver.py     # Integration tests (DO NOT MODIFY)
├── blackboard.json           # Shared state: problem, solution, params, verification
├── ralph_improvements.log    # Changelog from autonomous iterations
├── ralph_loop_eil51_prompt.md # Full task specification
└── README.md                 # This file
```

---

## Quick Start

### 1. Set up the problem in `blackboard.json`

```json
{
  "problem": {
    "type": "TSP",
    "instance": [
      [37, 52], [49, 49], [52, 64], [20, 26], [40, 30],
      [21, 47], [17, 63], [31, 62], [52, 33], [51, 21],
      [42, 41], [31, 32], [5, 25],  [12, 42], [36, 16],
      [52, 41], [27, 23], [17, 33], [13, 13], [57, 58],
      [62, 42], [42, 57], [16, 57], [8, 52],  [7, 38],
      [27, 68], [30, 48], [43, 67], [58, 48], [58, 27],
      [37, 69], [38, 46], [46, 10], [61, 33], [62, 63],
      [63, 69], [32, 22], [45, 35], [59, 15], [5, 6],
      [10, 17], [21, 10], [5, 64],  [30, 15], [39, 10],
      [32, 39], [25, 32], [25, 55], [48, 28], [56, 37],
      [30, 40]
    ],
    "optimal": 426,
    "n": 51,
    "distance_type": "EUC_2D"
  },
  "strategies": {
    "current": "ga_tsp",
    "tried": [],
    "params": {
      "pop_size": 200,
      "gens": 500,
      "mutpb": 0.15,
      "cxpb": 0.7
    }
  },
  "best_solution": null,
  "best_cost": null,
  "verification": { "pass_rate": 0, "status": "pending", "error": null },
  "fitness_history": [],
  "feedback": { "gap": 1.0, "pass_rate": 0, "stagnant_count": 0, "ready_for_test": false },
  "iteration": 0,
  "test_passed": false,
  "promise": null
}
```

### 2. Run the pipeline

```bash
# Clean SPIN artifacts
rm -f pan pan.c pan.h pan.b pan.m pan.t pan.p pan.trail _spin_nvr.tmp

# Run the orchestrator
python3 -m agents.orchestrator
```

### 3. Check results

```bash
python3 -c "
import json
with open('blackboard.json') as f:
    bb = json.load(f)
print(f'Cost:    {bb["best_cost"]}')
print(f'Gap:     {bb["feedback"]["gap"]:.2%}')
print(f'SPIN:    {bb["verification"]["status"]}')
print(f'Promise: {bb["promise"]}')
"
```

### 4. Run tests

```bash
pytest tests/test_np_solver.py -v
```

---

## How It Works

### Phase 0 — Setup

1. Load the TSP instance coordinates into `blackboard.json`
2. Set `distance_type: "EUC_2D"` and `optimal: 426`
3. Ensure all distance computations use `round(sqrt(...))` — **not** raw float Euclidean
4. Configure SPIN runner for N=51: `pan -m100000`, timeout 120s

### Phase 1 — Iteration Loop

Each iteration performs:

```
CLEAN  →  RUN orchestrator  →  OBSERVE blackboard  →  DIAGNOSE  →  IMPROVE  →  REPEAT
```

The orchestrator internally runs:
1. **GA phase** — evolve a population of tours (200 pop × 500 gens)
2. **Seeding** — inject nearest-neighbor heuristic tours into 20% of the population
3. **Elite extraction** — pull top 3 from Hall of Fame + NN seeds as ILS starting points
4. **ILS phase** — for each starting tour, run 200 double-bridge kicks with 2-opt refinement
5. **Write** best tour to blackboard
6. **Promela generation** — encode the tour as a SPIN model
7. **SPIN verification** — compile and run the model checker
8. **Feedback** — compute gap, update parameters, check stagnation
9. **Promise check** — if gap < 5% and SPIN passes, emit `GAP_LT_5_PERCENT_VERIFIED`

### Diagnosis Decision Tree

```
Python exception?
├── YES → Fix the bug, py_compile, re-run
└── NO ↓

SPIN compile error?
├── YES → Fix promela_gen.py (N mismatch, indexing)
└── NO ↓

SPIN verification fails?
├── YES → Fix Promela model logic
└── NO ↓

gap ≥ 5% and pass_rate ≥ 0.95?
├── YES → Improve solver (escalation ladder)
└── NO ↓

stagnant_count > 3?
├── YES → Escalate improvements
└── NO → Run another iteration
```

### Escalation Ladder

| Level | Trigger | Action |
|-------|---------|--------|
| 1 | gap > 10% | Verify EUC_2D distances, ensure 2-opt is working |
| 2 | gap > 7% | Add nearest-neighbor seeding + Or-opt |
| 3 | gap > 6% | Add ILS with double-bridge kicks (200+) |
| 4 | gap > 5% | Increase ILS kicks to 500, add more start points |
| 5 | gap > 5% still | Add 3-opt moves inside local search |
| 6 | stagnant > 10 | Double population, fresh restart |
| 7 | stagnant > 20 | Add simulated annealing post-processing |

---

## Core Components

### Blackboard

**File:** `blackboard.json`

The central shared state. All agents read from and write to this JSON file. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `problem.instance` | `[[x,y], ...]` | City coordinates |
| `problem.optimal` | `int` | Known optimal tour cost |
| `problem.distance_type` | `string` | `"EUC_2D"` — determines distance function |
| `strategies.params` | `object` | GA parameters: `pop_size`, `gens`, `mutpb`, `cxpb` |
| `best_solution` | `[int, ...]` | Best tour found (0-indexed city permutation) |
| `best_cost` | `int` | Cost of best tour |
| `verification.status` | `string` | `"PASS"`, `"FAIL"`, or `"pending"` |
| `verification.pass_rate` | `float` | 0.0 – 1.0 |
| `feedback.gap` | `float` | `(best_cost - optimal) / optimal` |
| `feedback.stagnant_count` | `int` | Consecutive iterations without improvement |
| `promise` | `string or null` | `"GAP_LT_5_PERCENT_VERIFIED"` on success |

### GA + Local Search Solver

**File:** `strategies/ga_tsp.py`

The solver combines multiple techniques:

- **Genetic Algorithm** (via DEAP): ordered crossover, swap mutation, tournament selection
- **Nearest-Neighbor Seeding**: deterministic greedy tours seed 20% of the initial population
- **2-opt Local Search**: iterative edge-swap improvement
- **Or-opt**: segment relocation (segments of 1, 2, and 3 cities)
- **Double-Bridge Perturbation**: 4-edge random reconnection to escape local optima
- **Iterated Local Search (ILS)**: `local_search → double_bridge → local_search` repeated

### SPIN Verification

**Files:** `models/promela_gen.py`, `verification/spin_runner.py`

The Promela model encodes:
1. **Tour validity** — every city appears exactly once (permutation check)
2. **Cost correctness** — the computed cost matches the claimed cost

SPIN exhaustively checks these properties. If verification passes, the solution is **formally proven correct** — not just tested.

```
promela_gen.py:   Candidate tour → Promela source (.pml)
spin_runner.py:   .pml → spin -a → gcc pan.c → ./pan -m100000 → PASS/FAIL
```

### Feedback Agent

**File:** `agents/feedback.py`

Reads blackboard state after each iteration and:
- Computes gap: `(best_cost - optimal) / optimal`
- Detects stagnation (no improvement for N iterations)
- Tunes GA parameters (increase gens, adjust mutation rate)
- Guards parameter bounds: `pop_size ≤ 1000`, `gens ≤ 2000`, `mutpb ≤ 0.3`

### Orchestrator

**File:** `agents/orchestrator.py`

The main loop that ties everything together. Run with:

```bash
python3 -m agents.orchestrator
```

It calls solver → verification → feedback → promise check in sequence, and runs pytest at the end.

---

## Distance Convention (Critical)

**This is the single most important implementation detail.**

TSPLIB `EUC_2D` instances use **integer-rounded** Euclidean distances:

```python
import math

def euc_2d(a, b):
    # TSPLIB EUC_2D: round to nearest integer.
    return round(math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2))

def tour_cost(tour, coords):
    # Total tour cost using TSPLIB EUC_2D convention.
    n = len(tour)
    return sum(euc_2d(coords[tour[i]], coords[tour[(i+1) % n]]) for i in range(n))
```

**Why this matters:**
- Raw `math.dist` returns floats (e.g., `14.142135...`)
- TSPLIB expects integers (e.g., `14`)
- The proven optimal of 426 is computed with integer distances
- Using float distances produces a *different* optimal, making the 5% gap check meaningless

The previous run's only bug was this mismatch. Once fixed, the solver hit optimal on the first iteration.

---

## Configuration

### GA Parameters (in `blackboard.json`)

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `pop_size` | 200 | 50–1000 | Population size |
| `gens` | 500 | 100–2000 | Generations per GA run |
| `mutpb` | 0.15 | 0.05–0.30 | Mutation probability |
| `cxpb` | 0.7 | 0.5–0.9 | Crossover probability |

### ILS Parameters (in `ga_tsp.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_kicks` | 200 | Double-bridge perturbations per ILS run |
| `n_starts` | ~56 | Starting tours (NN seeds + GA elites) |

### SPIN Parameters (in `spin_runner.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| Search depth | `-m100000` | Max search depth for `pan` |
| Timeout | `120s` | Subprocess timeout |

---

## Algorithmic Toolkit

### 2-opt

Iteratively reverses tour segments to remove crossing edges:

```
Before:  ... → A → B → ... → C → D → ...
After:   ... → A → C → ... → B → D → ...  (segment B..C reversed)
```

Applied if `delta = d(A,C) + d(B,D) - d(A,B) - d(C,D) < 0`.

### Or-opt

Relocates segments of 1, 2, or 3 consecutive cities to a better position in the tour. Complements 2-opt by handling moves that 2-opt cannot express.

### Double-Bridge

A 4-opt perturbation that randomly splits the tour into 4 segments and reconnects them in a non-sequential order. This is the standard escape mechanism from 2-opt local optima:

```python
def double_bridge(tour):
    n = len(tour)
    cuts = sorted(random.sample(range(1, n), 3))
    a, b, c, d = cuts[0], cuts[1], cuts[2], n
    return tour[:a] + tour[c:d] + tour[b:c] + tour[a:b]
```

### Iterated Local Search (ILS)

The core metaheuristic:
```
start → 2-opt → (best so far)
              ↓
        double-bridge kick
              ↓
        2-opt on perturbed tour
              ↓
        accept if improved → repeat N times
```

### Nearest-Neighbor Heuristic

Greedy construction: start at a city, always move to the nearest unvisited city. Fast (O(n²)), produces tours within ~20% of optimal. Used to seed the GA population.

---

## Optimization Guide

### For Speed

1. **Precompute the distance matrix** — replace per-call `euc_2d()` with an N×N lookup table
2. **Replace GA seeding with pure NN** — skip 200×500 GA generations, seed ILS directly
3. **Parallelize ILS restarts** — use `multiprocessing.Pool` across CPU cores
4. **Use Numba for 2-opt** — JIT-compile the inner loop for 10-50× speedup

### For Solution Quality (larger instances)

1. Add **Lin-Kernighan** style variable-depth moves
2. Increase ILS kicks to 500–1000
3. Add **3-opt** when ILS with 2-opt plateaus
4. Use **portfolio approach** — run multiple strategies concurrently

### For Scalability (500+ cities)

1. Simplify the Promela model — verify only permutation, compute cost in Python
2. Skip SPIN on intermediate iterations — only verify the final candidate
3. Use neighbor lists in 2-opt (only check nearest 10–15 neighbors per city)

---

## Extending to Other Problems

The architecture is problem-agnostic. To add a new problem type:

1. **Add a solver** in `strategies/` (e.g., `strategies/ga_knapsack.py`)
2. **Add a Promela model** in `models/` for the verification properties you care about
3. **Update `blackboard.json`** with the problem definition and optimality target
4. **Update `feedback.py`** with problem-specific gap calculation
5. **Update `orchestrator.py`** to dispatch to the new solver

Candidate problem classes:
- **Vehicle Routing Problem (VRP)**
- **Job-Shop Scheduling**
- **Graph Coloring**
- **Knapsack / Bin Packing**
- **Satisfiability (SAT)**

---

## Hard Rules

1. ❌ **NEVER** modify `tests/test_np_solver.py`
2. ❌ **NEVER** manually set `promise`, `test_passed`, `best_solution`, or `best_cost` in `blackboard.json`
3. ❌ **NEVER** hardcode a tour
4. ❌ **NEVER** skip `python3 -m agents.orchestrator` (always run the full pipeline)
5. ✅ **ALWAYS** use `euc_2d` (nearest-integer) distances — never raw Euclidean
6. ✅ **ALWAYS** clean SPIN artifacts before each run
7. ✅ **ALWAYS** `py_compile` changed files before running the orchestrator
8. ✅ **ALWAYS** log changes to `ralph_improvements.log`

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Gap is slightly off from expected | Using `math.dist` instead of `euc_2d` | Replace all distance calls with `round(math.sqrt(...))` |
| SPIN compile error | Promela `N` doesn't match city count | Update `#define N` in `promela_gen.py` |
| SPIN timeout | Search depth too shallow or timeout too short | Increase `-m` flag and subprocess timeout |
| `pan: invalid end state` | Promela model missing progress/end labels | Add `end:` labels to blocking states |
| GA finds same cost every run | Random seed is fixed | Remove or vary `random.seed(42)` |
| stagnant_count keeps growing | ILS stuck in basin of attraction | Escalate: more kicks, double-bridge, 3-opt |
| `ModuleNotFoundError: deap` | Missing dependency | `pip install deap` |
| Permission denied on `./pan` | Pan binary not executable | `chmod +x pan` (handled by spin_runner) |

---

## Benchmarks

### TSPLIB eil51

- **Instance:** 51 cities, Christofides/Eilon 1969
- **Proven optimal:** 426 (Concorde exact solver)
- **Distance type:** EUC_2D (integer-rounded Euclidean)
- **Pipeline result:** 426 (exact optimal, 0.00% gap)
- **Time:** ~3 minutes on Apple M-series
- **Verification:** SPIN PASS, 5/5 pytest PASS

### Future Targets

| Instance | Cities | Optimal | Status |
|----------|--------|---------|--------|
| eil51 | 51 | 426 | ✅ Solved |
| berlin52 | 52 | 7542 | 🔲 Planned |
| kroA100 | 100 | 21282 | 🔲 Planned |
| ch150 | 150 | 6528 | 🔲 Planned |
| tsp225 | 225 | 3916 | 🔲 Planned |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/lin-kernighan`)
3. Ensure all tests pass (`pytest tests/ -v`)
4. Ensure the orchestrator still reaches `GAP_LT_5_PERCENT_VERIFIED`
5. Submit a pull request

**Do not modify `tests/test_np_solver.py`.** Add new tests in separate files.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **TSPLIB** — Gerhard Reinelt, University of Heidelberg
- **SPIN** — Gerard Holzmann, Bell Labs / NASA JPL
- **DEAP** — Distributed Evolutionary Algorithms in Python
- **Concorde** — Applegate, Bixby, Chvátal, Cook (optimal TSP solver)

---

*Built with 🧬 metaheuristics, 🔍 formal verification, and ♻️ autonomous feedback loops.*
