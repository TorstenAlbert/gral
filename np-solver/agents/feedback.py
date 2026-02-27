import math
from agents.blackboard import Blackboard


def compute_fitness(bb: Blackboard) -> float:
    best_cost = bb.get("best_cost")
    optimal = bb.get("problem", "optimal")
    pass_rate = bb.get("verification", "pass_rate")

    gap = abs(best_cost - optimal) / optimal
    coverage = pass_rate  # proxy for state coverage
    fitness = (pass_rate * 100) + (1 / (gap + 0.01)) + math.log(coverage + 1)

    # Stagnation detection
    history = bb.get("fitness_history") or []
    stagnant = bb.get("feedback", "stagnant_count")
    if history and fitness <= history[-1]:
        stagnant += 1
    else:
        stagnant = 0

    # Append to history
    history.append(fitness)
    bb.set(history, "fitness_history")

    # Adaptive parameter tuning
    params = bb.get("strategies", "params")

    if pass_rate < 0.5:
        params["pop_size"] = int(params["pop_size"] * 1.2)

    if gap > 0.1:
        params["gens"] = params["gens"] + 50

    if stagnant > 5:
        params["mutpb"] = min(params["mutpb"] + 0.05, 0.3)

    # ready_for_test only when both conditions hold
    ready = gap < 0.05 and pass_rate >= 0.95

    bb.update({
        "strategies": {"params": params},
        "feedback": {
            "gap": gap,
            "pass_rate": pass_rate,
            "stagnant_count": stagnant,
            "ready_for_test": ready,
        },
    })

    return fitness


if __name__ == "__main__":
    bb = Blackboard()
    f = compute_fitness(bb)
    print(f"Fitness: {f:.4f}")
    print(f"Gap: {bb.get('feedback', 'gap'):.4f}")
    print(f"Ready: {bb.get('feedback', 'ready_for_test')}")
