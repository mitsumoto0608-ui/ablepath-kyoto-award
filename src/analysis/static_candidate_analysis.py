"""Canonical source-side construction and validation of static candidate analysis."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from src.analysis.candidate_network import (
    build_candidate_graph,
    build_path_matrix,
    candidate_components,
    choose_selectable_node_ids,
)


def canonical_text_sha256_bytes(payload: bytes) -> str:
    """Hash canonical Git text bytes independent of Windows checkout newlines."""
    return sha256(payload.replace(b"\r\n", b"\n")).hexdigest()


def canonical_text_sha256(path: Path) -> str:
    return canonical_text_sha256_bytes(Path(path).read_bytes())


CONNECTED_REASON = "Candidate connectivity only; accessibility, safety, and operation are unconfirmed."
DISCONNECTED_REASON = "No candidate-network connection exists between the selected nodes; accessibility, safety, and operation are unconfirmed."
CITY_INPUTS = (
    {"id": "kyoto_kiyomizu", "nodes": "cities/kyoto_kiyomizu/graph/real/candidate_nodes.geojson", "edges": "cities/kyoto_kiyomizu/graph/real/candidate_edges.geojson", "source": "openstreetmap_kiyomizu_named_corridor_20260830", "snapshot": "2026-08-30T00:00:00Z"},
    {"id": "kyoto_arashiyama", "nodes": "cities/kyoto_arashiyama/graph/walk_nodes.real.geojson", "edges": "cities/kyoto_arashiyama/graph/walk_edges.real.geojson", "source": "openstreetmap-overpass-arashiyama-20260829", "snapshot": "2026-08-29T00:00:00Z"},
    {"id": "fujisawa_enoshima", "nodes": "cities/fujisawa_enoshima/graph/candidate_walk_nodes.real.geojson", "edges": "cities/fujisawa_enoshima/graph/candidate_walk_edges.real.geojson", "source": "OSM_CANDIDATE_SOURCE", "snapshot": "2026-08-30T00:00:00Z"},
)


def authoritative_report_paths(root: Path, city_id: str) -> dict[str, Path]:
    """Return every source file whose bytes directly shape official analysis evidence."""
    paths = {
        "promotion_sha256": root / "reports/OFFICIAL_LOCAL_ARTIFACT_PROMOTION_V2.json",
        "plateau_sha256": root / "reports/PLATEAU_BUILDING_EVIDENCE_V1.json",
        "m7_sha256": root / "reports/M7_REAL_EDGE_STATUS.json",
    }
    if city_id.startswith("kyoto_"):
        group = "kiyomizu_gion" if city_id == "kyoto_kiyomizu" else "arashiyama"
        paths.update({
            "kyoto_status_sha256": root / "reports/KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json",
            "terrain_inventory_sha256": root / f"cities/{city_id}/terrain/official/dem_product_inventory.csv",
            "kyoto_parity_sha256": root / "reports/KYOTO_PARITY_STATUS.json",
            "kyoto_m7_pilot_sha256": root / "reports/KYOTO_M7_DEEP_PILOT_STATUS.json",
            "kyoto_facility_sha256": root / "inputs/staging/KYOTO-OFFICIAL-PARITY-V1/facility_records.json",
            "kyoto_facility_category_status_sha256": root / "inputs/staging/KYOTO-OFFICIAL-PARITY-V1/facility_category_status.json",
            "kyoto_flood_display_sha256": root / f"inputs/staging/KYOTO-OFFICIAL-PARITY-V1/a31b_{group}_display.geojson",
            "plateau_inventory_sha256": root / "inputs/staging/PLATEAU-BUILDING-EVIDENCE-V1/PLATEAU_BUILDING_AOI_INVENTORY.csv",
        })
    if city_id == "fujisawa_enoshima":
        paths.update({
            "terrain_inventory_sha256": root / f"cities/{city_id}/terrain/official/dem_product_inventory.csv",
            "facility_receipt_sha256": root / f"cities/{city_id}/facilities/official/facility_source_receipt.json",
            "facility_table_sha256": root / f"cities/{city_id}/facilities/official/FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json",
            "earthquake_inventory_sha256": root / f"cities/{city_id}/hazards/official/earthquake_scenario_inventory.csv",
            "liquefaction_inventory_sha256": root / f"cities/{city_id}/hazards/official/liquefaction_scenario_inventory.csv",
        })
    return paths


def summarize_m7_readiness(official_evidence: dict, readiness: list[dict]) -> dict:
    """Copy the authoritative reasoned-null M7 counts and rows without running M7."""
    m7 = official_evidence.get("m7") if isinstance(official_evidence, dict) else None
    if not isinstance(m7, dict):
        raise ValueError("official M7 summary is required")
    ready = m7.get("evidence_ready_count")
    computed = m7.get("computed_count")
    if isinstance(ready, bool) or not isinstance(ready, int) or ready < 0:
        raise ValueError("official M7 evidence-ready count is invalid")
    if isinstance(computed, bool) or not isinstance(computed, int) or computed < 0:
        raise ValueError("official M7 computed count is invalid")
    if not isinstance(readiness, list):
        raise ValueError("M7 readiness rows must be a list")
    if any(
        not isinstance(row, dict)
        or row.get("m7_evidence_ready") is not False
        or row.get("m7_computed") is not False
        or row.get("m7_result") is not None
        for row in readiness
    ):
        raise ValueError("M7 readiness rows contain an unsupported promotion")
    if ready != sum(row["m7_evidence_ready"] is True for row in readiness):
        raise ValueError("official M7 summary does not match readiness rows")
    if computed != sum(row["m7_computed"] is True for row in readiness):
        raise ValueError("official M7 summary does not match computed rows")
    return {
        "status": m7.get("status"),
        "ready_edge_count": ready,
        "computed_edge_count": computed,
    }


def build_static_candidate_analysis(
    context: dict,
    nodes: list[dict],
    edges: list[dict],
    official_evidence: dict,
    m7_readiness: list[dict],
) -> dict:
    """Build the complete deterministic analysis artifact consumed by the viewer."""
    if not isinstance(nodes, list):
        raise ValueError("candidate nodes must be a list")
    if any(
        not isinstance(edge, dict)
        or edge.get("geometry", {}).get("type") != "LineString"
        for edge in edges
    ):
        raise ValueError("static candidate edge must be a LineString")
    adjacency, _ = build_candidate_graph(edges)
    node_ids = []
    for node in nodes:
        node_id = node.get("properties", {}).get("node_id") if isinstance(node, dict) else None
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("candidate node_id must be a non-empty string")
        node_ids.append(node_id)
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("candidate node_id values must be unique")
    if not set(adjacency).issubset(node_ids):
        raise ValueError("candidate edge endpoint is not present in the node artifact")
    components = candidate_components(adjacency, node_ids)
    selectable = choose_selectable_node_ids(edges, node_ids)
    path_matrix = build_path_matrix(edges, selectable)
    start = selectable[0] if selectable else None
    end = selectable[1] if len(selectable) > 1 else None
    path_fixture = path_matrix.get(f"{start}__{end}")
    if path_fixture is None:
        path_fixture = {
            "start_node_id": start,
            "end_node_id": end,
            "status": "CONNECTED",
            "unit": "coordinate_degree",
            "edge_ids": [],
            "geometric_length": 0,
            "reason": CONNECTED_REASON,
        }
    m7_summary = summarize_m7_readiness(official_evidence, m7_readiness)
    result = {
        "topology": {
            "node_count": len(node_ids),
            "edge_count": len(edges),
            "connected_components": len(components),
            "topology_status": "CANDIDATE_REVIEW_REQUIRED",
        },
        "selectable_node_ids": selectable,
        "path_matrix": path_matrix,
        "path_fixture": path_fixture,
        "hazard_overlap": {
            "status": "NOT_CONNECTED",
            "value": None,
            "reason": "No trusted official hazard geometry is connected; no closure is derived.",
        },
        "m7": m7_summary,
        "m6": {"status": "NOT_COMPUTED", "reason": "M6/profile evaluation is not connected."},
    }
    artifact = {
        "analysis_id": f"{context['city_id']}:candidate-topology-v2",
        "analysis_type": "CANDIDATE_TOPOLOGY_STATIC_FIXTURE",
        "city_id": context["city_id"],
        "source_artifact_ids": context["source_artifact_ids"],
        "source_revision_ids": context["source_revision_ids"],
        "input_sha256": context["input_sha256"],
        "algorithm": "deterministic-undirected-dijkstra-coordinate-degree",
        "algorithm_version": "2.0.0",
        "parameters": {
            "coordinate_unit": "coordinate_degree",
            "input_binding": "sha256(node_geojson_bytes + 0x00 + edge_geojson_bytes); input order=node,edge",
            "tie_break": "lexical ordered edge-ID tuple",
        },
        "generated_at": context["snapshot_at"],
        "deterministic": True,
        "result": result,
        "official_evidence": official_evidence,
        "limitations": [
            "Candidate connectivity only",
            "coordinate_degree is not a geographic or meter distance",
            "Hazard, M7, M6, accessibility, safety, operation, and administrative validation are unconnected or not computed",
        ],
        "provenance": {
            "source_class": "VGI",
            "source_id": context["source_id"],
            "input_binding": "node bytes then NUL then edge bytes",
            "input_artifacts": context["source_artifact_ids"],
            "input_hashes": context["input_hashes"],
        },
        "safety_claim": False,
        "accessibility_claim": False,
        "admin_validated": False,
    }
    artifact.update(result)
    artifact["m7"] = {**result["m7"], "readiness": m7_readiness}
    artifact["interpretation"] = "Candidate network connectivity only; accessibility, safety, and operation are unconfirmed."
    return artifact


def validate_static_candidate_analysis(repo_root: Path, artifact: dict) -> dict:
    """Fail closed if canonical source bytes, report bindings, or safety truth are stale."""
    root = Path(repo_root).resolve()
    city_id = artifact.get("city_id") if isinstance(artifact, dict) else None
    try:
        city = next(item for item in CITY_INPUTS if item["id"] == city_id)
    except StopIteration as exc:
        raise ValueError("unsupported static analysis city") from exc
    node_bytes = (root / city["nodes"]).read_bytes()
    edge_bytes = (root / city["edges"]).read_bytes()
    expected_input = sha256(node_bytes + b"\0" + edge_bytes).hexdigest()
    if artifact.get("input_sha256") != expected_input:
        raise ValueError(f"{city_id} static analysis input SHA-256 is stale")
    if artifact.get("provenance", {}).get("input_hashes") != {
        "node_sha256": sha256(node_bytes).hexdigest(),
        "edge_sha256": sha256(edge_bytes).hexdigest(),
    }:
        raise ValueError(f"{city_id} static analysis input hash provenance is stale")
    nodes = json.loads(node_bytes)["features"]
    edges = json.loads(edge_bytes)["features"]
    revisions = sorted(
        {
            feature.get("properties", {}).get("revision_id")
            for feature in [*nodes, *edges]
            if feature.get("properties", {}).get("revision_id")
        }
    )
    if artifact.get("source_artifact_ids") != [city["nodes"], city["edges"]]:
        raise ValueError(f"{city_id} static analysis source artifacts are stale")
    if artifact.get("source_revision_ids") != revisions:
        raise ValueError(f"{city_id} static analysis source revisions are stale")
    official = artifact.get("official_evidence", {})
    if any(
        value is not False
        for value in (
            artifact.get("safety_claim"),
            artifact.get("accessibility_claim"),
            artifact.get("admin_validated"),
            official.get("safe_route_claim"),
            official.get("accessibility_claim"),
            official.get("admin_validated"),
        )
    ):
        raise ValueError("static analysis contains a forbidden safety or validation promotion")
    for key, path in authoritative_report_paths(root, city_id).items():
        expected = canonical_text_sha256(path)
        if official.get("source_hashes", {}).get(key) != expected:
            raise ValueError(f"{city_id} static analysis report SHA-256 is stale: {key}")
    if official.get("m7", {}).get("edge_receipts_source_sha256") != canonical_text_sha256(
        root / "reports/M7_ALL_EDGE_EVIDENCE_READINESS.json"
    ):
        raise ValueError(f"{city_id} static analysis M7 readiness source is stale")
    if city_id.startswith("kyoto_"):
        group = "kiyomizu_gion" if city_id == "kyoto_kiyomizu" else "arashiyama"
        point_path = root / f"inputs/staging/KYOTO-OFFICIAL-PARITY-V1/facility_points_{group}.geojson"
        point_hash = canonical_text_sha256(point_path)
        display = official.get("facility", {}).get("display_layer", {})
        if display.get("artifact_sha256") != point_hash or display.get("copied_sha256") != point_hash:
            raise ValueError(f"{city_id} static facility display binding is stale")
    m7_report = json.loads((root / "reports/M7_REAL_EDGE_STATUS.json").read_text(encoding="utf-8"))
    m7 = artifact.get("m7", {})
    if (
        m7.get("ready_edge_count") != m7_report.get("evidence_ready_count")
        or m7.get("computed_edge_count") != m7_report.get("computed_count")
        or artifact.get("result", {}).get("m7") != {
            key: m7.get(key) for key in ("status", "ready_edge_count", "computed_edge_count")
        }
        or len(m7.get("readiness", [])) != official.get("m7", {}).get("city_edge_count")
        or any(
            row.get("m7_evidence_ready") is not False
            or row.get("m7_computed") is not False
            or row.get("m7_result") is not None
            for row in m7.get("readiness", [])
        )
    ):
        raise ValueError(f"{city_id} static analysis M7 summary is stale or promoted")
    return artifact
