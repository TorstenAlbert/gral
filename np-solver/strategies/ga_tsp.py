import math
import random
import numpy as np
from deap import base, creator, tools, algorithms
from agents.blackboard import Blackboard


# ---------------------------------------------------------------------------
# Distance matrix + cost helpers
# ---------------------------------------------------------------------------

def euc_2d(a, b):
    """TSPLIB EUC_2D distance: nearest-integer Euclidean."""
    return round(math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2))


def make_dist(coords):
    n = len(coords)
    D = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = euc_2d(coords[i], coords[j])
            D[i][j] = d
            D[j][i] = d
    return D


def tour_cost_D(tour, D):
    n = len(tour)
    return sum(D[tour[i]][tour[(i + 1) % n]] for i in range(n))


def tour_cost(tour, coords):
    n = len(tour)
    return sum(euc_2d(coords[tour[i]], coords[tour[(i + 1) % n]]) for i in range(n))


# ---------------------------------------------------------------------------
# Delta-based 2-opt
# ---------------------------------------------------------------------------

def two_opt_d(tour, D):
    n = len(tour)
    best = tour[:]
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                a, b = best[i], best[i + 1]
                c, d = best[j], best[(j + 1) % n]
                delta = D[a][c] + D[b][d] - D[a][b] - D[c][d]
                if delta < -1e-10:
                    best[i + 1:j + 1] = best[i + 1:j + 1][::-1]
                    improved = True
    return best, tour_cost_D(best, D)


# ---------------------------------------------------------------------------
# Or-opt (delta-based)
# ---------------------------------------------------------------------------

def or_opt_d(tour, D, seg_size=1):
    n = len(tour)
    best = tour[:]
    improved = True
    while improved:
        improved = False
        for i in range(n):
            seg_end = (i + seg_size - 1) % n
            prev_i = (i - 1) % n
            next_seg = (seg_end + 1) % n

            removal_gain = (D[best[prev_i]][best[i]]
                            + D[best[seg_end]][best[next_seg]]
                            - D[best[prev_i]][best[next_seg]])

            j = next_seg
            for _ in range(n - seg_size - 1):
                next_j = (j + 1) % n
                if j == prev_i:
                    j = next_j
                    continue
                insertion_cost = (D[best[j]][best[i]]
                                  + D[best[seg_end]][best[next_j]]
                                  - D[best[j]][best[next_j]])
                delta = insertion_cost - removal_gain
                if delta < -1e-10:
                    segment = []
                    idx = i
                    for _ in range(seg_size):
                        segment.append(best[idx])
                        idx = (idx + 1) % n
                    flat = best[:]
                    positions_to_remove = {(i + s) % n for s in range(seg_size)}
                    remaining = [flat[k] for k in range(n) if k not in positions_to_remove]
                    j_city = flat[j]
                    j_pos = remaining.index(j_city)
                    best = remaining[:j_pos + 1] + segment + remaining[j_pos + 1:]
                    improved = True
                    break
                j = next_j
            if improved:
                break
    return best, tour_cost_D(best, D)


# ---------------------------------------------------------------------------
# 3-opt (delta-based, all 4 true 3-opt reconnections)
# ---------------------------------------------------------------------------

def three_opt_d(tour, D):
    n = len(tour)
    best = tour[:]
    improved = True
    while improved:
        improved = False
        for i in range(n - 4):
            for j in range(i + 2, n - 2):
                for k in range(j + 2, n if i > 0 else n - 1):
                    a, b = best[i], best[i + 1]
                    c, d = best[j], best[j + 1]
                    e, f = best[k], best[(k + 1) % n]
                    d0 = D[a][b] + D[c][d] + D[e][f]

                    delta1 = D[a][d] + D[e][b] + D[c][f] - d0   # A+C+B+D
                    delta2 = D[a][e] + D[d][b] + D[c][f] - d0   # A+C'+B+D
                    delta3 = D[a][d] + D[e][c] + D[b][f] - d0   # A+C+B'+D
                    delta4 = D[a][e] + D[d][c] + D[b][f] - d0   # A+C'+B'+D

                    best_delta = min(delta1, delta2, delta3, delta4)
                    if best_delta < -1e-10:
                        seg_A = best[:i + 1]
                        seg_B = best[i + 1:j + 1]
                        seg_C = best[j + 1:k + 1]
                        seg_D = best[k + 1:]
                        if best_delta == delta1:
                            best = seg_A + seg_C + seg_B + seg_D
                        elif best_delta == delta2:
                            best = seg_A + seg_C[::-1] + seg_B + seg_D
                        elif best_delta == delta3:
                            best = seg_A + seg_C + seg_B[::-1] + seg_D
                        else:
                            best = seg_A + seg_C[::-1] + seg_B[::-1] + seg_D
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break
    return best, tour_cost_D(best, D)


# ---------------------------------------------------------------------------
# Lin-Kernighan style moves (sequential improving edge exchanges)
# ---------------------------------------------------------------------------

def build_neighbor_lists(D, k=7):
    """For each city, store its k nearest neighbors."""
    n = len(D)
    neighbors = []
    for i in range(n):
        ranked = sorted(range(n), key=lambda j: D[i][j] if j != i else float('inf'))
        neighbors.append(ranked[:k])
    return neighbors


def lk_move(tour, D, neighbors):
    """One pass of Lin-Kernighan style moves (2.5-opt sequential search)."""
    n = len(tour)
    pos = [0] * n  # pos[city] = index in tour
    for idx, city in enumerate(tour):
        pos[city] = idx

    def next_city(idx):
        return tour[(idx + 1) % n]

    def prev_city(idx):
        return tour[(idx - 1) % n]

    improved = False
    best = tour[:]
    best_cost = tour_cost_D(best, D)

    for t1_idx in range(n):
        t1 = best[t1_idx]
        # Try both directions: delete edge (t1, t2) where t2 = next or prev
        for direction in [1, -1]:
            t2_idx = (t1_idx + direction) % n
            t2 = best[t2_idx]
            g0 = D[t1][t2]  # gain from deleting edge (t1, t2)

            # Try each neighbor of t1 as t3 (to add edge t2-t3)
            for t3 in neighbors[t2]:
                if t3 == t1 or t3 == t2:
                    continue
                g1 = g0 - D[t2][t3]
                if g1 <= 0:
                    break  # neighbors sorted by distance, no further gain possible

                t3_idx = pos[t3]
                # Try adding edge (t3, t4) where t4 closes a valid 3-opt tour
                for t4 in [best[(t3_idx + 1) % n], best[(t3_idx - 1) % n]]:
                    if t4 == t2 or t4 == t1:
                        continue
                    # Closing gain: g1 + D[t3][t4] - D[t4][t1]...
                    # Actually, build the resulting tour for accuracy
                    # This is a simplified LK: effectively a targeted 3-opt
                    t4_idx = pos[t4]
                    # Build candidate 3-opt tour
                    segs = sorted([(t1_idx, t2_idx), (t3_idx, t4_idx)], key=lambda x: min(x))
                    # This gets complex; fall back to checking the actual move
                    # Use the 3-opt delta we already have
                    pass

    # Fall back: return best found by standard local search
    return best, best_cost


# ---------------------------------------------------------------------------
# Simulated annealing for TSP (escape strong local optima)
# ---------------------------------------------------------------------------

def sa_tsp(tour, D, T_init=200.0, alpha=0.9998, max_iter=500000):
    """SA with mixed neighborhood: 2-opt and Or-opt(1) moves."""
    n = len(tour)
    best = tour[:]
    best_cost = tour_cost_D(best, D)
    current = best[:]
    current_cost = best_cost
    T = T_init

    for step in range(max_iter):
        T *= alpha
        if T < 0.001:
            break

        move_type = random.random()
        if move_type < 0.7:
            # 2-opt move
            i = random.randint(0, n - 2)
            j = random.randint(i + 1, n - 1)
            if i == 0 and j == n - 1:
                continue
            a, b = current[i], current[i + 1]
            c, d_city = current[j], current[(j + 1) % n]
            delta = D[a][c] + D[b][d_city] - D[a][b] - D[c][d_city]
            new = None
        else:
            # Or-opt(1): relocate a random city
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
            if abs(i - j) <= 1 or (i == 0 and j == n - 1):
                continue
            prev_i = (i - 1) % n
            next_i = (i + 1) % n
            city = current[i]
            after_j = current[(j + 1) % n]
            delta = (D[current[prev_i]][current[next_i]]
                     + D[current[j]][city] + D[city][after_j]
                     - D[current[prev_i]][city] - D[city][current[next_i]]
                     - D[current[j]][after_j])
            move_type = None  # flag for Or-opt branch

        if move_type is None:
            # Apply Or-opt move
            if delta < 0 or random.random() < math.exp(-delta / T):
                remaining = current[:i] + current[i+1:]
                # Find j's new position in remaining
                j_city = current[j]
                if j > i:
                    j_new = remaining.index(j_city)
                else:
                    j_new = j  # j < i, so index unchanged
                current = remaining[:j_new + 1] + [city] + remaining[j_new + 1:]
                current_cost += delta
                if current_cost < best_cost:
                    best = current[:]
                    best_cost = current_cost
        else:
            # Apply 2-opt move
            if delta < 0 or random.random() < math.exp(-delta / T):
                current[i + 1:j + 1] = current[i + 1:j + 1][::-1]
                current_cost += delta
                if current_cost < best_cost:
                    best = current[:]
                    best_cost = current_cost

    return best, best_cost


# ---------------------------------------------------------------------------
# Double-bridge + ILS
# ---------------------------------------------------------------------------

def double_bridge(tour):
    n = len(tour)
    pos = sorted(random.sample(range(1, n), 3))
    a, b, c = pos
    return tour[:a] + tour[b:c] + tour[a:b] + tour[c:]


def local_search(tour, D):
    """2-opt → Or-opt(1,2,3) → 3-opt → 2-opt."""
    t, _ = two_opt_d(tour, D)
    t, _ = or_opt_d(t, D, seg_size=1)
    t, _ = or_opt_d(t, D, seg_size=2)
    t, _ = or_opt_d(t, D, seg_size=3)
    t, _ = three_opt_d(t, D)
    t, c = two_opt_d(t, D)
    return t, c


def iterated_local_search(start_tour, D, n_kicks=100):
    best, best_cost = local_search(start_tour, D)
    current = best[:]
    for _ in range(n_kicks):
        kicked = double_bridge(current)
        candidate, cost = local_search(kicked, D)
        if cost < best_cost:
            best = candidate[:]
            best_cost = cost
            current = best[:]
        elif cost < best_cost * 1.005:
            current = candidate[:]
    return best, best_cost


def sa_then_ls(tour, D):
    """SA to escape local optima, followed by greedy local search."""
    t, _ = sa_tsp(tour, D)
    t, c = local_search(t, D)
    return t, c


# ---------------------------------------------------------------------------
# Nearest-neighbor constructive heuristic
# ---------------------------------------------------------------------------

def nearest_neighbor_tour(coords, D, start=0):
    n = len(coords)
    visited = [False] * n
    tour = [start]
    visited[start] = True
    for _ in range(n - 1):
        last = tour[-1]
        nearest = min(
            (i for i in range(n) if not visited[i]),
            key=lambda i: D[last][i]
        )
        tour.append(nearest)
        visited[nearest] = True
    return tour


# ---------------------------------------------------------------------------
# Main entry: GA seeding + ILS + SA
# ---------------------------------------------------------------------------

def run_ga(bb: Blackboard):
    coords = bb.get("problem", "instance")
    params = bb.get("strategies", "params")
    pop_size = params["pop_size"]
    gens = params["gens"]
    mutpb = params["mutpb"]
    cxpb = params["cxpb"]
    n = len(coords)

    D = make_dist(coords)

    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register(
        "individual",
        tools.initIterate,
        creator.Individual,
        lambda: list(np.random.permutation(n)),
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def eval_tour(individual):
        return (tour_cost_D(individual, D),)

    toolbox.register("evaluate", eval_tour)
    toolbox.register("mate", tools.cxOrdered)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    overall_best = None
    overall_cost = float('inf')

    # Collect diverse starting tours
    starting_tours = []
    for s in range(n):  # All n nearest-neighbor starts
        starting_tours.append(nearest_neighbor_tour(coords, D, s))

    # GA to generate additional diverse tours
    random.seed(42)
    np.random.seed(42)
    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(5)
    for start in range(min(pop_size // 5, n)):
        nn_tour = nearest_neighbor_tour(coords, D, start)
        ind = creator.Individual(nn_tour)
        ind.fitness.values = toolbox.evaluate(ind)
        pop[start] = ind
    algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb,
                        ngen=gens, halloffame=hof, verbose=False)
    for elite in list(hof):
        starting_tours.append([int(x) for x in elite])

    # Phase 1: ILS from all starting tours
    print(f"  Phase 1: ILS from {len(starting_tours)} starts, 200 kicks each...")
    ils_results = []
    for idx, start_tour in enumerate(starting_tours):
        t, c = iterated_local_search(start_tour, D, n_kicks=200)
        ils_results.append((c, t))
        if c < overall_cost:
            overall_best = t[:]
            overall_cost = c

    print(f"  Phase 1 best: {overall_cost:.2f}")

    # Phase 2: SA from best ILS solutions to escape 3-opt optima
    top_results = sorted(ils_results)[:10]
    print(f"  Phase 2: SA escape from top 10 ILS solutions...")
    for rank, (c_init, t_init) in enumerate(top_results):
        t_sa, c_sa = sa_then_ls(t_init, D)
        print(f"    SA-{rank+1}: {c_init:.2f} -> {c_sa:.2f}")
        if c_sa < overall_cost:
            overall_best = t_sa[:]
            overall_cost = c_sa

    bb.set(overall_best, "best_solution")
    bb.set(round(overall_cost, 6), "best_cost")
    print(f"GA Done: best cost={overall_cost:.2f}")


if __name__ == "__main__":
    bb = Blackboard()
    run_ga(bb)
    print(f"Best solution: {bb.get('best_solution')}")
    print(f"Best cost: {bb.get('best_cost')}")
