"""Contract tests for the honest Kyoto Arashiyama city pack."""

from __future__ import annotations

import csv
from copy import deepcopy
import json
import math
from pathlib import Path

import pytest
import yaml

from src.citypacks.loader import load_citypack
from src.hazards import HazardScenario, load_edge_observation_table


ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "cities" / "kyoto_arashiyama"

REQUIRED = {
    "city.yaml",
    "sources/source_manifest.csv",
    "sources/data_gap_register.csv",
    "geography/corridor.geojson",
    "graph/walk_nodes.geojson",
    "graph/walk_edges.geojson",
    "facilities/facilities.csv",
    "pois/pois.csv",
    "hazards/scenarios.yaml",
    "hazards/edge_physics.csv",
    "demand/demand_scenarios.csv",
    "viewer/city_config.json",
    "README.md",
}
GEO_FIELDS = {
    "schema_version",
    "source_crs",
    "processing_crs",
    "output_crs",
    "horizontal_unit",
    "vertical_unit",
    "axis_order",
    "coordinate_precision",
    "transform_history",
    "geometry_status",
    "source_feature_id",
    "stable_feature_id",
    "revision_id",
    "lineage",
}
FRESHNESS = {
    "CURRENT_CONFIRMED",
    "CURRENT_UNVERIFIED",
    "POSSIBLY_STALE",
    "SUPERSEDED",
    "UNKNOWN",
}
DATA_CLASSES = {
    "REAL",
    "OFFICIAL_METADATA_ONLY",
    "VGI_METADATA_ONLY",
    "MODEL_DERIVED",
    "SYNTHETIC_DEMO",
    "UNKNOWN",
}
READINESS_KEYS = {
    "facility_status",
    "entrance_status",
    "capacity_status",
    "operation_status",
    "demand_status",
    "origin_status",
    "profile_status",
    "kpi_status",
    "m6_status",
}
KPI_KEYS = {
    "physically_reachable",
    "accommodated",
    "overflow_waiting",
    "unreachable",
    "unknown_affected_upper_bound",
}
COMPLETION_KEYS = {
    "ENGINEERING_UI_COMPLETE",
    "DATA_STAGING_COMPLETE",
    "REAL_GEOMETRY_CONNECTED",
    "MODEL_CONNECTED",
    "ADMIN_VALIDATED",
    "overall",
}


def _json(relative: str) -> dict:
    return json.loads((PACK / relative).read_text(encoding="utf-8"))


def _yaml(relative: str) -> dict:
    return yaml.safe_load((PACK / relative).read_text(encoding="utf-8"))


def _csv(relative: str) -> list[dict[str, str]]:
    with (PACK / relative).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_required_pack_layout_is_complete() -> None:
    """[software_correctness] The city pack exposes every required integration artifact."""
    assert {path for path in REQUIRED if (PACK / path).is_file()} == REQUIRED


def test_contract_versions_use_supported_major(tmp_path: Path) -> None:
    """[software_correctness] The shared loader accepts v1 and rejects major 2 with migration guidance."""
    city = _yaml("city.yaml")
    viewer = _json("viewer/city_config.json")
    hazards = _yaml("hazards/scenarios.yaml")
    assert city["schema_version"] == viewer["schema_version"] == hazards["schema_version"] == "1.0.0"
    assert city["citypack_schema_version"].split(".")[0] == "1"
    assert city["hazard_schema_version"].split(".")[0] == "1"
    assert city["viewer_data_schema_version"].split(".")[0] == "1"
    assert viewer["citypack_schema_version"] == city["citypack_schema_version"]
    assert viewer["hazard_schema_version"] == hazards["hazard_schema_version"]
    assert city["schema_compatibility"] == {
        "supported_major": 1,
        "unsupported_major_policy": "REJECT_WITH_ACTIONABLE_ERROR",
        "migration_policy": "RECORD_REQUIRED_MIGRATION_NO_IMPLICIT_CONVERSION",
    }
    assert load_citypack(PACK, trusted_root=ROOT / "cities")["city_id"] == "kyoto_arashiyama"
    rejected_pack = tmp_path / "unsupported-major"
    rejected_pack.mkdir()
    unsupported = deepcopy(city)
    unsupported["citypack_schema_version"] = "2.0.0"
    (rejected_pack / "city.yaml").write_text(
        yaml.safe_dump(unsupported, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ValueError) as caught:
        load_citypack(rejected_pack, trusted_root=tmp_path)
    message = str(caught.value)
    assert "unsupported citypack_schema_version schema major 2" in message
    assert "supported major 1" in message
    assert "migration" in message.lower()
    for contract in (city["geospatial_contract"], viewer["geospatial_contract"], hazards["geospatial_contract"]):
        assert GEO_FIELDS <= contract.keys()
        assert contract["processing_crs"] == "EPSG:6674"


def test_city_status_and_readiness_are_truthful() -> None:
    """[source_conformance] Missing real inputs remain SYNTHETIC_DEMO, UNKNOWN, or NOT_COMPUTED."""
    city = _yaml("city.yaml")
    assert city["data_status"] == "SYNTHETIC_DEMO"
    assert city["official_metadata_status"] == "OFFICIAL_METADATA_ONLY"
    assert city["center_data_class"] == "SYNTHETIC_DEMO"
    assert set(city["readiness"]) == READINESS_KEYS
    assert set(city["readiness"].values()) <= {"UNKNOWN", "NOT_COMPUTED"}
    assert city["readiness"]["m6_status"] == "NOT_COMPUTED"
    assert set(city["kpis"]) == KPI_KEYS
    assert all(kpi["value"] is None and kpi["reason"] for kpi in city["kpis"].values())
    completion = city["completion_levels"]
    assert set(completion) == COMPLETION_KEYS
    assert completion["DATA_STAGING_COMPLETE"] is True
    assert completion["overall"] == "PARTIAL_COMPLETE"
    assert all(completion[key] is False for key in ("ENGINEERING_UI_COMPLETE", "REAL_GEOMETRY_CONNECTED", "MODEL_CONNECTED", "ADMIN_VALIDATED"))


def test_source_manifest_preserves_freshness_and_metadata_only_boundary() -> None:
    """[source_conformance] Official metadata never masquerades as a downloaded geometry dataset."""
    rows = _csv("sources/source_manifest.csv")
    required = {
        "valid_as_of", "freshness_status", "supersedes_dataset_id",
        "superseded_by_dataset_id", "recheck_by", "retrieval_etag",
        "retrieval_last_modified", "redistribution_status",
    }
    assert rows and required <= rows[0].keys()
    v4_required = {"artifact_schema_version", "spec_reference", "license_or_terms", "local_path", "sha256"}
    assert v4_required <= rows[0].keys()
    assert {row["freshness_status"] for row in rows} <= FRESHNESS
    assert {row["data_class"] for row in rows} <= DATA_CLASSES
    assert all(row["download_status"] == "METADATA_ONLY" for row in rows)
    assert all(row["record_kind"].endswith("METADATA") for row in rows)
    osm = next(row for row in rows if row["dataset_id"] == "osm_arashiyama_candidate")
    assert osm["record_kind"] == "VGI_METADATA"
    assert osm["data_class"] == "VGI_METADATA_ONLY"
    assert all(
        row["data_class"] == "OFFICIAL_METADATA_ONLY"
        for row in rows
        if row["record_kind"] == "OFFICIAL_METADATA"
    )
    assert all(row["artifact_schema_version"] == "1.0.0" and row["spec_reference"] and row["license_or_terms"] for row in rows)
    assert all(row["local_path"] == row["sha256"] == "" for row in rows)
    assert {"kyoto_hazard_map_2026", "mlit_katsura_maximum", "kyoto_saga_arashiyama_plan"} <= {row["dataset_id"] for row in rows}


def test_source_urls_are_allowlisted_and_have_recheck_dates() -> None:
    """[source_conformance] Every external metadata row is reviewable and scheduled for freshness recheck."""
    allowed = ("city.kyoto.lg.jp", "bousai.city.kyoto.lg.jp", "kkr.mlit.go.jp", "geospatial.jp", "openstreetmap.org", "gsi.go.jp")
    for row in _csv("sources/source_manifest.csv"):
        assert row["source_url"].startswith("https://")
        assert any(host in row["source_url"] for host in allowed)
        assert row["accessed_at"] == "2026-08-30"
        assert row["recheck_by"]


def test_geospatial_artifacts_carry_v4_lineage_contract() -> None:
    """[software_correctness] Corridor, node, edge, and QA artifacts declare CRS, units, revision, and lineage."""
    for relative in ("geography/corridor.geojson", "graph/walk_nodes.geojson", "graph/walk_edges.geojson", "graph/topology_qa.json"):
        artifact = _json(relative)
        assert GEO_FIELDS <= artifact.keys()
        assert artifact["processing_crs"] == "EPSG:6674"
        assert artifact["output_crs"] == "EPSG:4326"
        assert artifact["axis_order"] == "lon_lat"
        assert artifact["vertical_unit"] == "UNKNOWN"


def test_fixture_geometry_is_finite_and_row_level_synthetic() -> None:
    """[software_correctness] Every demo coordinate is finite and every feature discloses synthetic provenance."""
    for relative in ("geography/corridor.geojson", "graph/walk_nodes.geojson", "graph/walk_edges.geojson"):
        for feature in _json(relative)["features"]:
            props = feature["properties"]
            assert props["data_class"] == "SYNTHETIC_DEMO"
            assert props["geometry_status"] == "SYNTHETIC_DEMO_CANDIDATE"
            assert props["source_feature_id"] and props["stable_feature_id"] and props["lineage"]
            coordinates = feature["geometry"]["coordinates"]
            flat = coordinates if feature["geometry"]["type"] == "Point" else [v for pair in coordinates for v in pair]
            assert all(math.isfinite(float(value)) for value in flat)


def test_candidate_graph_references_are_dense_and_deterministic() -> None:
    """[software_correctness] Stable ordered edges reference known nodes without topology promotion."""
    nodes = _json("graph/walk_nodes.geojson")["features"]
    edges = _json("graph/walk_edges.geojson")["features"]
    node_ids = [feature["properties"]["node_id"] for feature in nodes]
    edge_ids = [feature["properties"]["edge_id"] for feature in edges]
    assert node_ids == sorted(node_ids) and edge_ids == sorted(edge_ids)
    assert len(node_ids) == len(set(node_ids)) == 6
    assert len(edge_ids) == len(set(edge_ids)) == 5
    node_coordinates = {feature["properties"]["node_id"]: feature["geometry"]["coordinates"] for feature in nodes}
    for feature in edges:
        props = feature["properties"]
        assert {props["from_node"], props["to_node"]} <= set(node_ids)
        assert props["topology_status"] == "CANDIDATE"
        assert props["accessibility_state"] == "UNKNOWN"
        assert {props["bridge"], props["tunnel"], props["level"], props["layer"]} == {"UNKNOWN"}
        assert feature["geometry"]["coordinates"][0] == node_coordinates[props["from_node"]]
        assert feature["geometry"]["coordinates"][-1] == node_coordinates[props["to_node"]]
        assert feature["geometry"]["coordinates"][0] != feature["geometry"]["coordinates"][-1]


def test_topology_qa_reports_unresolved_real_world_checks() -> None:
    """[software_correctness] QA reports fixture counts while refusing to claim real destination or bridge validity."""
    qa = _json("graph/topology_qa.json")
    nodes = _json("graph/walk_nodes.geojson")["features"]
    edges = _json("graph/walk_edges.geojson")["features"]
    node_ids = [feature["properties"]["node_id"] for feature in nodes]
    edge_ids = [feature["properties"]["edge_id"] for feature in edges]
    degrees = {node_id: 0 for node_id in node_ids}
    for feature in edges:
        degrees[feature["properties"]["from_node"]] += 1
        degrees[feature["properties"]["to_node"]] += 1
    computed = {
        "duplicate_node_ids": len(node_ids) - len(set(node_ids)),
        "duplicate_edge_ids": len(edge_ids) - len(set(edge_ids)),
        "dangling_endpoint_nodes": sum(value == 1 for value in degrees.values()),
        "self_loops": sum(feature["properties"]["from_node"] == feature["properties"]["to_node"] for feature in edges),
        "zero_length_edges": sum(feature["geometry"]["coordinates"][0] == feature["geometry"]["coordinates"][-1] for feature in edges),
    }
    assert qa["graph_status"] == "CANDIDATE"
    assert qa["counts"] == computed == {"duplicate_node_ids": 0, "duplicate_edge_ids": 0, "dangling_endpoint_nodes": 2, "self_loops": 0, "zero_length_edges": 0}
    assert set(qa["not_computed"]) == {"disconnected_real_destinations", "unsplit_hazard_boundaries", "grade_separated_false_intersections"}
    assert all(
        set(item) == {"status", "reason"}
        and item["status"] == "NOT_COMPUTED"
        and isinstance(item["reason"], str)
        and item["reason"].strip()
        for item in qa["not_computed"].values()
    )


def test_scenarios_are_bounded_and_worst_case_is_not_invented() -> None:
    """[source_conformance] Only approved comparison labels ship; official maximum-scale wording is not relabelled worst case."""
    hazards = _yaml("hazards/scenarios.yaml")
    scenarios = hazards["scenarios"]
    assert [row["scenario_id"] for row in scenarios] == ["RAIN_NORMAL", "RAIN_HEAVY", "FLOOD_DESIGN"]
    assert all(row["source_status"] == "SYNTHETIC_DEMO" for row in scenarios)
    assert all(row["official_or_assumption"] == "ABLEPATH_DESIGN" for row in scenarios)
    assert all(row["elapsed_time_sec"] is None and row["coverage_complete"] is False for row in scenarios)
    assert all(row["default_edge_state"] == "UNKNOWN" for row in scenarios)
    assert all(row["disclaimer"] == hazards["scenario_disclaimer"] for row in scenarios)
    assert scenarios[0]["source_ids"] == []
    assert scenarios[1]["source_ids"] == ["kyoto_hazard_map_2026"]
    assert scenarios[2]["source_ids"] == ["mlit_katsura_multistage", "kyoto_hazard_map_2026"]
    assert "FLOOD_WORST_CASE" in hazards["omitted_scenarios"]


def test_all_scenario_artifacts_satisfy_shared_hazard_contract() -> None:
    """[software_correctness] Every shipped scenario uses the shared exact nine-field immutable contract."""
    scenarios = _yaml("hazards/scenarios.yaml")["scenarios"]
    parsed = [HazardScenario.from_mapping(row) for row in scenarios]
    assert [scenario.scenario_id for scenario in parsed] == ["RAIN_NORMAL", "RAIN_HEAVY", "FLOOD_DESIGN"]


def test_edge_physics_never_derives_closure_from_overlap() -> None:
    """[software_correctness] Every scenario-edge row preserves unknown exposure and operation instead of opening or closing it."""
    rows = _csv("hazards/edge_physics.csv")
    edges = {f["properties"]["edge_id"] for f in _json("graph/walk_edges.geojson")["features"]}
    scenarios = {row["scenario_id"] for row in _yaml("hazards/scenarios.yaml")["scenarios"]}
    assert len(rows) == len(edges) * len(scenarios) == 15
    assert {(row["scenario_id"], row["edge_id"]) for row in rows} == {(s, e) for s in scenarios for e in edges}
    assert len({(row["scenario_id"], row["edge_id"]) for row in rows}) == len(rows)
    assert len({row["stable_feature_id"] for row in rows}) == len(rows)
    assert all(row["source_feature_id"] and row["revision_id"] and row["lineage"] for row in rows)
    assert all(row["hazard_overlap_status"] == "NOT_COMPUTED" and row["inundation_depth_m"] == "" for row in rows)
    assert all(row["official_closure"] == row["operational_rule_status"] == row["scenario_state"] == "UNKNOWN" for row in rows)


def test_actual_edge_table_loads_through_shared_runtime_adapter() -> None:
    """[software_correctness] Shipped CSV uses the exact reviewed UNKNOWN-only shared adapter."""
    records = load_edge_observation_table(PACK / "hazards" / "edge_physics.csv")
    assert len(records) == 15
    assert {record.dialect_id for record in records} == {"ARASHIYAMA_EDGE_UNKNOWN_V1"}
    assert all(record.observation.hazard_data_status == "UNKNOWN" for record in records)
    assert all(record.observation.overlap is None for record in records)
    assert all(record.observation.official_closure is None for record in records)


def test_no_facility_capacity_entrance_or_demand_is_invented() -> None:
    """[source_conformance] Header-only tables preserve missing facility, capacity, entrance, origin, and demand facts."""
    assert _csv("facilities/facilities.csv") == []
    assert _csv("demand/demand_scenarios.csv") == []


def test_viewer_disables_noncomputed_profiles_and_returns_null_kpis() -> None:
    """[ui_regression] The UI contract cannot present inactive M6/profile controls or fabricated KPI values."""
    viewer = _json("viewer/city_config.json")
    assert viewer["profile_selector"]["enabled"] is False
    assert viewer["profile_selector"]["status"] == "NOT_COMPUTED"
    assert viewer["evidence_policy_selector"]["enabled"] is False
    assert set(viewer["readiness"]) == READINESS_KEYS
    assert viewer["readiness"]["profile_status"] == viewer["readiness"]["kpi_status"] == "NOT_COMPUTED"
    assert viewer["readiness"]["m6_status"] == "NOT_COMPUTED"
    assert set(viewer["kpis"]) == KPI_KEYS
    for kpi in viewer["kpis"].values():
        assert kpi["value"] is None and kpi["reason"]


def test_viewer_exposes_source_attribution_and_static_disclaimer() -> None:
    """[ui_regression] Evidence IDs and non-live limitations remain visible to the shared viewer."""
    viewer = _json("viewer/city_config.json")
    source_ids = {row["dataset_id"] for row in _csv("sources/source_manifest.csv")}
    assert viewer["attribution"]
    assert {row["dataset_id"] for row in viewer["attribution"]} <= source_ids
    assert all(row["status"] in {"OFFICIAL_METADATA_ONLY", "VGI_METADATA_ONLY"} for row in viewer["attribution"])
    assert {layer["id"] for layer in viewer["layers"]} == {"synthetic_walk_graph", "official_flood_metadata", "official_landslide_metadata"}
    assert "ライブ" in viewer["scenario_disclaimer"] and "閉鎖を推定しません" in viewer["scenario_disclaimer"]


def test_gap_register_keeps_operational_and_model_blockers_open() -> None:
    """[source_conformance] Closure rules, facility operation, and M6 remain explicit unresolved blockers."""
    rows = _csv("sources/data_gap_register.csv")
    by_id = {row["gap_id"]: row for row in rows}
    assert by_id["ARA-GAP-003"]["status"] == "OPEN"
    assert by_id["ARA-GAP-008"]["severity"] == "BLOCKER"
    assert by_id["ARA-GAP-010"]["category"] == "profile"


def test_pack_contains_no_unsafe_or_overclaim_wording() -> None:
    """[source_conformance] Public city artifacts avoid real-time, administrative-validation, and automatic-closure claims."""
    text = "\n".join(path.read_text(encoding="utf-8") for path in PACK.rglob("*") if path.is_file())
    forbidden = (
        "行政" + "検証済みです",
        "リアルタイム" + "避難",
        "洪水域なので" + "CLOSED",
        "UNKNOWN" + "をOPEN",
        "道路台帳由来" + "座標",
    )
    assert not any(term in text for term in forbidden)
