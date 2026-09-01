"""Kyoto Kiyomizu V4 city-pack contract tests."""
from __future__ import annotations

import csv
import copy
import json
import math
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import pytest
import yaml

from src.hazards import HazardScenario, load_edge_observation_table


ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "cities" / "kyoto_kiyomizu"
DOC = ROOT / "docs" / "data" / "kyoto_kiyomizu" / "DATA_READINESS.md"
SCENARIOS = {"EQ_LOW", "EQ_MEDIUM", "EQ_HIGH"}
GEO_KEYS = {
    "schema_version", "source_crs", "processing_crs", "output_crs",
    "horizontal_unit", "vertical_unit", "axis_order", "coordinate_precision",
    "transform_history", "geometry_status", "source_feature_id",
    "stable_feature_id", "revision_id", "lineage",
}
FRESHNESS = {"CURRENT_CONFIRMED", "CURRENT_UNVERIFIED", "POSSIBLY_STALE", "SUPERSEDED", "UNKNOWN"}
ALLOWED_DOMAINS = {
    "api.plateauview.mlit.go.jp", "www.openstreetmap.org", "www.city.kyoto.lg.jp",
    "www.bousaimap.city.kyoto.lg.jp", "www.pref.kyoto.jp",
    "www.bousai.city.kyoto.lg.jp", "data.city.kyoto.lg.jp", "www.gsi.go.jp",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(relative: str) -> dict:
    return json.loads((PACK / relative).read_text(encoding="utf-8"))


def require_supported_schema_majors(city: dict) -> None:
    """Apply the declared fail-closed city-pack compatibility policy."""
    policy = city["schema_compatibility"]
    if policy["unsupported_major_policy"] != "REJECT_WITH_ACTIONABLE_ERROR":
        raise ValueError("unsupported schema major policy must fail closed")
    supported = str(policy["supported_major"])
    for key in (
        "schema_version", "citypack_schema_version",
        "hazard_schema_version", "viewer_data_schema_version",
    ):
        if str(city[key]).split(".", 1)[0] != supported:
            raise ValueError(f"unsupported {key}: {city[key]}")


def test_city_pack_has_exact_required_structure():
    """[software_correctness] Legacy pack and reviewed additive v2 lane form one exact set."""
    legacy_expected = {
        "city.yaml", "README.md", "sources/source_manifest.csv",
        "sources/data_gap_register.csv", "geography/corridor.metadata.json",
        "graph/walk_nodes.geojson", "graph/walk_edges.geojson",
        "graph/topology_qa.json",
        "facilities/facilities.csv", "pois/pois.csv", "hazards/scenarios.yaml",
        "hazards/edge_physics.csv", "demand/demand_scenarios.csv",
        "viewer/city_config.json",
    }
    v2_expected = {
        "geography/real/corridor.osm.geojson",
        "graph/real/candidate_edges.geojson",
        "graph/real/candidate_nodes.geojson",
        "graph/real/topology_qa.json",
        "hazards/official/landslide_warning_preview.geojson",
        "hazards/official/landslide_warning_preview.metadata.json",
        "model/m7_input_readiness.json",
        "realdata/artifact_manifest.v2.json",
        "realdata/status.json",
        "sources/plateau_26100_metadata.json",
        "sources/queries/osm_corridor_20260830.overpassql",
        "sources/queries/plateau_26100_bldg_tileset_url.txt",
        "sources/retained/osm_corridor_20260830.raw.json",
        "sources/retained/plateau_26100_bldg_tileset_20260830.json",
        "tools/build_realdata.py",
        "terrain/official/dem_product_inventory.csv",
        "terrain/official/source_receipt.json",
        "hazards/official/promotion_v2_receipt.json",
        "facilities/official/promotion_v2_status.json",
        "sources/receipts/official_local_promotion_v2.json",
    }
    actual = {path.relative_to(PACK).as_posix() for path in PACK.rglob("*") if path.is_file()}
    assert actual == legacy_expected | v2_expected


def test_schema_versions_are_explicit_supported_major_one():
    """[software_correctness] citypack/hazard/viewer schemaのmajor=1を明示し暗黙互換を許さない。"""
    city = yaml.safe_load((PACK / "city.yaml").read_text(encoding="utf-8"))
    assert city["schema_version"] == "1.0.0"
    assert {city[key] for key in (
        "citypack_schema_version", "hazard_schema_version", "viewer_data_schema_version"
    )} == {"1.0.0"}
    assert "geospatial" not in city
    geospatial = city["geospatial_contract"]
    assert GEO_KEYS <= geospatial.keys()
    assert geospatial["processing_crs"] == "EPSG:6674"
    assert geospatial["output_crs"] == "EPSG:4326"
    assert geospatial["axis_order"] == ["longitude", "latitude"]
    assert all(geospatial[key] for key in (
        "source_feature_id", "stable_feature_id", "revision_id", "lineage"
    ))
    assert city["schema_compatibility"] == {
        "supported_major": 1,
        "unsupported_major_policy": "REJECT_WITH_ACTIONABLE_ERROR",
        "migration_policy": "RECORD_REQUIRED_MIGRATION_NO_IMPLICIT_CONVERSION",
    }
    require_supported_schema_majors(city)

    unsupported_major_mutant = copy.deepcopy(city)
    unsupported_major_mutant["schema_version"] = "2.0.0"
    with pytest.raises(ValueError, match="unsupported schema_version"):
        require_supported_schema_majors(unsupported_major_mutant)


def test_source_manifest_has_v4_freshness_and_honest_download_status():
    """[source_conformance] metadata sourceにV4 freshness列を持たせ未取得をDOWNLOADEDとしない。"""
    rows = read_csv(PACK / "sources" / "source_manifest.csv")
    required = {
        "dataset_id", "source_class", "evidence_class", "source_url", "accessed_at",
        "valid_as_of", "freshness_status", "supersedes_dataset_id",
        "superseded_by_dataset_id", "recheck_by", "retrieval_etag",
        "retrieval_last_modified", "redistribution_status", "download_status",
        "sha256", "source_crs", "vertical_datum", "axis_order", "horizontal_unit",
        "vertical_unit", "geometry_status", "data_status", "lineage",
    }
    assert len(rows) == 9
    assert required <= rows[0].keys()
    assert len({row["dataset_id"] for row in rows}) == len(rows)
    assert all(row["accessed_at"] == "2026-08-30" for row in rows)
    assert all(row["freshness_status"] in FRESHNESS for row in rows)
    assert all(row["download_status"] == "METADATA_ONLY" for row in rows)
    assert all(row["sha256"] == "" for row in rows)
    osm = next(row for row in rows if row["dataset_id"] == "osm_kiyomizu_corridor")
    assert {osm[key] for key in ("source_class", "evidence_class", "data_status")} == {"VGI_METADATA_ONLY"}
    official = [row for row in rows if row is not osm]
    assert all(row["source_class"] == "OFFICIAL_METADATA_ONLY" for row in official)
    assert all(row["evidence_class"] == "OFFICIAL_METADATA_ONLY" for row in official)
    assert all(row["data_status"] == "OFFICIAL_METADATA_ONLY" for row in official)
    assert all(urlparse(row["source_url"]).hostname in ALLOWED_DOMAINS for row in rows)

    plateau = next(row for row in rows if row["dataset_id"] == "plateau_kyoto_2025_release")
    assert plateau["freshness_status"] == "UNKNOWN"
    assert plateau["version"] == "URL_REVERIFICATION_REQUIRED"
    assert plateau["download_status"] == "METADATA_ONLY"
    assert plateau["recheck_by"]


def test_official_metadata_is_not_mixed_with_feature_data_classes():
    """[source_conformance] OFFICIAL_METADATA_ONLYをREAL等のfeatureへ昇格しない。"""
    rows = read_csv(PACK / "sources" / "source_manifest.csv")
    assert all(row["data_status"] != "REAL" for row in rows)
    for relative in ("graph/walk_nodes.geojson", "graph/walk_edges.geojson"):
        document = load_json(relative)
        assert document["data_status"] == "SYNTHETIC_DEMO"
        assert all(feature["properties"]["data_status"] == "SYNTHETIC_DEMO" for feature in document["features"])
        assert all("OFFICIAL" not in feature["properties"]["lineage"] for feature in document["features"])


def test_geospatial_metadata_is_complete_at_collection_and_feature_level():
    """[software_correctness] V4 geospatial metadataを全artifact/featureに持たせる。"""
    for relative in ("graph/walk_nodes.geojson", "graph/walk_edges.geojson"):
        document = load_json(relative)
        assert GEO_KEYS <= document.keys()
        assert document["processing_crs"] == "EPSG:6674"
        assert document["output_crs"] == "EPSG:4326"
        assert document["axis_order"] == ["longitude", "latitude"]
        for feature in document["features"]:
            assert GEO_KEYS <= feature["properties"].keys()
            assert feature["properties"]["geometry_status"] == "SYNTHETIC_DEMO_CANDIDATE"


def test_every_geospatial_artifact_has_traceable_identity_and_lineage():
    """[source_conformance] geometry/QA成果物ごとにsource/stable/revision/lineageを必須化する。"""
    for relative in (
        "geography/corridor.metadata.json",
        "graph/walk_nodes.geojson",
        "graph/walk_edges.geojson",
        "graph/topology_qa.json",
    ):
        artifact = load_json(relative)
        assert GEO_KEYS <= artifact.keys()
        assert artifact["stable_feature_id"]
        assert artifact["revision_id"]
        assert artifact["lineage"]
        assert "source_feature_id" in artifact


def test_synthetic_geometries_are_finite_valid_and_deterministically_ordered():
    """[software_correctness] empty/null/nonfinite geometryを許さずstable ID順を固定する。"""
    nodes = load_json("graph/walk_nodes.geojson")
    edges = load_json("graph/walk_edges.geojson")
    node_ids = [feature["properties"]["stable_feature_id"] for feature in nodes["features"]]
    edge_ids = [feature["properties"]["stable_feature_id"] for feature in edges["features"]]
    assert node_ids == sorted(node_ids) and edge_ids == sorted(edge_ids)
    for feature in nodes["features"]:
        assert feature["geometry"]["type"] == "Point"
        coords = feature["geometry"]["coordinates"]
        assert len(coords) == 2 and all(type(value) is float and math.isfinite(value) for value in coords)
    for feature in edges["features"]:
        assert feature["geometry"]["type"] == "LineString"
        coords = feature["geometry"]["coordinates"]
        assert len(coords) >= 2 and all(type(value) is float and math.isfinite(value) for pair in coords for value in pair)
        assert len({tuple(pair) for pair in coords}) > 1


def test_candidate_topology_has_no_duplicate_dangling_self_loop_or_false_endpoint():
    """[software_correctness] synthetic candidateでもID・endpoint・zero-lengthの基本QAを通す。"""
    nodes = load_json("graph/walk_nodes.geojson")["features"]
    edges = load_json("graph/walk_edges.geojson")["features"]
    node_by_id = {feature["properties"]["node_id"]: feature for feature in nodes}
    assert len(node_by_id) == len(nodes)
    edge_ids = [feature["properties"]["edge_id"] for feature in edges]
    assert len(edge_ids) == len(set(edge_ids))
    for feature in edges:
        props = feature["properties"]
        assert props["from_node"] in node_by_id and props["to_node"] in node_by_id
        assert props["from_node"] != props["to_node"]
        assert feature["geometry"]["coordinates"][0] == node_by_id[props["from_node"]]["geometry"]["coordinates"]
        assert feature["geometry"]["coordinates"][-1] == node_by_id[props["to_node"]]["geometry"]["coordinates"]
    assert {feature["properties"]["node_id"] for feature in nodes} == {
        endpoint for edge in edges for endpoint in (edge["properties"]["from_node"], edge["properties"]["to_node"])
    }


def test_topology_qa_report_matches_computable_fixture_counts_and_marks_unknowns():
    """[software_correctness] V4 topology QAを再計算し、計算不能カテゴリは理由付きで止める。"""
    nodes = load_json("graph/walk_nodes.geojson")["features"]
    edges = load_json("graph/walk_edges.geojson")["features"]
    report = load_json("graph/topology_qa.json")
    node_ids = [item["properties"]["node_id"] for item in nodes]
    edge_ids = [item["properties"]["edge_id"] for item in edges]
    endpoint_counts = Counter(
        endpoint
        for edge in edges
        for endpoint in (edge["properties"]["from_node"], edge["properties"]["to_node"])
    )
    expected_counts = {
        "duplicate_node_ids": len(node_ids) - len(set(node_ids)),
        "duplicate_edge_ids": len(edge_ids) - len(set(edge_ids)),
        "dangling_endpoint_nodes": sum(count == 1 for count in endpoint_counts.values()),
        "self_loops": sum(
            edge["properties"]["from_node"] == edge["properties"]["to_node"] for edge in edges
        ),
        "zero_length_edges": sum(
            len({tuple(point) for point in edge["geometry"]["coordinates"]}) == 1 for edge in edges
        ),
    }
    assert report["counts"] == expected_counts
    assert set(report["not_computed"]) == {
        "disconnected_real_destinations",
        "unsplit_hazard_boundaries",
        "grade_separated_false_intersections",
    }
    assert all(
        set(value) == {"status", "reason"}
        and value["status"] == "NOT_COMPUTED"
        and value["reason"]
        for value in report["not_computed"].values()
    )


def test_facilities_pois_demand_capacity_and_entrances_are_not_invented():
    """[source_conformance] 未確認施設点・入口・容量・需要を0やcentroidで補完しない。"""
    assert read_csv(PACK / "facilities" / "facilities.csv") == []
    assert read_csv(PACK / "pois" / "pois.csv") == []
    demand = read_csv(PACK / "demand" / "demand_scenarios.csv")
    assert {row["scenario_id"] for row in demand} == SCENARIOS
    assert all(row["demand"] == "" for row in demand)
    assert all(row["origin_status"] == row["demand_status"] == row["capacity_status"] == "UNKNOWN" for row in demand)
    assert all(row["profile_status"] == row["kpi_status"] == "NOT_COMPUTED" for row in demand)
    assert all(row["reason"] for row in demand)


def test_earthquake_scenarios_do_not_invent_building_damage_or_edge_state():
    """[source_conformance] EQ三IDは比較用fixtureに留めdamage/debris/closureをUNKNOWNで保持する。"""
    document = yaml.safe_load((PACK / "hazards" / "scenarios.yaml").read_text(encoding="utf-8"))
    assert document["hazard_schema_version"] == "1.0.0"
    assert {scenario["scenario_id"] for scenario in document["scenarios"]} == SCENARIOS
    expected_keys = {
        "scenario_id", "hazard_type", "source_status", "official_or_assumption",
        "elapsed_time_sec", "coverage_complete", "default_edge_state",
        "disclaimer", "source_ids",
    }
    for scenario in document["scenarios"]:
        assert set(scenario) == expected_keys
        assert scenario["source_status"] == "SYNTHETIC_DEMO"
        assert scenario["official_or_assumption"] == "ABLEPATH_DESIGN"
        assert scenario["coverage_complete"] is False
        assert scenario["default_edge_state"] == "UNKNOWN"
        assert scenario["elapsed_time_sec"] is None
        assert scenario["source_ids"] == ["kyoto_web_hazard_earthquake"]
    layer = document["secondary_layers"][0]
    assert layer["geometry_status"] == layer["operation_rule_status"] == layer["edge_state_effect"] == "UNKNOWN"


def test_every_scenario_artifact_satisfies_shared_hazard_contract():
    """[software_correctness] 実artifact全件をshared exact 9-field parserへ投入してdriftを拒否する。"""
    document = yaml.safe_load((PACK / "hazards" / "scenarios.yaml").read_text(encoding="utf-8"))
    parsed = [HazardScenario.from_mapping(scenario) for scenario in document["scenarios"]]
    assert {scenario.scenario_id for scenario in parsed} == SCENARIOS
    assert all(scenario.source_status == "SYNTHETIC_DEMO" for scenario in parsed)
    assert all(scenario.official_or_assumption == "ABLEPATH_DESIGN" for scenario in parsed)
    assert all(scenario.source_ids == ("kyoto_web_hazard_earthquake",) for scenario in parsed)


def test_edge_physics_is_dense_but_all_unavailable_values_remain_null():
    """[software_correctness] scenario×edge密行列を持ちM7入力不足を0やOPENへ変換しない。"""
    rows = read_csv(PACK / "hazards" / "edge_physics.csv")
    edges = {feature["properties"]["edge_id"] for feature in load_json("graph/walk_edges.geojson")["features"]}
    expected = Counter((scenario, edge) for scenario in SCENARIOS for edge in edges)
    actual = Counter((row["scenario_id"], row["edge_id"]) for row in rows)
    assert actual == expected
    assert all(count == 1 for count in actual.values())
    null_fields = {
        "debris_present", "base_clear_width_m", "debris_intrusion_left_m",
        "debris_intrusion_right_m", "remaining_clear_width_m", "official_closure",
    }
    for row in rows:
        assert row["data_status"] == "SYNTHETIC_DEMO"
        assert row["damage_state"] == "UNKNOWN"
        assert all(row[field] == "" for field in null_fields)
        assert row["hazard_data_status"] == "UNKNOWN"
        assert row["profile_status"] == "NOT_COMPUTED"
        assert row["reason"]
        assert all(row[key] for key in (
            "source_feature_id", "stable_feature_id", "revision_id", "lineage"
        ))
    assert len({row["stable_feature_id"] for row in rows}) == len(rows)
    assert len({row["source_feature_id"] for row in rows}) == len(rows)


def test_actual_edge_table_loads_through_shared_runtime_adapter():
    """[software_correctness] 実artifactのheader・監査列を共有UNKNOWN-only契約で検証する。"""
    records = load_edge_observation_table(PACK / "hazards" / "edge_physics.csv")
    assert len(records) == 6
    assert {record.dialect_id for record in records} == {"KIYOMIZU_EDGE_UNKNOWN_V1"}
    assert all(record.observation.hazard_data_status == "UNKNOWN" for record in records)
    assert all(record.observation.overlap is None for record in records)
    assert all(record.observation.official_closure is None for record in records)


def test_readiness_and_kpis_are_null_with_actionable_reasons():
    """[software_correctness] M6/profileとKPIを非計算として明示しnull+reasonを固定する。"""
    city = yaml.safe_load((PACK / "city.yaml").read_text(encoding="utf-8"))
    readiness = city["readiness"]
    assert readiness == {
        "facility_status": "UNKNOWN", "entrance_status": "UNKNOWN",
        "capacity_status": "UNKNOWN", "operation_status": "UNKNOWN",
        "demand_status": "UNKNOWN", "origin_status": "UNKNOWN",
        "profile_status": "NOT_COMPUTED", "kpi_status": "NOT_COMPUTED",
        "m6_status": "NOT_COMPUTED",
    }
    assert set(city["kpis"]) == {
        "physically_reachable", "accommodated", "overflow_waiting",
        "unreachable", "unknown_affected_upper_bound",
    }
    assert all(item["value"] is None and item["reason"] for item in city["kpis"].values())
    viewer = load_json("viewer/city_config.json")
    assert "profile_control" not in viewer
    assert viewer["profile_selector"]["enabled"] is False
    assert viewer["profile_selector"]["status"] == "NOT_COMPUTED"
    assert all(item["value"] is None and item["reason"] for item in viewer["kpis"].values())
    assert city["completion_levels"] == {
        "ENGINEERING_UI_COMPLETE": False,
        "DATA_STAGING_COMPLETE": True,
        "REAL_GEOMETRY_CONNECTED": False,
        "MODEL_CONNECTED": False,
        "ADMIN_VALIDATED": False,
        "overall": "PARTIAL_COMPLETE",
    }


def test_gap_register_covers_real_geometry_model_and_kpi_blockers():
    """[target_validation] REAL接続・model・KPIを妨げる不足と次actionを明示する。"""
    rows = read_csv(PACK / "sources" / "data_gap_register.csv")
    assert len(rows) == 10
    assert len({row["gap_id"] for row in rows}) == len(rows)
    assert all(row["status"] in {"OPEN", "REQUIRES_APPLICATION"} for row in rows)
    assert all(row["next_action"] and row["impact"] for row in rows)
    assert {row["category"] for row in rows} >= {
        "geometry", "earthquake", "facility", "capacity_operation",
        "demand_origin", "accessibility", "kpi",
    }


def test_corridor_metadata_admits_missing_real_geometry():
    """[source_conformance] 候補回廊metadataをREAL geometryとせずmissing stepを固定する。"""
    corridor = load_json("geography/corridor.metadata.json")
    assert GEO_KEYS <= corridor.keys()
    assert corridor["corridor_status"] == "OFFICIAL_METADATA_ONLY"
    assert corridor["geometry_status"] == "UNKNOWN"
    assert corridor["coordinate_precision"] is None
    assert corridor["road_register_data_used"] is False
    assert corridor["missing_real_data_step"]


def test_no_unsafe_claim_or_unlabelled_real_model_data():
    """[source_conformance] 安全保証・個別被害予測・未表示REAL/MODEL_DERIVEDを成果物に入れない。"""
    paths = [path for path in PACK.rglob("*") if path.is_file()] + [DOC]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    prohibited = ["安全な" + "避難ルート", "リアルタイム" + "安全保証", "個別建物" + "倒壊予測"]
    assert all(phrase not in combined for phrase in prohibited)
    assert "京都市道路台帳平面図由来" not in combined
    assert "MODEL_DERIVED" in combined and "REAL" in combined
    assert "SYNTHETIC_DEMO" in combined and "UNKNOWN" in combined
