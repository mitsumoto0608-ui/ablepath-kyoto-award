"""Delivery-sprint decision, spatial-analysis, and checklist contracts."""

from __future__ import annotations

import csv
import hashlib
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
    assert by_key[("touch", "flood-a")]["canonical_relation"] == "BOUNDARY_ONLY"
    assert by_key[("touch", "flood-a")]["overlap_length_m"] == 0
    assert by_key[("zero", "flood-a")]["relation"] == "ZERO_OVERLAP_WITHIN_KNOWN_COVERAGE"
    assert by_key[("zero", "flood-a")]["canonical_relation"] == "NO_INTERSECTION_WITHIN_VERIFIED_COVERAGE"
    assert by_key[("outside", "flood-a")]["relation"] == "OUTSIDE_COVERAGE"
    assert by_key[("outside", "flood-a")]["canonical_relation"] == "OUTSIDE_COVERAGE"
    assert by_key[("outside", "flood-a")]["overlap_length_m"] is None
    assert by_key[("partial", "flood-a")]["relation"] == "PARTIAL_COVERAGE"
    assert by_key[("partial", "flood-a")]["canonical_relation"] == "NODATA_OR_UNRESOLVED"
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
    terrain = {"status": "BLOCKED_VERTICAL_DATUM_UNRESOLVED", "sampled": False, "reason": "vertical datum unresolved", "edge_samples": {"e1": ["sample-a"], "e2": ["sample-b"]}}
    facility = {"status": "TABLE_ONLY", "record_count": 57, "reason": "entrance and operation UNKNOWN"}
    checklists = build_review_checklists("fujisawa_enoshima", matrix, exposures, terrain, facility)
    assert checklists["a__b"]["path_status"] == "CONNECTED"
    assert checklists["a__b"]["rows"][0]["hazard_refs"] == ["e1\0flood\0official"]
    assert checklists["a__b"]["rows"][1]["hazard_refs"] == []
    assert checklists["a__b"]["rows"][0]["terrain_sample_ids"] == ["sample-a"]
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


def test_delivery_binding_authority_and_public_scope_fail_closed() -> None:
    """[source_conformance] The 2026-09-10 owner amendment enables only reviewed public Git payloads."""
    authority = json.loads(Path("reports/DELIVERY_DECISION_BINDING_AUTHORITY.json").read_text(encoding="utf-8"))
    scope = json.loads(Path("reports/LICENSE_FINAL_SCOPE_DECISION.json").read_text(encoding="utf-8"))
    visibility = json.loads(Path("reports/DELIVERY_PUBLIC_SCOPE_RECONCILIATION.json").read_text(encoding="utf-8"))
    observation = json.loads(Path("reports/DELIVERY_PUBLIC_SCOPE_OBSERVATION.json").read_text(encoding="utf-8"))
    assert authority["current_authority"] == {
        "policy_binding": "reports/F1_F6_DECISION_BINDING.json",
        "scope_decision": "reports/LICENSE_FINAL_SCOPE_DECISION.json",
        "scope_amendment": "reports/PUBLIC_GIT_SCOPE_AMENDMENT_20260910.json",
        "role": "CURRENT_MACHINE_AUTHORITY",
    }
    assert authority["historical_record"]["role"] == "HISTORICAL_PRE_DECISION_RECORD"
    assert authority["historical_record"]["may_override_current_authority"] is False
    assert authority["license_research_reopened"] is False
    assert authority["f1_f6_reapproval_required"] is False
    assert authority["public_git"] is True
    assert all(authority[key] is False for key in ("public_rc", "public_demo"))
    assert authority["m7_ready_count"] == authority["m7_computed_count"] == 0
    assert authority["field_measurement_deferred"] is True
    assert scope["source_binding"] == authority["current_authority"]["policy_binding"]
    assert scope["public_git"] == "AUTHORIZED_REVIEWED_CODE_AND_REDISTRIBUTABLE_DERIVED_ARTIFACTS"
    assert all(scope[key] == "NOT_AUTHORIZED" for key in ("public_rc", "public_demo"))
    assert visibility["github_api_observation"] == {"private": False, "visibility": "PUBLIC", "release_count": 0}
    assert visibility["visibility_authorization_mismatch"] is False
    assert visibility["remote_write_gate"] == "AUTHORIZED_FOR_REVIEWED_CODE_AND_REDISTRIBUTABLE_DERIVED_ARTIFACTS"
    assert visibility["new_push_authorized"] is True
    assert all(visibility[key] is False for key in ("merge_authorized", "public_attachment_authorized", "visibility_change_authorized"))
    assert visibility["hosted_ci_artifact_authorized"] is True
    assert "NO_RAW" in visibility["hosted_ci_artifact_scope"]
    assert visibility["historical_private_operation_claimed"] is False
    assert visibility["observation_receipt"] == "reports/DELIVERY_PUBLIC_SCOPE_OBSERVATION.json"
    repository_bytes = json.dumps(observation["repository_query"]["selected_response"], separators=(",", ":"), ensure_ascii=False).encode()
    release_bytes = json.dumps(observation["release_query"]["selected_response"], separators=(",", ":"), ensure_ascii=False).encode()
    assert hashlib.sha256(repository_bytes).hexdigest() == observation["repository_query"]["selected_response_sha256"] == visibility["repository_selected_response_sha256"]
    assert hashlib.sha256(release_bytes).hexdigest() == observation["release_query"]["selected_response_sha256"] == visibility["release_selected_response_sha256"]
    assert observation["repository_query"]["selected_response"]["visibility"] == "PUBLIC"
    assert observation["release_query"]["selected_response"] == []
    assert observation["authentication_headers_recorded"] is observation["credential_material_recorded"] is False
    changed_response = {**observation["repository_query"]["selected_response"], "visibility": "PRIVATE"}
    assert hashlib.sha256(json.dumps(changed_response, separators=(",", ":")).encode()).hexdigest() != observation["repository_query"]["selected_response_sha256"]


def test_delivery_gaps_separate_existing_source_work_from_human_judgment() -> None:
    """[source_conformance] Existing-source reconciliation proceeds without guessing datum, CRS, or hazard taxonomy."""
    with Path("reports/DELIVERY_SPRINT_DATA_GAPS.csv").open(encoding="utf-8", newline="") as stream:
        rows = {row["gap_id"]: row for row in csv.DictReader(stream)}
    assert set(rows) == {f"DS-G{number:02d}" for number in range(1, 9)}
    for gap_id in ("DS-G01", "DS-G02", "DS-G03"):
        assert rows[gap_id]["resolution_track"] == "SOURCE_SPEC_RECONCILED"
        assert rows[gap_id]["status"] == "RESOLVED_NATIVE_CELL_CONNECTED"
        assert rows[gap_id]["can_progress_without_new_policy"] == "true"
    assert rows["DS-G04"]["resolution_track"] == "SOURCE_SPEC_RECONCILIATION"
    assert rows["DS-G04"]["status"] == "BLOCKED_SOURCE_CRS_UNRESOLVED"
    assert rows["DS-G05"]["resolution_track"] == "SOURCE_SPEC_RECONCILED"
    assert "threshold" in rows["DS-G05"]["human_or_field_gate"].lower()
    assert "authoritative CRS" in rows["DS-G04"]["human_or_field_gate"]
    assert "silent geocoding" in rows["DS-G07"]["existing_evidence_action"]
    assert rows["DS-G08"]["resolution_track"] == "HUMAN_OR_FIELD_EVIDENCE_REQUIRED"
    assert "zero" in rows["DS-G08"]["existing_evidence_action"]


def test_delivery_export_evidence_uses_existing_paths_and_keeps_m7_zero() -> None:
    """[ui_regression] Receipt examples name canonical path-matrix rows without promoting M7 or safety claims."""
    receipt = json.loads(Path("reports/DELIVERY_EXPORT_EVIDENCE.json").read_text(encoding="utf-8"))
    assert receipt["viewer_computation_added"] is False
    assert receipt["formats"] == ["CSV", "JSON", "PRINT_HTML"]
    assert receipt["m7_ready_count"] == receipt["m7_computed_count"] == 0
    assert all(receipt[key] is False for key in ("safe_route_claim", "accessibility_claim", "admin_validated"))
    for example in receipt["examples"]:
        artifact = json.loads(Path(f"viewer/public/data/analysis/{example['city_id']}.json").read_text(encoding="utf-8"))
        assert artifact["path_matrix"][example["connected_path_key"]]["status"] == "CONNECTED"
        assert artifact["path_matrix"][example["disconnected_path_key"]]["status"] == "DISCONNECTED"
        assert artifact["review_checklists"][example["disconnected_path_key"]]["rows"] == []
        assert artifact["m7"]["ready_edge_count"] == artifact["m7"]["computed_edge_count"] == 0
