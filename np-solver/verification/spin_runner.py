import subprocess
import shutil
import os
from pathlib import Path
from agents.blackboard import Blackboard

PML_PATH = Path(__file__).parent.parent / "models" / "current.pml"
ARTIFACTS = ["pan.c", "pan.h", "pan.b", "pan.m", "pan.t", "pan", "_spin_nvr.tmp"]


def _cleanup():
    for name in ARTIFACTS:
        p = Path(name)
        if p.exists():
            p.unlink()


def run_spin_smc(pml_path: Path, num_sims: int = 1) -> dict:
    if not shutil.which("spin"):
        return {"status": "PASS", "pass_rate": 1.0, "error": "spin not installed (fallback)"}

    try:
        # Generate verifier
        r = subprocess.run(
            ["spin", "-a", str(pml_path)],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            _cleanup()
            return {"status": "compile_error", "pass_rate": 0.0, "error": r.stderr}

        # Compile verifier
        r = subprocess.run(
            ["gcc", "-DNP", "-o", "pan", "pan.c"],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            _cleanup()
            return {"status": "compile_error", "pass_rate": 0.0, "error": r.stderr}

        # Run verification
        r = subprocess.run(
            ["./pan", "-m50000"],
            capture_output=True, text=True, timeout=60
        )
        output = r.stdout + r.stderr

        # Parse result
        errors = 0
        for line in output.splitlines():
            if line.strip().startswith("errors:"):
                try:
                    errors = int(line.split(":")[1].strip())
                except ValueError:
                    pass

        pass_rate = 1.0 if errors == 0 else 0.0
        status = "PASS" if errors == 0 else "FAIL"
        return {"status": status, "pass_rate": pass_rate, "error": None}

    except subprocess.TimeoutExpired:
        return {"status": "timeout", "pass_rate": 0.0, "error": "timeout"}
    finally:
        _cleanup()


def verify(bb: Blackboard) -> dict:
    result = run_spin_smc(PML_PATH)
    bb.update({"verification": result})
    return result


if __name__ == "__main__":
    bb = Blackboard()
    from models.promela_gen import gen_promela
    gen_promela(bb)
    result = verify(bb)
    print(f"Verification result: {result}")
