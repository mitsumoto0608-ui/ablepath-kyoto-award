"""Public-payload regression checks for the DEM/Fujisawa continuation."""

from __future__ import annotations

import re
import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.build_public_official_evidence import (
    HAZARD_MEMBER_CONTRACTS,
    INTENSITY_CENTRE_TOLERANCE_M,
    INTENSITY_CROSS_CHECK_TOLERANCE_M,
    _COMMON_HAZARD_SHP_SHA256,
    _COMMON_HAZARD_TXT_SHA256,
    _COMMON_INTENSITY_SHP_SHA256,
    _COMMON_INTENSITY_TXT_SHA256,
    _bind_hazard_member_inventory,
    _jis_quarter_mesh_cell,
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


def _public_evidence() -> dict:
    return json.loads(PUBLIC_DERIVATIVES[0].read_text(encoding="utf-8"))


def test_fujisawa_intensity_members_are_bound_by_exact_identity_not_archive_order() -> None:
    """[source_conformance] Each intensity scenario binds one exact member; substitution fails closed."""
    contracts = HAZARD_MEMBER_CONTRACTS["01_.zip"]
    common = {"shp_sha256": _COMMON_INTENSITY_SHP_SHA256, "txt_sha256": _COMMON_INTENSITY_TXT_SHA256}
    observed = [
        {"shp_name": f"01_/{member_id}.shp", "member_path_sha256": path_sha256, "dbf_sha256": dbf_sha256, **common}
        for member_id, _label, path_sha256, dbf_sha256 in contracts
    ]
    expected_ids = [contract[0] for contract in contracts]
    assert [row["member_id"] for row in _bind_hazard_member_inventory(list(reversed(observed)), contracts, **common)] == expected_ids
    assert len({contract[2] for contract in contracts}) == len({contract[3] for contract in contracts}) == 8
    substituted = deepcopy(observed)
    substituted[0]["dbf_sha256"] = observed[1]["dbf_sha256"]
    with pytest.raises(ValueError, match="DBF bytes"):
        _bind_hazard_member_inventory(substituted, contracts, **common)
    # The liquefaction SHP/sidecar bytes must never satisfy an intensity member.
    foreign = deepcopy(observed)
    foreign[0]["shp_sha256"] = _COMMON_HAZARD_SHP_SHA256
    with pytest.raises(ValueError, match="SHP bytes"):
        _bind_hazard_member_inventory(foreign, contracts, **common)


def test_fujisawa_intensity_crs_closure_is_recorded_and_within_verification_tolerance() -> None:
    """[source_conformance] The provider-declared closure and the erroneous sidecar are both recorded."""
    hazards = _public_evidence()["fujisawa_hazards"]
    summary = hazards["intensity_distribution"]
    assert summary["status"] == "CONNECTED"
    assert summary["scenario_count"] == 8
    assert summary["exposure_only"] is True and summary["scenario_averaged"] is False
    layers = [layer for layer in hazards["layers"] if layer["layer_kind"] == "震度分布"]
    assert len(layers) == summary["scenario_count"]
    for layer in layers:
        closure = layer["crs_closure"]
        assert closure["decision"] == "EPSG:6677_JGD2011_ZONE_IX_PROVIDER_DECLARED"
        assert closure["display_geometry_source"] == "JIS_X_0410_MESH_CODE_EPSG_6668"
        assert closure["tolerance_m"] == INTENSITY_CROSS_CHECK_TOLERANCE_M
        assert closure["tolerance_scope"] == "VERIFICATION_ONLY_NOT_REGISTRY_NOT_EVALUATION"
        assert closure["scope"] == "APPLIES_ONLY_TO_01_INTENSITY_SCENARIO_MEMBERS"
        assert 0 < closure["max_vertex_error_m"] <= INTENSITY_CROSS_CHECK_TOLERANCE_M
        assert 0 < closure["max_sibling_vertex_error_m"] <= INTENSITY_CROSS_CHECK_TOLERANCE_M
        assert closure["erroneous_sidecar"] == {
            "text_sha256": _COMMON_INTENSITY_TXT_SHA256,
            "declared": "GCS_Tokyo",
            "status": "ERRONEOUS_SIDECAR_RECORDED_NOT_USED",
        }
        assert layer["source_crs"] == "EPSG:6668"
        assert "HAZARD_EXPOSURE_ONLY" in layer["limitations"] and "not averaged" in layer["limitations"]


def test_intensity_tolerance_breach_fails_closed() -> None:
    """[software_correctness] A tightened tolerance rejects the observed cross-check instead of passing."""
    observed = max(layer["crs_closure"]["max_vertex_error_m"] for layer in _public_evidence()["fujisawa_hazards"]["layers"] if layer["layer_kind"] == "震度分布")
    import scripts.build_public_official_evidence as builder

    builder._assert_intensity_cross_check(observed, 0.0, "IntS-01")
    original = builder.INTENSITY_CROSS_CHECK_TOLERANCE_M
    try:
        builder.INTENSITY_CROSS_CHECK_TOLERANCE_M = 0.0
        with pytest.raises(ValueError, match="cross-check exceeded"):
            builder._assert_intensity_cross_check(observed, 0.0, "IntS-01")
    finally:
        builder.INTENSITY_CROSS_CHECK_TOLERANCE_M = original


def test_intensity_features_carry_mesh_centre_attributes_and_no_derived_state() -> None:
    """[source_conformance] Every displayed cell is its own mesh-code cell and derives no state."""
    hazards = _public_evidence()["fujisawa_hazards"]
    forbidden = {"damage_state", "debris_present", "official_closure", "closed", "passable", "safety_state", "rank", "scenario_average"}
    feature_count = 0
    for layer in (row for row in hazards["layers"] if row["layer_kind"] == "震度分布"):
        for feature in layer["features"]:
            props = feature["properties"]
            assert not forbidden & set(props)
            longitude, latitude, delta_longitude, delta_latitude = _jis_quarter_mesh_cell(props["mesh_code"])
            from pyproj import Geod
            assert Geod(ellps="GRS80").inv(longitude + delta_longitude / 2, latitude + delta_latitude / 2, props["longitude_raw"], props["latitude_raw"])[2] <= INTENSITY_CENTRE_TOLERANCE_M
            ring = feature["geometry"]["coordinates"][0]
            assert ring[0] == ring[-1] == [longitude, latitude] and len(ring) == 5
            feature_count += 1
    assert feature_count == hazards["intensity_distribution"]["selected_feature_count"]
    assert hazards["closure_derived"] is False and hazards["damage_or_debris_inferred"] is False


def test_dem_section_is_reused_verbatim_and_recorded_as_such() -> None:
    """[source_conformance] The frozen DEM evidence is carried forward with an explicit reuse receipt."""
    payload = _public_evidence()
    rebuild = payload["dem_rebuild"]
    assert rebuild["mode"] == "REUSED_VERBATIM_FROM_COMMITTED_EVIDENCE"
    assert re.fullmatch(r"[0-9a-f]{64}", rebuild["source_sha256"])
    assert "DEM re-acquisition explicitly not repeated" in rebuild["reason"]
    dem = payload["dem"]
    assert dem["outer_sha256"] == "6b67adaabe15908189316eb34dd574bfe5854b9db509f29902eab7ecfc3a88db"
    assert sorted(dem["cities"]) == ["fujisawa_enoshima", "kyoto_arashiyama", "kyoto_kiyomizu"]
    assert dem["no_interpolation"] is dem["no_step_inference"] is True


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
        (lambda dem: {**dem, "cities": {**dem["cities"], "fujisawa_enoshima": {"injected_not_frozen": 123}}}, "frozen DEM section"),
    ):
        tampered = tmp_path / "tampered.json"
        payload = mutate(deepcopy(accepted))
        tampered.write_text(json.dumps({"dem": payload} if payload else payload, ensure_ascii=False), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            _reused_dem_section(tampered)


def test_intensity_centre_uses_the_authorized_metre_contract() -> None:
    """[source_conformance] T-B METHOD#3 allows 0.06 m, not a per-axis 1e-5 degree box.

    The provider's rounded centre passes; shifting its longitude by 5e-6 degree
    is independently over 0.06 m (GRS80) and must fail. This restores the supplied
    verification contract, not a production threshold or a new scientific value.
    """
    from pyproj import Geod
    from scripts.build_public_official_evidence import _intensity_cell

    feature = next(layer for layer in _public_evidence()["fujisawa_hazards"]["layers"] if layer["layer_kind"] == "震度分布")["features"][0]
    props = feature["properties"]
    record = {"KEY_CODE": props["mesh_code"], "ﾒｯｼｭｺｰﾄﾞ": props["mesh_code"], "LON": props["longitude_raw"], "LAT": props["latitude_raw"]}
    _intensity_cell(record)
    west, south, dx, dy = _jis_quarter_mesh_cell(props["mesh_code"])
    shifted = {**record, "LON": record["LON"] + 5e-6}
    assert Geod(ellps="GRS80").inv(west + dx / 2, south + dy / 2, shifted["LON"], shifted["LAT"])[2] > 0.06
    for invalid in (shifted, {**record, "LON": float("nan")}, {**record, "LAT": float("inf")}):
        with pytest.raises(ValueError, match="cell centre"):
            _intensity_cell(invalid)


def test_intensity_current_binding_is_resolvable_and_does_not_authorize_facilities() -> None:
    """[source_conformance] Retrospective 01_ metadata and CRS authority remain scope bound.

    Additional checks cover provenance, not a license assumption from a generic
    owner approval. Per-feature display flags are required by original T-B §5.
    """
    from hashlib import sha256

    mapping = json.loads((ROOT / "reports/FUJISAWA_INTENSITY_CRS_CLOSURE_RECEIPT.json").read_text(encoding="utf-8"))
    source = (ROOT / mapping["source_harness_receipt"]).read_bytes().replace(b"\r\n", b"\n")
    assert sha256(source).hexdigest() == mapping["source_harness_receipt_sha256"]
    assert {row["id"] for row in json.loads(source)["findings"]} == {"K1", "K2", "K3", "K4"}
    assert mapping["direct_provider_correction_of_01_confirmed"] is False
    license_bytes = (ROOT / "inputs/staging/FUJISAWA-INTENSITY-CRS-V1/license_binding.json").read_bytes().replace(b"\r\n", b"\n")
    binding = json.loads(license_bytes)
    assert binding["resource_id"] == "704a2ee0-0040-4a96-b92a-c8e36b559d3d"
    assert binding["retained_raw"]["sha256"] == "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442"
    assert binding["binding_mode"] == "RETROSPECTIVE_METADATA_MATCH_TO_RETAINED_RAW"
    assert binding["provider_published_sha256"] is binding["original_downloaded_at"] is None
    assert binding["fujisawa_city_facility_permission_granted"] is binding["public_history_resolved"] is binding["public_release_ready"] is False
    hazards = _public_evidence()["fujisawa_hazards"]
    summary = hazards["intensity_distribution"]
    assert summary["license_binding_sha256"] == sha256(license_bytes).hexdigest()
    assert summary["license_review"] == binding["status"] == "CC-BY-4.0"
    assert 0 < summary["crs_closure"]["max_centre_error_m"] <= 0.06
    delivered = json.loads((ROOT / "viewer/public/data/official/fujisawa_enoshima.delivery_hazards.geojson").read_text(encoding="utf-8"))
    selected = [feature for feature in delivered["features"] if "intensity_distribution" in feature["properties"].get("source_id", "")]
    assert len(selected) == summary["selected_feature_count"]
    assert all(feature["properties"]["_ablepath_display_only"] is feature["properties"]["_ablepath_exposure_only"] is True for feature in selected)
