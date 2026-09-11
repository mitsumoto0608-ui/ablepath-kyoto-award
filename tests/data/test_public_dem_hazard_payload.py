"""Public-payload regression checks for the DEM/Fujisawa continuation."""

from __future__ import annotations

import re
import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.build_public_official_evidence import (
    HAZARD_MEMBER_CONTRACTS,
    _COMMON_HAZARD_SHP_SHA256,
    _COMMON_HAZARD_TXT_SHA256,
    _bind_hazard_member_inventory,
)


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DERIVATIVES = (
    ROOT / "inputs/staging/PUBLIC-GIT-DEM-FUJISAWA-V1/official_evidence.json",
    ROOT / "viewer/public/data/analysis/kyoto_kiyomizu.json",
    ROOT / "viewer/public/data/analysis/kyoto_arashiyama.json",
    ROOT / "viewer/public/data/analysis/fujisawa_enoshima.json",
    ROOT / "viewer/public/data/official/fujisawa_enoshima.delivery_hazards.geojson",
)
FACILITY_ROW_DERIVATIVES = (
    ROOT / "cities/fujisawa_enoshima/facilities/official/facility_table_339.csv",
    ROOT / "cities/fujisawa_enoshima/facilities/official/enoshima_katase_facility_table_57.csv",
    ROOT / "cities/fujisawa_enoshima/facilities/official/FUJISAWA_ACCESSIBILITY_FACILITY_TABLE.json",
    ROOT / "cities/fujisawa_enoshima/facilities/official/FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json",
)
FORBIDDEN = (
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"[A-Za-z]:\\[^\r\n]*Dropbox", re.IGNORECASE),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
)


def _stream_text(path: Path):
    """Yield overlapping UTF-8 chunks so patterns cannot hide across chunk boundaries."""
    overlap = ""
    with path.open(encoding="utf-8", errors="replace") as handle:
        while chunk := handle.read(1024 * 1024):
            text = overlap + chunk
            yield text
            overlap = text[-512:]


def test_large_public_derivatives_are_portable_and_within_repository_cap() -> None:
    """[source_conformance] Every large public derivative is scanned, not skipped above 2 MiB."""
    for path in PUBLIC_DERIVATIVES:
        assert path.stat().st_size <= 10 * 1024 * 1024, path
        for chunk in _stream_text(path):
            assert all(pattern.search(chunk) is None for pattern in FORBIDDEN), path


def test_public_derivatives_do_not_retain_private_only_license_labels() -> None:
    """[source_conformance] Public viewer payloads require source-specific redistribution evidence."""
    for path in PUBLIC_DERIVATIVES:
        for chunk in _stream_text(path):
            assert "PRIVATE_INTERNAL_AND_PRIVATE_GIT_ONLY" not in chunk, path


def test_fujisawa_scenario_members_are_bound_by_exact_identity_not_archive_order() -> None:
    """[source_conformance] Reordering is harmless, while renamed/substituted members fail closed."""
    contracts = HAZARD_MEMBER_CONTRACTS["02_.zip"]
    observed = [
        {
            "shp_name": f"official/{member_id}.shp",
            "member_path_sha256": path_sha256,
            "shp_sha256": _COMMON_HAZARD_SHP_SHA256,
            "dbf_sha256": dbf_sha256,
            "txt_sha256": _COMMON_HAZARD_TXT_SHA256,
        }
        for member_id, _label, path_sha256, dbf_sha256 in contracts
    ]
    expected_ids = [contract[0] for contract in contracts]
    assert [row["member_id"] for row in _bind_hazard_member_inventory(list(reversed(observed)), contracts)] == expected_ids
    renamed = deepcopy(observed)
    renamed[0]["member_path_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="member set"):
        _bind_hazard_member_inventory(renamed, contracts)
    substituted = deepcopy(observed)
    substituted[0]["dbf_sha256"] = observed[1]["dbf_sha256"]
    with pytest.raises(ValueError, match="DBF bytes"):
        _bind_hazard_member_inventory(substituted, contracts)


def test_gsi_public_sample_scope_is_bound_to_official_terms_receipt() -> None:
    """[source_conformance] Public native-cell samples bind official terms without granting raw-package publication."""
    receipt = json.loads((ROOT / "inputs/staging/PUBLIC-GIT-DEM-FUJISAWA-V1/official_source_receipt.json").read_text(encoding="utf-8"))
    terms = receipt["sources"]["gsi_content_terms"]
    evidence = json.loads(PUBLIC_DERIVATIVES[0].read_text(encoding="utf-8"))["dem"]
    assert terms["response_sha256"] == evidence["license_response_sha256"]
    assert terms["url"] == evidence["license_url"]
    assert terms["legal_compliance_claim"] is evidence["legal_compliance_claim"] is False
    assert "NOT_RAW_PACKAGE_BLANKET" in evidence["license_scope"]


def test_unlicensed_fujisawa_facility_rows_are_excluded_but_historical_identity_is_retained() -> None:
    """[source_conformance] Missing provider permission excludes row data without erasing the auditable history."""
    receipt_path = ROOT / "cities/fujisawa_enoshima/facilities/official/facility_source_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["license_status"] == "LICENSE_REVIEW_REQUIRED"
    assert receipt["provider_redistribution_permission_bound"] is False
    assert receipt["public_git_current_tip_status"] == "METADATA_ONLY_ROW_DERIVATIVES_EXCLUDED"
    assert receipt["public_payload_files_present"] is False
    assert receipt["historical_public_git_reachability"] is True
    assert receipt["history_rewrite_performed"] is False
    for path in FACILITY_ROW_DERIVATIVES:
        assert not path.exists()
        identity = receipt["historical_derived_output_identities"][path.name]
        assert re.fullmatch(r"[0-9a-f]{64}", identity["sha256"])
        assert identity["rows"] in {57, 339}


def test_ci_art_uploads_only_after_public_payload_and_repository_gates_succeed() -> None:
    """[source_conformance] Reports, screenshots, and static dist cannot upload from a failed or unscanned job."""
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "if: always()" not in workflow
    assert "viewer:\n    name: Static viewer / Node 22\n    needs: python-linux" in workflow
    viewer_scan = workflow.index("Verify tracked public payload before artifact upload")
    viewer_upload = workflow.index("name: viewer-artifacts", viewer_scan)
    assert viewer_scan < viewer_upload
    assert workflow.count("if: success()") >= 2


def test_ci_uploads_are_fail_closed_behind_repository_scan() -> None:
    """[software_correctness] Public CI artifacts upload only after scans and successful producer jobs."""
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "if: always()" not in workflow
    assert "needs: python-linux" in workflow
    viewer_scan = workflow.index("Verify tracked public payload before artifact upload")
    viewer_upload = workflow.index("name: viewer-artifacts")
    assert viewer_scan < viewer_upload
    assert workflow.count("python scripts/overnight/verify_repository.py --root .") >= 2


def test_reused_dem_section_rejects_a_tampered_or_foreign_source(tmp_path: Path) -> None:
    """[software_correctness] Reuse copies frozen DEM evidence only after verifying its identity."""
    from scripts.build_public_official_evidence import _reused_dem_section

    accepted = json.loads(PUBLIC_DERIVATIVES[0].read_text(encoding="utf-8"))["dem"]
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"dem": accepted}, ensure_ascii=False), encoding="utf-8")
    section, receipt = _reused_dem_section(good)
    assert section == accepted
    assert receipt["mode"] == "REUSED_VERBATIM_FROM_COMMITTED_EVIDENCE"

    for mutate, message in (
        (lambda dem: {}, "no `dem` section"),
        (lambda dem: {**dem, "outer_sha256": "0" * 64}, "different DEM raw package"),
        (lambda dem: {key: value for key, value in dem.items() if key != "no_step_inference"}, "lacks required keys"),
        (lambda dem: {**dem, "cities": {"kyoto_kiyomizu": dem["cities"]["kyoto_kiyomizu"]}}, "exactly the bound cities"),
        (lambda dem: {**dem, "no_interpolation": False}, "no-inference contract"),
    ):
        tampered = tmp_path / "tampered.json"
        payload = mutate(deepcopy(accepted))
        tampered.write_text(json.dumps({"dem": payload} if payload else payload, ensure_ascii=False), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            _reused_dem_section(tampered)
