"""Gate 6 deterministic M7 real-edge pilot tests."""
from copy import deepcopy
from pathlib import Path

from src.analysis.m7_pilot import build_repository_report, evaluate_city_pilot


def _receipt(*, count=None):
    receipt = {
        "source_id": "field-survey-2026",
        "revision_id": "field-survey-2026-v1",
        "source_sha256": "a" * 64,
        "evidence_status": "SOURCE_TRACEABLE",
    }
    if count is not None:
        receipt.update({"coverage_status": "COMPLETE", "observed_count": count})
    return receipt


def _edge(index, *, ready=False):
    properties = {
        "edge_id": f"edge-{index:02d}",
        "source_id": "candidate-geometry-source",
        "revision_id": "candidate-geometry-v1",
        "source_feature_id": f"source-edge-{index:02d}",
        "geometry_status": "SOURCE_TRACEABLE_REAL",
    }
    if ready:
        properties.update(
            {
                "clear_width_m": 5.0,
                "left_buildings": [
                    {
                        "height_m": 10.0,
                        "setback_m": 2.0,
                        "damage_state": "COLLAPSED",
                        "debris_present": True,
                    }
                ],
                "right_buildings": [],
                "variant": "mean_case",
                "official_closure": None,
                "hazard_data_status": "UNKNOWN",
                "m7_provenance": {
                    "clear_width_m": _receipt(),
                    "left_buildings": _receipt(count=1),
                    "right_buildings": _receipt(count=0),
                    "variant": _receipt(),
                    "official_closure": _receipt(),
                    "hazard_data_status": _receipt(),
                },
            }
        )
    return {"type": "Feature", "properties": properties, "geometry": None}


def test_complete_evidence_ready_edge_is_computed_in_stable_pilot():
    """[source_conformance] 5.0 - max(0.31*10+1.10-2.0, 0) = 2.8 m for the sole evidence-ready edge."""
    edges = [_edge(index, ready=index == 2) for index in range(5, 0, -1)]

    result = evaluate_city_pilot("fixture_city", edges, pilot_size=5)

    assert [row["edge_id"] for row in result["edges"]] == [
        "edge-01",
        "edge-02",
        "edge-03",
        "edge-04",
        "edge-05",
    ]
    assert result["selected_edge_count"] == 5
    assert result["m7_evidence_ready_edge_count"] == 1
    assert result["m7_computed_edge_count"] == 1
    computed = result["edges"][1]
    assert computed["status"] == "COMPUTED"
    assert computed["m7_result"]["remaining_clear_width_m"] == 2.8
    assert computed["reason"] == "M7 ran only because every frozen-API input has source-traceable evidence."
    assert len(computed["m7_execution_receipt"]["input_sha256"]) == 64
    assert computed["m7_execution_receipt"]["per_field_provenance"] == edges[3]["properties"]["m7_provenance"]


def test_missing_width_or_side_evidence_remains_reasoned_null():
    """[software_correctness] Removing one frozen-API receipt must keep M7 null and expose a non-empty reason/missing_fields list."""
    incomplete = _edge(1, ready=True)
    del incomplete["properties"]["m7_provenance"]["right_buildings"]
    edges = [incomplete, *[_edge(index) for index in range(2, 6)]]

    result = evaluate_city_pilot("fixture_city", deepcopy(edges), pilot_size=5)
    row = result["edges"][0]

    assert row["m7_evidence_ready"] is False
    assert row["m7_computed"] is False
    assert row["m7_result"] is None
    assert row["missing_fields"]
    assert row["reason"]
    assert result["m7_evidence_ready_edge_count"] == 0
    assert result["m7_computed_edge_count"] == 0


def test_pilot_size_is_bounded_to_visible_review_budget():
    """[software_correctness] Gate 6 permits a visible deterministic pilot of 5 through 20 edges per city, never a silent larger batch."""
    edges = [_edge(index) for index in range(21)]
    for invalid in (4, 21, True):
        try:
            evaluate_city_pilot("fixture_city", edges, pilot_size=invalid)
        except ValueError:
            continue
        raise AssertionError("pilot_size outside 5..20 must fail")


def test_synthetic_or_unbound_geometry_cannot_enter_real_edge_pilot():
    """[source_conformance] A complete M7 fixture is still rejected when its candidate geometry is not explicitly source-traceable real data."""
    edges = [_edge(index, ready=True) for index in range(5)]
    edges[0]["properties"]["geometry_status"] = "SYNTHETIC_DEMO"

    try:
        evaluate_city_pilot("fixture_city", edges, pilot_size=5)
    except ValueError as exc:
        assert "not source-traceable real geometry" in str(exc)
        return
    raise AssertionError("synthetic geometry must not enter the real-edge pilot")


def test_current_three_city_pilot_remains_partial_and_reasoned_null():
    """[source_conformance] Current tracked real candidate artifacts select 5 edges per city but provide zero complete M7 evidence sets."""
    result = build_repository_report(Path(__file__).parents[2])

    assert result["status"] == "PARTIAL"
    assert result["selected_edge_count"] == 15
    assert result["evidence_ready_count"] == 0
    assert result["computed_count"] == 0
    assert all(len(city["candidate_artifact_sha256"]) == 64 for city in result["cities"])
    assert all(
        row["m7_result"] is None and row["missing_fields"] and row["reason"]
        for city in result["cities"]
        for row in city["edges"]
    )
