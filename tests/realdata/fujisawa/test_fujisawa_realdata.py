"""Acceptance tests for the source-traceable Fujisawa/Enoshima city pack."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
from pathlib import Path

import pytest

from src.citypacks import load_validated_geometry_manifest


ROOT = Path(__file__).resolve().parents[3]
CITY = ROOT / "cities" / "fujisawa_enoshima"


def _json(relative: str) -> dict[str, object]:
    return json.loads((CITY / relative).read_text(encoding="utf-8"))


def _builder_module():
    path = CITY / "sources" / "build_normalized.py"
    spec = importlib.util.spec_from_file_location("fujisawa_build_normalized", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fujisawa_v2_manifest_hash_binds_only_reviewed_vgi_geometry() -> None:
    """[source_conformance] Unbound A40 preview cannot mint an OFFICIAL geometry capability."""

    index = load_validated_geometry_manifest(
        CITY / "sources" / "real-artifacts-v2.json",
        trusted_root=CITY,
        expected_city_id="fujisawa_enoshima",
    )
    assert index.feature_ids_for("fujisawa-osm-corridor-v1")
    artifact_ids = {record.artifact_id for record in index.records}
    assert artifact_ids == {"fujisawa-osm-corridor-v1"}
    assert "fujisawa-official-tsunami-a40-v1" not in artifact_ids
    sources = {record.source_class for record in index.records}
    assert sources == {"VGI"}


def test_fujisawa_machine_readable_inventory_is_exact() -> None:
    """[software_correctness] Inventory includes the local LF hash contract; surprises fail closed."""

    expected = {
        ".gitattributes",
        "artifact_manifest.json",
        "city.yaml",
        "demand/demand_scenarios.csv",
        "facilities/facilities.csv",
        "facilities/tsunami_evacuation_facilities.csv",
        "geography/corridor.metadata.json",
        "geography/corridor.real.geojson",
        "geography/corridor_landmarks.json",
        "graph/candidate_topology_qa.real.json",
        "graph/candidate_walk_edges.real.geojson",
        "graph/candidate_walk_nodes.real.geojson",
        "graph/topology_qa.json",
        "graph/walk_edges.geojson",
        "graph/walk_nodes.geojson",
        "hazards/edge_states.csv",
        "hazards/official-tsunami.real.geojson",
        "hazards/scenarios.yaml",
        "pois/pois.csv",
        "README.md",
        "sources/a40-tsunami-source.clip.geojson",
        "sources/build_normalized.py",
        "sources/data_gap_register.csv",
        "sources/external-source-checksums.json",
        "sources/osm-corridor.overpassql",
        "sources/osm-corridor.raw.json",
        "sources/phase2_data_gaps.json",
        "sources/plateau_metadata.json",
        "sources/real-artifacts-v2.json",
        "sources/source_manifest.csv",
        "status.json",
        "viewer/city_config.json",
    }
    actual = {
        path.relative_to(CITY).as_posix()
        for path in CITY.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert actual == expected


def test_fujisawa_candidate_graph_contains_required_corridor_landmarks() -> None:
    """[target_validation] Named scope anchors are source-linked, while entrances remain unverified."""

    landmarks = _json("geography/corridor_landmarks.json")
    required = {
        item["landmark_id"]: item
        for item in landmarks["landmarks"]  # type: ignore[index]
    }
    assert set(required) == {
        "KATASE_COAST",
        "BENTEN_BRIDGE",
        "ENOSHIMA_ENTRANCE",
    }
    assert all(item["geometry_status"] == "SOURCE_TRACEABLE_REAL" for item in required.values())
    assert all(item["entrance_status"] == "UNKNOWN" for item in required.values())

    nodes = _json("graph/candidate_walk_nodes.real.geojson")
    edges = _json("graph/candidate_walk_edges.real.geojson")
    builder = _builder_module()
    node_ids = {feature["properties"]["node_id"] for feature in nodes["features"]}  # type: ignore[index]
    assert edges["metadata"]["topology_status"] == "CANDIDATE"  # type: ignore[index]
    assert len(edges["features"]) > 0  # type: ignore[arg-type]
    for feature in edges["features"]:  # type: ignore[index]
        properties = feature["properties"]
        assert properties["from_node"] in node_ids
        assert properties["to_node"] in node_ids
        assert properties["width_m"] is None
        assert properties["width_m_reason"]
        assert properties["slope"] is None
        assert properties["slope_reason"]
        assert properties["length_m"] is None
        assert properties["length_m_reason"]
        assert properties["official_closure"] is None
        assert properties["official_closure_reason"]
        assert properties["step_status"] == "UNKNOWN"
        assert properties["step_status_reason"]
        assert properties["accessibility_state"] == "UNKNOWN"
        assert properties["accessibility_state_reason"]
        assert properties["operation_status"] == "UNKNOWN"
        assert properties["operation_status_reason"]
        assert properties["edge_id"].startswith("FJ-OSM-E-")
        assert properties["stable_feature_id"].startswith("fujisawa-enoshima:edge:osm-")
        source_way_id = int(properties["source_feature_id"].split("/")[1].split("#")[0])
        start, end = feature["geometry"]["coordinates"]
        identity = {"source_way_id": source_way_id, "start": start, "end": end}
        digest = builder._canonical_sha256(identity)
        assert properties["source_feature_id"] == f"way/{source_way_id}#segment-sha256/{digest}"
        assert properties["edge_id"] == f"FJ-OSM-E-{digest[:16].upper()}"
        assert properties["stable_feature_id"] == f"fujisawa-enoshima:edge:osm-{digest[:16]}"

    for feature in nodes["features"]:  # type: ignore[index]
        properties = feature["properties"]
        assert properties["entrance_status"] == "UNKNOWN"
        assert properties["entrance_status_reason"]
        assert properties["node_id"].startswith("FJ-OSM-N-")
        coordinate = feature["geometry"]["coordinates"]
        assert properties["node_id"] == f"FJ-OSM-N-{builder._stable_token({'coordinate': coordinate})}"


def test_fujisawa_topology_qa_is_explicit_and_does_not_promote_candidate_graph() -> None:
    """[software_correctness] QA reports defects and grade separation without silent graph joins."""

    qa = _json("graph/candidate_topology_qa.real.json")
    assert qa["graph_status"] == "CANDIDATE"
    assert qa["counts"]["duplicate_node_ids"] == 0  # type: ignore[index]
    assert qa["counts"]["duplicate_edge_ids"] == 0  # type: ignore[index]
    assert qa["counts"]["self_loops"] == 0  # type: ignore[index]
    assert qa["counts"]["zero_length_edges"] == 0  # type: ignore[index]
    assert qa["geometric_crossing_policy"] == "NO_NODE_WITHOUT_SHARED_SOURCE_VERTEX"
    assert qa["promotion_status"] == "BLOCKED_FIELD_AND_ADMIN_REVIEW"

    nodes = _json("graph/candidate_walk_nodes.real.geojson")["features"]
    edges = _json("graph/candidate_walk_edges.real.geojson")["features"]
    node_ids = {feature["properties"]["node_id"] for feature in nodes}
    adjacency = {node_id: set() for node_id in node_ids}
    self_loops = 0
    zero_length = 0
    for feature in edges:
        props = feature["properties"]
        start, end = props["from_node"], props["to_node"]
        self_loops += start == end
        zero_length += feature["geometry"]["coordinates"][0] == feature["geometry"]["coordinates"][-1]
        adjacency[start].add(end)
        adjacency[end].add(start)
    components = 0
    unseen = set(node_ids)
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            for neighbor in adjacency[stack.pop()]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
    assert qa["counts"] == {
        "nodes": len(nodes),
        "edges": len(edges),
        "duplicate_node_ids": len(nodes) - len(node_ids),
        "duplicate_edge_ids": len(edges)
        - len({feature["properties"]["edge_id"] for feature in edges}),
        "dangling_endpoint_nodes": sum(len(neighbors) == 1 for neighbors in adjacency.values()),
        "self_loops": self_loops,
        "zero_length_edges": zero_length,
        "connected_components": components,
    }


def test_tsunami_metadata_is_not_a_generic_shelter_or_operational_claim() -> None:
    """[source_conformance] Tsunami evacuation metadata stays distinct and UNKNOWN operationally."""

    with (CITY / "facilities" / "tsunami_evacuation_facilities.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["facility_class"] for row in rows} == {"TSUNAMI_EVACUATION_FACILITY"}
    for row in rows:
        assert row["generic_shelter_status"] == "NOT_ASSERTED"
        assert row["geometry_status"] == "UNKNOWN"
        assert row["geometry_reason"]
        assert row["entrance_status"] == "UNKNOWN"
        assert row["entrance_reason"]
        assert row["capacity"] == ""
        assert row["capacity_reason"]
        assert row["operation_status"] == "UNKNOWN"
        assert row["operation_reason"]
        assert row["official_closure"] == ""
        assert row["official_closure_reason"]
        assert row["arrival_time"] == ""
        assert row["arrival_time_reason"]


def test_official_tsunami_is_an_unconnected_reasoned_preview() -> None:
    """[source_conformance] Derived A40 bytes preserve source facts but cannot imply connection."""

    preview = _json("hazards/official-tsunami.real.geojson")
    metadata = preview["metadata"]
    assert metadata["connection_status"] == "NOT_CONNECTED"
    assert metadata["coverage_complete"] is False
    assert metadata["coverage_reason"]
    assert metadata["source_crs"] == "EPSG:6668"
    assert metadata["output_crs"] == "UNVERIFIED_NOT_RELABELLED"
    assert metadata["original_source_trust_bound"] is False
    assert metadata["original_source_trust_reason"]
    for feature in preview["features"]:
        properties = feature["properties"]
        assert properties["source_class"] == "OFFICIAL_DERIVED_PREVIEW"
        assert properties["official_closure"] is None
        assert properties["official_closure_reason"]
        assert properties["operation_status"] == "UNKNOWN"
        assert properties["operation_status_reason"]
        assert properties["arrival_time_min"] is None
        assert properties["arrival_time_reason"]
        assert properties["hazard_value"] is None
        assert properties["hazard_value_reason"]


def test_fujisawa_truth_flags_keep_models_kpis_and_admin_validation_disabled() -> None:
    """[source_conformance] Real geometry does not imply M7/M6/KPI or administrative validation."""

    status = _json("status.json")
    assert status["REAL_GEOMETRY_CONNECTED"] is False
    assert status["REAL_VGI_CANDIDATE_DATA_AVAILABLE"] is True
    assert status["OFFICIAL_HAZARD_GEOMETRY_CONNECTED"] is False
    assert status["OFFICIAL_HAZARD_PREVIEW_AVAILABLE"] is True
    assert status["CANDIDATE_GRAPH_CONNECTED"] is False
    assert status["CANDIDATE_GRAPH_DATA_AVAILABLE"] is True
    assert status["PLATEAU_3D_CONNECTED"] is False
    assert status["M7_CONNECTED"] is False
    assert status["M6_CONNECTED"] is False
    assert status["KPI_CONNECTED"] is False
    assert status["ADMIN_VALIDATED"] is False
    for key, value in status["kpis"].items():  # type: ignore[index]
        assert value["value"] is None, key
        assert value["reason"], key

    city_text = (CITY / "city.yaml").read_text(encoding="utf-8")
    viewer = _json("viewer/city_config.json")
    assert "REAL_GEOMETRY_CONNECTED: false" in city_text
    assert viewer["realdata_lane"]["renderer_connected"] is False
    assert viewer["realdata_lane"]["official_hazard_connected"] is False
    assert viewer["realdata_lane"]["candidate_vgi_data_available"] is True


def test_external_json_reader_rejects_duplicate_nonfinite_and_oversize(tmp_path: Path) -> None:
    """[software_correctness] External JSON is bounded data, never an instruction or permissive parse."""

    builder = _builder_module()
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"a":1,"a":2}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        builder._read_json(duplicate, max_bytes=100)

    nonfinite = tmp_path / "nonfinite.json"
    nonfinite.write_text('{"a":NaN}', encoding="utf-8")
    with pytest.raises(ValueError, match="non-finite"):
        builder._read_json(nonfinite, max_bytes=100)

    oversized = tmp_path / "oversized.json"
    oversized.write_text('{"payload":"' + "x" * 100 + '"}', encoding="utf-8")
    with pytest.raises(ValueError, match="size"):
        builder._read_json(oversized, max_bytes=32)
    with pytest.raises(ValueError, match="finite decimal"):
        builder._finite_tag_number("NaN", "layer")
    with pytest.raises(ValueError, match="finite decimal"):
        builder._finite_tag_number("1e309", "layer")
    with pytest.raises(ValueError, match="exact OSM yes/no"):
        builder._osm_yes_no_unknown("external-instruction", "bridge")


def test_source_inventory_separates_vgi_capability_from_unbound_official_preview() -> None:
    """[source_conformance] Source rows and operator hashes cannot overstate connection authority."""

    with (CITY / "sources" / "source_manifest.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = {row["dataset_id"]: row for row in csv.DictReader(handle)}
    osm = rows["OSM_CANDIDATE_SOURCE"]
    assert osm["source_class"] == "VGI"
    assert osm["download_status"] == "BOUNDED_SNAPSHOT_RETAINED"
    assert osm["geometry_use"] == "CANDIDATE_GRAPH_SOURCE"
    assert osm["geometry_status"] == "SOURCE_TRACEABLE_REAL_CANDIDATE"
    assert osm["operation_status"] == "UNKNOWN"

    a40 = rows["A40_DERIVED_PREVIEW"]
    assert a40["source_class"] == "OFFICIAL_DERIVED_PREVIEW"
    assert a40["download_status"] == "DERIVED_PREVIEW_ONLY"
    assert a40["geometry_use"] == "PREVIEW_NOT_CONNECTED"
    assert a40["geometry_status"] == "DERIVED_PREVIEW_NOT_CONNECTED"
    assert "original ZIP" in a40["missing_fields"]

    checksums = _json("sources/external-source-checksums.json")
    for source in checksums["sources"]:
        assert source["connection_authority"] is False
        assert source["verification_status"] == "UNBOUND_OPERATOR_ASSERTION_NOT_CONNECTION_AUTHORITY"
        assert source["license_review_status"] == "HUMAN_PENDING"
        assert source["redistribution_status"] == "UNKNOWN"


def test_a40_preview_selection_is_order_stable_and_keeps_boundary_crossings() -> None:
    """[software_correctness] Source ordering cannot define IDs or silently drop crossing polygons."""

    builder = _builder_module()
    crossing = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [139.4799, 35.3020],
                [139.4802, 35.3020],
                [139.4802, 35.3022],
                [139.4799, 35.3020],
            ]],
        },
        "properties": {"A40_003": "fixture"},
    }
    inside = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [139.4810, 35.3030],
                [139.4812, 35.3030],
                [139.4812, 35.3032],
                [139.4810, 35.3030],
            ]],
        },
        "properties": {"A40_003": "fixture-2"},
    }
    forward = builder._select_a40_preview_features({"type": "FeatureCollection", "features": [crossing, inside]})
    reverse = builder._select_a40_preview_features({"type": "FeatureCollection", "features": [inside, crossing]})
    assert [item[0] for item in forward] == [item[0] for item in reverse]
    assert len(forward) == 2
    assert all(item[0].startswith("sha256:") for item in forward)
    assert all(math.isfinite(value) for _, feature in forward for ring in feature["geometry"]["coordinates"] for point in ring for value in point)
