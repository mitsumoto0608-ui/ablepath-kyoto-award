"""Gate 5–8 pre-mortem and bounded evidence protocol contract."""
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "reports" / "G5_G8_PREMORTEM_REGISTER.csv"
TRIGGERS = ROOT / "reports" / "G5_G8_RESEARCH_TRIGGER_STATUS.json"


def _rows() -> list[dict[str, str]]:
    with REGISTER.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_premortem_register_has_one_complete_row_for_each_problem_id() -> None:
    """[source_conformance] P01–P17 each retain a safe default, forbidden resolution, and mechanical check."""
    rows = _rows()
    expected = {f"P{number:02d}" for number in range(1, 18)}

    assert len(rows) == 17
    assert {row["problem_id"] for row in rows} == expected
    required = {
        "gate",
        "problem_class",
        "trigger",
        "likely_symptom",
        "impact",
        "safe_default",
        "first_diagnostic",
        "allowed_resolution",
        "forbidden_resolution",
        "source_type_required",
        "paper_required",
        "human_freeze_required",
        "mechanical_check",
        "owner",
        "status",
    }
    assert all(all(row[field].strip() for field in required) for row in rows)


def test_research_trigger_state_is_bounded_and_never_promotes_active_gaps() -> None:
    """[software_correctness] Active problems stay on conservative defaults and every packet is capped at five sources."""
    status = json.loads(TRIGGERS.read_text(encoding="utf-8"))
    problems = {item["problem_id"]: item for item in status["problems"]}

    assert set(problems) == {f"P{number:02d}" for number in range(1, 18)}
    assert status["literature_lane_is_gate_blocker"] is False
    assert status["packet_source_budget"]["default_maximum"] == 5
    assert status["production_rule"] == "NO_EVIDENCE_PACKET_NO_NEW_RESEARCH_DERIVED_PRODUCTION_BEHAVIOR"
    assert problems["P01"]["current_resolution"] == "NOT_CONNECTED_OR_METADATA_ONLY"
    assert problems["P08"]["current_resolution"] == "NOT_COMPUTED_WITH_MISSING_FIELDS_AND_REASON"
    assert problems["P09"]["human_freeze_required"] is True
    assert problems["P11"]["current_resolution"] == "VERIFIED_2D_FALLBACK_TESTS_CI_PENDING"
    assert problems["P12"]["current_resolution"] == "OFFICIAL_METADATA_WITH_UNKNOWN_OPERATION"


def test_human_freeze_problem_classes_remain_explicit() -> None:
    """[target_validation] Research cannot bypass frozen threshold, closure, safety, or source-authority decisions."""
    rows = {row["problem_id"]: row for row in _rows()}

    for problem_id in ("P05", "P06", "P07", "P08", "P09", "P12", "P13", "P14", "P15", "P16"):
        assert rows[problem_id]["human_freeze_required"] == "TRUE"
