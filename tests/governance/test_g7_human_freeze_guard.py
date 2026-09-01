import copy
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports" / "G7_HUMAN_FREEZE_DECISIONS.md"
RECORD = ROOT / "reports" / "G7_HUMAN_FREEZE_DECISIONS.json"
SCHEMA = ROOT / "reports" / "G7_HUMAN_FREEZE_DECISIONS.schema.json"

M6_IDS = [f"H{number}" for number in range(1, 21)]
HOKO_FREEZE_IDS = [f"F{number:02d}" for number in range(1, 17)]
HOKO_DECISION_IDS = [f"D{number:02d}" for number in range(1, 26)]
EXPECTED_IDS = M6_IDS + HOKO_FREEZE_IDS + HOKO_DECISION_IDS
REQUIRED_DECISION_FIELDS = {
    "id",
    "lane",
    "title",
    "recommended",
    "alternatives",
    "evidence",
    "effect",
    "checkbox",
    "selection",
    "blocking",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_enablement_guard(record: dict) -> None:
    freeze = record["freeze_record"]
    decisions = record["decisions"]
    enabled = (
        record["gates"]["m6"]["production_calculation_enabled"]
        or record["gates"]["hokonavi"]["production_adapter_enabled"]
    )
    required_freeze_fields = (
        "record_id",
        "reviewer_name",
        "reviewer_role",
        "decision_date",
        "signature_or_review_record",
        "source_commit",
    )
    if enabled and freeze["status"] != "APPROVED":
        raise ValueError("production enablement requires APPROVED human freeze")
    if freeze["status"] != "APPROVED":
        return
    if any(not isinstance(freeze[field], str) or not freeze[field].strip() for field in required_freeze_fields):
        raise ValueError("production enablement requires a complete signed freeze record")
    ids = [decision["id"] for decision in decisions]
    if ids != EXPECTED_IDS or len(set(ids)) != len(EXPECTED_IDS):
        raise ValueError("approved freeze requires the exact unique G7 decision set")
    for decision in decisions:
        expected_m6 = decision["id"].startswith("H")
        expected_lane = "M6" if expected_m6 else "HOKONAVI"
        if decision["lane"] != expected_lane:
            raise ValueError("approved freeze decision lane does not match its ID")
        if decision["blocking"]["m6"] is not expected_m6:
            raise ValueError("approved freeze has inconsistent M6 blocking metadata")
        if decision["blocking"]["hokonavi"] is not (not expected_m6):
            raise ValueError("approved freeze has inconsistent Hokonavi blocking metadata")
    if any(
        not isinstance(decision["selection"], str) or not decision["selection"].strip()
        for decision in decisions
    ):
        raise ValueError("production enablement requires every G7 decision to be selected")


def test_g7_decision_record_is_complete_but_unselected() -> None:
    """[source_conformance] The review record covers H1-H20, F01-F16, and D01-D25 without selecting them."""
    schema = _load(SCHEMA)
    record = _load(RECORD)
    report = REPORT.read_text(encoding="utf-8")

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "urn:ablepath:g7-human-freeze-decisions:1.0.0-review.1"
    assert schema["x-ablepath-required-decision-ids"] == EXPECTED_IDS
    assert schema["allOf"]
    assert schema["properties"]["gates"]["properties"]["m6"]["properties"][
        "production_calculation_enabled"
    ] == {"const": False}
    assert schema["properties"]["gates"]["properties"]["hokonavi"]["properties"][
        "production_adapter_enabled"
    ] == {"const": False}
    approval_then = schema["allOf"][0]["then"]["properties"]
    assert approval_then["decisions"]["items"]["properties"]["selection"] == {
        "type": "string",
        "minLength": 1,
        "pattern": ".*\\S.*",
    }
    assert record["schema_id"] == "ABLEPATH_G7_HUMAN_FREEZE_DECISIONS"
    assert record["schema_version"] == "1.0.0-review.1"
    assert record["document_role"] == "REVIEW_ONLY"
    assert record["freeze_record"]["status"] == "NOT_RECORDED"

    decisions = record["decisions"]
    assert [decision["id"] for decision in decisions] == EXPECTED_IDS
    assert len({decision["id"] for decision in decisions}) == 61
    for decision in decisions:
        assert set(decision) == REQUIRED_DECISION_FIELDS
        assert decision["recommended"]
        assert decision["alternatives"] and all(decision["alternatives"])
        assert decision["evidence"] and all(decision["evidence"])
        assert decision["effect"]
        assert decision["checkbox"] == "[ ]"
        assert decision["selection"] is None
        assert set(decision["blocking"]) == {"m6", "hokonavi", "reason"}
        assert decision["blocking"]["reason"]
        report_row = next(line for line in report.splitlines() if line.startswith(f"| {decision['id']} |"))
        for value in (
            decision["recommended"],
            *decision["alternatives"],
            *decision["evidence"],
            decision["effect"],
            decision["checkbox"],
            decision["blocking"]["reason"],
        ):
            assert value in report_row

    assert "M6_STATUS=READY_FOR_HUMAN_FREEZE" in report
    assert "M6_RESULT_STATUS=NOT_COMPUTED" in report
    assert "HOKONAVI_STATUS=READY_FOR_HUMAN_FREEZE" in report
    assert "HOKONAVI_PRODUCTION_ADAPTER=false" in report
    assert "ACTUAL_MODEL=UNVERIFIED" in report
    assert "MODEL_ROUTE_VERIFIED=false" in report


def test_missing_freeze_record_blocks_both_production_surfaces() -> None:
    """[software_correctness] Enabling M6 or Hokonavi without a complete signed freeze record fails closed."""
    record = _load(RECORD)
    _assert_enablement_guard(record)

    for lane, flag in (
        ("m6", "production_calculation_enabled"),
        ("hokonavi", "production_adapter_enabled"),
    ):
        mutated = copy.deepcopy(record)
        mutated["gates"][lane][flag] = True
        with pytest.raises(ValueError, match="requires APPROVED human freeze"):
            _assert_enablement_guard(mutated)

    incomplete = copy.deepcopy(record)
    incomplete["freeze_record"]["status"] = "APPROVED"
    incomplete["gates"]["m6"]["production_calculation_enabled"] = True
    with pytest.raises(ValueError, match="complete signed freeze record"):
        _assert_enablement_guard(incomplete)

    unsigned_choices = copy.deepcopy(record)
    unsigned_choices["freeze_record"].update(
        {
            "status": "APPROVED",
            "record_id": "TEST-ONLY-NOT-A-REAL-FREEZE",
            "reviewer_name": "TEST FIXTURE",
            "reviewer_role": "TEST FIXTURE",
            "decision_date": "2099-01-01",
            "signature_or_review_record": "TEST FIXTURE",
            "source_commit": "0" * 40,
        }
    )
    unsigned_choices["gates"]["hokonavi"]["production_adapter_enabled"] = True
    with pytest.raises(ValueError, match="every G7 decision"):
        _assert_enablement_guard(unsigned_choices)

    approved_without_selections = copy.deepcopy(unsigned_choices)
    approved_without_selections["gates"]["hokonavi"]["production_adapter_enabled"] = False
    with pytest.raises(ValueError, match="every G7 decision"):
        _assert_enablement_guard(approved_without_selections)

    blank_selections = copy.deepcopy(unsigned_choices)
    for decision in blank_selections["decisions"]:
        decision["selection"] = " "
    with pytest.raises(ValueError, match="every G7 decision"):
        _assert_enablement_guard(blank_selections)

    blank_signature = copy.deepcopy(blank_selections)
    for decision in blank_signature["decisions"]:
        decision["selection"] = "TEST FIXTURE SELECTION"
    blank_signature["freeze_record"]["signature_or_review_record"] = " "
    with pytest.raises(ValueError, match="complete signed freeze record"):
        _assert_enablement_guard(blank_signature)

    approved_but_incomplete = copy.deepcopy(record)
    approved_but_incomplete["freeze_record"]["status"] = "APPROVED"
    with pytest.raises(ValueError, match="complete signed freeze record"):
        _assert_enablement_guard(approved_but_incomplete)

    replaced_decision = copy.deepcopy(unsigned_choices)
    for decision in replaced_decision["decisions"]:
        decision["selection"] = "TEST FIXTURE SELECTION"
    replaced_decision["decisions"][-1]["id"] = "D24"
    with pytest.raises(ValueError, match="exact unique G7 decision set"):
        _assert_enablement_guard(replaced_decision)

    wrong_lane = copy.deepcopy(unsigned_choices)
    for decision in wrong_lane["decisions"]:
        decision["selection"] = "TEST FIXTURE SELECTION"
    wrong_lane["decisions"][0]["lane"] = "HOKONAVI"
    with pytest.raises(ValueError, match="lane does not match"):
        _assert_enablement_guard(wrong_lane)

    wrong_blocking = copy.deepcopy(wrong_lane)
    wrong_blocking["decisions"][0]["lane"] = "M6"
    wrong_blocking["decisions"][0]["blocking"]["m6"] = False
    with pytest.raises(ValueError, match="inconsistent M6 blocking"):
        _assert_enablement_guard(wrong_blocking)


def test_repository_truth_remains_disabled_before_human_freeze() -> None:
    """[source_conformance] The current production surfaces remain disabled while the G7 freeze is unrecorded."""
    record = _load(RECORD)
    assert record["gates"]["m6"] == {
        "status": "READY_FOR_HUMAN_FREEZE",
        "result_status": "NOT_COMPUTED",
        "production_calculation_enabled": False,
    }
    assert record["gates"]["hokonavi"] == {
        "status": "READY_FOR_HUMAN_FREEZE",
        "production_adapter_enabled": False,
    }

    mapping = (ROOT / "schemas" / "hokonavi_2024_mapping.yaml").read_text(encoding="utf-8")
    citypack_schema = _load(ROOT / "schemas" / "hazards" / "citypack-envelope.schema.json")
    completion = _load(ROOT / "reports" / "COMPLETION_LEVELS.json")
    assert "adapter_implemented: false" in mapping
    assert citypack_schema["properties"]["readiness"]["properties"]["m6_status"]["const"] == "NOT_COMPUTED"
    assert completion["M6_CONNECTED"] is False
    assert not (ROOT / "src" / "m6").exists()
    assert not (ROOT / "src" / "hokonavi").exists()
