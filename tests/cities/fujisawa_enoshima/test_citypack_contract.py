# -*- coding: utf-8 -*-
"""藤沢・江の島city packのV4安全契約。"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlparse

import yaml

from src.hazards import HazardScenario, load_edge_observation_table


ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "cities" / "fujisawa_enoshima"
KPI_KEYS = {
    "physically_reachable", "accommodated", "overflow_waiting",
    "unreachable", "unknown_affected_upper_bound",
}


def _csv_rows(relative: str) -> list[dict[str, str]]:
    with (PACK / relative).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _json(relative: str) -> dict:
    return json.loads((PACK / relative).read_text(encoding="utf-8"))


def _sha256(relative: str) -> str:
    return hashlib.sha256((PACK / relative).read_bytes()).hexdigest()


def _yaml(relative: str) -> dict:
    return yaml.safe_load((PACK / relative).read_text(encoding="utf-8"))


def test_required_citypack_files_exist():
    """[software_correctness] V4基盤と承認済みP0実geometry成果物を欠落させない。"""
    required = {
        "city.yaml",
        "artifact_manifest.json",
        "sources/source_manifest.csv",
        "sources/data_gap_register.csv",
        "geography/corridor.metadata.json",
        "graph/walk_nodes.geojson",
        "graph/walk_edges.geojson",
        "graph/topology_qa.json",
        "facilities/facilities.csv",
        "pois/pois.csv",
        "hazards/scenarios.yaml",
        "hazards/edge_states.csv",
        "demand/demand_scenarios.csv",
        "viewer/city_config.json",
        "README.md",
    }
    required_p0 = {
        ".gitattributes",
        "geography/corridor.real.geojson",
        "graph/candidate_walk_nodes.real.geojson",
        "graph/candidate_walk_edges.real.geojson",
        "graph/candidate_topology_qa.real.json",
        "realdata/artifact_manifest.v2.json",
        "sources/osm-corridor.overpassql",
        "sources/receipts/osm-corridor.raw.receipt.json",
        "sources/unresolved_contracts.json",
        "status.json",
    }
    actual = {str(path.relative_to(PACK)).replace("\\", "/") for path in PACK.rglob("*") if path.is_file()}
    assert actual == required | required_p0


def test_city_schema_versions_and_readiness_are_explicit():
    """[software_correctness] envelope schemaと9種readinessを明示し、暗黙変換を拒否する。"""
    city = _yaml("city.yaml")
    assert city["schema_version"] == "1.0.0"
    assert city["citypack_schema_version"] == "1.0.0"
    assert city["hazard_schema_version"] == "1.0.0"
    assert city["viewer_data_schema_version"] == "1.0.0"
    assert city["schema_compatibility"] == {
        "supported_major": 1,
        "unsupported_major_policy": "REJECT_WITH_ACTIONABLE_ERROR",
        "migration_policy": "RECORD_REQUIRED_MIGRATION_NO_IMPLICIT_CONVERSION",
    }
    readiness = city["readiness"]
    assert set(readiness) == {
        "facility_status", "entrance_status", "capacity_status", "operation_status",
        "demand_status", "origin_status", "profile_status", "kpi_status", "m6_status",
    }
    assert readiness["profile_status"] == "NOT_COMPUTED"
    assert readiness["m6_status"] == "NOT_COMPUTED"
    assert readiness["kpi_status"] == "NOT_COMPUTED"
    assert readiness["capacity_status"] == "UNKNOWN"
    assert readiness["operation_status"] == "UNKNOWN"


def test_kpis_are_null_with_actionable_reasons():
    """[target_validation] 不足データからKPI値や順位を捏造しない。"""
    city = _yaml("city.yaml")
    assert set(city["kpis"]) == KPI_KEYS
    for kpi in city["kpis"].values():
        assert set(kpi) == {"value", "reason"}
        assert kpi["value"] is None
        assert kpi["reason"].strip()
    assert city["completion_levels"] == {
        "ENGINEERING_UI_COMPLETE": False,
        "DATA_STAGING_COMPLETE": True,
        "REAL_GEOMETRY_CONNECTED": False,
        "MODEL_CONNECTED": False,
        "ADMIN_VALIDATED": False,
        "overall": "PARTIAL_COMPLETE",
    }


def test_source_manifest_has_v4_freshness_and_allowlisted_sources():
    """[source_conformance] source freshness・再配布・確認時点を各datasetへ保持する。"""
    rows = _csv_rows("sources/source_manifest.csv")
    assert len(rows) >= 7
    required = {
        "published_updated_date", "version_year_spec", "license_terms", "format",
        "crs", "vertical_datum", "download_status", "local_relative_path",
        "sha256", "geographic_coverage", "usable_fields", "missing_fields",
        "interpretation_limits",
        "valid_as_of", "freshness_status", "supersedes_dataset_id",
        "superseded_by_dataset_id", "recheck_by", "retrieval_etag",
        "retrieval_last_modified", "redistribution_status",
    }
    assert required <= set(rows[0])
    allowed_freshness = {
        "CURRENT_CONFIRMED", "CURRENT_UNVERIFIED", "POSSIBLY_STALE",
        "SUPERSEDED", "UNKNOWN", "FIXED_SNAPSHOT",
    }
    allowed_hosts = {
        "www.city.fujisawa.kanagawa.jp", "front.geospatial.jp", "www.gsi.go.jp",
        "www.openstreetmap.org", "overpass-api.de",
    }
    assert len({row["dataset_id"] for row in rows}) == len(rows)
    for row in rows:
        assert row["freshness_status"] in allowed_freshness
        assert row["accessed_at"] == "2026-08-30"
        assert row["recheck_by"]
        assert urlparse(row["url"]).scheme == "https"
        assert urlparse(row["url"]).hostname in allowed_hosts
        if row["dataset_id"] == "OSM_CANDIDATE_SOURCE":
            assert row["freshness_status"] == "FIXED_SNAPSHOT"
            assert row["download_status"] == "EXTERNAL_RAW_RECEIPT_ONLY"
        else:
            assert row["download_status"] == "METADATA_ONLY"
        assert row["local_relative_path"] == "" and row["sha256"] == ""
        assert row["geographic_coverage"] and row["usable_fields"]
        assert row["missing_fields"] and row["interpretation_limits"]
        assert row["geometry_use"] == "NONE"


def test_artifact_manifest_covers_all_machine_readable_artifacts():
    """[software_correctness] artifactごとのschema/geometry statusを暗黙にしない。"""
    manifest = _json("artifact_manifest.json")
    geospatial_keys = {
        "schema_version", "source_crs", "processing_crs", "output_crs",
        "horizontal_unit", "vertical_unit", "axis_order", "coordinate_precision",
        "transform_history", "geometry_status", "source_feature_id",
        "stable_feature_id", "revision_id", "lineage",
    }
    assert geospatial_keys <= set(manifest)
    listed = {entry["path"] for entry in manifest["artifacts"]}
    actual = {
        str(path.relative_to(PACK)).replace("\\", "/")
        for path in PACK.rglob("*")
        if path.is_file() and path.name not in {"README.md", "artifact_manifest.json"}
    }
    assert listed == actual
    assert {entry["schema_version"] for entry in manifest["artifacts"]} <= {"1.0.0", "2.0.0"}
    assert {
        entry["path"] for entry in manifest["artifacts"] if entry["schema_version"] == "2.0.0"
    } == {
        "geography/corridor.real.geojson",
        "graph/candidate_walk_nodes.real.geojson",
        "graph/candidate_walk_edges.real.geojson",
        "graph/candidate_topology_qa.real.json",
        "realdata/artifact_manifest.v2.json",
    }
    assert all(entry["geometry_status"] for entry in manifest["artifacts"])


def test_real_candidate_manifest_is_single_hash_bound_authority():
    """[source_conformance] v2 authority binds every P0 artifact to one fixed-snapshot receipt."""
    city = _yaml("city.yaml")
    envelope = _json("artifact_manifest.json")
    real = _json("realdata/artifact_manifest.v2.json")
    receipt_path = "sources/receipts/osm-corridor.raw.receipt.json"
    receipt = _json(receipt_path)
    sources = {row["dataset_id"]: row for row in _csv_rows("sources/source_manifest.csv")}
    expected = {
        "geography/corridor.real.geojson",
        "graph/candidate_walk_nodes.real.geojson",
        "graph/candidate_walk_edges.real.geojson",
        "graph/candidate_topology_qa.real.json",
    }
    assert city["p0_osm_candidate_artifact_manifest"] == "realdata/artifact_manifest.v2.json"
    assert real["schema_version"] == "2.0.0"
    assert real["authority"] == "FUJISAWA_P0_OSM_CANDIDATE_ONLY"
    assert real["source_dataset_id"] == "OSM_CANDIDATE_SOURCE"
    assert real["source_raw_sha256"] == receipt["raw_sha256"]
    assert {entry["artifact_path"] for entry in real["artifacts"]} == expected
    assert all(entry["source_receipt_path"] == receipt_path for entry in real["artifacts"])
    assert all(_sha256(entry["artifact_path"]) == entry["sha256"] for entry in real["artifacts"])
    envelope_v2 = {
        entry["path"] for entry in envelope["artifacts"]
        if entry["schema_version"] == "2.0.0" and entry["path"] != "realdata/artifact_manifest.v2.json"
    }
    assert envelope_v2 == expected
    source = sources[real["source_dataset_id"]]
    assert source["freshness_status"] == "FIXED_SNAPSHOT"
    assert source["download_status"] == "EXTERNAL_RAW_RECEIPT_ONLY"
    assert source["source_class"] == "VGI_METADATA_ONLY"


def test_real_geometry_is_absent_and_demo_geometry_is_unmistakable():
    """[source_conformance] 合成geometryを実geometryやOSM取得物として表示しない。"""
    for relative in ("graph/walk_nodes.geojson", "graph/walk_edges.geojson"):
        collection = _json(relative)
        metadata = collection["metadata"]
        assert metadata["geometry_status"] == "SYNTHETIC_DEMO"
        assert metadata["topology_status"] == "CANDIDATE"
        assert metadata["processing_crs"] == "EPSG:6677"
        assert metadata["output_crs"] == "EPSG:4326"
        assert metadata["axis_order"] == "longitude_latitude"
        assert metadata["vertical_unit"] == "UNKNOWN"
        for feature in collection["features"]:
            props = feature["properties"]
            assert props["data_status"] == "SYNTHETIC_DEMO"
            assert props["geometry_status"] == "SYNTHETIC_DEMO"
            assert props["source_feature_id"].startswith("SYNTHETIC-DEMO-")
            assert props["stable_feature_id"]
            assert props["revision_id"]
            assert props["lineage"] == ["FIXTURE_VALUE"]


def test_candidate_graph_references_are_valid_and_deterministic():
    """[software_correctness] edge端点・ID・座標有限性を検証し、candidate以上を主張しない。"""
    nodes = _json("graph/walk_nodes.geojson")["features"]
    edges = _json("graph/walk_edges.geojson")["features"]
    node_ids = [feature["properties"]["node_id"] for feature in nodes]
    edge_ids = [feature["properties"]["edge_id"] for feature in edges]
    assert node_ids == sorted(node_ids) and len(node_ids) == len(set(node_ids))
    assert edge_ids == sorted(edge_ids) and len(edge_ids) == len(set(edge_ids))
    for feature in nodes:
        assert all(math.isfinite(value) for value in feature["geometry"]["coordinates"])
    for feature in edges:
        props = feature["properties"]
        assert props["from_node"] in node_ids and props["to_node"] in node_ids
        assert props["from_node"] != props["to_node"]
        assert props["bridge"] == "UNKNOWN" and props["tunnel"] == "UNKNOWN"
        assert props["length_m"] is None
        assert all(math.isfinite(value) for point in feature["geometry"]["coordinates"] for value in point)


def test_static_hazard_scenarios_do_not_invent_numbers_or_operations():
    """[target_validation] 静的physical snapshotと運用状態を分離し、未確認時刻等をnullにする。"""
    payload = _yaml("hazards/scenarios.yaml")
    assert payload["hazard_schema_version"] == "1.0.0"
    assert payload["evaluation_mode"] == "STATIC_SNAPSHOT_COMPARISON"
    scenarios = payload["scenarios"]
    assert [row["scenario_id"] for row in scenarios] == [
        "TSUNAMI_STRICT", "TSUNAMI_OPERATIONAL", "TSUNAMI_SENSITIVITY"
    ]
    for row in scenarios:
        assert set(row) == {
            "scenario_id", "hazard_type", "source_status", "official_or_assumption",
            "elapsed_time_sec", "coverage_complete", "default_edge_state",
            "disclaimer", "source_ids",
        }
        scenario = HazardScenario.from_mapping(row)
        assert scenario.source_status == "SYNTHETIC_DEMO"
        assert scenario.official_or_assumption == "ABLEPATH_DESIGN"
        assert scenario.elapsed_time_sec is None
        assert scenario.coverage_complete is False
        assert scenario.default_edge_state == "UNKNOWN"
    for row in _csv_rows("hazards/edge_states.csv"):
        assert row["snapshot_mode"] == "STATIC_SNAPSHOT_COMPARISON"
        assert row["physical_state"] == "UNKNOWN"
        assert row["operational_state"] == "UNKNOWN"
        assert row["arrival_time_min"] == row["inundation_depth_m"] == row["closure_time_min"] == ""


def test_actual_edge_table_loads_through_shared_runtime_adapter():
    """[software_correctness] 実CSVをexact header・UNKNOWN-only共有adapterで検証する。"""
    records = load_edge_observation_table(PACK / "hazards" / "edge_states.csv")
    assert len(records) == 3
    assert {record.dialect_id for record in records} == {"FUJISAWA_EDGE_UNKNOWN_V1"}
    assert all(record.observation.hazard_data_status == "UNKNOWN" for record in records)
    assert all(record.observation.overlap is None for record in records)
    assert all(record.observation.official_closure is None for record in records)


def test_facility_types_and_unknowns_are_not_conflated():
    """[source_conformance] 指定種別と入口・容量・運用の未知を別fieldで保持する。"""
    rows = _csv_rows("facilities/facilities.csv")
    assert len(rows) == 1
    row = rows[0]
    allowed_types = {
        "designated_emergency_evacuation_place", "designated_shelter",
        "tourist_emergency_evacuation_plaza", "temporary_stay_facility",
        "tsunami_evacuation_building", "other",
    }
    assert row["facility_type"] in allowed_types
    assert row["data_status"] == "OFFICIAL_METADATA_ONLY"
    assert row["geometry_status"] == "UNKNOWN"
    assert row["entrance_status"] == "UNKNOWN"
    assert row["capacity"] == "" and row["capacity_status"] == "UNKNOWN"
    assert row["operation_status"] == "UNKNOWN" and row["official_closure"] == ""


def test_demand_and_profile_remain_uncomputed():
    """[target_validation] 合成originから需要・profile結果を作らない。"""
    for row in _csv_rows("demand/demand_scenarios.csv"):
        assert row["demand_value"] == ""
        assert row["data_status"] == "UNKNOWN"
        assert row["demand_status"] == "UNKNOWN"
        assert row["origin_status"] == "SYNTHETIC_DEMO"
        assert row["profile_status"] == "NOT_COMPUTED"
        assert row["reason"]


def test_viewer_contract_disables_profile_and_exposes_null_reasons():
    """[ui_regression] 未計算selectorをactiveにせず、KPI不足理由を保持する。"""
    viewer = _json("viewer/city_config.json")
    assert viewer["viewer_data_schema_version"] == "1.0.0"
    assert viewer["profile_selector"]["enabled"] is False
    assert viewer["profile_selector"]["status"] == "NOT_COMPUTED"
    assert viewer["kpi_status"] == "NOT_COMPUTED"
    assert set(viewer["kpis"]) == KPI_KEYS
    for kpi in viewer["kpis"].values():
        assert kpi["value"] is None and kpi["reason"]
    assert "ライブの安全案内" in viewer["scenario_disclaimer"]


def test_gap_register_covers_each_readiness_blocker():
    """[target_validation] nullのまま残す理由と取得actionを追跡可能にする。"""
    rows = _csv_rows("sources/data_gap_register.csv")
    assert len(rows) >= 8
    assert len({row["gap_id"] for row in rows}) == len(rows)
    categories = {row["category"] for row in rows}
    assert {"REAL_GEOMETRY", "HAZARD_GEOMETRY", "FACILITY_ENTRANCE", "FACILITY_OPERATION", "FACILITY_CAPACITY", "DEMAND_AND_ORIGINS", "M6_PROFILE", "TIME_DEPENDENCE"} <= categories
    for row in rows:
        assert row["status"] == "BLOCKED"
        assert row["description"] and row["required_action"] and row["blocking_kpis"]
