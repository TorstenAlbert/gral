import json, os, pytest
from pathlib import Path

BB_PATH = Path(__file__).parent.parent / "blackboard.json"

def test_blackboard_get():
    from agents.blackboard import Blackboard
    bb = Blackboard()
    assert bb.get("problem", "type") == "TSP"

def test_blackboard_set_and_persist():
    from agents.blackboard import Blackboard
    bb = Blackboard()
    bb.set(42, "iteration")
    bb2 = Blackboard()
    assert bb2.get("iteration") == 42
    bb.set(0, "iteration")  # reset

def test_blackboard_update():
    from agents.blackboard import Blackboard
    bb = Blackboard()
    bb.update({"test_passed": True})
    bb2 = Blackboard()
    assert bb2.get("test_passed") is True
    bb.update({"test_passed": False})  # reset

def test_blackboard_increment():
    from agents.blackboard import Blackboard
    bb = Blackboard()
    bb.set(0, "iteration")
    bb.increment("iteration")
    assert bb.get("iteration") == 1
    bb.set(0, "iteration")  # reset
