"""Acceptance tests for the A31b provenance-resolution trust root."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


ROOT = Path(__file__).resolve().parents[3]
STAGING = ROOT / "inputs" / "staging" / "ARA-A31B-PROVENANCE-RESOLUTION-V1"
PACK = ROOT / "cities" / "kyoto_arashiyama"
ARCHIVE = STAGING / "A31b-25_10_5235_GEOJSON.zip"
EXPECTED_ARCHIVE_SHA256 = "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c"
EXPECTED_ARCHIVE_SIZE = 55_502_814
EXPECTED_MEMBER = "20_想定最大規模/A31b-20-25_10_5235.geojson"
EXPECTED_MEMBER_SHA256 = "d1c2d03734fed6471e20da7e1285084dbedc46195525dd791068ed584adbdc52"
EXPECTED_METADATA_MEMBER = "メタデータ/KS-META-A31b-25_10_5235.xml"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portable_member_index(source: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    """Index members by POSIX-style names and reject separator aliases."""

    members: dict[str, zipfile.ZipInfo] = {}
    for member in source.infolist():
        portable_name = member.filename.replace("\\", "/")
        assert portable_name not in members, (
            f"ambiguous ZIP members normalize to {portable_name!r}"
        )
        members[portable_name] = member
    return members


def test_a31b_staging_archive_is_the_exact_official_download() -> None:
    """[source_conformance] Trust-root and portable member IDs match the official archive."""

    assert ARCHIVE.stat().st_size == EXPECTED_ARCHIVE_SIZE
    assert _sha256(ARCHIVE) == EXPECTED_ARCHIVE_SHA256
    with zipfile.ZipFile(ARCHIVE) as source:
        members = _portable_member_index(source)
        assert EXPECTED_MEMBER in members
        assert EXPECTED_METADATA_MEMBER in members
        assert all(not PurePosixPath(name).is_absolute() for name in members)
        assert all(".." not in PurePosixPath(name).parts for name in members)
        digest = hashlib.sha256()
        with source.open(members[EXPECTED_MEMBER]) as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        assert digest.hexdigest() == EXPECTED_MEMBER_SHA256
        with source.open(members[EXPECTED_MEMBER]) as handle:
            assert b'"name": "urn:ogc:def:crs:EPSG::6668"' in handle.read(512)
        metadata = source.read(members[EXPECTED_METADATA_MEMBER]).decode("shift_jis")
        assert "JGD2011 / (B,L)" in metadata
        assert "2026-03-06" in metadata


def test_a31b_staging_contract_records_source_license_crs_and_lineage() -> None:
    """[source_conformance] Staging metadata binds source URL, hash, license review, CRS, and lineage without capability promotion."""

    assert (STAGING / "TASK_INPUT_README.md").is_file()
    with (STAGING / "source_manifest.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    row = rows[0]
    assert row["source_url"] == "https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip"
    assert row["catalog_url"] == "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-A31b-2025.html"
    assert row["sha256"] == EXPECTED_ARCHIVE_SHA256
    assert row["source_archive_member"] == EXPECTED_MEMBER
    assert row["source_member_sha256"] == EXPECTED_MEMBER_SHA256
    assert row["metadata_archive_member"] == EXPECTED_METADATA_MEMBER
    assert row["source_crs"] == "EPSG:6668"
    assert row["output_crs"] == "EPSG:4326"
    assert row["license"] == "CC_BY_4.0"
    assert row["license_review_status"] == "AGENT_REVIEWED_HUMAN_PENDING"
    assert row["geometry_status"] == "PREPARED_NOT_CONNECTED"
    assert row["connection_status"] == "NOT_CONNECTED"


def test_a31b_resolution_preserves_unknown_and_non_connection_truth() -> None:
    """[software_correctness] Reverified source bytes do not create closure, passage, model, or viewer truth."""

    status = json.loads((PACK / "realdata_status.json").read_text(encoding="utf-8"))
    assert status["OFFICIAL_HAZARD_GEOMETRY_CONNECTED"] is False
    assert status["MODEL_CONNECTED"] is False
    assert status["REAL_GEOMETRY_CONNECTED_TO_VIEWER"] is False
    overlap_path = PACK / "hazards" / "edge_hazard_overlap.real.csv"
    with overlap_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert all(row["scenario_state"] == "UNKNOWN" for row in rows)
    assert all(row["official_closure"] == "" for row in rows)
    assert all(row["official_closure_reason"] for row in rows)
