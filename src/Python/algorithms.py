"""Implement the six graph methods and your route helper. See the README at the repository root."""

import heapq


class DSU:
    """Disjoint set union with path compression and union by size."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            next_x = self.parent[x]
            self.parent[x] = root
            x = next_x
        return root

    def union(self, a, b):
        """Merge two sets. Return the new root size, or 0 if already merged."""
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return 0
        if self.size[root_a] < self.size[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]
        return self.size[root_a]


def dsu(request):
    n = request["n"]
    operations = request["operations"]

    sets = DSU(n)
    components = n
    largest = 1 if n > 0 else 0
    states = []

    for u, v in operations:
        new_size = sets.union(u, v)
        if new_size > 0:
            components -= 1
            if new_size > largest:
                largest = new_size
        states.append([components, largest])

    return {"states": states}


def kruskal(request):
    """Separate Kruskal implementation; return cost, edge_ids, components."""
    n = request["n"]
    edges = request["edges"]

    edge_order = sorted(range(len(edges)), key=lambda i: edges[i][2])

    sets = DSU(n)
    cost = 0
    edge_ids = []

    for i in edge_order:
        u, v, w = edges[i]
        if sets.union(u, v) > 0:  
            cost += w
            edge_ids.append(i)

    components = n - len(edge_ids)
    return {"cost": cost, "edge_ids": edge_ids, "components": components}


def prim(request):
    """Separate Prim implementation; restart for every unvisited component."""
    n = request["n"]
    edges = request["edges"]

    graph = [[] for _ in range(n)]
    for i in range(len(edges)):
        u, v, w = edges[i]
        graph[u].append((w, i, v))
        graph[v].append((w, i, u))

    visited = [False] * n
    cost = 0
    edge_ids = []
    components = 0

    for start in range(n):
        if visited[start]:
            continue

        components += 1
        visited[start] = True
        heap = []
        for item in graph[start]:
            heapq.heappush(heap, item)

        while heap:
            w, edge_id, v = heapq.heappop(heap)
            if visited[v]:
                continue
            visited[v] = True
            cost += w
            edge_ids.append(edge_id)
            for item in graph[v]:
                if not visited[item[2]]:
                    heapq.heappush(heap, item)

    return {"cost": cost, "edge_ids": edge_ids, "components": components}


def scc(request):
    """Kosaraju with two DFS passes; return component and condensation."""
    n = request["n"]
    edges = request["edges"]

    graph = [[] for _ in range(n)]
    reversed_graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        reversed_graph[v].append(u)

    visited = [False] * n
    next_index = [0] * n  
    finish_order = []

    for start in range(n):
        if visited[start]:
            continue
        visited[start] = True
        stack = [start]
        while stack:
            u = stack[-1]
            if next_index[u] < len(graph[u]):
                v = graph[u][next_index[u]]
                next_index[u] += 1
                if not visited[v]:
                    visited[v] = True
                    stack.append(v)
            else:
                finish_order.append(u)
                stack.pop()

  
    component = [-1] * n
    component_count = 0

    for start in reversed(finish_order):
        if component[start] != -1:
            continue
        component[start] = component_count
        stack = [start]
        while stack:
            u = stack.pop()
            for v in reversed_graph[u]:
                if component[v] == -1:
                    component[v] = component_count
                    stack.append(v)
        component_count += 1
    seen = set()
    condensation = []
    for u, v in edges:
        a = component[u]
        b = component[v]
        if a != b and (a, b) not in seen:
            seen.add((a, b))
            condensation.append([a, b])

    return {"component": component, "condensation": condensation}


def topological_sort(n, edges):
    """Three-state DFS (0 = white, 1 = gray, 2 = black).

    Returns (acyclic, order). If a cycle exists, order is empty.
    """
    graph = [[] for _ in range(n)]
    for edge in edges:
        graph[edge[0]].append(edge[1])

    state = [0] * n
    next_index = [0] * n
    order = []

    for start in range(n):
        if state[start] != 0:
            continue
        state[start] = 1
        stack = [start]
        while stack:
            u = stack[-1]
            if next_index[u] < len(graph[u]):
                v = graph[u][next_index[u]]
                next_index[u] += 1
                if state[v] == 1:
                    return False, []
                if state[v] == 0:
                    state[v] = 1
                    stack.append(v)
            else:
                state[u] = 2
                order.append(u)
                stack.pop()

    order.reverse()
    return True, order


def topo(request):
    """Three-state DFS and reverse finish order; return acyclic and order."""
    n = request["n"]
    edges = request["edges"]

    acyclic, order = topological_sort(n, edges)
    return {"acyclic": acyclic, "order": order}


def dag(request):
    """Whole-graph cycle check and DAG relaxation; add your own route helper."""
    n = request["n"]
    source = request["source"]
    edges = request["edges"]

    acyclic, order = topological_sort(n, edges)
    if not acyclic:
        return {"acyclic": False, "distance": [], "parent_edge": []}

    graph = [[] for _ in range(n)]
    for i in range(len(edges)):
        u, v, w = edges[i]
        graph[u].append((v, w, i))

    distance = [None] * n  
    parent_edge = [-1] * n
    distance[source] = 0

    for u in order:
        if distance[u] is None:
            continue
        for v, w, edge_id in graph[u]:
            new_dist = distance[u] + w
            if distance[v] is None or new_dist < distance[v]:
                distance[v] = new_dist
                parent_edge[v] = edge_id

    return {"acyclic": True, "distance": distance, "parent_edge": parent_edge}


def reconstruct_route(source, target, parent_edge, edges):
    """Return (vertices, edge_ids) of the route, or None if target is unreachable."""
    if target == source:
        return [source], []
    if parent_edge[target] == -1:
        return None

    vertices = [target]
    edge_ids = []
    current = target
    while current != source:
        edge_id = parent_edge[current]
        edge_ids.append(edge_id)
        current = edges[edge_id][0]  
        vertices.append(current)

    vertices.reverse()
    edge_ids.reverse()
    return vertices, edge_ids