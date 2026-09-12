"""[source_conformance] V2 readiness matrix, exposure-only join and closure receipts are derived, not hardcoded, and never promote states."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_v2_matrix_counts_are_derived_from_v1_and_preserve_zero_ready():
    """[source_conformance] all/deep/ready/computed in V2 equal recomputation over its own edges and over V1 edges."""
    v1 = _load("reports/M7_ALL_EDGE_EVIDENCE_READINESS.json")
    v2 = _load("reports/M7_ALL_EDGE_EVIDENCE_READINESS_V2.json")
    assert v2["all_edge_count"] == len(v2["edges"]) == len(v1["edges"])
    assert v2["deep_pilot_count"] == sum(1 for e in v2["edges"] if e["deep_pilot"]) == sum(1 for e in v1["edges"] if e["deep_pilot"])
    assert v2["evidence_ready_count"] == sum(1 for e in v2["edges"] if e["m7_evidence_ready"]) == v1["evidence_ready_count"]
    assert v2["computed_count"] == sum(1 for e in v2["edges"] if e["m7_computed"]) == v1["computed_count"]
    assert {e["edge_id"] for e in v2["edges"]} == {e["edge_id"] for e in v1["edges"]}
    for e in v2["edges"]:
        cv = e["contract_v2"]
        assert cv["setback_m"] in {"PROXY_NOT_SETBACK", "UNKNOWN"}
        assert cv["damage_state"].startswith("UNKNOWN") and cv["debris_present"] == "UNKNOWN"
        assert cv["official_closure"] != "False"
    rows = list(csv.DictReader((ROOT / "reports" / "M7_ALL_EDGE_EVIDENCE_READINESS_V2.csv").open(encoding="utf-8")))
    assert len(rows) == v2["all_edge_count"]
    freq = v2["missing_field_frequency_612"]
    assert freq["clear_width_m"] == v2["all_edge_count"] and freq["setback_m"] == v2["all_edge_count"]


def test_exposure_only_join_never_generates_damage_debris_or_closure():
    """[source_conformance] 347 historical joins are excluded from public rows, not zero exposure; no damage, debris or closure generated."""
    j = _load("reports/M7_PILOT_EXPOSURE_ONLY_JOIN_V1.json")
    assert j["label"] == "HAZARD_EXPOSURE_ONLY"
    assert j["record_count"] == len(j["records"])
    assert j["record_count"] == 0 and j["historical_record_count"] == 347
    assert sum(j["historical_summary"].values()) == 347 and j["summary"] is None
    assert j["public_exclusion_reason"]
    assert j["damage_state_generated"] == 0 and j["debris_present_generated"] == 0 and j["closure_generated"] == 0
    for r in j["records"]:
        assert r["exposure_class"] == "HAZARD_EXPOSURE_ONLY" and r["damage_state"] is None and r["debris_present"] is None
    side = _load("inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/M7_BUILDING_SIDE_CANDIDATES.json")
    pairs = {(a["edge_id"], c["gml_id"]) for a in side["areas"] for c in a["left_candidates"] + a["right_candidates"]}
    assert {(r["edge_id"], r["gml_id"]) for r in j["records"]} == pairs


def test_closure_receipts_keep_none_and_unknown():
    """[source_conformance] official_closure stays None and hazard_data_status UNKNOWN for every pilot edge until a bounded receipt exists."""
    rec = _load("inputs/staging/M7-CLOSURE-STATUS-RECEIPTS-V1/closure_and_hazard_status_receipts.json")
    v1 = _load("reports/M7_ALL_EDGE_EVIDENCE_READINESS.json")
    pilot = {e["edge_id"] for e in v1["edges"] if e["deep_pilot"]}
    assert {e["edge_id"] for e in rec["edges"]} == pilot
    for e in rec["edges"]:
        assert e["official_closure"] is None and e["hazard_data_status"] == "UNKNOWN"
        assert all(c["result"] != "False" for c in e["automated_source_checks"])
