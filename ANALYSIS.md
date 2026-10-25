# Assignment 3: Graph Algorithms. Analysis

Language: Python 3.14.2 (Windows 11). Code: `src/Python/algorithms.py`.

## Build, run and test commands

```powershell
python tools/run.py --setup
python tools/run.py --check                          # 36 public cases
python tools/run.py --input tests/my_cases.jsonl     # own JSON Lines cases
python -m pip install pytest
python -m pytest tests -q                            # own automated tests
python tools/bench.py                                # Kruskal vs Prim benchmark
```

## General notes

**State reset.** Every method is a function that builds all its data (parent arrays,
adjacency lists, heaps, visited arrays) from the request. There are no globals, so a
request cannot affect the next one. `test_mixed_requests_state_reset` runs mixed requests
twice and in reverse order in one process and compares the results.

**Deep DFS.** Python's recursion limit would fail on a chain of 100000 vertices, so all DFS
passes (SCC pass 1 and 2, topological sort) use an explicit stack. `next_index[u]` stores
which neighbour of `u` is checked next, so a suspended vertex never rescans its neighbours.
The tests use a chain of 100000 vertices.

## DSU (`dsu`)

- **Steps.** Every vertex starts as its own root with size 1. For each pair `[u,v]` find both
  roots, attach the smaller tree to the larger one, add sizes, and record `[components, largest]`.
- **Invariant.** `parent` forms a forest. `size[r]` is the number of vertices in the tree
  of root `r`. `components` is the number of roots. `largest` is the maximum size of any root.
- **Correctness.** Union only merges two different roots, so two vertices share a root exactly
  when a chain of processed operations connects them. Path compression only changes the
  parent of a vertex to its root and does not change the partition. Repeated and self
  unions have equal roots, so nothing changes.
- **Boundary cases.** n=0 gives `states=[]`; initially `largest=1` for n>0; loops;
  repeated unions.
- **Complexity.** Time O(n + q α(n)), memory O(n + q) with the states.

## Kruskal (`kruskal`)

- **Steps.** Sort edge IDs by weight (the edges themselves stay in place, so IDs stay original).
  For each edge in order, take it if `union(u,v)` merges two different components.
- **Invariant.** The selected edges form a forest, and it is contained in some minimum
  spanning forest.
- **Correctness.** Cut property: the lightest edge crossing between two different components
  can be added to a minimum forest. Loops and edges inside one component are skipped.
  Negative weights need no special case, because only the order matters.
- **Boundary cases.** n=0; isolates (counted by `components = n - selected`); loops; parallel
  edges; totals beyond 32 bits (Python integers).
- **Complexity.** Time O(n + m log m), memory O(n + m).

## Prim (`prim`)

- **Steps.** Build adjacency lists with `(weight, edge_id, neighbour)`. For every unvisited
  start vertex begin a new component (counter +1), push its edges to a heap, repeatedly
  pop the lightest edge and, if it leads to an unvisited vertex, take it and push that
  vertex's edges.
- **Invariant.** The visited part of the current component is a tree that is part of a minimum
  spanning tree of that component. The heap holds the edges leaving it, plus stale edges.
- **Correctness.** The popped lightest edge crossing the cut (visited, unvisited) is safe by the
  cut property. Stale edges to visited vertices are skipped. The restart for every
  unvisited vertex gives a forest, and isolates become components with no edges.
- **Boundary cases.** Same as Kruskal; loops lead to a visited vertex and are skipped.
- **Complexity.** Lazy heap: up to 2m entries, time O(n + m log m), memory O(n + m).

## SCC, Kosaraju (`scc`)

- **Steps.** Build the graph and its transpose. Pass 1: iterative DFS on the original graph,
  record vertices in finish order. Pass 2: take vertices in decreasing finish order, and
  DFS on the transpose; every tree is one component. Then collect distinct pairs
  `(component[u], component[v])` with different labels using a set.
- **Invariant.** In pass 2 every started DFS tree contains exactly the vertices of one SCC.
- **Correctness.** The vertex with the largest finish time lies in a source component of the
  condensation. In the transpose, edges between components are reversed, so DFS from it
  cannot leave its component. Remove it and repeat.
- **Boundary cases.** n=0; isolates; self-loops (internal, so not in the condensation);
  duplicate edges give one condensation pair.
- **Complexity.** Time O(n + m), memory O(n + m).

## Topological sort (`topo`)

- **Steps.** Three-state DFS (0 unvisited, 1 active, 2 finished) from every unvisited vertex.
  An edge to an active vertex means a cycle, so return `acyclic=false, order=[]`.
  Otherwise reverse the finish order.
- **Invariant.** Active vertices are exactly the vertices on the current DFS stack.
- **Correctness.** An edge to an active vertex closes a cycle along the stack. Without such
  edges, every edge `u->v` has `v` finished before `u`, so after reversing `u` comes
  before `v`. An edge to a finished vertex is not a cycle.
- **Boundary cases.** n=0; self-loop is a cycle; duplicate edges; several components.
- **Complexity.** Time O(n + m), memory O(n + m).

## DAG shortest paths (`dag`) and route helper

- **Steps.** Run the topological sort on the **whole** graph. If a cycle exists (even one that
  the source cannot reach) return `acyclic=false` with empty arrays. Otherwise set
  `distance[source]=0` and relax outgoing edges of vertices in topological order, skipping
  unreachable ones (`None`). `parent_edge[v]` is the original ID of the edge that gave the
  best distance.
- **Invariant.** When `u` is processed, `distance[u]` is final, because all its predecessors
  came earlier in the order.
- **Correctness.** Every path follows the topological order, so relaxing in that order finds
  the shortest path, also with negative weights. Strict `<` keeps the first of equal
  (tied or parallel) edges.
- **Boundary cases.** n=1; unreachable vertices (`null`, -1); negative weights; parallel and
  tied edges; cycle outside the source's reach.
- **Complexity.** Time O(n + m), memory O(n + m).
- **Helper `reconstruct_route(source, target, parent_edge, edges)`.** Returns
  `(vertices, edge_ids)`. For an unreachable target it returns `None` (documented
  no-route result). Time and output O(L).

### Route helper calls

Graph A: `edges = [[0,1,5],[0,1,5],[1,2,-3],[0,2,10]]`, source 0, `parent_edge = [-1,0,2,-1]`.

| Call | Result | Check |
|---|---|---|
| `reconstruct_route(0, 2, ...)` | vertices `[0,1,2]`, edge IDs `[0,2]` | 0->1 then 1->2, weight 5 + (-3) = 2 = distance |
| `reconstruct_route(0, 0, ...)` | `([0], [])` | the source |
| `reconstruct_route(0, 3, ...)` | `None` | vertex 3 is unreachable |
| `reconstruct_route(0, 1, ...)` | vertices `[0,1]`, edge ID `0` | edges 0 and 1 are parallel and tied, the first is kept |

Assignment example: `edges = [[0,1,3],[0,2,8],[1,2,-7],[2,3,4]]`, `parent_edge = [-1,0,2,3,-1]`.
Route to 3: vertices `[0,1,2,3]`, edge IDs `[0,2,3]`, weight 3 - 7 + 4 = 0 = `distance[3]`.
Directions were checked in `test_examples_from_assignment`.

## Benchmark: Kruskal vs Prim

- **Command.** `python tools/bench.py`. Output saved in `tools/bench_output.txt`.
- **Environment.** Python 3.14.2, Windows 11, Intel64 Family 6 Model 186, 12 logical cores
  (from the benchmark output).
- **Inputs.** `random.Random(12345)`; a chain of n-1 edges for connectivity plus random edges
  (loops and parallel edges possible), weights in [-10^9, 10^9]. Both methods get the same
  graph at each size.
- **Timer and warm-up.** `time.perf_counter`; one warm-up run per method, 5 timed runs.
- **Boundary.** Only the algorithm call is timed. Graph generation, building the request,
  JSON parsing and I/O are excluded for both methods. Python has no compilation step.
- **Correctness first.** Before timing, the script asserts equal cost and component count and
  checks that each selected edge set is acyclic, has n - components edges and sums to the cost.

| n | m | Kruskal runs (s) | Kruskal median | Prim runs (s) | Prim median |
|---|---|---|---|---|---|
| 1000 | 5000 | <0.0026, 0.0026, 0.0024, 0.0021, 0.0021> | <0.0024s> | <0.003, 0.0029, 0.003, 0.0029, 0.0029> | <0.0029s> |
| 10000 | 50000 | <0.0318, 0.0399, 0.0351, 0.0362, 0.0372> | <0.0362s> | <0.1851, 0.1426, 0.1054, 0.1006, 0.183> | <0.1426s> |
| 100000 | 250000 | <0.3398, 0.3257, 0.3215, 0.3416, 0.4079> | <0.3398s> | <0.6624, 0.9427, 0.8606, 0.778, 0.7549> | <0.7780s> |

**Observations.**  Kruskal was faster than Prim at all three sizes,
by roughly a factor of 2.4 to 3.2 in my runs. Both have the same asymptotic bound
O(m log m), so the difference is in constants. A possible explanation (not measured separately):
sorting runs in C inside Python, while Prim performs many Python-level `heappush` and `heappop`
calls on a heap of up to 2m entries.

**Limitations.** One machine, one graph per size, 5 runs, Python only, a random graph with a chain
(results may differ for dense or special graphs). One Prim run at the largest size was an outlier
(about 1.18 s against about 0.62 to 0.70 s), probably system noise, so medians are used.

## Sources and AI assistance

I used the lecture notes and the assignment specification. I used Chat GPT to ask git commits and ask about correctness of algorithms and I asked to write examples to see what the difference. I verified the work by
running the 36 public checks, my own JSON Lines cases, 21 automated pytest tests and the
benchmark on my machine.