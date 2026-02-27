# PromelaGenerator

Generates a Promela model that verifies the current best tour is a valid Hamiltonian cycle.

**Reads:** best_solution, problem.n
**Writes:** models/current.pml (file on disk)
**Rules:** NEVER use array literal syntax `byte tour[N] = {…}`. Always use individual assignments in init block. Include `assert(valid == 1);`.
