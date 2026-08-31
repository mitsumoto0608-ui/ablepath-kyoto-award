"""Pure deterministic candidate-network summaries; never derives safety or access states."""
from __future__ import annotations

from heapq import heappop, heappush
from math import hypot, isfinite

M7_FIELDS = ("clear_width_m", "building_height_m", "setback_m", "damage_state", "debris_present", "variant", "official_closure", "hazard_data_status")
CONNECTED_REASON = "Candidate connectivity only; accessibility, safety, and operation are unconfirmed."
DISCONNECTED_REASON = "No candidate-network connection exists between the selected nodes; accessibility, safety, and operation are unconfirmed."

def _node_ids(nodes):
    ids = []
    for node in nodes:
        node_id = node.get("properties", {}).get("node_id") if isinstance(node, dict) else None
        if not isinstance(node_id, str) or not node_id: raise ValueError("candidate node_id must be a non-empty string")
        ids.append(node_id)
    if len(ids) != len(set(ids)): raise ValueError("candidate node_id values must be unique")
    return sorted(ids)

def _edge_length(edge):
    coords = edge.get("geometry", {}).get("coordinates") if isinstance(edge, dict) else None
    if not isinstance(coords, list) or len(coords) < 2: raise ValueError("candidate edge must have at least two coordinate positions")
    length = 0.0
    for first, second in zip(coords, coords[1:]):
        if not (isinstance(first, list) and isinstance(second, list) and len(first) >= 2 and len(second) >= 2): raise ValueError("candidate edge coordinates must be positions")
        if not all(isinstance(value, (int, float)) and isfinite(value) for value in [*first[:2], *second[:2]]): raise ValueError("candidate edge coordinates must be finite")
        length += hypot(second[0] - first[0], second[1] - first[1])
    if length <= 0: raise ValueError("candidate edge must have non-zero coordinate-degree length")
    return length

def summarize(nodes: list[dict], edges: list[dict], start: str, end: str) -> dict:
    """Return deterministic candidate-only topology/path and reasoned-null readiness."""
    if not isinstance(nodes, list) or not isinstance(edges, list): raise ValueError("candidate nodes and edges must be lists")
    node_ids = _node_ids(nodes); known = set(node_ids)
    if start not in known or end not in known: raise ValueError("selected node is not in the candidate graph")
    adjacency = {node_id: [] for node_id in node_ids}; edge_ids = set(); normalized_edges = []
    for edge in edges:
        props = edge.get("properties", {}) if isinstance(edge, dict) else {}
        edge_id, a, b = props.get("edge_id"), props.get("from_node"), props.get("to_node")
        if not all(isinstance(value, str) and value for value in (edge_id, a, b)): raise ValueError("candidate edge identifiers and endpoints must be non-empty strings")
        if edge_id in edge_ids: raise ValueError("candidate edge_id values must be unique")
        if a not in known or b not in known: raise ValueError("edge endpoint is not a candidate node")
        if a == b: raise ValueError("candidate edge cannot have the same endpoint twice")
        edge_ids.add(edge_id); length = _edge_length(edge)
        adjacency[a].append((b, edge_id, length)); adjacency[b].append((a, edge_id, length)); normalized_edges.append((edge_id, props))
    for neighbours in adjacency.values(): neighbours.sort(key=lambda row: (row[1], row[0]))
    unseen, components = set(node_ids), 0
    while unseen:
        components += 1; pending = [min(unseen)]; unseen.remove(pending[0])
        while pending:
            current = pending.pop()
            for nxt, _, _ in adjacency[current]:
                if nxt in unseen: unseen.remove(nxt); pending.append(nxt)
    queue = [(0.0, (), start)]; previous = {start: None}; best = {start: (0.0, ())}
    while queue:
        cost, route, current = heappop(queue)
        if (cost, route) != best.get(current): continue
        for nxt, edge_id, length in adjacency[current]:
            candidate = (cost + length, route + (edge_id,))
            if candidate < best.get(nxt, (float("inf"), ())):
                best[nxt] = candidate; previous[nxt] = (current, edge_id, length); heappush(queue, (candidate[0], candidate[1], nxt))
    if end in previous:
        route, cursor = [], end
        while previous[cursor] is not None: cursor, edge_id, _ = previous[cursor]; route.append(edge_id)
        path = {"status": "CONNECTED", "edge_ids": list(reversed(route)), "geometric_length": best[end][0], "unit": "coordinate_degree", "reason": CONNECTED_REASON}
    else:
        path = {"status": "DISCONNECTED", "edge_ids": [], "geometric_length": None, "unit": "coordinate_degree", "reason": DISCONNECTED_REASON}
    readiness = [{"edge_id": edge_id, "status": "NOT_COMPUTED", "m7_result": None, "missing_fields": [field for field in M7_FIELDS if props.get(field) in (None, "UNKNOWN", "")], "reason": "Required source-traceable M7 inputs are incomplete."} for edge_id, props in sorted(normalized_edges)]
    return {"topology": {"nodes": len(nodes), "edges": len(edges), "connected_components": components}, "path": path, "hazard_overlap": {"status": "NOT_CONNECTED", "reason": "No trusted official hazard geometry is connected; no closure is derived."}, "m7": {"ready_edge_count": 0, "computed_edge_count": 0, "readiness": readiness}, "m6": {"status": "NOT_COMPUTED", "reason": "Human freeze is pending."}}
