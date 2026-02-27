import math
import pytest
from agents.blackboard import Blackboard
from strategies.ga_tsp import run_ga
from verification.spin_runner import verify
from models.promela_gen import gen_promela

def _setup_bb():
    bb = Blackboard()
    run_ga(bb)
    gen_promela(bb)
    verify(bb)
    return bb

def test_compute_fitness_updates_history():
    from agents.feedback import compute_fitness
    bb = _setup_bb()
    initial_len = len(bb.get("fitness_history"))
    compute_fitness(bb)
    bb2 = Blackboard()
    assert len(bb2.get("fitness_history")) == initial_len + 1

def test_gap_is_computed():
    from agents.feedback import compute_fitness
    bb = _setup_bb()
    compute_fitness(bb)
    bb2 = Blackboard()
    gap = bb2.get("feedback", "gap")
    cost = bb2.get("best_cost")
    optimal = bb2.get("problem", "optimal")
    expected_gap = abs(cost - optimal) / optimal
    assert abs(gap - expected_gap) < 1e-6

def test_mutpb_cap():
    from agents.feedback import compute_fitness
    bb = _setup_bb()
    # Force stagnation scenario
    bb.set(10, "feedback", "stagnant_count")
    bb.set(0.28, "strategies", "params", "mutpb")
    compute_fitness(bb)
    bb2 = Blackboard()
    assert bb2.get("strategies", "params", "mutpb") <= 0.3
