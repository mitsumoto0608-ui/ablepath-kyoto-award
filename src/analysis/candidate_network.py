"""Pure deterministic candidate-network summaries; never derives safety or access states."""
from __future__ import annotations

from heapq import heappop, heappush
from math import hypot, isfinite
from numbers import Real

M7_API_FIELDS = (
    "clear_width_m",
    "left_buildings",
    "right_buildings",
    "variant",
    "official_closure",
    "hazard_data_status",
)
M7_BUILDING_FIELDS = ("height_m", "setback_m", "damage_state", "debris_present")
M7_VARIANTS = {"mean_case", "sensitivity_high_case"}
M7_DAMAGE_STATES = {"COLLAPSED", "DAMAGED"}
M7_HAZARD_DATA_STATUSES = {"KNOWN", "UNKNOWN"}
CONNECTED_REASON = "Candidate connectivity only; accessibility, safety, and operation are unconfirmed."
DISCONNECTED_REASON = "No candidate-network connection exists between the selected nodes; accessibility, safety, and operation are unconfirmed."


def _is_finite_real(value, *, positive=False):
    return (
        not isinstance(value, bool)
        and isinstance(value, Real)
        and isfinite(value)
        and (value > 0 if positive else value >= 0)
    )


def _building_missing(building, path):
    if not isinstance(building, dict):
        return [path]
    missing = [f"{path}.{field}" for field in M7_BUILDING_FIELDS if field not in building]
    if "height_m" in building and not _is_finite_real(building["height_m"], positive=True):
        missing.append(f"{path}.height_m")
    if "setback_m" in building and not _is_finite_real(building["setback_m"]):
        missing.append(f"{path}.setback_m")
    damage_state = building.get("damage_state")
    if "damage_state" in building and (
        not isinstance(damage_state, str) or damage_state not in M7_DAMAGE_STATES
    ):
        missing.append(f"{path}.damage_state")
    debris_present = building.get("debris_present")
    if "debris_present" in building and type(debris_present) is not bool:
        missing.append(f"{path}.debris_present")
    if damage_state == "DAMAGED" and debris_present is True:
        missing.append(f"{path}.damage_state+debris_present")
    return missing


def _side_missing(value, field):
    if not isinstance(value, list) or len(value) > 1:
        return [field]
    missing = []
    for index, building in enumerate(value):
        missing.extend(_building_missing(building, f"{field}[{index}]"))
    return missing


def _m7_structural_missing(props):
    missing = [field for field in M7_API_FIELDS if field not in props]
    if "clear_width_m" in props and not _is_finite_real(props["clear_width_m"]):
        missing.append("clear_width_m")
    for field in ("left_buildings", "right_buildings"):
        if field in props:
            missing.extend(_side_missing(props[field], field))
    if "variant" in props and (
        not isinstance(props["variant"], str) or props["variant"] not in M7_VARIANTS
    ):
        missing.append("variant")
    if "official_closure" in props and (
        props["official_closure"] is not None and type(props["official_closure"]) is not bool
    ):
        missing.append("official_closure")
    if "hazard_data_status" in props and (
        not isinstance(props["hazard_data_status"], str)
        or props["hazard_data_status"] not in M7_HAZARD_DATA_STATUSES
    ):
        missing.append("hazard_data_status")
    return list(dict.fromkeys(missing))


def _m7_evidence_missing(props):
    provenance = props.get("m7_provenance")
    if not isinstance(provenance, dict):
        return [f"m7_provenance.{field}" for field in M7_API_FIELDS]
    missing = []
    for field in M7_API_FIELDS:
        record = provenance.get(field)
        path = f"m7_provenance.{field}"
        if not isinstance(record, dict):
            missing.append(path)
            continue
        for receipt_field in ("source_id", "revision_id"):
            if not isinstance(record.get(receipt_field), str) or not record[receipt_field].strip():
                missing.append(f"{path}.{receipt_field}")
        source_sha256 = record.get("source_sha256")
        if (
            not isinstance(source_sha256, str)
            or len(source_sha256) != 64
            or any(character not in "0123456789abcdef" for character in source_sha256)
        ):
            missing.append(f"{path}.source_sha256")
        if record.get("evidence_status") != "SOURCE_TRACEABLE":
            missing.append(f"{path}.evidence_status")
        if field in ("left_buildings", "right_buildings"):
            if record.get("coverage_status") != "COMPLETE":
                missing.append(f"{path}.coverage_status")
            observed_count = record.get("observed_count")
            buildings = props.get(field)
            if (
                isinstance(observed_count, bool)
                or not isinstance(observed_count, int)
                or observed_count < 0
                or not isinstance(buildings, list)
                or observed_count != len(buildings)
            ):
                missing.append(f"{path}.observed_count")
    return list(dict.fromkeys(missing))


def _m7_readiness(edge_id, props):
    structural_missing = _m7_structural_missing(props)
    evidence_missing = _m7_evidence_missing(props)
    structurally_callable = not structural_missing
    evidence_ready = structurally_callable and not evidence_missing
    missing_fields = structural_missing + [
        field for field in evidence_missing if field not in structural_missing
    ]
    if evidence_ready:
        reason = "M7 inputs are structurally callable and evidence-ready; M7 was not run."
    elif structurally_callable:
        reason = "M7 inputs are structurally callable, but source-traceable evidence is incomplete; M7 was not run."
    else:
        reason = "M7 inputs are not structurally callable; M7 was not run."
    return {
        "edge_id": edge_id,
        "status": "NOT_COMPUTED",
        "m7_api_structurally_callable": structurally_callable,
        "m7_evidence_ready": evidence_ready,
        "m7_computed": False,
        "m7_result": None,
        "missing_fields": missing_fields,
        "reason": reason,
    }


def assess_m7_readiness(edge_id: str, props: dict) -> dict:
    """Return the frozen M7 API/evidence gate without running the M7 model."""
    if not isinstance(edge_id, str) or not edge_id:
        raise ValueError("edge_id must be a non-empty string")
    if not isinstance(props, dict):
        raise TypeError("M7 edge properties must be a dict")
    return _m7_readiness(edge_id, props)

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
    readiness = [assess_m7_readiness(edge_id, props) for edge_id, props in sorted(normalized_edges)]
    return {"topology": {"nodes": len(nodes), "edges": len(edges), "connected_components": components}, "path": path, "hazard_overlap": {"status": "NOT_CONNECTED", "reason": "No trusted official hazard geometry is connected; no closure is derived."}, "m7": {"ready_edge_count": sum(row["m7_evidence_ready"] for row in readiness), "computed_edge_count": sum(row["m7_computed"] for row in readiness), "readiness": readiness}, "m6": {"status": "NOT_COMPUTED", "reason": "Human freeze is pending."}}
