"""Regression gates for the Phase 2 truth-sync and hazard quarantine."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from src.citypacks.realdata import (
    RealArtifactContractError,
    load_validated_geometry_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "cities" / "kyoto_kiyomizu"
PREVIEW = PACK / "hazards" / "official" / "landslide_warning_preview.geojson"
PREVIEW_METADATA = (
    PACK / "hazards" / "official" / "landslide_warning_preview.metadata.json"
)
MANIFEST = PACK / "realdata" / "artifact_manifest.v2.json"
PREVIEW_SHA256 = "c9cea5f7b874e829c53c3df40c6479a8aa8869607f2928b5ed436b4113c9ad6f"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_kiyomizu_current_docs_separate_artifact_from_scoped_viewer_connection() -> None:
    """[source_conformance] Artifact facts remain shared while only global truth claims viewer scope."""

    for relative in (
        "README.md",
        "cities/kyoto_kiyomizu/README.md",
        "docs/data/kyoto_kiyomizu/DATA_READINESS.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "2026-08-30T00:00:00Z" in text
        assert "17 ways / 142 nodes" in text
        assert "SOURCE_TRACEABLE_REAL" in text and "VGI" in text
        assert "21 nodes / 19 edges / 2 components" in text
        assert "NOT_ESTABLISHED" in text
        assert "M7_CONNECTED_TO_REAL_EDGES=false" in text
        assert "M6_CONNECTED=false" in text
        assert "KPI_CONNECTED=false" in text
        assert "realdata/artifact_manifest.v2.json" in text
        assert "sources/source_manifest.csv" in text

    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "MAPLIBRE_RUNTIME_IMPLEMENTED=true" in root_readme
    assert "MAPLIBRE_CONNECTED=true" in root_readme
    assert (
        "MAPLIBRE_CONNECTED_SCOPE=KIYOMIZU_EXPLICIT_OPT_IN_CANDIDATE_ONLY"
        in root_readme
    )
    assert "REAL_GEOMETRY_CONNECTED_TO_VIEWER=true" in root_readme
    assert (
        "REAL_GEOMETRY_CONNECTED_TO_VIEWER_SCOPE=KIYOMIZU_CANDIDATE_ONLY"
        in root_readme
    )
    assert "ALL_THREE_CITIES_REAL_GEOMETRY=false" in root_readme
    assert "MODEL_CONNECTED=false" in root_readme

    city_readme = (PACK / "README.md").read_text(encoding="utf-8")
    readiness = (ROOT / "docs/data/kyoto_kiyomizu/DATA_READINESS.md").read_text(
        encoding="utf-8"
    )
    assert "`REAL` | なし" not in city_readme
    assert "snapshot未固定" not in readiness
    assert "corridor geometryは未取得" not in readiness


def test_v1_source_catalogue_points_to_hash_bound_v2_authority_without_reclassification() -> None:
    """[source_conformance] Historical metadata stays VGI_METADATA_ONLY and names the v2 authority."""

    with (PACK / "sources" / "source_manifest.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    row = next(item for item in rows if item["dataset_id"] == "osm_kiyomizu_corridor")
    assert row["source_class"] == "VGI_METADATA_ONLY"
    assert row["evidence_class"] == "VGI_METADATA_ONLY"
    assert row["data_status"] == "VGI_METADATA_ONLY"
    assert row["freshness_status"] == "SUPERSEDED"
    assert row["superseded_by_dataset_id"] == "kiyomizu_osm_named_corridor_20260830"
    record = " ".join(row.values())
    for expected in (
        "realdata/artifact_manifest.v2.json",
        "2026-08-30T00:00:00Z",
        "sources/retained/osm_corridor_20260830.raw.json",
        "3d21ce674776c5c3e37c507c09a9458e062d2d31f5718b3e702313838ef7d2ec",
        "geography/real/corridor.osm.geojson",
        "48b08553a9c2d7f8388bd893e83133287e01ad2efa9326116f5e8d3a31836dc7",
        "Overpass",
        "2026-08-30T13:41:06Z",
        "endpoint=UNKNOWN",
    ):
        assert expected in record


def test_global_viewer_scope_and_city_artifact_scope_are_machine_readable() -> None:
    """[source_conformance] Kiyomizu viewer truth never promotes all-city, model, or real 3D state."""

    global_status = _json(ROOT / "reports" / "COMPLETION_LEVELS.json")
    assert global_status["KIYOMIZU_REAL_ARTIFACT_CAPABILITY"] is True
    assert global_status["KIYOMIZU_CANDIDATE_GRAPH_AVAILABLE"] is True
    assert global_status["REAL_GEOMETRY_ARTIFACTS_AVAILABLE"] == "PARTIAL"
    assert global_status["ALL_THREE_CITIES_REAL_GEOMETRY"] is False
    assert global_status["REAL_GEOMETRY_CONNECTED"] is True
    assert (
        global_status["REAL_GEOMETRY_CONNECTED_SCOPE"]
        == "KIYOMIZU_CANDIDATE_VIEWER_ONLY_NOT_MODEL_PIPELINE"
    )
    assert global_status["REAL_GEOMETRY_CONNECTED_TO_VIEWER"] is True
    assert (
        global_status["REAL_GEOMETRY_CONNECTED_TO_VIEWER_SCOPE"]
        == "KIYOMIZU_CANDIDATE_ONLY"
    )
    assert global_status["REAL_MAP_COMPLETE"] is False
    assert global_status["MAPLIBRE_RUNTIME_IMPLEMENTED"] is True
    assert global_status["MAPLIBRE_CONNECTED"] is True
    assert (
        global_status["MAPLIBRE_CONNECTED_SCOPE"]
        == "KIYOMIZU_EXPLICIT_OPT_IN_CANDIDATE_ONLY"
    )
    assert global_status["KIYOMIZU_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER"] is True
    assert global_status["ALL_THREE_CITIES_MAPLIBRE_CONNECTED"] is False
    assert global_status["CESIUM_RUNTIME_IMPLEMENTED"] is True
    assert global_status["CESIUM_CONNECTED"] is False
    assert global_status["PLATEAU_3D_CONNECTED"] is False
    assert (
        global_status["THREE_D_IMPLEMENTATION"]
        == "RUNTIME_IMPLEMENTED_MOCKED_GATE_REAL_TILESET_NOT_VALIDATED"
    )
    assert global_status["M7_CONNECTED_TO_REAL_EDGES"] is False
    assert global_status["M6_CONNECTED"] is False
    assert global_status["KPI_CONNECTED"] is False
    assert global_status["ADMIN_VALIDATED"] is False
    assert global_status["DEMO_COMPLETE"] is False
    assert global_status["PUBLIC_RELEASE_READY"] is False

    city_status = _json(PACK / "realdata" / "status.json")
    assert city_status["REAL_GEOMETRY_CONNECTED"] is True
    assert (
        city_status["REAL_GEOMETRY_CONNECTED_SCOPE"]
        == "CITYPACK_VALIDATED_ARTIFACT_CAPABILITY"
    )
    # The citypack status is an artifact-capability snapshot, not the authority
    # for the later scoped viewer runtime connection recorded in the global report.
    assert city_status["REAL_GEOMETRY_CONNECTED_TO_VIEWER"] is False


def test_root_attribution_separates_real_vgi_preview_synthetic_and_unknown() -> None:
    """[source_conformance] Attribution records source nature without eligibility overclaim."""

    text = (ROOT / "data" / "ATTRIBUTION.md").read_text(encoding="utf-8")
    for expected in (
        "legacy `data/`",
        "SYNTHETIC_DEMO",
        "SOURCE_TRACEABLE_REAL",
        "© OpenStreetMap contributors",
        "Data available under ODbL 1.0",
        "HUMAN_GATE",
        "出典：京都市防災情報マップ",
        "NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT",
        "UNKNOWN",
    ):
        assert expected in text
    assert "同梱データはすべてSYNTHETIC" not in text


def test_official_hazard_preview_is_machine_readably_quarantined_without_geometry_change() -> None:
    """[source_conformance] Hash-referenced preview bytes remain outside every connectable capability."""

    metadata = _json(PREVIEW_METADATA)
    preview = _json(PREVIEW)
    assert hashlib.sha256(PREVIEW.read_bytes()).hexdigest() == PREVIEW_SHA256
    assert metadata["preview_sha256"] == PREVIEW_SHA256
    assert metadata["capability_status"] == "NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT"
    assert metadata["connection_status"] == metadata["capability_status"]
    assert metadata["trust_status"] == "HASH_REFERENCED_RAW_NOT_IN_TRUST_ROOT"
    assert metadata["analysis_eligible"] is False
    assert metadata["model_eligible"] is False
    assert metadata["viewer_eligible"] is False
    assert metadata["official_closure"] is None
    assert metadata["edge_state_effect"] == "NONE"
    assert metadata["quarantine_scope"] == "ALL_FEATURES_IN_COMPANION_PREVIEW"
    assert metadata["feature_count"] == len(preview["features"])
    assert "source geometry nature" in metadata["data_class_semantics"]
    for item in preview["features"]:
        properties = item["properties"]
        assert properties["city_id"] == metadata["city_id"]
        assert properties["source_id"] == metadata["source_id"]
        assert properties["source_class"] == metadata["source_class"] == "OFFICIAL"
        assert properties["data_class"] == metadata["data_class"] == "REAL"
        assert (
            properties["geometry_status"]
            == metadata["geometry_status"]
            == "SOURCE_TRACEABLE_REAL_PREVIEW"
        )
    assert (
        metadata["data_class_scope"]
        == "SOURCE_GEOMETRY_NATURE_ONLY_NOT_CAPABILITY_ELIGIBILITY"
    )
    assert all(
        item["properties"]["edge_state_effect"] == "NONE"
        and item["properties"]["operation_status"] == "UNKNOWN"
        for item in preview["features"]
    )

    manifest = _json(MANIFEST)
    manifest_paths = {record["artifact_path"] for record in manifest["artifacts"]}
    assert "hazards/official/landslide_warning_preview.geojson" not in manifest_paths
    capability = load_validated_geometry_manifest(
        MANIFEST, trusted_root=PACK, expected_city_id="kyoto_kiyomizu"
    )
    with pytest.raises(RealArtifactContractError, match="not validated connectable"):
        capability.records_for("kiyomizu-official-landslide-preview-20260830")
    with pytest.raises(RealArtifactContractError, match="unresolved source_id"):
        capability.artifact_index.sources_for(metadata["source_id"])


def test_report_authority_and_public_release_gate_are_current() -> None:
    """[target_validation] Current evidence and historical snapshots cannot be confused."""

    authority = (ROOT / "reports" / "REPORT_AUTHORITY.md").read_text(encoding="utf-8")
    for heading in (
        "CURRENT_AUTHORITATIVE",
        "HISTORICAL_SNAPSHOT",
        "CURRENT_BUT_PUBLICLY_BLOCKED",
    ):
        assert heading in authority
    for expected in (
        "reports/PHASE2_AUTONOMOUS_REALDATA_REPORT.md",
        "reports/PHASE3_MAP_UI_STATUS.md",
        "PR #2",
        "33330312591",
        "PR #3",
        "RELEASE_MANIFEST.json",
        "cities/kyoto_kiyomizu/realdata/artifact_manifest.v2.json",
        "cities/kyoto_kiyomizu/realdata/status.json",
    ):
        assert expected in authority
    public_gate = (ROOT / "reports" / "PUBLIC_RELEASE_GATE.md").read_text(
        encoding="utf-8"
    )
    assert "PUBLIC_RELEASE_READY=false" in public_gate
    assert "SERVER_SIDE_BRANCH_PROTECTION=false" in public_gate


def test_readme_declares_full_suite_prerequisites_and_preserves_safety_language() -> None:
    """[software_correctness] Full-suite instructions expose pwsh/UI prerequisites and UNKNOWN safety."""

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for expected in ("Git", "Python", "PowerShell 7", "`pwsh`", "Node", "npm", "Playwright"):
        assert expected in readme
    assert "minimal Linux" in readme
    assert "local-main-guard" in readme
    assert "UNKNOWNをPASS" in readme
    assert "UNKNOWN→OPEN" not in readme
    assert "安全な避難ルートを提供" not in readme
