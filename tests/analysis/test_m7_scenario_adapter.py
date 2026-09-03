"""Tests for the DISABLED M7 experimental scenario adapter.

The adapter must stay inert: it labels everything NON_REAL / EXPERIMENTAL and
refuses to invoke the frozen M7 residual-width core.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analysis import m7_scenario_adapter
from src.analysis.m7_scenario_adapter import (
    M7CoreInvocationForbidden,
    M7ExperimentalInputRejected,
    build_experimental_input,
    reproducible_realization,
    run_m7_core,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "m7_evidence"
ADAPTER_SOURCE = Path(m7_scenario_adapter.__file__).read_text(encoding="utf-8")
PROBABILITIES = {
    "NO_DAMAGE": 0.5,
    "PARTIAL_DAMAGE": 0.3,
    "HALF_COLLAPSE": 0.1,
    "LARGE_SCALE_HALF_COLLAPSE": 0.05,
    "COMPLETE_COLLAPSE": 0.05,
}


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def build() -> dict:
    return build_experimental_input(
        fixture("scenario_realization.NON_REAL.json"),
        [fixture("damage_distribution.NON_REAL.json")],
        [fixture("debris_conditional_probability.NON_REAL.json")],
        [fixture("setback_official_pending.NON_REAL.json")],
        [{"official_height_m": 7.5, "height_status": "OFFICIAL_ATTRIBUTE_PRESENT",
          "height_provenance_lod1HeightType": "2",
          "height_method_flag": "POINT_CLOUD_MEDIAN"}],
    )


def test_experimental_input_is_labelled_non_real_and_disabled():
    """[software_correctness] The adapter output is labelled and never production."""
    payload = build()
    assert payload["label"] == "NON_REAL_EXPERIMENTAL"
    assert payload["production_eligible"] is False
    assert payload["m7_core_invoked"] is False
    assert payload["eligible_record_count"] == 0
    assert len(payload["input_sha256"]) == 64


def test_experimental_input_is_deterministic():
    """[software_correctness] The same fixtures always yield the same receipt."""
    assert build()["input_sha256"] == build()["input_sha256"]


def test_invalid_record_fails_the_whole_build_closed():
    """[software_correctness] One failing record rejects the entire assembly."""
    broken = fixture("setback_official_pending.NON_REAL.json")
    broken["metric_crs"] = "EPSG:4326"
    with pytest.raises(M7ExperimentalInputRejected) as excinfo:
        build_experimental_input(
            fixture("scenario_realization.NON_REAL.json"), [], [], [broken], [])
    assert any("E_CRS_GEOGRAPHIC" in error for error in excinfo.value.errors)


def test_seeded_realization_is_reproducible():
    """[software_correctness] A pinned seed reproduces the realization exactly."""
    first = reproducible_realization(20260903, PROBABILITIES, 0)
    second = reproducible_realization(20260903, PROBABILITIES, 0)
    assert first == second
    assert first["realization_sha256"] == second["realization_sha256"]
    assert first["realized_state"] in PROBABILITIES
    other = reproducible_realization(20260904, PROBABILITIES, 0)
    assert other["realization_sha256"] != first["realization_sha256"]


def test_realization_without_a_seed_raises():
    """[software_correctness] An unseeded realization is refused, never defaulted."""
    with pytest.raises(M7ExperimentalInputRejected) as excinfo:
        reproducible_realization(None, PROBABILITIES, 0)
    assert excinfo.value.errors == ["E_ADAPTER_SEED_REQUIRED"]


def test_realization_rejects_unnormalised_probabilities():
    """[software_correctness] A non-normalised distribution is refused."""
    with pytest.raises(M7ExperimentalInputRejected):
        reproducible_realization(1, {"A": 0.4, "B": 0.4}, 0)


def test_m7_core_invocation_is_forbidden():
    """[software_correctness] The disabled adapter never runs the frozen M7 core."""
    with pytest.raises(M7CoreInvocationForbidden):
        run_m7_core(edge_id="NON-REAL-EDGE-0001")


def test_adapter_source_never_touches_the_frozen_core():
    """[source_conformance] The adapter imports and calls no residual-width core."""
    assert "residual_width" not in ADAPTER_SOURCE
    assert "calculate_residual_width(" not in ADAPTER_SOURCE
