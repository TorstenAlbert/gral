# GASolver

Runs the DEAP genetic algorithm to find a near-optimal TSP tour.

**Reads:** problem.instance, problem.n, strategies.params (pop_size, gens, mutpb, cxpb)
**Writes:** best_solution (list of city indices), best_cost (float)
**Rules:** Use cxOrdered + mutShuffleIndexes(0.05) + selTournament(3). Guard creator with hasattr check.
