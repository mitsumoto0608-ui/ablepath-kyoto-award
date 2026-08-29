# -*- coding: utf-8 -*-
"""藤沢・江の島city packの最終V4 hardening契約。"""
from __future__ import annotations

import copy
import csv
import json
import math
from collections import Counter
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "cities" / "fujisawa_enoshima"
DOC = ROOT / "docs" / "data" / "fujisawa_enoshima" / "SOURCE_AND_GAP_NOTES.md"
SUPPORTED_MAJOR = 1
V4_FIELDS = {
    "schema_version", "source_crs", "processing_crs", "output_crs",
    "horizontal_unit", "vertical_unit", "axis_order", "coordinate_precision",
    "transform_history", "geometry_status", "source_feature_id",
    "stable_feature_id", "revision_id", "lineage",
}
KPI_KEYS = {
    "physically_reachable", "accommodated", "overflow_waiting",
    "unreachable", "unknown_affected_upper_bound",
}
READINESS_KEYS = {
    "facility_status", "entrance_status", "capacity_status", "operation_status",
    "demand_status", "origin_status", "profile_status", "kpi_status", "m6_status",
}


def _json(relative: str) -> dict:
    return json.loads((PACK / relative).read_text(encoding="utf-8"))


def _yaml(relative: str) -> dict:
    return yaml.safe_load((PACK / relative).read_text(encoding="utf-8"))


def _csv(relative: str) -> list[dict[str, str]]:
    with (PACK / relative).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _require_supported_major(payload: dict, key: str, artifact: str) -> None:
    """Pack-local compatibility gate until a shared citypack loader exists."""
    value = payload.get(key)
    try:
        major = int(str(value).split(".", 1)[0])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {artifact} schema version {value!r}; expected semantic version") from exc
    if major != SUPPORTED_MAJOR:
        raise ValueError(
            f"Unsupported {artifact} schema major {major}; supported major is "
            f"{SUPPORTED_MAJOR}. Record a migration; implicit conversion is forbidden."
        )


def test_schema_major_two_mutant_is_rejected_actionably() -> None:
    """[software_correctness] major=2 mutantを暗黙解釈せずmigration要求付きで拒否する。"""
    city = _yaml("city.yaml")
    version_keys = {
        "schema_version": "envelope",
        "citypack_schema_version": "citypack",
        "hazard_schema_version": "hazard",
        "viewer_data_schema_version": "viewer",
    }
    for key, artifact in version_keys.items():
        _require_supported_major(city, key, artifact)
        mutant = copy.deepcopy(city)
        mutant[key] = "2.0.0"
        with pytest.raises(ValueError, match=rf"Unsupported {artifact} schema major 2.*migration"):
            _require_supported_major(mutant, key, artifact)
    assert city["schema_compatibility"] == {
        "supported_major": 1,
        "unsupported_major_policy": "REJECT_WITH_ACTIONABLE_ERROR",
        "migration_policy": "RECORD_REQUIRED_MIGRATION_NO_IMPLICIT_CONVERSION",
    }


def test_every_machine_artifact_carries_its_own_v4_contract() -> None:
    """[software_correctness] manifest記載だけでなく各machine-readable artifact自身を検証する。"""
    city = _yaml("city.yaml")
    assert V4_FIELDS <= city["geospatial_contract"].keys()
    assert V4_FIELDS <= _json("artifact_manifest.json").keys()
    assert V4_FIELDS <= _json("geography/corridor.metadata.json").keys()
    assert V4_FIELDS <= _json("graph/walk_nodes.geojson")["metadata"].keys()
    assert V4_FIELDS <= _json("graph/walk_edges.geojson")["metadata"].keys()
    assert V4_FIELDS <= _json("graph/topology_qa.json").keys()
    assert V4_FIELDS <= _yaml("hazards/scenarios.yaml").keys()
    assert V4_FIELDS <= _json("viewer/city_config.json").keys()
    for relative in (
        "sources/source_manifest.csv", "sources/data_gap_register.csv",
        "facilities/facilities.csv", "pois/pois.csv",
        "hazards/edge_states.csv", "demand/demand_scenarios.csv",
    ):
        rows = _csv(relative)
        assert rows, relative
        assert V4_FIELDS <= rows[0].keys(), relative
        assert all(row["schema_version"] == "1.0.0" for row in rows)


def test_official_metadata_does_not_imply_geometry_or_operation() -> None:
    """[source_conformance] 公式metadata、geometry、operationを独立した軸として保持する。"""
    sources = _csv("sources/source_manifest.csv")
    city = _yaml("city.yaml")
    viewer = _json("viewer/city_config.json")
    assert city["official_metadata_status"] == "OFFICIAL_METADATA_ONLY"
    assert city["official_data_targets"]["plateau_2025"]["catalog_status"] == "OFFICIAL_METADATA_ONLY"
    assert city["readiness"]["facility_status"] == "OFFICIAL_METADATA_ONLY"
    assert next(layer for layer in viewer["layers"] if layer["id"] == "official_tsunami_metadata")["status"] == "OFFICIAL_METADATA_ONLY"
    assert _json("geography/corridor.metadata.json")["geometry_status"] == "UNKNOWN"
    assert {row["source_class"] for row in sources} == {"OFFICIAL_METADATA_ONLY", "VGI_METADATA_ONLY"}
    for row in sources:
        assert row["download_status"] == "METADATA_ONLY"
        assert row["geometry_use"] == "NONE"
        assert row["geometry_status"] == "UNKNOWN"
        assert row["operation_status"] == "UNKNOWN"
    facility = _csv("facilities/facilities.csv")[0]
    assert facility["record_kind"] == "OFFICIAL_METADATA_ONLY"
    assert facility["data_status"] == "OFFICIAL_METADATA_ONLY"
    assert facility["geometry_status"] == facility["entrance_status"] == "UNKNOWN"
    assert facility["capacity"] == "" and facility["capacity_status"] == "UNKNOWN"
    assert facility["operation_status"] == "UNKNOWN" and facility["official_closure"] == ""


def test_edge_states_are_exact_dense_unique_cross_product() -> None:
    """[software_correctness] scenario×edgeを欠落・重複・orphanなしのexact dense matrixにする。"""
    rows = _csv("hazards/edge_states.csv")
    scenarios = {row["scenario_id"] for row in _yaml("hazards/scenarios.yaml")["scenarios"]}
    edges = {feature["properties"]["edge_id"] for feature in _json("graph/walk_edges.geojson")["features"]}
    expected = {(scenario, edge) for scenario in scenarios for edge in edges}
    pairs = [(row["scenario_id"], row["edge_id"]) for row in rows]
    assert len(rows) == len(expected)
    assert set(pairs) == expected
    assert set(Counter(pairs).values()) == {1}


def test_every_synthetic_edge_state_has_unique_traceability() -> None:
    """[source_conformance] 合成rowにもsource/stable ID、revision、lineageを必須化する。"""
    rows = _csv("hazards/edge_states.csv")
    for key in ("source_feature_id", "stable_feature_id"):
        values = [row[key] for row in rows]
        assert all(values) and len(values) == len(set(values))
    for row in rows:
        assert row["data_status"] == row["geometry_status"] == "SYNTHETIC_DEMO"
        assert row["source_feature_id"].startswith("SYNTHETIC-DEMO-")
        assert row["revision_id"] and row["lineage"]
        assert row["physical_state"] == row["operational_state"] == "UNKNOWN"


def test_graph_endpoints_match_nodes_and_edges_are_nonzero() -> None:
    """[software_correctness] ID参照だけでなく座標端点一致・finite・zero-length拒否を検証する。"""
    nodes = _json("graph/walk_nodes.geojson")["features"]
    edges = _json("graph/walk_edges.geojson")["features"]
    node_coordinates = {feature["properties"]["node_id"]: feature["geometry"]["coordinates"] for feature in nodes}
    for feature in edges:
        props = feature["properties"]
        coordinates = feature["geometry"]["coordinates"]
        assert coordinates[0] == node_coordinates[props["from_node"]]
        assert coordinates[-1] == node_coordinates[props["to_node"]]
        assert coordinates[0] != coordinates[-1]
        assert all(math.isfinite(float(value)) for point in coordinates for value in point)


def test_topology_qa_is_explicit_and_recomputed() -> None:
    """[software_correctness] computed QA件数と、計算不能3項目のreasonを固定する。"""
    nodes = _json("graph/walk_nodes.geojson")["features"]
    edges = _json("graph/walk_edges.geojson")["features"]
    node_ids = [feature["properties"]["node_id"] for feature in nodes]
    edge_ids = [feature["properties"]["edge_id"] for feature in edges]
    degree = Counter(endpoint for edge in edges for endpoint in (edge["properties"]["from_node"], edge["properties"]["to_node"]))
    computed = {
        "duplicate_node_ids": len(node_ids) - len(set(node_ids)),
        "duplicate_edge_ids": len(edge_ids) - len(set(edge_ids)),
        "dangling_endpoint_nodes": sum(value == 1 for value in degree.values()),
        "self_loops": sum(edge["properties"]["from_node"] == edge["properties"]["to_node"] for edge in edges),
        "zero_length_edges": sum(edge["geometry"]["coordinates"][0] == edge["geometry"]["coordinates"][-1] for edge in edges),
    }
    qa = _json("graph/topology_qa.json")
    assert set(qa) == V4_FIELDS | {
        "graph_status", "data_class", "counts", "not_computed", "promotion_blocker",
    }
    assert qa["graph_status"] == "CANDIDATE"
    assert qa["data_class"] == "SYNTHETIC_DEMO"
    assert qa["counts"] == computed
    assert set(qa["not_computed"]) == {
        "disconnected_real_destinations",
        "unsplit_hazard_boundaries",
        "grade_separated_false_intersections",
    }
    for entry in qa["not_computed"].values():
        assert set(entry) == {"status", "reason"}
        assert entry["status"] == "NOT_COMPUTED"
        assert entry["reason"]
    assert qa["promotion_blocker"]
    assert "topology_qa" not in _json("artifact_manifest.json")


def test_source_references_resolve_without_promoting_unknowns() -> None:
    """[source_conformance] provenance IDをmanifestへ参照整合し、UNKNOWNを状態語へ変換しない。"""
    source_ids = {row["dataset_id"] for row in _csv("sources/source_manifest.csv")}
    for row in _csv("hazards/edge_states.csv"):
        assert set(filter(None, row["source_dataset_ids"].split("|"))) <= source_ids
        assert row["arrival_time_min"] == row["inundation_depth_m"] == row["closure_time_min"] == ""
    for gap in _csv("sources/data_gap_register.csv"):
        assert not gap["source_dataset_id"] or gap["source_dataset_id"] in source_ids


def test_kpis_and_unavailable_inputs_remain_null_with_reason() -> None:
    """[target_validation] 不足した需要・容量・topology・profileを数値やPASSへ変換しない。"""
    city = _yaml("city.yaml")
    viewer = _json("viewer/city_config.json")
    assert set(city["readiness"]) == READINESS_KEYS
    assert city["readiness"]["m6_status"] == "NOT_COMPUTED"
    assert set(city["kpis"]) == KPI_KEYS
    assert set(viewer["kpis"]) == KPI_KEYS
    for payload in (city["kpis"], viewer["kpis"]):
        for item in payload.values():
            assert set(item) == {"value", "reason"}
            assert item["value"] is None and item["reason"].strip()
    assert city["readiness"]["profile_status"] == "NOT_COMPUTED"
    assert viewer["profile_selector"] == {
        "enabled": False,
        "status": "NOT_COMPUTED",
        "reason": "M6/profile evaluation is not connected.",
    }
    for row in _csv("demand/demand_scenarios.csv"):
        assert row["demand_value"] == "" and row["demand_status"] == "UNKNOWN"
        assert row["profile_status"] == "NOT_COMPUTED" and row["reason"]


def test_pack_has_no_forbidden_claim_path_or_secret_marker() -> None:
    """[source_conformance] public artifactへ安全保証、ローカルpath、credentialを混入しない。"""
    paths = [path for path in PACK.rglob("*") if path.is_file()] + [DOC]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    prohibited = (
        "安全な" + "避難ルート", "UNKNOWN" + "をOPEN", "UNKNOWN" + "をPASS",
        "C:" + "\\Users\\", "Drop" + "box", "api_" + "key", "client_" + "secret",
        "BEGIN " + "PRIVATE KEY",
    )
    assert all(value not in text for value in prohibited)
