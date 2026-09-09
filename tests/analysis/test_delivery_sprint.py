"""Delivery-sprint decision, spatial-analysis, and checklist contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analysis.delivery_sprint import (
    build_edge_hazard_exposure,
    build_review_checklists,
    select_intersecting_source_features,
    validate_f1_f6_binding,
)


def _line(edge_id: str, coordinates: list[list[float]]) -> dict:
    return {
        "type": "Feature",
        "properties": {"edge_id": edge_id, "from_node": "a", "to_node": "b"},
        "geometry": {"type": "LineString", "coordinates": coordinates},
    }


def _polygon(properties: dict, coordinates: list[list[float]]) -> dict:
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": {"type": "Polygon", "coordinates": [coordinates]},
    }


def test_approved_binding_keeps_unapproved_details_and_values_closed() -> None:
    """[source_conformance] Approved F1-F6 policy never implies values or detailed mappings."""
    binding = json.loads(Path("reports/F1_F6_DECISION_BINDING.json").read_text(encoding="utf-8"))
    assert validate_f1_f6_binding(binding) == binding
    for mutation in (
        {"source_zip_sha256": "0" * 64},
        {"value_available": True},
        {"m7_ready_count": 1},
        {"f2": {"concrete_taxonomy_mapping_approved": True}},
        {"f6": {**binding["f6"], "public_demo": True}},
    ):
        changed = json.loads(json.dumps(binding))
        changed.update(mutation)
        with pytest.raises(ValueError):
            validate_f1_f6_binding(changed)


def test_hazard_overlap_preserves_touch_zero_outside_and_scenario_separation() -> None:
    """[software_correctness] A 0.02-degree fixture is clipped exactly before EPSG:6674 length."""
    coverage = _polygon({}, [[135.0, 35.0], [135.1, 35.0], [135.1, 35.1], [135.0, 35.1], [135.0, 35.0]])
    layers = [
        {
            "source_id": "official-a",
            "source_revision": "2026-01-01",
            "source_sha256": "b" * 64,
            "source_url": "https://example.invalid/a",
            "license_status": "FIXTURE_ONLY",
            "limitations": "Synthetic fixture; no operational inference.",
            "scenario_id": "flood-a",
            "source_crs": "EPSG:6668",
            "coverage": coverage,
            "coverage_crs": "EPSG:4326",
            "coverage_evidence": {"status": "FULL_SOURCE_SCAN_INTERSECTED_WITH_BOUND_AOI", "selection_sha256": "f" * 64},
            "class_field": "class",
            "features": [
                _polygon({"class": "SOURCE_CLASS_1", "source_feature_id": "p1"}, [[135.02, 35.02], [135.04, 35.02], [135.04, 35.04], [135.02, 35.04], [135.02, 35.02]]),
                _polygon({"class": "SOURCE_CLASS_2", "source_feature_id": "p2"}, [[135.03, 35.02], [135.05, 35.02], [135.05, 35.04], [135.03, 35.04], [135.03, 35.02]]),
            ],
        },
        {
            "source_id": "official-b",
            "source_revision": "2026-01-02",
            "source_sha256": "c" * 64,
            "source_url": "https://example.invalid/b",
            "license_status": "FIXTURE_ONLY",
            "limitations": "Synthetic fixture; no operational inference.",
            "scenario_id": "flood-b",
            "source_crs": "EPSG:6668",
            "coverage": coverage,
            "coverage_crs": "EPSG:4326",
            "coverage_evidence": {"status": "FULL_SOURCE_SCAN_INTERSECTED_WITH_BOUND_AOI", "selection_sha256": "f" * 64},
            "class_field": "class",
            "features": [_polygon({"class": "OTHER", "source_feature_id": "p3"}, [[135.06, 35.02], [135.08, 35.02], [135.08, 35.04], [135.06, 35.04], [135.06, 35.02]])],
        },
    ]
    edges = [
        _line("cross", [[135.01, 35.03], [135.09, 35.03]]),
        _line("touch", [[135.01, 35.02], [135.02, 35.02]]),
        _line("zero", [[135.01, 35.08], [135.09, 35.08]]),
        _line("outside", [[135.2, 35.2], [135.3, 35.3]]),
        _line("partial", [[134.99, 35.03], [135.03, 35.03]]),
    ]
    rows = build_edge_hazard_exposure("kyoto_kiyomizu", edges, layers, "EPSG:6674")
    by_key = {(row["edge_id"], row["scenario_id"]): row for row in rows}
    assert by_key[("cross", "flood-a")]["relation"] == "INTERSECTS"
    assert by_key[("cross", "flood-a")]["overlap_length_m"] > 0
    assert by_key[("cross", "flood-a")]["source_classes"] == ["SOURCE_CLASS_1", "SOURCE_CLASS_2"]
    assert by_key[("cross", "flood-b")]["source_classes"] == ["OTHER"]
    assert by_key[("touch", "flood-a")]["relation"] == "TOUCHES"
    assert by_key[("touch", "flood-a")]["overlap_length_m"] == 0
    assert by_key[("zero", "flood-a")]["relation"] == "ZERO_OVERLAP_WITHIN_KNOWN_COVERAGE"
    assert by_key[("outside", "flood-a")]["relation"] == "OUTSIDE_COVERAGE"
    assert by_key[("outside", "flood-a")]["overlap_length_m"] is None
    assert by_key[("partial", "flood-a")]["relation"] == "PARTIAL_COVERAGE"
    assert by_key[("partial", "flood-a")]["overlap_length_m"] is None
    assert by_key[("cross", "flood-a")]["metric_crs"] == "EPSG:6674"
    for row in rows:
        assert row["official_closure"] is None
        assert row["damage_state"] is None
        assert row["debris_present"] is None


def test_hazard_contract_rejects_wrong_crs_and_unsafe_fields() -> None:
    """[source_conformance] Wrong CRS and hazard-derived operational state fail closed."""
    coverage = _polygon({}, [[135, 35], [136, 35], [136, 36], [135, 36], [135, 35]])
    base = {"source_id": "x", "source_revision": "v", "source_sha256": "d" * 64, "source_url": "https://example.invalid/source", "license_status": "FIXTURE_ONLY", "limitations": "Synthetic fixture.", "scenario_id": "s", "source_crs": "EPSG:6668", "coverage": coverage, "coverage_crs": "EPSG:4326", "coverage_evidence": {"status": "FULL_SOURCE_SCAN_INTERSECTED_WITH_BOUND_AOI", "selection_sha256": "f" * 64}, "class_field": "class", "features": []}
    with pytest.raises(ValueError):
        build_edge_hazard_exposure("kyoto_kiyomizu", [_line("e", [[135.1, 35.1], [135.2, 35.2]])], [{**base, "source_crs": "EPSG:4326"}], "EPSG:6674")
    with pytest.raises(ValueError):
        build_edge_hazard_exposure("kyoto_kiyomizu", [_line("e", [[135.1, 35.1], [135.2, 35.2]])], [{**base, "coverage_crs": "EPSG:6668"}], "EPSG:6674")
    unsafe = _polygon({"class": "x", "official_closure": True}, [[135.1, 35.1], [135.2, 35.1], [135.2, 35.2], [135.1, 35.2], [135.1, 35.1]])
    with pytest.raises(ValueError):
        build_edge_hazard_exposure("kyoto_kiyomizu", [_line("e", [[135.1, 35.1], [135.2, 35.2]])], [{**base, "features": [unsafe]}], "EPSG:6674")


def test_review_checklists_are_precomputed_for_each_path_fixture() -> None:
    """[ui_regression] Each static path fixture receives source-linked checks and explicit unknowns."""
    matrix = {
        "a__b": {"status": "CONNECTED", "edge_ids": ["e1", "e2"], "geometric_length": 1.0, "unit": "coordinate_degree", "reason": "candidate only"},
        "a__c": {"status": "DISCONNECTED", "edge_ids": [], "geometric_length": None, "unit": "coordinate_degree", "reason": "no candidate connection"},
    }
    exposures = [{"edge_id": "e1", "scenario_id": "flood", "relation": "INTERSECTS", "overlap_length_m": 12.5, "source_id": "official", "source_revision": "v1", "source_sha256": "e" * 64, "source_classes": ["raw-class"], "official_closure": None, "damage_state": None, "debris_present": None}]
    terrain = {"status": "BLOCKED_VERTICAL_DATUM_UNRESOLVED", "sampled": False, "reason": "vertical datum unresolved"}
    facility = {"status": "TABLE_ONLY", "record_count": 57, "reason": "entrance and operation UNKNOWN"}
    checklists = build_review_checklists("fujisawa_enoshima", matrix, exposures, terrain, facility)
    assert checklists["a__b"]["path_status"] == "CONNECTED"
    assert checklists["a__b"]["rows"][0]["hazard_refs"] == ["e1\0flood\0official"]
    assert checklists["a__b"]["rows"][1]["hazard_refs"] == []
    assert checklists["a__b"]["terrain"]["sampled"] is False
    assert checklists["a__c"]["status"] == "SUPPORTED_UNCOMPUTED"
    assert checklists["a__c"]["rows"] == []


def test_kyoto_facility_source_fields_preserve_listed_values_and_unknown_runtime_state() -> None:
    """[source_conformance] Original XLSX attributes stay distinct from current operation and access claims."""
    path = Path("inputs/staging/DELIVERY-SPRINT-V1/kyoto_facility_source_fields.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["binding_method"] == "OFFICIAL_NUMBER_OR_EXACT_SOURCE_COORDINATES"
    assert payload["silent_geocoding"] is False
    assert payload["current_operation_inferred"] is False
    assert len(payload["records"]) == 77
    by_source = {}
    for record in payload["records"]:
        by_source.setdefault(record["source_id"], []).append(record)
        assert len(record["source_sha256"]) == 64
        assert record["current_operation_status"] == "UNKNOWN"
        assert record["entrance_status"] == "UNKNOWN"
        assert record["unlock_status"] == "UNKNOWN"
        assert record["step_free_status"] == "UNKNOWN"
        assert record["disaster_availability_status"] == "UNKNOWN"
        assert record["accessibility_status"] == "UNKNOWN"
    assert any("listed_maximum_capacity" in row["source_attributes"] for row in by_source["kyoto_designated_shelters_r80818"])
    assert any("flood_evacuation_target_districts" in row["source_attributes"] for row in by_source["kyoto_emergency_shelters_r80818"])
    assert any("listed_opening_hours" in row["source_attributes"] for row in by_source["kyoto_public_toilets_00307"])


def test_source_selection_transforms_aoi_crs_before_intersection() -> None:
    """[software_correctness] EPSG:4326 AOI is explicitly transformed before EPSG:6674 source selection."""
    aoi = _polygon({}, [[135.77, 34.99], [135.78, 34.99], [135.78, 35.00], [135.77, 35.00], [135.77, 34.99]])
    from pyproj import Transformer
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:6674", always_xy=True, allow_ballpark=False)
    ring = [list(transformer.transform(x, y)) for x, y in aoi["geometry"]["coordinates"][0]]
    source = [_polygon({"id": "inside"}, ring)]
    assert select_intersecting_source_features(source, aoi, source_crs="EPSG:6674", coverage_crs="EPSG:4326") == source
    assert select_intersecting_source_features(source, aoi, source_crs="EPSG:6674", coverage_crs="EPSG:6674") == []
