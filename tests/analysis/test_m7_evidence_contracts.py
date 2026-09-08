"""Fail-closed contract tests for the M7 V2 evidence validators.

Every fixture under ``fixtures/m7_evidence/`` is synthetic and labelled
NON_REAL; no real building, edge, or measurement is asserted here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from src.analysis.m7_evidence_contracts import (
    PROJECTED_CRS_ALLOWLIST,
    ValidationResult,
    load_schema,
    m7_eligibility,
    validate_damage_state_evidence,
    validate_debris_presence_evidence,
    validate_height_evidence,
    validate_scenario_realization,
    validate_setback_evidence,
    validate_side_coverage,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "m7_evidence"
READINESS_JSON = ROOT / "reports" / "M7_ALL_EDGE_EVIDENCE_READINESS.json"
DOC_VALIDATORS = {
    "M7_SETBACK_INPUT_CONTRACT_V2.md": validate_setback_evidence,
    "M7_DAMAGE_STATE_INPUT_CONTRACT_V2.md": validate_damage_state_evidence,
    "M7_DEBRIS_PRESENCE_INPUT_CONTRACT_V2.md": validate_debris_presence_evidence,
}
JSON_BLOCK = re.compile(r"```json\n(.*?)\n```", re.DOTALL)


def fixture(name: str) -> dict:
    """Load one synthetic NON_REAL evidence fixture."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def codes(result: ValidationResult) -> set[str]:
    """Reduce reported errors to their bare, greppable error codes."""
    return {error.split(":")[0] for error in result.errors}


# --------------------------------------------------------------------------
# happy paths
# --------------------------------------------------------------------------


def test_observed_setback_evidence_validates_and_is_eligible():
    """[software_correctness] An accepted observed setback record is eligible."""
    result = validate_setback_evidence(fixture("setback_observed_eligible.NON_REAL.json"))
    assert result.ok, result.errors
    assert result.eligibility["eligible"] is True


def test_official_boundary_derived_setback_validates_but_is_not_eligible():
    """[software_correctness] A pending official-derived record stays ineligible."""
    record = fixture("setback_official_pending.NON_REAL.json")
    result = validate_setback_evidence(record)
    assert result.ok, result.errors
    assert result.eligibility == {
        "eligible": False,
        "reason": "E_SETBACK_EVIDENCE_NOT_ACCEPTED",
    }
    assert m7_eligibility("setback", record) == result.eligibility


def test_observed_damage_state_maps_explicitly_when_accepted():
    """[software_correctness] Observed post-event state maps only via an explicit receipt."""
    result = validate_damage_state_evidence(
        fixture("damage_observed_accepted.NON_REAL.json"))
    assert result.ok, result.errors
    assert result.eligibility["eligible"] is True


def test_probability_distribution_remains_non_categorical():
    """[software_correctness] A damage distribution never becomes a core state."""
    record = fixture("damage_distribution.NON_REAL.json")
    result = validate_damage_state_evidence(record)
    assert result.ok, result.errors
    assert record["mapping_to_m7_core"] is None
    assert result.eligibility == {
        "eligible": False,
        "reason": "E_DAMAGE_DISTRIBUTION_NEVER_ELIGIBLE",
    }


def test_observed_debris_bool_maps_explicitly():
    """[software_correctness] An accepted observed debris boolean maps to the core."""
    result = validate_debris_presence_evidence(
        fixture("debris_observed_accepted.NON_REAL.json"))
    assert result.ok, result.errors
    assert result.eligibility["eligible"] is True


def test_conditional_probability_debris_is_never_eligible():
    """[software_correctness] A conditional probability is a record, never a boolean."""
    result = validate_debris_presence_evidence(
        fixture("debris_conditional_probability.NON_REAL.json"))
    assert result.ok, result.errors
    assert result.eligibility == {
        "eligible": False,
        "reason": "E_DEBRIS_PROBABILITY_NEVER_ELIGIBLE",
    }


def test_exposure_only_join_does_not_affect_damage_or_debris():
    """[software_correctness] Hazard exposure stays exposure and maps to nothing."""
    record = fixture("damage_exposure_only.NON_REAL.json")
    result = validate_damage_state_evidence(record)
    assert result.ok, result.errors
    assert record["mapping_to_m7_core"] is None
    assert record["mapping_status"] == "MAPPING_FORBIDDEN_EXPOSURE_ONLY"
    assert result.eligibility["eligible"] is False


def test_scenario_realization_validates_and_is_never_production_eligible():
    """[software_correctness] A scenario realization is experimental by construction."""
    result = validate_scenario_realization(
        fixture("scenario_realization.NON_REAL.json"))
    assert result.ok, result.errors
    assert result.eligibility == {
        "eligible": False,
        "reason": "E_SCENARIO_NEVER_PRODUCTION_ELIGIBLE",
    }


def test_edge_counts_remain_derived_from_the_receipt():
    """[source_conformance] Tracked edge counts are derived, never literals."""
    receipt = json.loads(READINESS_JSON.read_text(encoding="utf-8"))
    edges = receipt["edges"]
    assert receipt["all_edge_count"] == len(edges)
    assert receipt["deep_pilot_count"] == sum(
        1 for edge in edges if edge["deep_pilot"])


def test_worked_examples_in_contract_docs_validate():
    """[source_conformance] Every embedded worked example matches its validator."""
    seen_proxy = False
    for filename, validator in DOC_VALIDATORS.items():
        text = (ROOT / "docs" / "review" / filename).read_text(encoding="utf-8")
        blocks = JSON_BLOCK.findall(text)
        assert blocks, filename
        for block in blocks:
            record = json.loads(block)
            result = validator(record)
            assert result.ok, (filename, result.errors)
            if record.get("setback_status") == "PROXY_NOT_SETBACK":
                seen_proxy = True
                assert result.eligibility == {
                    "eligible": False,
                    "reason": "E_SETBACK_PROXY_NEVER_ELIGIBLE",
                }
    assert seen_proxy


def test_load_schema_exposes_the_frozen_contract_ids():
    """[source_conformance] Schemas load by short name and keep their contract ids."""
    assert load_schema("setback")["x-ablepath"]["contract_id"] == (
        "M7_SETBACK_INPUT_CONTRACT_V2")
    assert load_schema("scenario_realization")["properties"][
        "production_eligible"]["const"] is False


# --------------------------------------------------------------------------
# fatal mutations
# --------------------------------------------------------------------------


def test_proxy_record_claimed_eligible_is_rejected():
    """[software_correctness] A proxy record can never be accepted."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["setback_status"] = "PROXY_NOT_SETBACK"
    result = validate_setback_evidence(record)
    assert "E_PROXY_NOT_SETBACK_PROMOTED" in codes(result)
    assert result.eligibility["eligible"] is False


def test_centerline_renamed_as_setback_is_rejected():
    """[software_correctness] A centerline proxy renamed as setback is rejected."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["boundary_role"] = "CANDIDATE_CENTERLINE_PROXY"
    result = validate_setback_evidence(record)
    assert "E_CENTERLINE_PROXY_AS_SETBACK" in codes(result)


def test_centroid_geometry_role_and_method_are_rejected():
    """[software_correctness] Centroid distance is never a setback."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["building_geometry_role"] = "CENTROID_FORBIDDEN"
    record["measurement_or_derivation_method"] = "Building CENTROID to boundary"
    result = validate_setback_evidence(record)
    assert {"E_CENTROID_FORBIDDEN_ROLE", "E_CENTROID_METHOD"} <= codes(result)


def test_missing_sha_is_rejected():
    """[software_correctness] An eligible-claiming record without a SHA is rejected."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["boundary_sha256"] = None
    assert "E_SHA256_MISSING" in codes(validate_setback_evidence(record))


def test_malformed_sha_is_rejected():
    """[software_correctness] A SHA that is not 64 hex characters is rejected."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["building_sha256"] = "deadbeef"
    assert "E_SHA256_MALFORMED" in codes(validate_setback_evidence(record))


def test_unknown_boundary_role_is_never_silently_promoted():
    """[software_correctness] UNKNOWN boundary role never becomes eligible."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["boundary_role"] = "UNKNOWN"
    result = validate_setback_evidence(record)
    assert "E_BOUNDARY_ROLE_UNKNOWN_PROMOTED" in codes(result)
    assert result.eligibility["eligible"] is False


def test_station_order_is_enforced():
    """[software_correctness] Station intervals must not run backwards."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["station_start_m"], record["station_end_m"] = 20.0, 12.0
    assert "E_STATION_ORDER_INVALID" in codes(validate_setback_evidence(record))


@pytest.mark.parametrize("crs", ["EPSG:4326", "EPSG:4612", "EPSG:6668", "EPSG:6697"])
def test_geographic_crs_is_rejected(crs):
    """[software_correctness] A geographic CRS can never carry a metric distance."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["metric_crs"] = crs
    assert "E_CRS_GEOGRAPHIC" in codes(validate_setback_evidence(record))


def test_non_allowlisted_projected_crs_is_not_eligible():
    """[software_correctness] Only allowlisted projected CRS codes are eligible."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["metric_crs"] = "EPSG:6675"
    assert record["metric_crs"] not in PROJECTED_CRS_ALLOWLIST
    result = validate_setback_evidence(record)
    assert result.ok, result.errors
    assert result.eligibility == {
        "eligible": False, "reason": "E_CRS_NOT_ALLOWLISTED"}


@pytest.mark.parametrize(
    "bad_value", [True, float("nan"), float("inf"), float("-inf"), 10**1000]
)
def test_setback_value_rejects_bool_and_non_finite_numbers(bad_value):
    """[software_correctness] M7 numeric evidence must be finite and not boolean."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["setback_value_m"] = bad_value
    result = validate_setback_evidence(record)
    assert result.ok is False
    assert result.eligibility["eligible"] is False
    assert "E_SETBACK_VALUE_INVALID" in codes(result)


def test_official_road_boundary_proxy_is_not_eligible_without_offset_contract():
    """[source_conformance] An unbound road-boundary proxy never becomes setback."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["boundary_role"] = "OFFICIAL_ROAD_BOUNDARY_PROXY"
    result = validate_setback_evidence(record)
    assert result.ok, result.errors
    assert result.eligibility == {
        "eligible": False,
        "reason": "E_ROAD_BOUNDARY_OFFSET_CONTRACT_NOT_FROZEN",
    }


@pytest.mark.parametrize(
    "bad_value", [True, float("nan"), float("inf"), "0.5", 10**1000]
)
def test_damage_probability_rejects_malformed_numeric_values(bad_value):
    """[software_correctness] Invalid probabilities fail closed without exceptions."""
    record = fixture("damage_distribution.NON_REAL.json")
    record["damage_state_probabilities"]["NO_DAMAGE"] = bad_value
    result = validate_damage_state_evidence(record)
    assert result.ok is False
    assert result.eligibility["eligible"] is False
    assert "E_PROBABILITY_VALUE_INVALID" in codes(result)


def test_malformed_crs_is_rejected():
    """[software_correctness] A CRS must be written as EPSG:<code>."""
    record = fixture("setback_observed_eligible.NON_REAL.json")
    record["metric_crs"] = "JGD2011 / Zone VII"
    assert "E_CRS_MALFORMED" in codes(validate_setback_evidence(record))


def test_hazard_overlap_cannot_create_damage():
    """[software_correctness] Hazard-zone overlap never becomes a damage state."""
    record = fixture("damage_exposure_only.NON_REAL.json")
    record["intensity_measure_type"] = "LANDSLIDE_ZONE_OVERLAP"
    record["mapping_to_m7_core"] = "DAMAGED"
    record["mapping_status"] = "MAPPED_EXPLICIT"
    assert "E_EXPOSURE_MAPPED_TO_DAMAGE" in codes(
        validate_damage_state_evidence(record))


def test_distribution_cannot_be_mapped_to_a_core_state():
    """[software_correctness] A distribution mapped to a core enum is rejected."""
    record = fixture("damage_distribution.NON_REAL.json")
    record["intensity_measure_type"] = "NOT_APPLICABLE"
    record["mapping_to_m7_core"] = "DAMAGED"
    record["mapping_status"] = "MAPPED_EXPLICIT"
    assert "E_DISTRIBUTION_MAPPED_TO_CATEGORICAL" in codes(
        validate_damage_state_evidence(record))


def test_probabilities_must_sum_to_one():
    """[software_correctness] A distribution that does not sum to 1 is rejected."""
    record = fixture("damage_distribution.NON_REAL.json")
    record["damage_state_probabilities"]["NO_DAMAGE"] = 0.9
    assert "E_PROBABILITIES_NOT_NORMALISED" in codes(
        validate_damage_state_evidence(record))


def test_probability_keys_must_belong_to_the_declared_taxonomy():
    """[source_conformance] Distribution keys must exist in the declared taxonomy."""
    record = fixture("damage_distribution.NON_REAL.json")
    probabilities = record["damage_state_probabilities"]
    probabilities["INVENTED_STATE"] = probabilities.pop("NO_DAMAGE")
    assert "E_PROBABILITY_KEY_NOT_IN_TAXONOMY" in codes(
        validate_damage_state_evidence(record))


def test_unknown_damage_is_never_coerced_to_damaged():
    """[software_correctness] UNKNOWN damage never falls back to DAMAGED."""
    record = fixture("damage_exposure_only.NON_REAL.json")
    record["intensity_measure_type"] = "NOT_APPLICABLE"
    record["intensity_measure_value"] = None
    record["mapping_to_m7_core"] = "DAMAGED"
    record["mapping_status"] = "MAPPED_EXPLICIT"
    assert "E_UNKNOWN_COERCED_TO_DAMAGED" in codes(
        validate_damage_state_evidence(record))


def test_taxonomy_version_is_required_for_any_mapping():
    """[software_correctness] A mapping without a taxonomy version is rejected."""
    record = fixture("damage_observed_accepted.NON_REAL.json")
    record["damage_taxonomy_version"] = None
    assert "E_TAXONOMY_VERSION_MISSING" in codes(
        validate_damage_state_evidence(record))


def test_experimental_damage_realization_requires_a_seed():
    """[software_correctness] An unseeded realization is never promoted."""
    record = fixture("damage_observed_accepted.NON_REAL.json")
    record["evidence_kind"] = "MODEL_REALIZATION_EXPERIMENTAL"
    record["scenario_id"] = "NON-REAL-SCENARIO-001"
    record["validation_status"] = "PENDING_HUMAN_FREEZE"
    record["realization_id"] = "NON-REAL-REALIZATION-0001"
    record["realization_method"] = "inverse-cdf draw"
    record["realization_seed"] = None
    result = validate_damage_state_evidence(record)
    assert "E_REALIZATION_SEED_MISSING" in codes(result)


def test_experimental_damage_realization_is_never_production_eligible():
    """[software_correctness] A seeded realization is still not production input."""
    record = fixture("damage_observed_accepted.NON_REAL.json")
    record["evidence_kind"] = "MODEL_REALIZATION_EXPERIMENTAL"
    record["scenario_id"] = "NON-REAL-SCENARIO-001"
    record["validation_status"] = "PENDING_HUMAN_FREEZE"
    record["realization_id"] = "NON-REAL-REALIZATION-0001"
    record["realization_method"] = "inverse-cdf draw"
    record["realization_seed"] = 20260903
    result = validate_damage_state_evidence(record)
    assert result.ok, result.errors
    assert result.eligibility == {
        "eligible": False, "reason": "E_DAMAGE_EXPERIMENTAL_NOT_PRODUCTION"}


def test_probability_over_threshold_cannot_create_a_debris_bool():
    """[software_correctness] A probability is never thresholded into a boolean."""
    record = fixture("debris_conditional_probability.NON_REAL.json")
    record["mapping_to_m7_core"] = True
    result = validate_debris_presence_evidence(record)
    assert "E_PROBABILITY_THRESHOLD_TO_BOOL" in codes(result)


def test_unknown_debris_is_never_coerced_to_false():
    """[software_correctness] UNKNOWN debris never falls back to false."""
    record = fixture("debris_conditional_probability.NON_REAL.json")
    record["debris_evidence_kind"] = "UNKNOWN"
    record["probability_of_presence"] = None
    record["mapping_to_m7_core"] = False
    assert "E_UNKNOWN_COERCED_TO_FALSE" in codes(
        validate_debris_presence_evidence(record))


def test_debris_extent_cannot_set_presence():
    """[software_correctness] Debris extent never decides the presence boolean."""
    record = fixture("debris_conditional_probability.NON_REAL.json")
    record["debris_evidence_kind"] = "OFFICIAL_ASSET_LEVEL_SCENARIO"
    record["probability_of_presence"] = None
    record["probability_model_id"] = None
    record["probability_model_version"] = None
    record["mapping_to_m7_core"] = True
    assert "E_EXTENT_USED_AS_PRESENCE" in codes(
        validate_debris_presence_evidence(record))


def test_experimental_debris_realization_requires_seed_and_model():
    """[software_correctness] A stochastic debris realization must be reproducible."""
    record = fixture("debris_conditional_probability.NON_REAL.json")
    record["debris_evidence_kind"] = "EXPERIMENTAL_STOCHASTIC_REALIZATION"
    record["probability_model_id"] = None
    record["probability_model_version"] = None
    result = validate_debris_presence_evidence(record)
    assert {"E_DEBRIS_REALIZATION_SEED_MISSING",
            "E_DEBRIS_REALIZATION_ID_MISSING",
            "E_DEBRIS_PROBABILITY_MODEL_MISSING"} <= codes(result)


def test_scenario_realization_rejects_production_eligible_true():
    """[software_correctness] production_eligible=true is refused at this version."""
    record = fixture("scenario_realization.NON_REAL.json")
    record["production_eligible"] = True
    record["experimental_only"] = False
    result = validate_scenario_realization(record)
    assert {"E_SCENARIO_PRODUCTION_ELIGIBLE_TRUE",
            "E_SCENARIO_EXPERIMENTAL_ONLY_FALSE"} <= codes(result)


def test_scenario_realization_rejects_omitted_seed_and_generator():
    """[software_correctness] An unseeded, generator-less realization is rejected."""
    record = fixture("scenario_realization.NON_REAL.json")
    record["seed"] = None
    record["random_generator"] = ""
    result = validate_scenario_realization(record)
    assert {"E_SEED_MISSING", "E_RANDOM_GENERATOR_MISSING"} <= codes(result)


HEIGHT_SENTINEL = {
    "official_height_m": -9999,
    "height_status": "INVALID_SENTINEL",
    "height_provenance_lod1HeightType": "2",
}
HEIGHT_UNIFORM = {
    "official_height_m": 3.0,
    "height_status": "OFFICIAL_ATTRIBUTE_PRESENT",
    "height_provenance_lod1HeightType": "0",
}
HEIGHT_STOREY = {
    "official_height_m": 6.0,
    "height_status": "OFFICIAL_ATTRIBUTE_PRESENT",
    "height_provenance_lod1HeightType": "9",
}


@pytest.mark.parametrize("record,code", [
    (HEIGHT_SENTINEL, "E_HEIGHT_INVALID_SENTINEL"),
    (HEIGHT_UNIFORM, "E_HEIGHT_UNIFORM_VALUE_NOT_EVIDENCE"),
    (HEIGHT_STOREY, "E_HEIGHT_STOREY_ESTIMATE_NOT_ELIGIBLE"),
])
def test_height_sentinel_uniform_and_storey_estimates_are_rejected(record, code):
    """[source_conformance] Sentinel, uniform, and storey heights are not evidence."""
    result = validate_height_evidence(dict(record))
    assert code in codes(result)
    assert result.eligibility["eligible"] is False


@pytest.mark.parametrize("code,flag", [
    ("2", "POINT_CLOUD_MEDIAN"),
    ("6", "AERIAL_PHOTOGRAMMETRY_MAX"),
])
def test_height_candidate_classes_need_distinct_method_flags(code, flag):
    """[source_conformance] Classes A and B are candidates and never the same method."""
    record = {
        "official_height_m": 7.5,
        "height_status": "OFFICIAL_ATTRIBUTE_PRESENT",
        "height_provenance_lod1HeightType": code,
        "height_method_flag": flag,
    }
    result = validate_height_evidence(record)
    assert result.ok, result.errors
    assert result.eligibility == {
        "eligible": False, "reason": "E_HEIGHT_CANDIDATE_ONLY_NOT_FROZEN"}

    same_method = dict(record, height_method_flag="SAME_METHOD")
    assert "E_HEIGHT_METHOD_FLAG_NOT_DISTINCT" in codes(
        validate_height_evidence(same_method))

    del record["height_method_flag"]
    assert "E_HEIGHT_METHOD_FLAG_MISSING" in codes(validate_height_evidence(record))


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), 10**1000])
def test_height_evidence_rejects_non_finite_or_unrepresentable_values(bad_value):
    """[source_conformance] Height candidates must contain finite real values."""
    record = {
        "official_height_m": bad_value,
        "height_status": "OFFICIAL_ATTRIBUTE_PRESENT",
        "height_provenance_lod1HeightType": "2",
        "height_method_flag": "POINT_CLOUD_MEDIAN",
    }
    result = validate_height_evidence(record)
    assert result.ok is False
    assert result.eligibility["eligible"] is False
    assert "E_HEIGHT_VALUE_MISSING" in codes(result)


def test_side_coverage_requires_a_complete_receipt():
    """[software_correctness] PACKAGE_COMPLETE is not an M7 side coverage receipt."""
    assert validate_side_coverage({"coverage_status": "COMPLETE"}).eligibility[
        "eligible"] is True
    package = validate_side_coverage(
        {"coverage_status": "PACKAGE_COMPLETE_WITHIN_AOI"})
    assert package.eligibility == {
        "eligible": False, "reason": "E_SIDE_COVERAGE_NOT_COMPLETE_RECEIPT"}
    assert validate_side_coverage({"coverage_status": "PARTIAL"}).eligibility == {
        "eligible": False, "reason": "E_SIDE_COVERAGE_INCOMPLETE"}


def test_non_mapping_records_fail_closed():
    """[software_correctness] A non-object record is rejected, never coerced."""
    for validator in (validate_setback_evidence, validate_damage_state_evidence,
                      validate_debris_presence_evidence,
                      validate_scenario_realization, validate_height_evidence):
        result = validator(["not", "a", "record"])
        assert result.ok is False
        assert result.eligibility["eligible"] is False
