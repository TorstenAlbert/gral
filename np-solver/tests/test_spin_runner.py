import pytest
from agents.blackboard import Blackboard
from models.promela_gen import gen_promela
from strategies.ga_tsp import run_ga

def test_spin_runner_returns_dict():
    from verification.spin_runner import verify
    bb = Blackboard()
    run_ga(bb)
    gen_promela(bb)
    result = verify(bb)
    assert isinstance(result, dict)
    assert "status" in result
    assert "pass_rate" in result

def test_spin_updates_blackboard():
    from verification.spin_runner import verify
    bb = Blackboard()
    run_ga(bb)
    gen_promela(bb)
    verify(bb)
    bb2 = Blackboard()
    status = bb2.get("verification", "status")
    assert status in ("PASS", "FAIL", "compile_error", "timeout", "spin_missing")
