import pytest, math
from agents.blackboard import Blackboard

bb = Blackboard()

def tour_cost(tour, coords):
    n = len(tour)
    return sum(math.dist(coords[tour[i]], coords[tour[(i+1)%n]]) for i in range(n))

def test_solution_exists():
    assert bb.get("best_solution") is not None, "Keine Lösung gefunden"

def test_spin_verified():
    status = bb.get("verification", "status")
    assert status == "PASS", f"SPIN Verifikation fehlgeschlagen: {status}"

def test_pass_rate_high():
    rate = bb.get("verification", "pass_rate")
    assert rate >= 0.95, f"SPIN-Rate zu niedrig: {rate}"

def test_gap_acceptable():
    cost = bb.get("best_cost")
    optimal = bb.get("problem", "optimal")
    gap = abs(cost - optimal) / optimal
    assert gap < 0.05, f"Lösung zu weit von Optimal: gap={gap:.3f} ({gap*100:.1f}%)"

def test_hamiltonian_valid():
    tour = bb.get("best_solution")
    n = bb.get("problem", "n")
    assert sorted(tour) == list(range(n)), "Tour kein gültiger Hamiltonian Cycle"
