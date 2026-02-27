import math
import numpy as np
from deap import base, creator, tools, algorithms
from agents.blackboard import Blackboard


def tour_cost(tour, coords):
    n = len(tour)
    return sum(
        math.dist(coords[tour[i]], coords[tour[(i + 1) % n]])
        for i in range(n)
    )


def run_ga(bb: Blackboard):
    coords = bb.get("problem", "instance")
    params = bb.get("strategies", "params")
    pop_size = params["pop_size"]
    gens = params["gens"]
    mutpb = params["mutpb"]
    cxpb = params["cxpb"]
    n = len(coords)

    # Guard against duplicate creator registration across iterations
    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("indices", np.random.permutation, n)
    toolbox.register(
        "individual",
        tools.initIterate,
        creator.Individual,
        lambda: list(np.random.permutation(n)),
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def eval_tour(individual):
        return (tour_cost(individual, coords),)

    toolbox.register("evaluate", eval_tour)
    toolbox.register("mate", tools.cxOrdered)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(1)

    algorithms.eaSimple(
        pop,
        toolbox,
        cxpb=cxpb,
        mutpb=mutpb,
        ngen=gens,
        halloffame=hof,
        verbose=False,
    )

    # Convert numpy int types to plain Python int for JSON serialization
    best = [int(x) for x in hof[0]]
    cost = tour_cost(best, coords)

    bb.set(best, "best_solution")
    bb.set(round(cost, 6), "best_cost")


if __name__ == "__main__":
    bb = Blackboard()
    run_ga(bb)
    print(f"Best solution: {bb.get('best_solution')}")
    print(f"Best cost: {bb.get('best_cost')}")
