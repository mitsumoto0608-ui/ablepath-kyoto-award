"""Fail-closed adapters for the three retained source-manifest v1 dialects.

The overnight city lanes were authored independently and have different CSV
headers.  This module preserves every raw field while exposing a small common
truth vocabulary.  Dialect selection is by an exact, versioned header; there is
no city-name fallback and no implicit promotion to REAL.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


MAX_MANIFEST_BYTES = 2_000_000
MAX_MANIFEST_ROWS = 5_000
MAX_FIELD_CHARS = 20_000

KIYOMIZU_V1_FIELDS = tuple(
    "dataset_id,title,issuing_organization,source_class,evidence_class,source_url,"
    "published_or_updated_at,accessed_at,valid_as_of,freshness_status,"
    "supersedes_dataset_id,superseded_by_dataset_id,recheck_by,retrieval_etag,"
    "retrieval_last_modified,redistribution_status,version,download_status,file_name,"
    "local_path,sha256,license,format,source_crs,vertical_datum,axis_order,"
    "horizontal_unit,vertical_unit,geographic_coverage,usable_fields,missing_fields,"
    "interpretation_limits,geometry_status,data_status,source_feature_id,lineage".split(",")
)
ARASHIYAMA_V1_FIELDS = tuple(
    "dataset_id,title,issuing_organization,record_kind,data_class,source_url,"
    "published_or_updated_at,accessed_at,valid_as_of,freshness_status,"
    "supersedes_dataset_id,superseded_by_dataset_id,recheck_by,retrieval_etag,"
    "retrieval_last_modified,redistribution_status,download_status,format,source_crs,"
    "vertical_datum,geographic_coverage,usable_fields,missing_fields,"
    "interpretation_limits,artifact_schema_version,spec_reference,license_or_terms,"
    "local_path,sha256".split(",")
)
FUJISAWA_V1_FIELDS = tuple(
    "dataset_id,title,publisher,url,source_class,accessed_at,published_updated_date,"
    "version_year_spec,license_terms,format,crs,vertical_datum,download_status,"
    "local_relative_path,sha256,geographic_coverage,usable_fields,missing_fields,"
    "interpretation_limits,valid_as_of,freshness_status,supersedes_dataset_id,"
    "superseded_by_dataset_id,recheck_by,retrieval_etag,retrieval_last_modified,"
    "redistribution_status,geometry_use,notes,schema_version,source_feature_id,"
    "stable_feature_id,revision_id,lineage,source_crs,processing_crs,output_crs,"
    "horizontal_unit,vertical_unit,axis_order,coordinate_precision,transform_history,"
    "geometry_status,operation_status".split(",")
)

_FRESHNESS = {
    "CURRENT_CONFIRMED",
    "CURRENT_UNVERIFIED",
    "POSSIBLY_STALE",
    "SUPERSEDED",
    "UNKNOWN",
}
_METADATA_CLASS_TO_KIND = {
    "OFFICIAL_METADATA_ONLY": "OFFICIAL_METADATA",
    "VGI_METADATA_ONLY": "VGI_METADATA",
}
_RECORD_KINDS = {"OFFICIAL_METADATA", "VGI_METADATA"}


class SourceManifestContractError(ValueError):
    """Raised when a manifest cannot be normalized without guessing."""


@dataclass(frozen=True, slots=True)
class NormalizedSourceRecord:
    schema_version: str
    dialect_id: str
    dataset_id: str
    record_kind: str
    data_class: str
    source_url: str
    freshness_status: str
    download_status: str
    raw: Mapping[str, str]


def _required_text(row: Mapping[str, str], field: str, dialect_id: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise SourceManifestContractError(f"{dialect_id}.{field} must be non-empty text")
    if len(value) > MAX_FIELD_CHARS:
        raise SourceManifestContractError(f"{dialect_id}.{field} exceeds the field-size limit")
    return value


def _normalize_row(dialect_id: str, row: dict[str, str]) -> NormalizedSourceRecord:
    if any(value is None or len(value) > MAX_FIELD_CHARS for value in row.values()):
        raise SourceManifestContractError(f"{dialect_id} contains a malformed or oversized field")
    if dialect_id == "kiyomizu-v1.0.0":
        data_class = _required_text(row, "source_class", dialect_id)
        if row["evidence_class"] != data_class or row["data_status"] != data_class:
            raise SourceManifestContractError(
                "kiyomizu-v1.0.0 truth fields must agree; implicit class conversion is forbidden"
            )
        source_url = _required_text(row, "source_url", dialect_id)
        record_kind = _METADATA_CLASS_TO_KIND.get(data_class, "")
    elif dialect_id == "arashiyama-v1.0.0":
        if row["artifact_schema_version"] != "1.0.0":
            raise SourceManifestContractError("unsupported Arashiyama manifest schema major")
        data_class = _required_text(row, "data_class", dialect_id)
        record_kind = _required_text(row, "record_kind", dialect_id)
        source_url = _required_text(row, "source_url", dialect_id)
    elif dialect_id == "fujisawa-v1.0.0":
        if row["schema_version"] != "1.0.0":
            raise SourceManifestContractError("unsupported Fujisawa manifest schema major")
        data_class = _required_text(row, "source_class", dialect_id)
        source_url = _required_text(row, "url", dialect_id)
        record_kind = _METADATA_CLASS_TO_KIND.get(data_class, "")
    else:  # pragma: no cover - internal call guard
        raise SourceManifestContractError(f"unsupported source-manifest dialect: {dialect_id}")
    expected_kind = _METADATA_CLASS_TO_KIND.get(data_class)
    if expected_kind is None:
        raise SourceManifestContractError(
            f"unsupported metadata-only data_class: {data_class}"
        )
    if record_kind not in _RECORD_KINDS:
        raise SourceManifestContractError(f"unsupported record_kind: {record_kind}")
    if record_kind != expected_kind:
        raise SourceManifestContractError(
            f"record_kind {record_kind} contradicts data_class {data_class}"
        )
    if not source_url.startswith("https://"):
        raise SourceManifestContractError("source_url must use HTTPS")
    freshness = _required_text(row, "freshness_status", dialect_id)
    if freshness not in _FRESHNESS:
        raise SourceManifestContractError(f"unsupported freshness_status: {freshness}")
    return NormalizedSourceRecord(
        schema_version="1.0.0",
        dialect_id=dialect_id,
        dataset_id=_required_text(row, "dataset_id", dialect_id),
        record_kind=record_kind,
        data_class=data_class,
        source_url=source_url,
        freshness_status=freshness,
        download_status=_required_text(row, "download_status", dialect_id),
        raw=MappingProxyType(dict(row)),
    )


def load_source_manifest(path: str | Path) -> tuple[NormalizedSourceRecord, ...]:
    """Load an exact known v1 dialect and return immutable normalized records."""
    manifest = Path(path)
    if manifest.is_symlink() or not manifest.is_file():
        raise SourceManifestContractError("source manifest must be a regular non-symlink file")
    size = manifest.stat().st_size
    if size <= 0 or size > MAX_MANIFEST_BYTES:
        raise SourceManifestContractError("source manifest is empty or exceeds the size limit")
    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = tuple(reader.fieldnames or ())
        if len(header) != len(set(header)):
            raise SourceManifestContractError("source manifest contains duplicate header fields")
        dialect_by_header = {
            KIYOMIZU_V1_FIELDS: "kiyomizu-v1.0.0",
            ARASHIYAMA_V1_FIELDS: "arashiyama-v1.0.0",
            FUJISAWA_V1_FIELDS: "fujisawa-v1.0.0",
        }
        dialect_id = dialect_by_header.get(header)
        if dialect_id is None:
            raise SourceManifestContractError(
                "unsupported source-manifest header; record an explicit migration"
            )
        rows: list[NormalizedSourceRecord] = []
        seen_ids: set[str] = set()
        for raw in reader:
            if len(rows) >= MAX_MANIFEST_ROWS:
                raise SourceManifestContractError("source manifest exceeds the row-count limit")
            if None in raw:
                raise SourceManifestContractError("source manifest row has extra columns")
            record = _normalize_row(dialect_id, raw)
            if record.dataset_id in seen_ids:
                raise SourceManifestContractError(
                    f"duplicate source dataset_id: {record.dataset_id}"
                )
            seen_ids.add(record.dataset_id)
            rows.append(record)
    if not rows:
        raise SourceManifestContractError("source manifest must contain at least one row")
    return tuple(rows)
