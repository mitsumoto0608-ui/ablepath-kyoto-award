"""Gate 5–8 aggregate status contract."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_gate5_to_gate8_status_matches_lane_receipts_without_truth_promotion() -> None:
    """[source_conformance] Aggregate status copies lane counts/states and keeps every public safety/admin claim false."""
    status = _read("reports/GATE5_TO_GATE8_STATUS.json")
    gate5 = _read("reports/G5_OFFICIAL_HAZARD_STATUS.json")
    gate6 = _read("reports/G6_M7_REAL_EDGE_PILOT.json")
    gate7 = _read("reports/G7_HUMAN_FREEZE_DECISIONS.json")
    gate8 = _read("reports/G8_PLATEAU_FACILITY_STATUS.json")

    assert status["gate5_official_hazard"] == {
        "status": gate5["status"],
        "connected_cities": gate5["connected_cities"],
        "connected_layers": gate5["layers"],
        "closure_derived": False,
    }
    assert status["gate6_m7_real_edge"] == {
        "status": gate6["status"],
        "selected_edge_count": gate6["selected_edge_count"],
        "evidence_ready_count": gate6["evidence_ready_count"],
        "computed_count": gate6["computed_count"],
    }
    assert status["gate7_m6"] == {
        "status": gate7["gates"]["m6"]["status"],
        "production_connected": gate7["gates"]["m6"]["production_calculation_enabled"],
    }
    assert status["gate7_hokonavi"] == {
        "status": gate7["gates"]["hokonavi"]["status"],
        "production_connected": gate7["gates"]["hokonavi"]["production_adapter_enabled"],
    }
    assert status["gate8_plateau_3d"] == {
        key: gate8["gate8_plateau_3d"][key]
        for key in ("status", "connected_cities", "real_tileset")
    }
    assert status["gate8_facilities"] == {
        key: gate8["gate8_facilities"][key]
        for key in ("status", "connected_sources", "operation_inferred")
    }
    assert status["safe_route_claim"] is False
    assert status["accessibility_claim"] is False
    assert status["admin_validated"] is False
    assert status["public_release_ready"] is False


def test_gate5_to_gate8_partial_lanes_are_not_relabelled_as_complete() -> None:
    """[software_correctness] Zero connected/computed evidence cannot be represented as a PASS gate or release readiness."""
    status = _read("reports/GATE5_TO_GATE8_STATUS.json")

    assert status["gate5_official_hazard"]["status"] == "PARTIAL"
    assert status["gate5_official_hazard"]["connected_layers"] == []
    assert status["gate6_m7_real_edge"] == {
        "status": "PARTIAL",
        "selected_edge_count": 15,
        "evidence_ready_count": 0,
        "computed_count": 0,
    }
    assert status["gate8_plateau_3d"]["status"] == "PARTIAL"
    assert status["gate8_plateau_3d"]["real_tileset"] is False
    assert status["gate8_facilities"]["status"] == "BLOCKED"
