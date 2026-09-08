"""[source_conformance] PLATEAU building evidence V2 stays a candidate inventory: no setback, no damage, no M7 call."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "inputs" / "staging" / "PLATEAU-BUILDING-EVIDENCE-V2"


def _side():
    return json.loads((STAGING / "M7_BUILDING_SIDE_CANDIDATES.json").read_text(encoding="utf-8"))


def test_v2_candidates_never_carry_setback_damage_or_debris():
    """[source_conformance] every candidate keeps setback_m/damage_state/debris_present null and proximity is not setback."""
    side = _side()
    assert side["method_status"] == "CANDIDATE_ENUMERATION_ONLY_SETBACK_NOT_FROZEN"
    assert side["centroid_used"] is False and side["hazard_derived_damage_or_debris"] is False and side["m7_invoked"] is False
    candidates = [c for a in side["areas"] for c in a["left_candidates"] + a["right_candidates"]]
    assert candidates, "V2 must list at least one candidate"
    for c in candidates:
        assert c["setback_m"] is None and c["damage_state"] is None and c["debris_present"] is None
        assert c["method_status"] == "PROXY_NOT_SETBACK" and c["m7_eligible"] is False
        assert "nearest_geometry_distance_m" in c and "proximity_min_footprint_vertex_to_edge_m" not in c
        assert c["stable_building_id"], "stable uro:buildingID required"
        if c["height_status"] == "INVALID_SENTINEL":
            assert c["official_height_m"] is None
        else:
            assert c["official_height_m"] is not None and c["official_height_m"] > 0 and c["height_uom"] == "m"
    for a in side["areas"]:
        assert a["m7_evidence_ready"] is False
        assert a["coverage_status"].startswith("PACKAGE_COMPLETE") or a["coverage_status"] == "INCOMPLETE"
        assert "setback_m (method not frozen)" in a["missing_fields"]


def test_v2_matrix_and_report_derive_from_side_candidates():
    """[source_conformance] height matrix rows and report counts equal the side-candidate file (no hardcoded totals)."""
    side = _side()
    rows = list(csv.DictReader((STAGING / "M7_HEIGHT_EVIDENCE_MATRIX.csv").open(encoding="utf-8")))
    by_edge = {a["edge_id"]: a for a in side["areas"]}
    assert {r["edge_id"] for r in rows} == set(by_edge)
    for r in rows:
        a = by_edge[r["edge_id"]]
        assert int(r["candidate_count"]) == a["left_count"] + a["right_count"] == len(a["left_candidates"]) + len(a["right_candidates"])
        assert r["usable_as_m7_height_evidence"] == "false"
        assert r["geometry_derived_height_status"] == "DERIVED_CANDIDATE_NOT_FROZEN_NOT_COMPUTED"
    report = json.loads((ROOT / "reports" / "PLATEAU_BUILDING_EVIDENCE_V2.json").read_text(encoding="utf-8"))
    assert report["candidate_count"] == sum(a["left_count"] + a["right_count"] for a in side["areas"])
    assert report["m7_evidence_ready_count"] == 0 and report["m7_computed_count"] == 0 and report["setback_values_generated"] == 0
    readiness = json.loads((ROOT / "reports" / "M7_ALL_EDGE_EVIDENCE_READINESS.json").read_text(encoding="utf-8"))
    pilot_ids = {e["edge_id"] for e in readiness["edges"] if e["deep_pilot"]}
    assert set(by_edge) == pilot_ids, "V2 must cover exactly the deep-pilot edges"
    assert readiness["evidence_ready_count"] == 0 and readiness["computed_count"] == 0


def test_v2_receipts_match_v1_package_hashes_and_track_no_raw():
    """[source_conformance] V2 package SHA-256 equals the V1 receipt values; no raw archive is tracked."""
    v1 = json.loads((ROOT / "inputs" / "staging" / "PLATEAU-BUILDING-EVIDENCE-V1" / "source_receipts.json").read_text(encoding="utf-8"))
    v2 = json.loads((STAGING / "source_receipts.json").read_text(encoding="utf-8"))
    v1_sha = {p["dataset_id"]: p["sha256"] for p in v1["packages"]}
    for p in v2["packages"]:
        assert p["sha256"] == v1_sha[p["dataset_id"]] and p["sha256_verified"] is True
    assert v2["raw_tracked_in_git"] is False
    assert not list(STAGING.glob("*.gml")) and not list(STAGING.glob("*.zip"))
