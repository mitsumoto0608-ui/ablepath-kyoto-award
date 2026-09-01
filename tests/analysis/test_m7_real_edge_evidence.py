"""Regression tests for the bounded 612-edge M7 evidence-readiness receipt."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from src.analysis.candidate_network import M7_API_FIELDS, assess_m7_readiness


ROOT = Path(__file__).resolve().parents[2]
READINESS_JSON = ROOT / "reports" / "M7_ALL_EDGE_EVIDENCE_READINESS.json"
READINESS_CSV = ROOT / "reports" / "M7_ALL_EDGE_EVIDENCE_READINESS.csv"
STATUS_JSON = ROOT / "reports" / "M7_REAL_EDGE_STATUS.json"
MISSING_COUNTS_CSV = ROOT / "reports" / "M7_MISSING_FIELD_COUNTS.csv"
CITY_ARTIFACTS = {
    "kyoto_kiyomizu": ROOT
    / "cities/kyoto_kiyomizu/graph/real/candidate_edges.geojson",
    "kyoto_arashiyama": ROOT
    / "cities/kyoto_arashiyama/graph/walk_edges.real.geojson",
    "fujisawa_enoshima": ROOT
    / "cities/fujisawa_enoshima/graph/candidate_walk_edges.real.geojson",
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_edges() -> list[tuple[str, str, dict]]:
    rows = []
    for city_id, path in CITY_ARTIFACTS.items():
        artifact = _json(path)
        for feature in artifact["features"]:
            props = feature["properties"]
            rows.append((city_id, props["edge_id"], props))
    return sorted(rows, key=lambda row: (row[0], row[1]))


def _csv_projection(row: dict) -> dict[str, str]:
    """Project one JSON receipt into every column of the tracked CSV."""
    return {
        "city_id": row["city_id"],
        "edge_id": row["edge_id"],
        "deep_pilot": json.dumps(row["deep_pilot"]),
        "deep_pilot_group": row["deep_pilot_group"] or "",
        "selection_basis": row["selection_basis"],
        "status": row["status"],
        "m7_api_structurally_callable": json.dumps(
            row["m7_api_structurally_callable"]
        ),
        "m7_evidence_ready": json.dumps(row["m7_evidence_ready"]),
        "m7_computed": json.dumps(row["m7_computed"]),
        "m7_result": json.dumps(row["m7_result"]),
        **{
            f"{field}_status": row["field_evidence_status"][field]
            for field in M7_API_FIELDS
        },
        "missing_fields_json": json.dumps(
            row["missing_fields"], ensure_ascii=False, separators=(",", ":")
        ),
        "reason": row["reason"],
        "implicit_defaults_used": json.dumps(row["implicit_defaults_used"]),
        "damage_or_debris_derived_from_hazard": json.dumps(
            row["damage_or_debris_derived_from_hazard"]
        ),
        "source_artifact": row["source_artifact"],
        "source_artifact_sha256": row["source_artifact_sha256"],
    }


def test_all_612_edges_match_frozen_readiness_contract() -> None:
    """[source_conformance] Every current real candidate edge is represented once."""
    report = _json(READINESS_JSON)
    actual = {(row["city_id"], row["edge_id"]): row for row in report["edges"]}
    expected = _artifact_edges()

    assert len(expected) == len(actual) == report["all_edge_count"] == 612
    assert set(actual) == {(city_id, edge_id) for city_id, edge_id, _ in expected}
    for city_id, edge_id, props in expected:
        receipt = actual[(city_id, edge_id)]
        frozen = assess_m7_readiness(edge_id, props)
        for field in (
            "status",
            "m7_api_structurally_callable",
            "m7_evidence_ready",
            "m7_computed",
            "m7_result",
            "missing_fields",
            "reason",
        ):
            assert receipt[field] == frozen[field]


def test_fixed_deep_pilot_is_five_lexical_edges_per_city() -> None:
    """[software_correctness] The 15-edge review baseline is stable and non-ranking."""
    report = _json(READINESS_JSON)
    selected = [row for row in report["edges"] if row["deep_pilot"]]
    assert len(selected) == 15
    for city_id, path in CITY_ARTIFACTS.items():
        edge_ids = sorted(
            feature["properties"]["edge_id"] for feature in _json(path)["features"]
        )
        assert sorted(row["edge_id"] for row in selected if row["city_id"] == city_id) == edge_ids[:5]
    assert all(row["selection_basis"] == "LEXICAL_EDGE_ID_BASELINE" for row in selected)


def test_receipts_are_canonical_and_duplicate_generation_is_deterministic() -> None:
    """[software_correctness] JSON and CSV bytes have stable canonical ordering."""
    report_bytes = READINESS_JSON.read_bytes()
    report = json.loads(report_bytes)
    assert report_bytes == (
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    rows = list(csv.DictReader(READINESS_CSV.read_text(encoding="utf-8").splitlines()))
    assert [(row["city_id"], row["edge_id"]) for row in rows] == sorted(
        (row["city_id"], row["edge_id"]) for row in rows
    )
    canonical_edges = json.dumps(
        report["edges"], ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    assert hashlib.sha256(canonical_edges).hexdigest() == report["edge_receipts_sha256"]


def test_artifact_receipts_and_csv_projection_bind_current_candidate_bytes() -> None:
    """[source_conformance] Receipts bind current source bytes and CSV mirrors JSON."""
    report = _json(READINESS_JSON)
    for city_id, artifact_path in CITY_ARTIFACTS.items():
        receipt = report["artifact_receipts"][city_id]
        relative_path = artifact_path.relative_to(ROOT).as_posix()
        artifact_sha256 = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        edge_count = len(_json(artifact_path)["features"])
        assert receipt == {
            "candidate_artifact": relative_path,
            "candidate_artifact_sha256": artifact_sha256,
            "edge_count": edge_count,
        }
        city_rows = [row for row in report["edges"] if row["city_id"] == city_id]
        assert len(city_rows) == edge_count
        assert all(row["source_artifact"] == relative_path for row in city_rows)
        assert all(
            row["source_artifact_sha256"] == artifact_sha256 for row in city_rows
        )

    csv_rows = list(
        csv.DictReader(READINESS_CSV.read_text(encoding="utf-8").splitlines())
    )
    assert csv_rows == [_csv_projection(row) for row in report["edges"]]


def test_missing_field_and_status_summaries_are_derived_from_edge_receipts() -> None:
    """[software_correctness] All tracked summaries derive from the 612 receipts."""
    report = _json(READINESS_JSON)
    status = _json(STATUS_JSON)
    edges = report["edges"]
    structural_missing = {
        field: sum(
            row["field_evidence_status"][field] == "MISSING" for row in edges
        )
        for field in M7_API_FIELDS
    }
    evidence_missing = {
        field: sum(
            row["field_evidence_status"][field] != "EVIDENCE_READY" for row in edges
        )
        for field in M7_API_FIELDS
    }
    count_rows = list(
        csv.DictReader(MISSING_COUNTS_CSV.read_text(encoding="utf-8").splitlines())
    )
    assert [row["field"] for row in count_rows] == list(M7_API_FIELDS)
    for row in count_rows:
        field = row["field"]
        assert int(row["structural_missing_edge_count"]) == structural_missing[field]
        assert int(row["evidence_missing_edge_count"]) == evidence_missing[field]
        assert int(row["blocked_edge_count"]) == evidence_missing[field]
        assert row["next_acquisition"]
        assert row["prohibited_derivation"]

    derived_counts = {
        "all_edge_count": len(edges),
        "deep_pilot_count": sum(row["deep_pilot"] for row in edges),
        "structurally_callable_count": sum(
            row["m7_api_structurally_callable"] for row in edges
        ),
        "evidence_ready_count": sum(row["m7_evidence_ready"] for row in edges),
        "computed_count": sum(row["m7_computed"] for row in edges),
    }
    for key, value in derived_counts.items():
        assert report[key] == status[key] == value
    assert status["structural_missing_field_counts"] == structural_missing
    assert status["missing_field_counts"] == evidence_missing


def test_incomplete_real_edges_never_receive_silent_defaults_or_results() -> None:
    """[target_validation] Missing evidence fails closed with an explicit acquisition reason."""
    report = _json(READINESS_JSON)
    status = _json(STATUS_JSON)
    assert status["structurally_callable_count"] == 0
    assert status["evidence_ready_count"] == 0
    assert status["computed_count"] == 0
    assert status["m7_connected_to_real_edges"] is False
    assert status["m7_evidence_pipeline_complete"] is True
    for row in report["edges"]:
        assert row["status"] == "NOT_COMPUTED"
        assert row["m7_result"] is None
        assert row["missing_fields"]
        assert row["reason"]
        assert row["implicit_defaults_used"] is False
        assert row["damage_or_debris_derived_from_hazard"] is False
        assert set(row["field_evidence_status"]) == set(M7_API_FIELDS)
        assert all(
            value in {"MISSING", "STRUCTURAL_VALUE_WITHOUT_EVIDENCE"}
            for value in row["field_evidence_status"].values()
        )
