import os
import platform
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "Python"))

from algorithms import DSU, kruskal, prim

SEED = 12345
SIZES = [(1000, 5000), (10000, 50000), (100000, 250000)]  # (n, m)
REPEATS = 5


def make_graph(n, m, seed):
    rnd = random.Random(seed)
    edges = []
    for i in range(1, n):  # a chain first, so the graph is connected
        edges.append([i - 1, i, rnd.randint(-10**9, 10**9)])
    while len(edges) < m:  # extra random edges (loops and parallel edges are possible)
        edges.append([rnd.randrange(n), rnd.randrange(n), rnd.randint(-10**9, 10**9)])
    return edges


def check_forest(n, edges, result):
    """Selected edges must have no cycle, n - components edges and the claimed cost."""
    sets = DSU(n)
    total = 0
    for i in result["edge_ids"]:
        u, v, w = edges[i]
        assert sets.union(u, v) > 0, "cycle or loop selected"
        total += w
    assert total == result["cost"], "cost does not match selected edges"
    assert len(result["edge_ids"]) == n - result["components"]


def measure(function, request):
    function(request)  # warm-up, not counted
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        function(request)
        times.append(time.perf_counter() - start)
    return times


print("Python", platform.python_version(), "|", platform.platform())
print("CPU:", platform.processor(), "| logical cores:", os.cpu_count())
print("seed =", SEED, "| timer = time.perf_counter | repeats =", REPEATS, "| 1 warm-up run per method")
print("timed: only the algorithm call. NOT timed: graph generation, request building, JSON parsing, I/O")

for n, m in SIZES:
    edges = make_graph(n, m, SEED)
    request = {"n": n, "edges": edges}

    kruskal_result = kruskal(request)
    prim_result = prim(request)
    assert kruskal_result["cost"] == prim_result["cost"], "algorithms disagree on cost"
    assert kruskal_result["components"] == prim_result["components"]
    check_forest(n, edges, kruskal_result)
    check_forest(n, edges, prim_result)

    for name, function in (("kruskal", kruskal), ("prim", prim)):
        times = measure(function, request)
        rounded = [round(t, 4) for t in times]
        print(f"n={n} m={m} {name}: runs={rounded} median={statistics.median(times):.4f}s")