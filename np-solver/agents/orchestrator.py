import subprocess
import sys
from pathlib import Path

from agents.blackboard import Blackboard
from strategies.ga_tsp import run_ga
from models.promela_gen import gen_promela
from verification.spin_runner import verify
from agents.feedback import compute_fitness

MAX_ITER = 100
TESTS_DIR = Path(__file__).parent.parent / "tests"


def run_tests() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(TESTS_DIR / "test_np_solver.py"), "-v", "--tb=short"],
        capture_output=False,
    )
    return result.returncode == 0


def main():
    bb = Blackboard()
    print("=== NP-Solver Autonomous Loop ===")

    for i in range(MAX_ITER):
        iteration = bb.get("iteration")
        print(f"\n--- Iteration {iteration + 1} ---")

        # 1. GA solve
        print("  [1/4] Running GA solver...")
        run_ga(bb)
        cost = bb.get("best_cost")
        optimal = bb.get("problem", "optimal")
        gap = abs(cost - optimal) / optimal
        print(f"        best_cost={cost:.4f}, gap={gap*100:.1f}%")

        # 2. Generate Promela
        print("  [2/4] Generating Promela model...")
        gen_promela(bb)

        # 3. SPIN verification
        print("  [3/4] Running SPIN verification...")
        result = verify(bb)
        print(f"        status={result['status']}, pass_rate={result['pass_rate']}")

        # 4. Feedback & adaptive tuning
        print("  [4/4] Computing fitness and tuning params...")
        fitness = compute_fitness(bb)
        print(f"        fitness={fitness:.4f}")

        # 5. Advance iteration counter
        bb.increment("iteration")

        # 6. Check readiness
        ready = bb.get("feedback", "ready_for_test")
        if ready:
            print("\n  [CHECK] Conditions met — running test suite...")
            if run_tests():
                bb.set(True, "test_passed")
                bb.set("GAP_LT_5_PERCENT_VERIFIED", "promise")
                print("\n<promise>GAP_LT_5_PERCENT_VERIFIED</promise>")
                sys.exit(0)
            else:
                print("  [CHECK] Tests failed — continuing...")

    print(f"\n[ABORT] Reached max iterations ({MAX_ITER}) without meeting criteria.")
    sys.exit(1)


if __name__ == "__main__":
    main()
