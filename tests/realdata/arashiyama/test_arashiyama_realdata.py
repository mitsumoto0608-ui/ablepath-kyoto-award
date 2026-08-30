"""Acceptance tests for the source-traceable Arashiyama real-data lane."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

from src.citypacks import load_validated_geometry_manifest


ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "cities" / "kyoto_arashiyama"

EXPECTED_CITYPACK_FILES = {
    ".gitattributes",
    "README.md",
    "city.yaml",
    "demand/demand_scenarios.csv",
    "facilities/facilities.csv",
    "geography/corridor.geojson",
    "geography/corridor.real.geojson",
    "graph/graph_provenance.real.json",
    "graph/topology_qa.json",
    "graph/topology_qa.real.json",
    "graph/walk_edges.geojson",
    "graph/walk_edges.real.geojson",
    "graph/walk_nodes.geojson",
    "graph/walk_nodes.real.geojson",
    "hazards/edge_hazard_overlap.real.csv",
    "hazards/edge_hazard_overlap.real.manifest.json",
    "hazards/edge_physics.csv",
    "hazards/flood_a31b_2025.prepared.geojson",
    "hazards/flood_a31b_2025.quarantine.json",
    "hazards/scenarios.yaml",
    "pois/pois.csv",
    "realdata_status.json",
    "sources/data_gap_register.csv",
    "sources/flood_a31b_2025.preparation.json",
    "sources/kyoto_inner_flood.metadata.json",
    "sources/optional_preparation_status.json",
    "sources/osm_arashiyama_20260829.overpassql",
    "sources/osm_arashiyama_20260829.raw.json",
    "sources/plateau_kyoto_2025.metadata.json",
    "sources/realdata_fileset.json",
    "sources/realdata_manifest.json",
    "sources/retention_receipt.json",
    "sources/source_manifest.csv",
    "tools/build_realdata.py",
    "viewer/city_config.json",
}


def test_csv_artifacts_use_platform_independent_lf_bytes(tmp_path: Path) -> None:
    """[software_correctness] Manifest-bound CSV bytes stay LF on Windows and Linux."""

    script = PACK / "tools" / "build_realdata.py"
    spec = importlib.util.spec_from_file_location("arashiyama_build_realdata", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode
    output = tmp_path / "canonical.csv"

    first_sha = module._write_csv(output, [{"edge_id": "E-1", "state": "UNKNOWN"}])
    first_bytes = output.read_bytes()
    second_sha = module._write_csv(output, [{"edge_id": "E-1", "state": "UNKNOWN"}])

    assert first_bytes == b"edge_id,state\nE-1,UNKNOWN\n"
    assert b"\r\n" not in first_bytes
    assert first_sha == second_sha == hashlib.sha256(first_bytes).hexdigest()


def _json(relative: str) -> dict:
    return json.loads((PACK / relative).read_text(encoding="utf-8"))


def _csv(relative: str) -> list[dict[str, str]]:
    with (PACK / relative).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _coordinates(geometry: dict) -> list[list[float]]:
    if geometry["type"] == "Point":
        return [geometry["coordinates"]]
    if geometry["type"] == "LineString":
        return geometry["coordinates"]
    if geometry["type"] == "Polygon":
        return [coordinate for ring in geometry["coordinates"] for coordinate in ring]
    if geometry["type"] == "MultiPolygon":
        return [
            coordinate
            for polygon in geometry["coordinates"]
            for ring in polygon
            for coordinate in ring
        ]
    raise AssertionError(f"unsupported geometry type: {geometry['type']}")


def _expected_osm_bool(tags: dict[str, str], key: str) -> tuple[bool | str, bool]:
    raw = tags.get(key)
    if raw in {"yes", "true", "1"}:
        return True, False
    if raw in {"no", "false", "0"}:
        return False, False
    return "UNKNOWN", True


def _expected_osm_number(tags: dict[str, str], key: str) -> tuple[float | int | None, bool]:
    raw = tags.get(key)
    if raw is None:
        return None, True
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None, True
    if not math.isfinite(value):
        return None, True
    return (int(value) if value.is_integer() else value), False


def test_whole_citypack_inventory_is_exact() -> None:
    """[source_conformance] The complete legacy-plus-additive citypack rejects missing and unexpected files."""
    actual = {
        path.relative_to(PACK).as_posix()
        for path in PACK.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    assert actual == EXPECTED_CITYPACK_FILES


def test_fixed_time_bounded_osm_query_is_retained() -> None:
    """[source_conformance] The OSM snapshot is time-fixed and bounded to the declared Arashiyama corridor."""
    query = (PACK / "sources" / "osm_arashiyama_20260829.overpassql").read_text(
        encoding="utf-8"
    )
    assert '[date:"2026-08-29T00:00:00Z"]' in query
    assert "(35.008700,135.674800,35.015300,135.680200)" in query
    assert 'way["highway"~' in query
    assert query.count("(") == query.count(")")


def test_real_artifacts_are_checksum_bound_and_source_classes_stay_separate() -> None:
    """[source_conformance] Git-normalized artifacts match their checksums without promoting VGI to official."""
    manifest = _json("sources/realdata_manifest.json")
    assert manifest["schema_version"] == "2.0.0"
    assert manifest["city_id"] == "kyoto_arashiyama"
    retention = _json("sources/retention_receipt.json")
    assert retention["repository_includes_bounded_osm_raw"] is True
    assert retention["external_location"] == "ablepath-raw/kyoto_arashiyama"
    assert "C:\\" not in json.dumps(manifest, ensure_ascii=False)
    records = manifest["artifacts"]
    assert [row["stable_feature_id"] for row in records] == sorted(
        row["stable_feature_id"] for row in records
    )
    assert {row["source_class"] for row in records} == {"VGI"}
    for row in records:
        path = PACK / row["artifact_path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        assert row["data_class"] == "REAL"
        assert row["geometry_status"] == "SOURCE_TRACEABLE_REAL"
        assert row["license_review_status"] == "AGENT_REVIEWED_HUMAN_PENDING"
        assert row["source_url"].startswith("https://")
        assert row["source_sha256"]
        assert row["source_crs"] == row["output_crs"] == "EPSG:4326"
        assert row["axis_order"] == "longitude_latitude"
        assert row["horizontal_unit"] == "degree"
        assert row["vertical_datum"] is None and row["vertical_datum_reason"]
    validated = load_validated_geometry_manifest(
        PACK / "sources" / "realdata_manifest.json",
        trusted_root=PACK,
        expected_city_id="kyoto_arashiyama",
    )
    assert validated.feature_ids_for("arashiyama-osm-corridor-v1")


def test_candidate_graph_is_real_deterministic_and_preserves_grade_tags() -> None:
    """[software_correctness] OSM nodes split only at shared IDs and bridge/tunnel/layer/level tags survive normalization."""
    nodes = _json("graph/walk_nodes.real.geojson")["features"]
    edges = _json("graph/walk_edges.real.geojson")["features"]
    node_ids = [feature["properties"]["node_id"] for feature in nodes]
    edge_ids = [feature["properties"]["edge_id"] for feature in edges]
    assert node_ids == sorted(node_ids)
    assert edge_ids == sorted(edge_ids)
    assert len(node_ids) == len(set(node_ids))
    assert len(edge_ids) == len(set(edge_ids))
    node_coordinates = {
        feature["properties"]["node_id"]: feature["geometry"]["coordinates"]
        for feature in nodes
    }
    for feature in edges:
        props = feature["properties"]
        assert props["source_id"] == "openstreetmap-overpass-arashiyama-20260829"
        assert props["source_sha256"]
        assert props["retrieval_query_sha256"]
        assert props["revision_id"] == "osm-2026-08-29-v1"
        assert props["lineage"]
        assert props["source_class"] == "VGI"
        assert props["data_class"] == "REAL"
        assert props["geometry_status"] == "SOURCE_TRACEABLE_REAL"
        assert props["topology_status"] == "CANDIDATE"
        assert props["accessibility_state"] == "UNKNOWN"
        assert props["width_m"] is None and props["width_reason"]
        assert props["step_height_m"] is None and props["step_height_reason"]
        assert props["running_slope"] is None and props["running_slope_reason"]
        assert props["operation_status"] == "UNKNOWN" and props["operation_reason"]
        for nullable in ("foot", "name", "name:en", "osm_access_tag", "osm_width_tag"):
            reason_key = f"{nullable}_reason"
            if props[nullable] is None:
                assert props[reason_key], f"{nullable} null must have a field-level reason"
            else:
                assert props[reason_key] is None
        assert props["from_node"] in node_coordinates and props["to_node"] in node_coordinates
        endpoint_ids = sorted(
            int(node_id.rsplit("-", 1)[1])
            for node_id in (props["from_node"], props["to_node"])
        )
        way_id = int(props["source_feature_id"].split("/", 1)[1].split("#", 1)[0])
        assert props["stable_feature_id"] == (
            f"kyoto-arashiyama:osm-way-{way_id:012d}:"
            f"nodes-{endpoint_ids[0]:012d}-{endpoint_ids[1]:012d}"
        )
        assert "centroid" not in props["stable_feature_id"].lower()
        assert feature["geometry"]["coordinates"][0] == node_coordinates[props["from_node"]]
        assert feature["geometry"]["coordinates"][-1] == node_coordinates[props["to_node"]]
        assert feature["geometry"]["coordinates"][0] != feature["geometry"]["coordinates"][-1]
        assert {"bridge", "tunnel", "layer", "level"} <= props.keys()
        tags = props["source_tags"]
        for key in ("bridge", "tunnel"):
            expected, expects_reason = _expected_osm_bool(tags, key)
            assert props[key] == expected
            assert bool(props[f"{key}_reason"]) is expects_reason
        for key in ("layer", "level"):
            expected, expects_reason = _expected_osm_number(tags, key)
            assert props[key] == expected
            assert bool(props[f"{key}_reason"]) is expects_reason
    bridge_edges = [feature for feature in edges if feature["properties"]["bridge"] not in (None, "UNKNOWN", "no")]
    assert bridge_edges, "Togetsukyo/bridge-tagged approach must survive the bounded extract"
    assert any(
        "渡月橋" in str(feature["properties"].get("name"))
        or "Togetsu" in str(feature["properties"].get("name:en"))
        for feature in bridge_edges
    )


def test_candidate_nodes_and_graph_outputs_are_bound_to_retained_source_hashes() -> None:
    """[source_conformance] Every candidate feature has provenance and the graph sidecar binds exact output bytes."""
    nodes = _json("graph/walk_nodes.real.geojson")["features"]
    edges = _json("graph/walk_edges.real.geojson")["features"]
    for feature in [*nodes, *edges]:
        props = feature["properties"]
        assert props["source_id"] == "openstreetmap-overpass-arashiyama-20260829"
        assert props["source_feature_id"]
        assert props["stable_feature_id"] == feature["id"]
        assert props["revision_id"] == "osm-2026-08-29-v1"
        assert props["lineage"]
        assert props["source_sha256"] == hashlib.sha256(
            (PACK / "sources/osm_arashiyama_20260829.raw.json").read_bytes()
        ).hexdigest()
        assert props["retrieval_query_sha256"] == hashlib.sha256(
            (PACK / "sources/osm_arashiyama_20260829.overpassql").read_bytes()
        ).hexdigest()
    assert all(
        feature["properties"]["source_feature_id"].startswith("node/")
        and "centroid" not in feature["properties"]["node_id"].lower()
        for feature in nodes
    )
    provenance = _json("graph/graph_provenance.real.json")
    assert provenance["capability_status"] == "SOURCE_TRACEABLE_CANDIDATE"
    assert provenance["source_artifact_path"] == "sources/osm_arashiyama_20260829.raw.json"
    assert provenance["source_crs"] == provenance["processing_crs"] == provenance["output_crs"] == "EPSG:4326"
    assert provenance["axis_order"] == "longitude_latitude"
    assert provenance["horizontal_unit"] == "degree"
    assert provenance["transform_history"]
    for output in provenance["outputs"]:
        assert hashlib.sha256((PACK / output["path"]).read_bytes()).hexdigest() == output["sha256"]


def test_stable_edge_id_survives_unrelated_osm_node_insertion() -> None:
    """[software_correctness] FIXTURE_VALUE: inserting node 15 into 10-20 keeps unchanged physical segment 20-30 stable."""
    script = PACK / "tools" / "build_realdata.py"
    spec = importlib.util.spec_from_file_location("arashiyama_stable_id_mutation", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode

    def raw(node_ids: list[int], longitudes: list[float]) -> dict:
        return {
            "elements": [
                {
                    "type": "way",
                    "id": 7,
                    "nodes": node_ids,
                    "geometry": [
                        {"lon": longitude, "lat": 35.01}
                        for longitude in longitudes
                    ],
                    "tags": {"highway": "footway"},
                }
            ]
        }

    _, _, base_edges = module._osm_segments(
        raw([10, 20, 30], [135.6760, 135.6765, 135.6770]),
        source_sha256="fixture-source",
        query_sha256="fixture-query",
    )
    _, _, revised_edges = module._osm_segments(
        raw([10, 15, 20, 30], [135.6760, 135.67625, 135.6765, 135.6770]),
        source_sha256="fixture-source",
        query_sha256="fixture-query",
    )
    base_20_30 = next(
        edge["properties"]["stable_feature_id"]
        for edge in base_edges
        if edge["properties"]["from_node"].endswith("000000000020")
        and edge["properties"]["to_node"].endswith("000000000030")
    )
    revised_20_30 = next(
        edge["properties"]["stable_feature_id"]
        for edge in revised_edges
        if edge["properties"]["from_node"].endswith("000000000020")
        and edge["properties"]["to_node"].endswith("000000000030")
    )
    assert base_20_30 == revised_20_30


def test_real_geometries_are_small_finite_and_within_declared_bounds() -> None:
    """[software_correctness] Normalized features are finite, bounded, and small enough for Git delivery."""
    bounds = (135.6748, 35.0087, 135.6802, 35.0153)
    for relative in (
        "geography/corridor.real.geojson",
        "graph/walk_nodes.real.geojson",
        "graph/walk_edges.real.geojson",
        "hazards/flood_a31b_2025.prepared.geojson",
    ):
        path = PACK / relative
        assert path.stat().st_size < 5_000_000
        payload = _json(relative)
        assert payload["type"] == "FeatureCollection" and payload["features"]
        for feature in payload["features"]:
            for lon, lat in _coordinates(feature["geometry"]):
                assert math.isfinite(lon) and math.isfinite(lat)
                assert bounds[0] - 0.000001 <= lon <= bounds[2] + 0.000001
                assert bounds[1] - 0.000001 <= lat <= bounds[3] + 0.000001


def test_topology_qa_is_recomputed_and_never_promotes_candidate_graph() -> None:
    """[software_correctness] QA counts are derived from the shipped graph and unresolved checks stay explicit."""
    qa = _json("graph/topology_qa.real.json")
    nodes = _json("graph/walk_nodes.real.geojson")["features"]
    edges = _json("graph/walk_edges.real.geojson")["features"]
    node_ids = [feature["properties"]["node_id"] for feature in nodes]
    edge_ids = [feature["properties"]["edge_id"] for feature in edges]
    degrees = {node_id: 0 for node_id in node_ids}
    for feature in edges:
        degrees[feature["properties"]["from_node"]] += 1
        degrees[feature["properties"]["to_node"]] += 1
    assert qa["graph_status"] == "CANDIDATE"
    assert qa["counts"]["duplicate_node_ids"] == len(node_ids) - len(set(node_ids)) == 0
    assert qa["counts"]["duplicate_edge_ids"] == len(edge_ids) - len(set(edge_ids)) == 0
    assert qa["counts"]["dangling_endpoint_nodes"] == sum(value == 1 for value in degrees.values())
    assert qa["counts"]["self_loops"] == sum(
        edge["properties"]["from_node"] == edge["properties"]["to_node"] for edge in edges
    )
    assert qa["counts"]["zero_length_edges"] == sum(
        edge["geometry"]["coordinates"][0] == edge["geometry"]["coordinates"][-1]
        for edge in edges
    )
    assert qa["counts"]["geometric_crossings_promoted_to_nodes"] == 0
    assert qa["issue_register_status"] == "OPEN"
    assert len(qa["issues"]) == qa["counts"]["dangling_endpoint_nodes"]
    assert {
        (issue["feature_id"], issue["issue_type"], issue["status"])
        for issue in qa["issues"]
    } == {
        (node_id, "DANGLING_ENDPOINT", "OPEN")
        for node_id, degree in degrees.items()
        if degree == 1
    }
    assert all(issue["issue_id"] and issue["reason"] for issue in qa["issues"])
    assert all(
        issue["qa_code"] == "UNEXPECTED_DANGLE"
        and issue["severity"] == "REVIEW_REQUIRED"
        and issue["owner"] == "FIELD_QA"
        for issue in qa["issues"]
    )
    assert qa["not_computed"]["disconnected_verified_destinations"]["status"] == "NOT_COMPUTED"
    assert qa["not_computed"]["field_verified_connectivity"]["status"] == "NOT_COMPUTED"


def test_official_flood_overlap_preserves_depth_rank_but_never_generates_closure() -> None:
    """[source_conformance] A31b overlap/depth rank is physical exposure only; no edge state is invented."""
    hazard = _json("hazards/flood_a31b_2025.prepared.geojson")
    assert hazard["features"]
    assert all(feature["properties"]["source_class"] == "OFFICIAL" for feature in hazard["features"])
    assert all(feature["properties"]["data_class"] == "OFFICIAL_METADATA_ONLY" for feature in hazard["features"])
    assert all(feature["properties"]["geometry_status"] == "PREPARED_NOT_CONNECTED" for feature in hazard["features"])
    assert all(feature["properties"]["connection_status"] == "NOT_CONNECTED" for feature in hazard["features"])
    assert all(feature["properties"]["hazard_type"] == "FLOOD" for feature in hazard["features"])
    assert all(feature["properties"]["scenario_state"] == "UNKNOWN" for feature in hazard["features"])
    assert all(feature["properties"]["official_closure"] is None for feature in hazard["features"])
    assert all(feature["properties"]["official_closure_reason"] for feature in hazard["features"])
    assert all(feature["properties"]["source_id"] for feature in hazard["features"])
    assert all(feature["properties"]["source_sha256"] for feature in hazard["features"])
    assert all(feature["properties"]["revision_id"] for feature in hazard["features"])
    assert all(feature["properties"]["source_axis_order"] for feature in hazard["features"])
    assert all(feature["properties"]["output_axis_order"] == "longitude_latitude" for feature in hazard["features"])
    preparation = _json("sources/flood_a31b_2025.preparation.json")
    assert all(feature["properties"]["source_id"] == preparation["source_id"] for feature in hazard["features"])
    assert all(feature["properties"]["revision_id"] == preparation["revision_id"] for feature in hazard["features"])
    assert all(feature["properties"]["depth_rank_code"] is not None for feature in hazard["features"])
    rows = _csv("hazards/edge_hazard_overlap.real.csv")
    assert rows
    row_edge_ids = [row["edge_id"] for row in rows]
    graph_edge_ids = [
        feature["properties"]["edge_id"]
        for feature in _json("graph/walk_edges.real.geojson")["features"]
    ]
    assert row_edge_ids == graph_edge_ids == sorted(set(graph_edge_ids))
    assert row_edge_ids[:-1] != graph_edge_ids, "truncated overlap rows must fail exact coverage"
    assert [*row_edge_ids, row_edge_ids[-1]] != graph_edge_ids, "duplicated overlap rows must fail exact coverage"
    assert all(row["data_class"] == "MODEL_DERIVED" for row in rows)
    assert all(row["source_class"] == "MODEL" for row in rows)
    assert all(row["connection_status"] == "NOT_CONNECTED" for row in rows)
    assert all(row["hazard_capability_status"] == "NOT_CONNECTED" for row in rows)
    assert all(row["hazard_overlap_status"] in {"OVERLAPS", "NO_OVERLAP"} for row in rows)
    assert all(row["official_closure"] == "" for row in rows)
    assert all(row["official_closure_reason"] for row in rows)
    assert all(row["scenario_state"] == "UNKNOWN" for row in rows)
    assert all(row["inundation_depth_m"] == "" for row in rows)
    assert all(row["inundation_depth_reason"] for row in rows)
    assert all(row["depth_rank_codes"] or row["hazard_overlap_status"] == "NO_OVERLAP" for row in rows)
    sidecar = _json("hazards/edge_hazard_overlap.real.manifest.json")
    assert sidecar["data_class"] == "MODEL_DERIVED"
    assert sidecar["connection_status"] == "NOT_CONNECTED"
    assert sidecar["revision_id"] and sidecar["lineage"]
    assert [item["path"] for item in sidecar["inputs"]] == sorted(
        item["path"] for item in sidecar["inputs"]
    )
    for item in [*sidecar["inputs"], sidecar["output"]]:
        assert hashlib.sha256((PACK / item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_osm_capability_fileset_closes_raw_query_normalized_and_manifest_hashes() -> None:
    """[source_conformance] The connected OSM capability names and hashes its exact trust-root fileset."""
    closure = _json("sources/realdata_fileset.json")
    assert closure["capability_id"] == "arashiyama-osm-corridor-v1"
    assert closure["connection_status"] == "CONNECTED"
    expected = {
        "geography/corridor.real.geojson",
        "sources/osm_arashiyama_20260829.overpassql",
        "sources/osm_arashiyama_20260829.raw.json",
        "sources/realdata_manifest.json",
    }
    assert {item["path"] for item in closure["exact_fileset"]} == expected
    for item in closure["exact_fileset"]:
        assert hashlib.sha256((PACK / item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_legacy_catalogue_points_to_hash_bound_authority_without_reclassification() -> None:
    """[source_conformance] Legacy VGI metadata is superseded by, not conflated with, the retained real-data authority."""
    rows = _csv("sources/source_manifest.csv")
    row = next(item for item in rows if item["dataset_id"] == "osm_arashiyama_candidate")
    assert row["data_class"] == "VGI_METADATA_ONLY"
    assert row["freshness_status"] == "SUPERSEDED"
    assert row["superseded_by_dataset_id"] == "openstreetmap-overpass-arashiyama-20260829"
    assert row["download_status"] == "METADATA_ONLY"
    assert row["artifact_schema_version"] == "1.0.0"
    assert row["local_path"] == row["sha256"] == ""
    record = " ".join(row.values())
    for expected in (
        "sources/realdata_manifest.json",
        "sources/osm_arashiyama_20260829.raw.json",
        "2026-08-29T00:00:00Z",
        "1cde93d68bebf633989e825cbd5ac1e772cee81508043f44beb311250a1e8013",
    ):
        assert expected in record


def test_gap_register_acknowledges_candidate_artifact_without_closing_human_gates() -> None:
    """[source_conformance] Resolved acquisition wording cannot erase PLATEAU, field, hazard, or operation gaps."""
    rows = _csv("sources/data_gap_register.csv")
    geometry = next(item for item in rows if item["gap_id"] == "ARA-GAP-001")
    hazard = next(item for item in rows if item["gap_id"] == "ARA-GAP-002")
    assert "Source-traceable OSM candidate graph exists" in geometry["impact"]
    assert "No real candidate graph" not in geometry["impact"]
    assert geometry["status"] == "OPEN" and geometry["severity"] == "HIGH"
    assert "outside the shared trust root" in hazard["impact"]
    assert hazard["status"] == "OPEN" and hazard["severity"] == "HIGH"


def test_truth_flags_keep_models_kpis_and_admin_validation_disconnected() -> None:
    """[source_conformance] Real geometry does not imply M7, M6, KPI, PLATEAU runtime, or administrative validation."""
    status = _json("realdata_status.json")
    assert status["REAL_GEOMETRY_CONNECTED"] is True
    assert status["REAL_GEOMETRY_CONNECTED_SCOPE"] == "CITYPACK_VALIDATED_ARTIFACT_CAPABILITY"
    assert status["REAL_GEOMETRY_CONNECTED_TO_VIEWER"] is False
    assert status["OFFICIAL_HAZARD_GEOMETRY_CONNECTED"] is False
    assert status["OFFICIAL_HAZARD_GEOMETRY_PREPARED"] is True
    assert status["CANDIDATE_GRAPH_CONNECTED"] is True
    assert status["CANDIDATE_GRAPH_CONNECTED_SCOPE"] == "CITYPACK_ARTIFACT_FILES_ONLY"
    assert status["CANDIDATE_GRAPH_CONNECTED_TO_MODEL"] is False
    assert status["PLATEAU_METADATA_CONNECTED"] is True
    assert status["PLATEAU_3D_CONNECTED"] is False
    assert status["M7_CONNECTED"] is False
    assert status["MODEL_CONNECTED"] is False
    assert status["M6_CONNECTED"] is False
    assert status["KPI_CONNECTED"] is False
    assert status["ADMIN_VALIDATED"] is False
    assert status["kpis"] and all(
        item["value"] is None and item["reason"] for item in status["kpis"].values()
    )
    city = (PACK / "city.yaml").read_text(encoding="utf-8")
    viewer = _json("viewer/city_config.json")
    readme = (PACK / "README.md").read_text(encoding="utf-8")
    assert "data_status: SYNTHETIC_DEMO" in city
    assert viewer["data_status"] == "SYNTHETIC_DEMO"
    assert all(layer["id"] != "real_walk_graph" for layer in viewer["layers"])
    assert "REAL_GEOMETRY_CONNECTED_TO_VIEWER=false" in readme
    assert "CANDIDATE_GRAPH_CONNECTED_TO_MODEL=false" in readme


def test_unconnected_official_metadata_uses_null_with_reason() -> None:
    """[source_conformance] Flood, inner-flood, and PLATEAU metadata never fill unavailable capability fields."""
    flood = _json("sources/flood_a31b_2025.preparation.json")
    assert flood["data_class"] == "OFFICIAL_METADATA_ONLY"
    assert flood["shared_v2_connection_status"] == "NOT_CONNECTED"
    assert flood["source_id"] and flood["source_sha256"]
    assert flood["valid_as_of"] is None and flood["valid_as_of_reason"]
    inner_flood = _json("sources/kyoto_inner_flood.metadata.json")
    plateau = _json("sources/plateau_kyoto_2025.metadata.json")
    for metadata in (inner_flood, plateau):
        assert metadata["data_class"] == "OFFICIAL_METADATA_ONLY"
        assert metadata["geometry_connection_status"] == "NOT_CONNECTED"
        for field in ("license", "source_sha256", "source_crs", "vertical_datum"):
            assert metadata[field] is None and metadata[f"{field}_reason"]


def test_connected_osm_build_is_stdlib_only_and_fresh_output_deterministic(tmp_path: Path) -> None:
    """[software_correctness] Two fresh `python -S` builds reproduce the connected OSM/candidate capability without optional GIS packages."""
    output_relatives = (
        "geography/corridor.real.geojson",
        "graph/graph_provenance.real.json",
        "graph/topology_qa.real.json",
        "graph/walk_edges.real.geojson",
        "graph/walk_nodes.real.geojson",
        "sources/optional_preparation_status.json",
        "sources/osm_arashiyama_20260829.raw.json",
        "sources/realdata_fileset.json",
        "sources/realdata_manifest.json",
    )
    results = []
    for run in ("a", "b"):
        fresh_pack = tmp_path / f"pack-{run}"
        fresh_raw = tmp_path / f"raw-{run}"
        (fresh_pack / "sources").mkdir(parents=True)
        fresh_raw.mkdir()
        shutil.copy2(PACK / "sources/osm_arashiyama_20260829.overpassql", fresh_pack / "sources")
        shutil.copy2(PACK / "sources/osm_arashiyama_20260829.raw.json", fresh_raw)
        subprocess.run(
            [
                sys.executable,
                "-S",
                str(PACK / "tools/build_realdata.py"),
                "--pack",
                str(fresh_pack),
                "--raw-root",
                str(fresh_raw),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert not (fresh_pack / "hazards/flood_a31b_2025.prepared.geojson").exists()
        results.append(
            {
                relative: hashlib.sha256((fresh_pack / relative).read_bytes()).hexdigest()
                for relative in output_relatives
            }
        )
    assert results[0] == results[1]
    shipped = {
        relative: hashlib.sha256((PACK / relative).read_bytes()).hexdigest()
        for relative in output_relatives
    }
    assert results[0] == shipped
    blocker = _json("sources/optional_preparation_status.json")
    assert blocker["status"] == "OPTIONAL_PREPARATION"
    assert blocker["connection_status"] == "NOT_CONNECTED"
    assert blocker["runtime_dependencies_declared_by_project"] is False
    assert blocker["reason"]


def test_builder_rejects_mutated_query_and_raw_trust_roots(tmp_path: Path) -> None:
    """[source_conformance] One-byte query or raw mutations fail before normalized artifacts are emitted."""
    for mutation in ("query", "raw"):
        fresh_pack = tmp_path / f"pack-{mutation}"
        fresh_raw = tmp_path / f"raw-{mutation}"
        (fresh_pack / "sources").mkdir(parents=True)
        fresh_raw.mkdir()
        query_bytes = (PACK / "sources/osm_arashiyama_20260829.overpassql").read_bytes()
        raw_bytes = (PACK / "sources/osm_arashiyama_20260829.raw.json").read_bytes()
        (fresh_pack / "sources/osm_arashiyama_20260829.overpassql").write_bytes(
            query_bytes + (b"\n" if mutation == "query" else b"")
        )
        (fresh_raw / "osm_arashiyama_20260829.raw.json").write_bytes(
            raw_bytes + (b"\n" if mutation == "raw" else b"")
        )
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                str(PACK / "tools/build_realdata.py"),
                "--pack",
                str(fresh_pack),
                "--raw-root",
                str(fresh_raw),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        expected = "query checksum mismatch" if mutation == "query" else "source checksum mismatch"
        assert expected in result.stderr


def test_retained_preview_rebind_rejects_unknown_bytes(tmp_path: Path) -> None:
    """[source_conformance] A mutated quarantined preview cannot receive trusted source metadata during ID rebind."""
    fresh_pack = tmp_path / "pack-preview-mutation"
    fresh_raw = tmp_path / "raw-preview-mutation"
    (fresh_pack / "sources").mkdir(parents=True)
    (fresh_pack / "hazards").mkdir(parents=True)
    fresh_raw.mkdir()
    shutil.copy2(PACK / "sources/osm_arashiyama_20260829.overpassql", fresh_pack / "sources")
    shutil.copy2(PACK / "sources/osm_arashiyama_20260829.raw.json", fresh_raw)
    preview = (PACK / "hazards/flood_a31b_2025.prepared.geojson").read_bytes() + b"\n"
    (fresh_pack / "hazards/flood_a31b_2025.prepared.geojson").write_bytes(preview)
    result = subprocess.run(
        [
            sys.executable,
            "-S",
            str(PACK / "tools/build_realdata.py"),
            "--pack",
            str(fresh_pack),
            "--raw-root",
            str(fresh_raw),
            "--rebind-retained-preview",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "retained preview checksum mismatch" in result.stderr
