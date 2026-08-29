import csv
import json
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "inputs" / "staging" / "kyoto-kiyomizu-v0"
MANIFEST = STAGING / "source_manifest.csv"
GAPS = STAGING / "data_gap_register.csv"
ACQUISITION_LOG = STAGING / "acquisition_log.csv"
SCHEMA = ROOT / "schemas" / "source_manifest.schema.json"
DOC = ROOT / "docs" / "data" / "KYOTO_OFFICIAL_DATA_STAGING.md"

EXPECTED_COLUMNS = [
    "dataset_id", "title", "issuing_organization", "source_class", "source_url",
    "published_or_updated_at", "accessed_at", "version", "download_status",
    "file_name", "local_path", "sha256", "license", "format", "horizontal_crs",
    "vertical_datum", "geographic_coverage", "official_status", "usable_fields",
    "missing_fields", "notes", "downloaded_at", "file_hash",
    "vertical_crs_or_datum", "coordinate_epoch", "axis_order", "horizontal_unit",
    "vertical_unit", "transformation_method",
]

DOWNLOAD_STATUSES = {
    "DOWNLOADED", "METADATA_ONLY", "BLOCKED", "NOT_FOUND", "REQUIRES_APPLICATION"
}
OFFICIAL_STATUSES = {
    "OFFICIAL_PUBLISHED", "OFFICIAL_CONFIRMATION_REQUIRED", "VGI_NON_OFFICIAL", "UNKNOWN"
}


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        return reader.fieldnames, list(reader)


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest_rows() -> list[dict[str, str]]:
    return _read_csv(MANIFEST)[1]


def _constraint_errors(field: str, value: object, constraints: dict) -> list[str]:
    errors: list[str] = []
    if constraints.get("type") == "string" and not isinstance(value, str):
        return [f"{field}:type"]
    if not isinstance(value, str):
        return errors
    if "enum" in constraints and value not in constraints["enum"]:
        errors.append(f"{field}:enum")
    # JSON Schema ``pattern`` uses search semantics rather than implicit full-match.
    if "pattern" in constraints and re.search(constraints["pattern"], value) is None:
        errors.append(f"{field}:pattern")
    if len(value) < constraints.get("minLength", 0):
        errors.append(f"{field}:minLength")
    if "maxLength" in constraints and len(value) > constraints["maxLength"]:
        errors.append(f"{field}:maxLength")
    return errors


def _row_errors(row: dict[str, str], schema: dict) -> list[str]:
    errors: list[str] = []
    required = schema["required"]
    for field in required:
        if field not in row:
            errors.append(f"{field}:missing")
    if schema["additionalProperties"] is False:
        for field in set(row) - set(schema["properties"]):
            errors.append(f"{field}:additional")
    for field, constraints in schema["properties"].items():
        if field in row:
            errors.extend(_constraint_errors(field, row[field], constraints))

    conditional = schema["allOf"][0]
    branch = "then" if row.get("download_status") == "DOWNLOADED" else "else"
    for field, constraints in conditional[branch]["properties"].items():
        errors.extend(_constraint_errors(field, row.get(field), constraints))
    return errors


def _assert_calendar_date(value: str, *, unknown_allowed: bool) -> None:
    if unknown_allowed and value == "UNKNOWN":
        return
    date.fromisoformat(value)


def test_schema_metadata_and_csv_header_are_exact(schema: dict) -> None:
    """[software_correctness] Schema metadata and the exact 29-column CSV contract stay aligned."""
    header, _ = _read_csv(MANIFEST)

    assert header == EXPECTED_COLUMNS
    assert schema["required"] == EXPECTED_COLUMNS
    assert set(schema["properties"]) == set(EXPECTED_COLUMNS)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"].endswith("/source_manifest.schema.json")
    assert "official and VGI metadata staging" in schema["title"]
    assert "does not authorize raw-data use" in schema["description"]
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert len(schema["allOf"]) == 1
    assert {"if", "then", "else"} == set(schema["allOf"][0])


def test_every_manifest_row_satisfies_properties_enums_dates_and_allof(
    manifest_rows: list[dict[str, str]], schema: dict
) -> None:
    """[source_conformance] Every real row satisfies property and download-branch constraints."""
    assert len(manifest_rows) == 23
    assert len({row["dataset_id"] for row in manifest_rows}) == 23
    for row in manifest_rows:
        assert _row_errors(row, schema) == [], row["dataset_id"]
        _assert_calendar_date(row["published_or_updated_at"], unknown_allowed=True)
        _assert_calendar_date(row["accessed_at"], unknown_allowed=False)
        if row["downloaded_at"]:
            datetime.fromisoformat(row["downloaded_at"].replace("Z", "+00:00"))
        assert row["download_status"] in DOWNLOAD_STATUSES
        assert row["official_status"] in OFFICIAL_STATUSES
        assert row["source_class"] in {"OFFICIAL", "VGI"}
        assert all(value == value.strip() for value in row.values())


def test_in_memory_downloaded_and_non_downloaded_contract_is_bidirectional(
    manifest_rows: list[dict[str, str]], schema: dict
) -> None:
    """[software_correctness] Synthetic rows prove both allOf branches accept and reject correctly."""
    digest = "a" * 64
    downloaded = dict(manifest_rows[0])
    downloaded.update(
        download_status="DOWNLOADED",
        file_name="source.zip",
        local_path="DROPBOX_CONFIGURED_PATH/source.zip",
        sha256=digest,
        downloaded_at="2026-08-30T12:34:56+09:00",
        file_hash=f"sha256:{digest}",
    )
    assert _row_errors(downloaded, schema) == []

    missing_hash = dict(downloaded, sha256="", file_hash="")
    assert {error.split(":", 1)[0] for error in _row_errors(missing_hash, schema)} >= {
        "sha256", "file_hash"
    }

    metadata_only = dict(manifest_rows[0], download_status="METADATA_ONLY")
    assert _row_errors(metadata_only, schema) == []
    false_download = dict(metadata_only, sha256=digest, file_hash=f"sha256:{digest}")
    assert {error.split(":", 1)[0] for error in _row_errors(false_download, schema)} >= {
        "sha256", "file_hash"
    }


def test_status_counts_do_not_claim_a_download(manifest_rows: list[dict[str, str]]) -> None:
    """[source_conformance] Corrected inventory has 20 metadata rows and zero downloaded rows."""
    counts = Counter(row["download_status"] for row in manifest_rows)
    assert counts == Counter(
        {"METADATA_ONLY": 20, "BLOCKED": 1, "NOT_FOUND": 1, "REQUIRES_APPLICATION": 1}
    )
    assert counts["DOWNLOADED"] == 0
    for row in manifest_rows:
        assert row["downloaded_at"] == ""
        assert row["sha256"] == ""
        assert row["file_hash"] == ""
        assert row["file_name"] == ""
        assert row["local_path"] == ""


def test_corrected_official_metadata_is_exact(manifest_rows: list[dict[str, str]]) -> None:
    """[source_conformance] API and official-page corrections are frozen without claiming raw files."""
    by_id = {row["dataset_id"]: row for row in manifest_rows}
    plateau = by_id["plateau_kyoto_2025_release"]
    assert plateau["download_status"] == "METADATA_ONLY"
    assert plateau["version"] == "2025年度版spec 5.0"
    assert plateau["source_url"].endswith("/26100_kyoto-shi_city_2025_citygml_1_op.zip")
    assert "city_code=26100" in plateau["usable_fields"]
    assert "file_size=2700713500" in plateau["usable_fields"]

    toilet = by_id["kyoto_public_toilets_open_data"]
    assert toilet["published_or_updated_at"] == "2026-03-06"
    assert toilet["format"] == "XLSX"
    shelters = by_id["kyoto_designated_emergency_places"]
    assert shelters["published_or_updated_at"] == "2026-08-28"


def test_important_unknowns_and_negative_safety_phrases_are_exact(
    manifest_rows: list[dict[str, str]]
) -> None:
    """[source_conformance] Unknown coordinate/operation facts and explicit prohibitions remain visible."""
    by_id = {row["dataset_id"]: row for row in manifest_rows}
    assert by_id["plateau_kyoto_2023_3dtiles_mvt"]["horizontal_crs"] == "UNKNOWN"
    for dataset_id in (
        "kyoto_web_hazard_flood", "kyoto_web_hazard_inland",
        "kyoto_web_hazard_landslide", "kyoto_web_hazard_earthquake",
    ):
        row = by_id[dataset_id]
        assert row["published_or_updated_at"] == "UNKNOWN"
        assert row["version"] == "UNKNOWN"
        assert "CLOSED" in row["notes"] and "決定しない" in row["notes"]

    capacity = by_id["kyoto_emergency_plaza_capacity_operation"]
    assert capacity["issuing_organization"] == "京都市行財政局防災危機管理室"
    assert capacity["version"] == "UNKNOWN"
    assert "facility manager" in capacity["missing_fields"]
    assert "容量を算出せず" in capacity["notes"]

    assert all(row["vertical_crs_or_datum"] == "UNKNOWN" for row in manifest_rows)
    assert all(row["coordinate_epoch"] == "UNKNOWN" for row in manifest_rows)
    assert all(row["axis_order"] == "UNKNOWN" for row in manifest_rows)
    assert all(row["transformation_method"] == "UNKNOWN" for row in manifest_rows)


def test_osm_is_vgi_xml_and_pbf_is_missing(manifest_rows: list[dict[str, str]]) -> None:
    """[source_conformance] Only the observed OSM XML export is represented; PBF stays missing."""
    osm = next(row for row in manifest_rows if row["dataset_id"] == "osm_kiyomizu_corridor")
    assert osm["source_class"] == "VGI"
    assert osm["official_status"] == "VGI_NON_OFFICIAL"
    assert osm["license"] == "ODbL 1.0"
    assert osm["format"] == "OSM XML"
    assert "PBF" in osm["missing_fields"]
    assert "PASS" in osm["notes"]


def test_gap_register_is_complete_and_references_manifest_ids(
    manifest_rows: list[dict[str, str]]
) -> None:
    """[target_validation] Gap IDs, enums, actions and evidence references are auditable."""
    header, rows = _read_csv(GAPS)
    expected_header = [
        "gap_id", "category", "required_dataset_or_fact", "impact", "severity",
        "status", "owner", "next_action", "evidence",
    ]
    assert header == expected_header
    assert len(rows) == 12
    assert len({row["gap_id"] for row in rows}) == len(rows)
    manifest_ids = {row["dataset_id"] for row in manifest_rows}
    for row in rows:
        assert re.fullmatch(r"GAP-[0-9]{3}", row["gap_id"])
        assert all(row[field].strip() for field in expected_header)
        assert row["severity"] in {"BLOCKER", "HIGH", "MEDIUM", "LOW"}
        assert row["status"] in {"OPEN", "BLOCKED", "REQUIRES_APPLICATION"}
        assert row["owner"] in {"HUMAN", "DATA", "FIELD"}
        assert set(row["evidence"].split(";")) <= manifest_ids | {"ALL"}


def test_acquisition_log_is_complete_and_references_manifest_ids(
    manifest_rows: list[dict[str, str]]
) -> None:
    """[software_correctness] Acquisition records have unique keys, enums and valid dataset references."""
    header, rows = _read_csv(ACQUISITION_LOG)
    expected_header = [
        "attempted_at", "dataset_id", "action", "result", "status",
        "http_or_tool_detail", "next_action",
    ]
    assert header == expected_header
    assert rows
    manifest_ids = {row["dataset_id"] for row in manifest_rows}
    keys = set()
    for row in rows:
        assert all(row[field].strip() for field in expected_header)
        datetime.fromisoformat(row["attempted_at"])
        assert row["dataset_id"] in manifest_ids | {"ALL"}
        assert row["status"] in DOWNLOAD_STATUSES
        key = (row["attempted_at"], row["dataset_id"], row["action"])
        assert key not in keys
        keys.add(key)
    assert not any(row["status"] == "DOWNLOADED" for row in rows)


def test_docs_and_staging_contain_no_raw_data() -> None:
    """[software_correctness] Documentation and exact folder contents agree that no raw file exists."""
    doc = DOC.read_text(encoding="utf-8")
    staging_readme = (STAGING / "README.md").read_text(encoding="utf-8")
    assert "`DOWNLOADED=0`" in doc
    assert "`download_status=DOWNLOADED` は0件" in staging_readme
    assert "京都市道路台帳平面図" in staging_readme
    assert {path.name for path in STAGING.iterdir() if path.is_file()} == {
        "README.md", "source_manifest.csv", "data_gap_register.csv", "acquisition_log.csv"
    }
