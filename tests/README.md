# Tests

## Commands (from the repository root)

```powershell
python tools/run.py --check
python tools/run.py --input tests/my_cases.jsonl
python -m pytest tests -q
```

## JSON Lines cases (`my_cases.jsonl`)

{"task":"ping"}
{"task":"dsu","n":3,"operations":[[0,0],[0,1],[0,1],[1,2]]}
{"task":"kruskal","n":4,"edges":[[0,0,-5],[0,1,4],[0,1,-2],[1,2,3]]}
{"task":"prim","n":4,"edges":[[0,0,-5],[0,1,4],[0,1,-2],[1,2,3]]}
{"task":"scc","n":4,"edges":[[0,1],[1,0],[1,2],[2,3],[1,2]]}
{"task":"topo","n":3,"edges":[[0,1],[1,2],[2,0]]}
{"task":"dag","n":4,"source":0,"edges":[[0,1,1],[2,3,1],[3,2,1]]}
{"task":"dag","n":4,"source":0,"edges":[[0,1,5],[0,1,5],[1,2,-3],[0,2,10]]}

## Automated tests (`test_algorithms.py`)

Boundaries (n=0, isolates, loops, repeated unions), parallel/tied edges, negative weights,
totals beyond 32 bits, cycle unreachable from the source, random Kruskal/Prim comparison
with brute force, random SCC comparison with a reachability matrix (exact membership and
exact condensation), examples from the assignment, mixed requests in one process
(state reset), a 100000-vertex deep chain, and random full-limit inputs (m = 250000).

## Non-unique answers

Topological order, SCC labels and parent edges are checked by validity.
`test_topo_valid_order_by_validity_not_equality` accepts the alternative order [0,3,1,2]
and rejects [1,0,2,3]. `test_dag_invalid_witness_is_rejected` rejects a parent_edge that
does not reproduce the claimed distance.

## pytest output

```
21 passed in 2.87s
```