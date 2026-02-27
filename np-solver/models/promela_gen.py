from pathlib import Path
from agents.blackboard import Blackboard

PML_PATH = Path(__file__).parent / "current.pml"


def gen_promela(bb: Blackboard):
    tour = bb.get("best_solution")
    n = len(tour)

    lines = []
    lines.append(f"/* TSP Hamiltonian Cycle Verification — {n} cities */")
    lines.append(f"byte tour[{n}];")
    lines.append("byte visited[6];")  # will be 0-initialized by Promela
    lines.append("")
    lines.append("proctype VerifyTour() {")
    lines.append(f"    byte i = 0;")
    lines.append(f"    byte valid = 1;")
    lines.append(f"    do")
    lines.append(f"    :: i < {n} ->");
    lines.append(f"        if")
    lines.append(f"        :: visited[tour[i]] == 1 -> valid = 0")
    lines.append(f"        :: else -> visited[tour[i]] = 1")
    lines.append(f"        fi;")
    lines.append(f"        i++")
    lines.append(f"    :: i >= {n} -> break")
    lines.append(f"    od;")
    lines.append(f"    assert(valid == 1)")
    lines.append("}")
    lines.append("")
    lines.append("init {")
    for idx, city in enumerate(tour):
        lines.append(f"    tour[{idx}] = {city};")
    lines.append("    run VerifyTour();")
    lines.append("}")

    PML_PATH.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    bb = Blackboard()
    gen_promela(bb)
    print(f"Wrote {PML_PATH}")
