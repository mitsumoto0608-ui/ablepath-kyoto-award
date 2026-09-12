"""Regression gates for the corrected V2 local-artifact promotion receipt."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "inputs" / "staging" / "OFFICIAL-LOCAL-ARTIFACT-PROMOTION-V2"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_corrected_v2_receipts_and_source_bindings_fail_closed() -> None:
    """[source_conformance] The corrected ZIP and four found families retain exact, non-promoted evidence."""

    receipt = _json(STAGING / "corrected_v2_receipt.json")
    assert receipt["sha256"] == "297f6aa0f1c9abc28ef22f62fa305006f9d58307f112a40c92543e8188cbc574"
    assert receipt["member_count"] == 17
    assert receipt["crc_status"] == "PASS"
    assert receipt["supersedes"]["true_missing_data_count"] == 1

    bindings = _json(STAGING / "source_bindings.json")
    assert bindings["true_missing_data_count"] == 0
    assert bindings["model_route_verified"] is False
    assert all(item["found"] for item in bindings["families"])
    assert not any(item["connected"] for item in bindings["families"])
    assert not any("C:" + "\\" in json.dumps(item, ensure_ascii=False) for item in bindings["families"])
    raw_sha256 = [item["sha256"] for item in bindings["families"]]
    assert all(re.fullmatch(r"[0-9a-f]{64}", value) for value in raw_sha256)
    facility = next(
        item
        for item in bindings["families"]
        if item["dataset_id"] == "fujisawa_webgis_toilets_accessibility"
    )
    expected_facility_sha256 = (
        "71bd70b0703086017e26d71cf4d73b76bcb0d14aaa0143c351e4763442b4530d"
    )
    assert facility["sha256"] == expected_facility_sha256
    facility_receipt = _json(
        ROOT
        / "cities"
        / "fujisawa_enoshima"
        / "facilities"
        / "official"
        / "facility_source_receipt.json"
    )
    assert facility_receipt["raw_sha256"] == expected_facility_sha256


def test_dem_products_and_aoi_are_separated_without_vertical_datum_inference() -> None:
    """[target_validation] Twelve DEM products remain product-specific and terrain-unconnected pending datum/AOI review."""

    rows = _rows(STAGING / "dem_product_inventory.csv")
    assert len(rows) == 12
    assert {row["mesh_id"] for row in rows} == {"523536", "523545", "523546", "523973"}
    assert {row["dem_class"] for row in rows} == {"DEM1A", "DEM5A", "DEM5B"}
    assert not any(row["dem_class"] == "DEM10B" for row in rows)
    assert all(row["vertical_datum"] == "NOT_EXPLICIT_IN_INSPECTED_GML" for row in rows)
    assert all(row["terrain_connected"] == "false" for row in rows)
    assert all(row["validation_result"] == "CRS_REVIEW_REQUIRED" for row in rows)


def test_scenario_outputs_and_facility_receipt_preserve_unknowns() -> None:
    """[target_validation] Hazard scenarios stay fail-closed and unlicensed facility rows stay outside the public tip."""

    earthquake = _rows(ROOT / "cities" / "fujisawa_enoshima" / "hazards" / "official" / "earthquake_scenario_inventory.csv")
    liquefaction = _rows(ROOT / "cities" / "fujisawa_enoshima" / "hazards" / "official" / "liquefaction_scenario_inventory.csv")
    assert len(earthquake) == 9
    assert len({row["dataset_id"] for row in earthquake}) == 9
    assert len(liquefaction) == 9
    assert len({row["dataset_id"] for row in liquefaction}) == 9
    assert all("DO_NOT_DERIVE_CLOSED" in row["safety_boundary"] for row in earthquake + liquefaction)

    facility_dir = ROOT / "cities" / "fujisawa_enoshima" / "facilities" / "official"
    receipt = _json(facility_dir / "facility_source_receipt.json")
    assert receipt["license_status"] == "LICENSE_REVIEW_REQUIRED"
    assert receipt["provider_redistribution_permission_bound"] is False
    assert receipt["public_payload_files_present"] is False
    assert receipt["historical_public_git_reachability"] is True
    assert receipt["history_rewrite_performed"] is False
    for name, expected in receipt["historical_derived_output_identities"].items():
        assert not (facility_dir / name).exists()
        assert re.fullmatch(r"[0-9a-f]{64}", expected["sha256"])
        assert expected["rows"] in {57, 339}

    hazard_receipt = _json(
        ROOT / "cities" / "fujisawa_enoshima" / "hazards" / "official" / "source_receipt.json"
    )
    assert _sha256(
        ROOT / "cities" / "fujisawa_enoshima" / "hazards" / "official" / "earthquake_scenario_inventory.csv"
    ) == hazard_receipt["earthquake"]["inventory_sha256"]
    assert _sha256(
        ROOT / "cities" / "fujisawa_enoshima" / "hazards" / "official" / "liquefaction_scenario_inventory.csv"
    ) == hazard_receipt["liquefaction"]["inventory_sha256"]


def test_kyoto_scoped_display_connection_does_not_claim_analysis_or_safety() -> None:
    """[software_correctness] Approved AOI display is true while terrain/hazard analysis and safety stay false.

    The expectation changed because the reviewed A31b source-feature selections and three
    source-coordinate facility categories are now connected to the internal viewer. This
    does not connect elevation analysis, hazard edge analysis, landslide, or operational
    facility truth and cannot derive closure or accessibility.
    """

    status = _json(ROOT / "reports" / "KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json")
    assert status["closure_derived"] is False
    assert status["safe_route_claim"] is False
    assert status["accessibility_claim"] is False
    for city in ("kyoto_kiyomizu", "kyoto_arashiyama"):
        truth = status["cities"][city]
        assert truth["dem_found"] is True
        assert truth["dem_inventory_validated"] is True
        assert truth["terrain_connected"] is False
        assert truth["terrain_elevation_analysis_connected"] is False
        assert truth["flood_connected"] is True
        assert truth["flood_connected_scope"].endswith("DISPLAY_ONLY_NOT_EDGE_OVERLAP_OR_OPERATIONAL_STATE")
        assert truth["landslide_connected"] is False
        assert truth["official_facility_map_connected"] is True
        assert truth["official_facility_connection_scope"].endswith("SOURCE_PROVIDED_COORDINATES_ONLY")

    receipt = _json(ROOT / "cities" / "fujisawa_enoshima" / "facilities" / "official" / "facility_source_receipt.json")
    for relative in (
        "cities/fujisawa_enoshima/facilities/official/facility_table_339.csv",
        "cities/fujisawa_enoshima/facilities/official/enoshima_katase_facility_table_57.csv",
        "cities/fujisawa_enoshima/facilities/official/FUJISAWA_ACCESSIBILITY_FACILITY_TABLE.json",
        "cities/fujisawa_enoshima/facilities/official/FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json",
    ):
        assert not (ROOT / relative).exists()
        assert Path(relative).name in receipt["historical_derived_output_identities"]
