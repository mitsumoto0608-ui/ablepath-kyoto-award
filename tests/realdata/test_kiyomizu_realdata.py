"""Acceptance checks for the Kyoto Kiyomizu source-traceable data lane."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from src.citypacks.realdata import load_validated_geometry_manifest


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "cities" / "kyoto_kiyomizu"
REAL = PACK / "realdata"
MANIFEST = REAL / "artifact_manifest.v2.json"


def _json(relative: str) -> dict:
    return json.loads((PACK / relative).read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_osm_manifest_issues_v2_geometry_capability() -> None:
    """[source_conformance] fixed query/raw/normalized bytes must be hash-bound by v2."""
    capability = load_validated_geometry_manifest(
        MANIFEST,
        trusted_root=PACK,
        expected_city_id="kyoto_kiyomizu",
    )
    artifact_ids = tuple(dict.fromkeys(record.artifact_id for record in capability.records))
    assert artifact_ids == ("kiyomizu_osm_named_corridor_20260830",)
    assert len(capability.feature_ids_for(artifact_ids[0])) == 17


def test_retained_osm_response_is_fixed_time_bounded_and_minimal() -> None:
    """[source_conformance] retained response contains only the seven named corridor groups."""
    query_path = PACK / "sources" / "queries" / "osm_corridor_20260830.overpassql"
    raw_path = PACK / "sources" / "retained" / "osm_corridor_20260830.raw.json"
    query = query_path.read_text(encoding="utf-8")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    manifest = _json("realdata/artifact_manifest.v2.json")
    records = manifest["artifacts"]
    assert '[date:"2026-08-30T00:00:00Z"]' in query
    assert "(34.9948,135.7775,35.0046,135.7850)" in query
    assert raw_path.stat().st_size < 100_000
    ways = [element for element in raw["elements"] if element["type"] == "way"]
    nodes = [element for element in raw["elements"] if element["type"] == "node"]
    assert len(ways) == 17 and len(nodes) == 142
    assert {way["tags"]["name"] for way in ways} == {
        "東大路通", "ねねの小径", "一年坂", "二年坂", "三年坂", "清水坂", "八坂通"
    }
    assert {record["source_sha256"] for record in records} == {_sha(raw_path)}
    assert {record["retrieval_query_sha256"] for record in records} == {_sha(query_path)}


def test_candidate_graph_is_derived_without_inventing_accessibility_values() -> None:
    """[source_conformance] 17 ways split only at shared OSM IDs; width/slope/step stay null."""
    nodes_doc = _json("graph/real/candidate_nodes.geojson")
    edges_doc = _json("graph/real/candidate_edges.geojson")
    nodes = nodes_doc["features"]
    edges = edges_doc["features"]
    node_by_id = {feature["properties"]["node_id"]: feature for feature in nodes}
    assert len(nodes) == 21 and len(node_by_id) == 21
    assert len(edges) == 19
    assert [feature["id"] for feature in nodes] == sorted(feature["id"] for feature in nodes)
    assert [feature["id"] for feature in edges] == sorted(feature["id"] for feature in edges)
    for feature in edges:
        props = feature["properties"]
        assert props["topology_status"] == "CANDIDATE"
        assert props["accessibility_state"] == "UNKNOWN"
        assert props["base_clear_width_m"] is None
        assert props["running_slope"] is None
        assert props["step_height_m"] is None
        assert props["operation_status"] == "UNKNOWN"
        assert props["from_node"] in node_by_id and props["to_node"] in node_by_id
        assert feature["geometry"]["coordinates"][0] == node_by_id[props["from_node"]]["geometry"]["coordinates"]
        assert feature["geometry"]["coordinates"][-1] == node_by_id[props["to_node"]]["geometry"]["coordinates"]


def test_topology_qa_matches_graph_and_keeps_crossings_non_connecting() -> None:
    """[software_correctness] QA counts are recomputable and planar crossing never adds a node."""
    nodes = _json("graph/real/candidate_nodes.geojson")["features"]
    edges = _json("graph/real/candidate_edges.geojson")["features"]
    report = _json("graph/real/topology_qa.json")
    node_ids = [feature["properties"]["node_id"] for feature in nodes]
    edge_ids = [feature["properties"]["edge_id"] for feature in edges]
    endpoint_counts = Counter(
        endpoint
        for edge in edges
        for endpoint in (edge["properties"]["from_node"], edge["properties"]["to_node"])
    )
    assert report["counts"]["duplicate_node_ids"] == len(node_ids) - len(set(node_ids)) == 0
    assert report["counts"]["duplicate_edge_ids"] == len(edge_ids) - len(set(edge_ids)) == 0
    assert report["counts"]["self_loops"] == 0
    assert report["counts"]["zero_length_edges"] == 0
    assert report["counts"]["dangling_endpoint_nodes"] == sum(value == 1 for value in endpoint_counts.values())
    assert report["counts"]["geometric_crossings_promoted_to_nodes"] == 0
    assert report["topology_status"] == "CANDIDATE_REVIEW_REQUIRED"
    assert report["route_continuity"] == "NOT_ESTABLISHED"


def test_official_hazard_preview_is_not_promoted_to_connected_capability() -> None:
    """[source_conformance] citywide official ZIP stays external, so clipped preview cannot issue v2 capability."""
    preview = _json("hazards/official/landslide_warning_preview.geojson")
    metadata = _json("hazards/official/landslide_warning_preview.metadata.json")
    assert len(preview["features"]) == 16
    assert all(feature["properties"]["source_class"] == "OFFICIAL" for feature in preview["features"])
    assert all(feature["properties"]["geometry_status"] == "SOURCE_TRACEABLE_REAL_PREVIEW" for feature in preview["features"])
    assert metadata["connection_status"] == "NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT"
    assert metadata["source_zip_sha256"] == "ac40e0b7116d81516dc10e279f5ca67ba48bbece68dc1164ec8f1d3e0c095828"
    manifest = _json("realdata/artifact_manifest.v2.json")
    assert {record["artifact_role"] for record in manifest["artifacts"]} == {"CORRIDOR_GEOMETRY"}


def test_plateau_and_model_readiness_are_truthful() -> None:
    """[target_validation] metadata URL does not become 3D/model connection or invented M7 inputs."""
    plateau = _json("sources/plateau_26100_metadata.json")
    readiness = _json("model/m7_input_readiness.json")
    status = _json("realdata/status.json")
    assert plateau["source_class"] == "OFFICIAL"
    assert plateau["data_class"] == "OFFICIAL_METADATA_ONLY"
    assert plateau["plateau_3d_connected"] is False
    assert readiness["building_height_experiment"]["status"] == "NOT_COMPUTED"
    assert readiness["eligible_edge_count"] == 0
    assert readiness["m7_connected"] is False
    assert status == {
        "REAL_GEOMETRY_CONNECTED": True,
        "OFFICIAL_HAZARD_GEOMETRY_CONNECTED": False,
        "PLATEAU_3D_CONNECTED": False,
        "CANDIDATE_GRAPH_CONNECTED": True,
        "M7_CONNECTED": False,
        "M6_CONNECTED": False,
        "KPI_CONNECTED": False,
        "ADMIN_VALIDATED": False,
        "REAL_GEOMETRY_CONNECTED_SCOPE": "CITYPACK_VALIDATED_ARTIFACT_CAPABILITY",
        "REAL_GEOMETRY_CONNECTED_TO_VIEWER": False,
    }


def test_no_osm_planar_crossing_is_silently_joined() -> None:
    """[software_correctness] only identical OSM node IDs may connect source ways."""
    edges = _json("graph/real/candidate_edges.geojson")["features"]
    membership: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        props = edge["properties"]
        for node_id in props["source_node_ids"]:
            membership[node_id].add(props["edge_id"])
    report = _json("graph/real/topology_qa.json")
    expected_shared = sorted(node_id for node_id, members in membership.items() if len(members) > 1)
    assert report["shared_source_node_ids"] == expected_shared
    assert report["nearest_neighbour_join_applied"] is False
