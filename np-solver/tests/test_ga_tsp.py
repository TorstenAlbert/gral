import pytest
from agents.blackboard import Blackboard

def test_ga_produces_solution():
    from strategies.ga_tsp import run_ga
    bb = Blackboard()
    run_ga(bb)
    bb2 = Blackboard()
    assert bb2.get("best_solution") is not None
    assert bb2.get("best_cost") is not None

def test_ga_solution_is_valid_tour():
    from strategies.ga_tsp import run_ga
    bb = Blackboard()
    run_ga(bb)
    bb2 = Blackboard()
    tour = bb2.get("best_solution")
    n = bb2.get("problem", "n")
    assert sorted(tour) == list(range(n))

def test_ga_cost_is_positive():
    from strategies.ga_tsp import run_ga
    bb = Blackboard()
    run_ga(bb)
    bb2 = Blackboard()
    assert bb2.get("best_cost") > 0
