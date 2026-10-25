import itertools
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "Python"))

import main
from algorithms import dsu, kruskal, prim, scc, topo, dag, reconstruct_route


# ---------- helpers: answers are checked by validity, not by equality ----------

def brute_force_forest(n, edges):
    """Return (components, cost): fewest components, then smallest cost."""
    best = None
    for k in range(len(edges) + 1):
        for subset in itertools.combinations(range(len(edges)), k):
            parent = list(range(n))

            def find(x):
                while parent[x] != x:
                    x = parent[x]
                return x

            is_forest = True
            cost = 0
            for i in subset:
                u, v, w = edges[i]
                ru, rv = find(u), find(v)
                if ru == rv:
                    is_forest = False
                    break
                parent[ru] = rv
                cost += w
            if is_forest:
                candidate = (n - len(subset), cost)
                if best is None or candidate < best:
                    best = candidate
    return best


def is_valid_topo_order(n, edges, order):
    if sorted(order) != list(range(n)):
        return False
    position = {v: i for i, v in enumerate(order)}
    return all(position[u] < position[v] for u, v in edges)


def is_valid_witness(n, edges, source, distance, parent_edge):
    """Check that parent_edge really builds the claimed distances."""
    if distance[source] != 0 or parent_edge[source] != -1:
        return False
    for v in range(n):
        if v == source:
            continue
        if distance[v] is None:
            if parent_edge[v] != -1:
                return False
        else:
            u, to, w = edges[parent_edge[v]]
            if to != v or distance[u] is None or distance[u] + w != distance[v]:
                return False
    return True


def reachability(n, edges):
    reach = [[i == j for j in range(n)] for i in range(n)]
    for u, v in edges:
        reach[u][v] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    return reach


# ---------- DSU ----------

def test_dsu_empty():
    assert dsu({"n": 0, "operations": []}) == {"states": []}


def test_dsu_loop_and_repeated_union():
    # loop (0,0) changes nothing, (0,1) merges, repeat (0,1) changes nothing, (1,2) merges
    result = dsu({"n": 3, "operations": [[0, 0], [0, 1], [0, 1], [1, 2]]})
    assert result["states"] == [[3, 1], [2, 2], [2, 2], [1, 3]]


def test_dsu_state_reset_between_requests():
    request = {"n": 2, "operations": [[0, 1]]}
    assert dsu(request) == dsu(request) == {"states": [[1, 2]]}


# ---------- Kruskal / Prim ----------

def test_mst_empty_and_isolates():
    for fn in (kruskal, prim):
        assert fn({"n": 0, "edges": []}) == {"cost": 0, "edge_ids": [], "components": 0}
        assert fn({"n": 3, "edges": []}) == {"cost": 0, "edge_ids": [], "components": 3}


def test_mst_negative_weights_loops_parallel():
    edges = [[0, 0, -5], [0, 1, 4], [0, 1, -2], [1, 2, 3]]
    for fn in (kruskal, prim):
        result = fn({"n": 4, "edges": edges})
        # loop is skipped, cheaper parallel edge 2 is used, edge 3 joins vertex 2, vertex 3 is isolated
        assert result["cost"] == 1
        assert sorted(result["edge_ids"]) == [2, 3]
        assert result["components"] == 2


def test_mst_random_against_brute_force():
    rnd = random.Random(1)
    for _ in range(200):
        n = rnd.randint(1, 6)
        edges = [[rnd.randrange(n), rnd.randrange(n), rnd.randint(-5, 5)]
                 for _ in range(rnd.randint(0, 7))]
        expected = brute_force_forest(n, edges)
        for fn in (kruskal, prim):
            result = fn({"n": n, "edges": edges})
            assert (result["components"], result["cost"]) == expected
            assert len(set(result["edge_ids"])) == len(result["edge_ids"]) == n - result["components"]
            assert sum(edges[i][2] for i in result["edge_ids"]) == result["cost"]


def test_extreme_weights_use_big_totals():
    edges = [[0, 1, 10**9], [1, 2, 10**9]]
    for fn in (kruskal, prim):
        assert fn({"n": 3, "edges": edges})["cost"] == 2 * 10**9


# ---------- SCC ----------

def test_scc_cycle_and_parallel_condensation():
    edges = [[0, 1], [1, 0], [1, 2], [2, 3], [1, 2]]
    result = scc({"n": 4, "edges": edges})
    comp = result["component"]
    assert comp[0] == comp[1]
    assert len({comp[0], comp[2], comp[3]}) == 3
    assert len(result["condensation"]) == 2  # parallel edge 1->2 is counted once
    assert all(a != b for a, b in result["condensation"])


def test_scc_empty_and_single_loop():
    assert scc({"n": 0, "edges": []}) == {"component": [], "condensation": []}
    assert scc({"n": 1, "edges": [[0, 0]]}) == {"component": [0], "condensation": []}


def test_scc_random_against_reachability():
    rnd = random.Random(2)
    for _ in range(200):
        n = rnd.randint(0, 7)
        edges = []
        if n > 0:
            for _ in range(rnd.randint(0, 12)):
                edges.append([rnd.randrange(n), rnd.randrange(n)])
        result = scc({"n": n, "edges": edges})
        comp = result["component"]
        reach = reachability(n, edges)
        for a in range(n):
            for b in range(n):
                same = comp[a] == comp[b]
                assert same == (reach[a][b] and reach[b][a])
        expected = {(comp[u], comp[v]) for u, v in edges if comp[u] != comp[v]}
        got = [tuple(pair) for pair in result["condensation"]]
        assert len(got) == len(set(got))  # no duplicate pairs
        assert set(got) == expected


# ---------- Topological sort ----------

def test_topo_cycle_and_self_loop():
    assert topo({"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}) == {"acyclic": False, "order": []}
    assert topo({"n": 1, "edges": [[0, 0]]}) == {"acyclic": False, "order": []}


def test_topo_valid_order_by_validity_not_equality():
    edges = [[0, 1], [1, 2], [0, 3]]
    result = topo({"n": 4, "edges": edges})
    assert result["acyclic"]
    assert is_valid_topo_order(4, edges, result["order"])
    # another valid answer must also be accepted by the checker
    assert is_valid_topo_order(4, edges, [0, 3, 1, 2])
    # an invalid order must be rejected
    assert not is_valid_topo_order(4, edges, [1, 0, 2, 3])


def test_topo_empty():
    assert topo({"n": 0, "edges": []}) == {"acyclic": True, "order": []}


# ---------- DAG ----------

def test_dag_cycle_unreachable_from_source_still_false():
    edges = [[0, 1, 1], [2, 3, 1], [3, 2, 1]]
    result = dag({"n": 4, "source": 0, "edges": edges})
    assert result == {"acyclic": False, "distance": [], "parent_edge": []}


def test_dag_negative_parallel_unreachable():
    edges = [[0, 1, 5], [0, 1, 5], [1, 2, -3], [0, 2, 10]]
    result = dag({"n": 4, "source": 0, "edges": edges})
    assert result["acyclic"]
    assert result["distance"] == [0, 5, 2, None]
    assert result["parent_edge"][0] == -1 and result["parent_edge"][3] == -1
    assert is_valid_witness(4, edges, 0, result["distance"], result["parent_edge"])


def test_dag_invalid_witness_is_rejected():
    edges = [[0, 1, 5], [1, 2, -3], [0, 2, 10]]
    # claims distance 2 for vertex 2, but points to the edge 0->2 of weight 10
    assert not is_valid_witness(3, edges, 0, [0, 5, 2], [-1, 0, 2])
    assert is_valid_witness(3, edges, 0, [0, 5, 2], [-1, 0, 1])


def test_route_helper_cases():
    edges = [[0, 1, 5], [0, 1, 5], [1, 2, -3], [0, 2, 10]]
    result = dag({"n": 4, "source": 0, "edges": edges})
    parent = result["parent_edge"]
    assert reconstruct_route(0, 2, parent, edges)[0] == [0, 1, 2]   # reachable target
    assert reconstruct_route(0, 0, parent, edges) == ([0], [])      # source
    assert reconstruct_route(0, 3, parent, edges) is None           # unreachable
    vertices, edge_ids = reconstruct_route(0, 1, parent, edges)     # tied parallel edges
    assert vertices == [0, 1] and edge_ids[0] in (0, 1)


# ---------- examples from the assignment ----------

def test_examples_from_assignment():
    assert dsu({"n": 4, "operations": [[0, 1], [1, 2], [0, 2], [3, 3]]}) == {
        "states": [[3, 2], [2, 3], [2, 3], [2, 3]]}

    for fn in (kruskal, prim):
        result = fn({"n": 4, "edges": [[0, 1, 4], [1, 2, 2], [0, 2, 3]]})
        assert result["cost"] == 5 and result["components"] == 2
        assert sorted(result["edge_ids"]) == [1, 2]

    edges = [[0, 1, 3], [0, 2, 8], [1, 2, -7], [2, 3, 4]]
    result = dag({"n": 5, "source": 0, "edges": edges})
    assert result["distance"] == [0, 3, -4, 0, None]
    assert is_valid_witness(5, edges, 0, result["distance"], result["parent_edge"])
    vertices, edge_ids = reconstruct_route(0, 3, result["parent_edge"], edges)
    assert vertices == [0, 1, 2, 3]
    assert sum(edges[i][2] for i in edge_ids) == 0
    for i in range(len(edge_ids)):  # check the direction of every edge on the route
        assert edges[edge_ids[i]][0] == vertices[i]
        assert edges[edge_ids[i]][1] == vertices[i + 1]


# ---------- state reset: mixed requests in one process ----------

def test_mixed_requests_state_reset():
    requests = [
        {"task": "ping"},
        {"task": "dsu", "n": 3, "operations": [[0, 1], [1, 2]]},
        {"task": "kruskal", "n": 3, "edges": [[0, 1, 5], [1, 2, 1]]},
        {"task": "scc", "n": 3, "edges": [[0, 1], [1, 0]]},
        {"task": "topo", "n": 2, "edges": [[0, 1]]},
        {"task": "dag", "n": 2, "source": 0, "edges": [[0, 1, 7]]},
        {"task": "prim", "n": 3, "edges": [[0, 1, 5], [1, 2, 1]]},
    ]
    first = [main.handle(r) for r in requests]
    second = [main.handle(r) for r in requests]
    third = [main.handle(r) for r in reversed(requests)]
    assert first == second
    assert first == list(reversed(third))
    assert first[0] == {"status": "ready"}


def test_deep_chain():
    n = 100000
    edges = [[i, i + 1, 1] for i in range(n - 1)]
    pairs = [[u, v] for u, v, _ in edges]

    assert dag({"n": n, "source": 0, "edges": edges})["distance"][-1] == n - 1
    assert topo({"n": n, "edges": pairs})["acyclic"]
    assert len(set(scc({"n": n, "edges": pairs})["component"])) == n
    assert kruskal({"n": n, "edges": edges})["components"] == 1
    assert prim({"n": n, "edges": edges})["components"] == 1


def test_full_limits_random():
    rnd = random.Random(3)
    n, m = 100000, 250000

    weighted = [[rnd.randrange(n), rnd.randrange(n), rnd.randint(-10**9, 10**9)]
                for _ in range(m)]
    k = kruskal({"n": n, "edges": weighted})
    p = prim({"n": n, "edges": weighted})
    assert k["cost"] == p["cost"] and k["components"] == p["components"]
    assert len(k["edge_ids"]) == n - k["components"]

    operations = [[rnd.randrange(n), rnd.randrange(n)] for _ in range(m)]
    assert len(dsu({"n": n, "operations": operations})["states"]) == m

    dag_edges = []
    for _ in range(m):
        u = rnd.randrange(n - 1)
        v = rnd.randint(u + 1, n - 1)  # u < v, so the graph is acyclic
        dag_edges.append([u, v, rnd.randint(-10**9, 10**9)])
    result = dag({"n": n, "source": 0, "edges": dag_edges})
    assert result["acyclic"]
    assert is_valid_witness(n, dag_edges, 0, result["distance"], result["parent_edge"])