import csv
import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "inputs" / "staging" / "PLATEAU-BUILDING-EVIDENCE-V1"
REPORT = ROOT / "reports" / "PLATEAU_BUILDING_EVIDENCE_V1.json"
AOIS = {
    ("kyoto_kiyomizu", "kiyomizu"),
    ("kyoto_kiyomizu", "gion"),
    ("kyoto_kiyomizu", "kiyomizu_gion_connector"),
    ("kyoto_arashiyama", "arashiyama"),
    ("fujisawa_enoshima", "enoshima_katase"),
}


def _validate_unpromoted_candidate(area):
    if area["coverage_status"] == "COMPLETE" and not area.get("coverage_receipt"):
        raise ValueError("COMPLETE side coverage requires a coverage receipt")
    if area["m7_evidence_ready"]:
        raise ValueError("unverified PLATEAU candidate cannot be M7 evidence-ready")
    if "setback_m" in area:
        raise ValueError("setback_m is forbidden before method freeze")


def test_plateau_inventory_separates_five_aoi_evidence_and_fallback_states():
    """[source_conformance] Five AOIs stay package-bound but unconnected without building evidence."""
    receipts = json.loads((STAGING / "source_receipts.json").read_text(encoding="utf-8"))
    packages = {
        package["dataset_id"]: (
            package["city_code"],
            package["sha256"],
        )
        for package in receipts["packages"]
    }
    assert packages == {
        "plateau_kyoto_2025_citygml_v5": (
            "26100",
            "3ea8f10ac188b7042d151efdf29534f060196e523b1d66e8eb892e82a7ec293c",
        ),
        "plateau_fujisawa_2025_citygml_v5": (
            "14205",
            "7e85ff8e1642b9c2cc627f356acedbe792e95fac25febe2ee70c9312d6c415ea",
        ),
    }
    assert receipts["remote_tileset"]["root_sha256"] == (
        "ce58a92bb9da595d9251cd72b7b77af6da9a3748628a0e8370ffc6fbc6312242"
    )

    with (STAGING / "PLATEAU_BUILDING_AOI_INVENTORY.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert {(row["city_id"], row["subarea_id"]) for row in rows} == AOIS
    assert {row["connection_mode"] for row in rows} == {"NOT_CONNECTED"}
    assert {row["fallback"] for row in rows} == {"EXISTING_DETERMINISTIC_2D"}
    assert {row["stable_building_id_status"] for row in rows} == {"NOT_INSPECTED"}
    assert {row["official_height_attribute_status"] for row in rows} == {
        "UNKNOWN_NOT_INSPECTED"
    }
    assert {row["bounded_derivative_status"] for row in rows} == {"NOT_CREATED"}

    status = json.loads(REPORT.read_text(encoding="utf-8"))
    assert status["target_aoi_count"] == 5
    assert status["package_receipt_bound_count"] == 2
    assert status["package_raw_verified_in_authorized_scope_count"] == 0
    assert status["building_side_candidate_count"] == 0
    assert status["not_connected_2d_fallback_aoi_count"] == 5
    assert status["m7_evidence_ready_count"] == 0
    assert status["m7_computed_count"] == 0
    assert status["safe_route_claim"] is False
    assert status["accessibility_claim"] is False


def test_plateau_candidates_fail_closed_without_complete_coverage_or_setback_freeze():
    """[software_correctness] Missing coverage cannot become an empty-side proof or M7 input."""
    packet = json.loads(
        (STAGING / "M7_BUILDING_SIDE_CANDIDATES.json").read_text(encoding="utf-8")
    )
    assert packet["candidate_count"] == 0
    assert packet["centroid_distance_forbidden"] is True
    for area in packet["areas"]:
        _validate_unpromoted_candidate(area)
        assert area["coverage_status"] == "INCOMPLETE"
        assert area["coverage_receipt"] is None
        assert area["left_candidates"] == []
        assert area["right_candidates"] == []
        assert area["reason"]

    invalid = dict(packet["areas"][0], coverage_status="COMPLETE")
    with pytest.raises(ValueError, match="coverage receipt"):
        _validate_unpromoted_candidate(invalid)


def test_plateau_packet_contains_no_local_paths_secrets_or_raw_citygml():
    """[source_conformance] Sanitized tracked evidence excludes local paths, secrets, and raw models."""
    tracked_packet_files = [path for path in STAGING.rglob("*") if path.is_file()]
    tracked_packet_files += [
        ROOT / "reports" / "PLATEAU_BUILDING_EVIDENCE_V1.json",
        ROOT / "reports" / "PLATEAU_BUILDING_EVIDENCE_V1.md",
    ]
    forbidden_path = re.compile(r"(?:[A-Za-z]:\\|/Users/|\\Users\\)")
    forbidden_secret = re.compile(
        r"(?:token=|authorization:|cookie:|x-amz-signature=)", re.IGNORECASE
    )
    for path in tracked_packet_files:
        assert path.suffix.lower() not in {".gml", ".xml", ".zip", ".pdf", ".xlsx"}
        text = path.read_text(encoding="utf-8")
        assert not forbidden_path.search(text)
        assert not forbidden_secret.search(text)
