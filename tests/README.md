# Your tests / Ваши тесты

# Tests

## Commands (run from the repository root)

```powershell
python tools/run.py --check
python tools/run.py --input tests/my_cases.jsonl
python -m pytest tests -q
```

## JSON Lines cases (`my_cases.jsonl`)

| Line | Task | Expected (with justification) | Actual |
|---|---|---|---|
| 1 | ping | {"status":"ready"}: ping must be preserved | {"status":"ready"} |
| 2 | dsu | [[3,1],[2,2],[2,2],[1,3]]: loop and repeated union change nothing | {"states":[[3,1],[2,2],[2,2],[1,3]]} |
| 3 | kruskal | cost 1, edge_ids {2,3}, 2 components: loop skipped, cheaper parallel edge -2 used, plus edge of weight 3, vertex 3 isolated | {"cost":1,"edge_ids":[2,3],"components":2} |
| 4 | prim | same graph, same optimal forest | {"cost":1,"edge_ids":[2,3],"components":2} |
| 5 | scc | 3 components ({0,1}, {2}, {3}), 2 distinct condensation pairs; labels may differ | {"component":[0,0,1,2],"condensation":[[0,1],[1,2]]} |
| 6 | topo | cycle 0->1->2->0 gives acyclic=false, empty order | {"acyclic":false,"order":[]} |
| 7 | dag | cycle 2<->3 is unreachable from source, but the whole graph is checked | {"acyclic":false,"distance":[],"parent_edge":[]} |
| 8 | dag | 0->1->2 costs 5-3=2 < 10; tied parallel edges 0 and 1, first one kept; vertex 3 unreachable | {"acyclic":true,"distance":[0,5,2,null],"parent_edge":[-1,0,2,-1]} |

## Automated tests (`test_algorithms.py`)

Describe each group briefly: boundaries (n=0, isolates, loops), parallel edges,
negative weights, full limits (n = 100000 deep chain), cycle unreachable from source,
random Kruskal/Prim comparison with brute force, repeated requests (state reset).

## Non-unique answers

Topological order, SCC labels and shortest-path witnesses are checked by validity.
`test_topo_valid_order_by_validity_not_equality` accepts an alternative valid order [0,3,1,2]
and rejects [1,0,2,3]. `test_dag_invalid_witness_is_rejected` rejects a parent_edge
that does not reproduce the claimed distance.

## pytest output

(paste the real output of `python -m pytest tests -q`)
