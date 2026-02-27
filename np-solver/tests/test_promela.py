import pytest
from pathlib import Path
from agents.blackboard import Blackboard

PML_PATH = Path(__file__).parent.parent / "models" / "current.pml"

def test_promela_file_created():
    from models.promela_gen import gen_promela
    bb = Blackboard()
    # Need a solution to generate promela for
    tour = list(range(bb.get("problem", "n")))
    bb.set(tour, "best_solution")
    gen_promela(bb)
    assert PML_PATH.exists()

def test_promela_contains_init_block():
    from models.promela_gen import gen_promela
    bb = Blackboard()
    tour = list(range(bb.get("problem", "n")))
    bb.set(tour, "best_solution")
    gen_promela(bb)
    content = PML_PATH.read_text()
    assert "init {" in content

def test_promela_no_array_literals():
    from models.promela_gen import gen_promela
    bb = Blackboard()
    tour = list(range(bb.get("problem", "n")))
    bb.set(tour, "best_solution")
    gen_promela(bb)
    content = PML_PATH.read_text()
    # Promela does not support: byte tour[N] = {0,1,2,...}
    assert "= {" not in content

def test_promela_contains_assert():
    from models.promela_gen import gen_promela
    bb = Blackboard()
    tour = list(range(bb.get("problem", "n")))
    bb.set(tour, "best_solution")
    gen_promela(bb)
    content = PML_PATH.read_text()
    assert "assert" in content
