"""Additive Phase 2 contracts for source-traceable geospatial artifacts.

This module does not change the three legacy metadata-only source-manifest
dialects.  ``REAL`` means only that geometry is traceable to a retained source;
it does not mean official, administratively validated, safe, or passable.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import json
import math
from numbers import Real
from pathlib import Path, PurePosixPath
import re
import stat
from types import MappingProxyType
from typing import Any, Mapping
from urllib.parse import urlsplit


REAL_ARTIFACT_SCHEMA_VERSION = "2.0.0"
MAX_REAL_ARTIFACT_MANIFEST_BYTES = 5_000_000
MAX_REAL_ARTIFACT_RECORDS = 100_000
MAX_TEXT_CHARS = 20_000
MAX_NORMALIZED_ARTIFACT_BYTES = 100_000_000
MAX_SOURCE_ARTIFACT_BYTES = 250_000_000
MAX_RETRIEVAL_QUERY_BYTES = 5_000_000

REAL_ARTIFACT_V2_FIELDS = (
    "city_id",
    "artifact_id",
    "artifact_path",
    "artifact_role",
    "source_id",
    "source_url",
    "source_reference",
    "source_class",
    "data_class",
    "accessed_at",
    "valid_as_of",
    "valid_as_of_reason",
    "license",
    "license_terms_url",
    "license_review_status",
    "redistribution_status",
    "redistribution_obligations",
    "sha256",
    "source_artifact_path",
    "source_sha256",
    "retrieval_method",
    "retrieval_query_path",
    "retrieval_query_sha256",
    "snapshot_at",
    "snapshot_reason",
    "source_revision",
    "source_crs",
    "processing_crs",
    "output_crs",
    "axis_order",
    "horizontal_unit",
    "vertical_datum",
    "vertical_datum_reason",
    "transform_history",
    "source_feature_id",
    "stable_feature_id",
    "revision_id",
    "lineage",
    "geometry_status",
)

_SOURCE_CLASSES = {"OFFICIAL", "VGI", "MODEL", "SYNTHETIC"}
_DATA_CLASSES_BY_SOURCE = {
    "OFFICIAL": {"REAL", "OFFICIAL_METADATA_ONLY", "OFFICIAL_OPERATION_RECORD", "UNKNOWN"},
    "VGI": {"REAL", "VGI_METADATA_ONLY", "UNKNOWN"},
    "MODEL": {"MODEL_DERIVED", "UNKNOWN"},
    "SYNTHETIC": {"SYNTHETIC_DEMO", "UNKNOWN"},
}
_GEOMETRY_BY_DATA = {
    "REAL": {"SOURCE_TRACEABLE_REAL", "QUARANTINED_INVALID"},
    "OFFICIAL_METADATA_ONLY": {"METADATA_ONLY", "UNKNOWN"},
    "VGI_METADATA_ONLY": {"METADATA_ONLY", "UNKNOWN"},
    "MODEL_DERIVED": {"MODEL_DERIVED", "QUARANTINED_INVALID"},
    "SYNTHETIC_DEMO": {"SYNTHETIC_DEMO", "QUARANTINED_INVALID"},
    "UNKNOWN": {"UNKNOWN", "QUARANTINED_INVALID"},
    "OFFICIAL_OPERATION_RECORD": {"NOT_APPLICABLE"},
}
_REDISTRIBUTION = {"PERMITTED_WITH_OBLIGATIONS", "PROHIBITED", "UNKNOWN"}
_ARTIFACT_ROLES = {
    "CORRIDOR_GEOMETRY",
    "OFFICIAL_HAZARD_GEOMETRY",
    "OFFICIAL_OPERATION_RECORD",
    "MODEL_OUTPUT",
    "SYNTHETIC_FIXTURE",
}
_LICENSE_REVIEW = {
    "AGENT_REVIEWED_HUMAN_PENDING",
    "HUMAN_REVIEWED",
    "UNREVIEWED",
}
_UNRESOLVED_LICENSE_TOKENS = {
    "unknown",
    "tbd",
    "review_required",
    "unverified",
    "n/a",
    "none",
    "unspecified",
}
_RETRIEVAL_METHODS = {
    "BOUNDED_QUERY",
    "OFFICIAL_DOWNLOAD",
    "METADATA_CAPTURE",
    "MODEL_COMPUTATION",
    "SYNTHETIC_FIXTURE",
}
_AXIS_ORDERS = {"longitude_latitude", "easting_northing"}
_HORIZONTAL_UNITS = {"degree", "metre"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_SNAPSHOT = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
_FEATURE_KEYS = {"type", "id", "geometry", "properties"}
_FEATURE_LINEAGE_KEYS = {
    "city_id",
    "artifact_id",
    "source_id",
    "source_class",
    "data_class",
    "source_feature_id",
    "stable_feature_id",
    "revision_id",
    "lineage",
    "geometry_status",
}
_CORRIDOR_FEATURE_PROPERTIES = {
    "bridge",
    "bridge_reason",
    "tunnel",
    "tunnel_reason",
    "layer",
    "layer_reason",
    "level",
    "level_reason",
}
_HAZARD_FEATURE_PROPERTIES = {
    "hazard_type",
    "hazard_category",
    "hazard_category_reason",
    "hazard_value",
    "hazard_value_unit",
    "hazard_value_reason",
}
_ALLOWED_FEATURE_PROPERTIES = (
    _FEATURE_LINEAGE_KEYS | _CORRIDOR_FEATURE_PROPERTIES | _HAZARD_FEATURE_PROPERTIES
)


class RealArtifactContractError(ValueError):
    """Raised when a Phase 2 artifact cannot be trusted without guessing."""


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RealArtifactContractError(f"{name} must be non-empty text")
    if len(value) > MAX_TEXT_CHARS or any(ord(character) < 32 for character in value):
        raise RealArtifactContractError(f"{name} is oversized or contains control characters")
    return value


def _text_tuple(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise RealArtifactContractError(f"{name} must be a non-empty text list")
    items = tuple(_text(item, f"{name}[]") for item in value)
    if len(items) != len(set(items)):
        raise RealArtifactContractError(f"{name} must not contain duplicate entries")
    return items


def _iso_date(value: object, name: str) -> str:
    text = _text(value, name)
    if not _DATE.fullmatch(text):
        raise RealArtifactContractError(f"{name} must use YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(text)
    except ValueError as error:
        raise RealArtifactContractError(f"{name} must be a real calendar date") from error
    if parsed.isoformat() != text:
        raise RealArtifactContractError(f"{name} must use canonical ISO date text")
    return text


def _utc_second(value: object, name: str) -> str:
    text = _text(value, name)
    if not _SNAPSHOT.fullmatch(text):
        raise RealArtifactContractError(
            f"{name} must use canonical UTC second text"
        )
    try:
        parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise RealArtifactContractError(
            f"{name} must be a real UTC calendar timestamp"
        ) from error
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != text:
        raise RealArtifactContractError(
            f"{name} must use canonical UTC second text"
        )
    return text


def _https_url(value: object, name: str = "source_url") -> str:
    source_url = _text(value, name)
    parsed = urlsplit(source_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise RealArtifactContractError(f"{name} must be an HTTPS URL without credentials")
    return source_url


def _optional_text_with_reason(
    value: object, reason: object, name: str
) -> tuple[str | None, str | None]:
    if value is None:
        return None, _text(reason, f"{name}_reason")
    if reason is not None:
        raise RealArtifactContractError(f"{name}_reason must be null when {name} is known")
    return _text(value, name), None


def _repo_relative_path(value: object, name: str) -> str:
    text = _text(value, name)
    if "\\" in text:
        raise RealArtifactContractError(f"{name} must use repository-relative POSIX syntax")
    path = PurePosixPath(text)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise RealArtifactContractError(f"{name} must be a contained repository-relative path")
    return text


def _optional_repo_relative_path(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _repo_relative_path(value, name)


@dataclass(frozen=True, slots=True)
class RealArtifactLineage:
    """Immutable exact provenance for one source feature in a versioned artifact."""

    city_id: str
    artifact_id: str
    artifact_path: str
    artifact_role: str
    source_id: str
    source_url: str | None
    source_reference: str | None
    source_class: str
    data_class: str
    accessed_at: str
    valid_as_of: str | None
    valid_as_of_reason: str | None
    license: str
    license_terms_url: str | None
    license_review_status: str
    redistribution_status: str
    redistribution_obligations: tuple[str, ...]
    sha256: str
    source_artifact_path: str
    source_sha256: str
    retrieval_method: str
    retrieval_query_path: str | None
    retrieval_query_sha256: str | None
    snapshot_at: str | None
    snapshot_reason: str | None
    source_revision: str
    source_crs: str
    processing_crs: str
    output_crs: str
    axis_order: str
    horizontal_unit: str
    vertical_datum: str | None
    vertical_datum_reason: str | None
    transform_history: tuple[str, ...]
    source_feature_id: str
    stable_feature_id: str
    revision_id: str
    lineage: tuple[str, ...]
    geometry_status: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "RealArtifactLineage":
        """Validate exact fields and preserve source/data/geometry axes separately."""
        if not isinstance(value, Mapping):
            raise RealArtifactContractError("real artifact lineage must be a mapping")
        keys = set(value)
        expected = set(REAL_ARTIFACT_V2_FIELDS)
        if keys != expected:
            raise RealArtifactContractError(
                "real artifact lineage keys must be exact: "
                f"missing={sorted(expected - keys)}, extra={sorted(keys - expected)}"
            )

        source_class = _text(value["source_class"], "source_class")
        data_class = _text(value["data_class"], "data_class")
        geometry_status = _text(value["geometry_status"], "geometry_status")
        artifact_role = _text(value["artifact_role"], "artifact_role")
        if source_class not in _SOURCE_CLASSES:
            raise RealArtifactContractError(f"unsupported source_class: {source_class}")
        if artifact_role not in _ARTIFACT_ROLES:
            raise RealArtifactContractError(f"unsupported artifact_role: {artifact_role}")
        if data_class not in _DATA_CLASSES_BY_SOURCE[source_class]:
            raise RealArtifactContractError(
                f"source_class {source_class} contradicts data_class {data_class}"
            )
        if geometry_status not in _GEOMETRY_BY_DATA[data_class]:
            raise RealArtifactContractError(
                f"source_class {source_class} / data_class {data_class} contradicts "
                f"geometry_status {geometry_status}"
            )
        if artifact_role == "OFFICIAL_HAZARD_GEOMETRY" and source_class != "OFFICIAL":
            raise RealArtifactContractError("official hazard geometry requires OFFICIAL source_class")
        if artifact_role == "OFFICIAL_OPERATION_RECORD" and (
            source_class != "OFFICIAL" or data_class != "OFFICIAL_OPERATION_RECORD"
        ):
            raise RealArtifactContractError("official operation role requires an OFFICIAL operation record")
        if artifact_role == "MODEL_OUTPUT" and source_class != "MODEL":
            raise RealArtifactContractError("model output role requires MODEL source_class")
        if artifact_role == "SYNTHETIC_FIXTURE" and source_class != "SYNTHETIC":
            raise RealArtifactContractError("synthetic fixture role requires SYNTHETIC source_class")

        if source_class in {"OFFICIAL", "VGI"}:
            source_url = _https_url(value["source_url"])
            if value["source_reference"] is not None:
                raise RealArtifactContractError("external sources require null source_reference")
            source_reference = None
        else:
            if value["source_url"] is not None:
                raise RealArtifactContractError("MODEL/SYNTHETIC sources require null source_url")
            source_url = None
            source_reference = _repo_relative_path(value["source_reference"], "source_reference")

        license_text = _text(value["license"], "license")
        license_review = _text(value["license_review_status"], "license_review_status")
        if license_review not in _LICENSE_REVIEW:
            raise RealArtifactContractError(f"unsupported license_review_status: {license_review}")
        license_terms_url = (
            None
            if value["license_terms_url"] is None
            else _https_url(value["license_terms_url"], "license_terms_url")
        )
        redistribution = _text(
            value["redistribution_status"], "redistribution_status"
        )
        if redistribution not in _REDISTRIBUTION:
            raise RealArtifactContractError(
                f"unsupported redistribution_status: {redistribution}"
            )
        obligations = _text_tuple(
            value["redistribution_obligations"], "redistribution_obligations"
        )
        if data_class in {"REAL", "OFFICIAL_OPERATION_RECORD"} and (
            license_text.strip().casefold() in _UNRESOLVED_LICENSE_TOKENS
            or redistribution != "PERMITTED_WITH_OBLIGATIONS"
            or license_review == "UNREVIEWED"
            or license_terms_url is None
            or not obligations
        ):
            raise RealArtifactContractError(
                "connected artifacts require reviewed license terms and explicit redistribution obligations"
            )

        sha256 = _text(value["sha256"], "sha256")
        if not _SHA256.fullmatch(sha256):
            raise RealArtifactContractError("sha256 must be lowercase 64-hex text")
        source_sha256 = _text(value["source_sha256"], "source_sha256")
        if not _SHA256.fullmatch(source_sha256):
            raise RealArtifactContractError("source_sha256 must be lowercase 64-hex text")
        source_artifact_path = _repo_relative_path(
            value["source_artifact_path"], "source_artifact_path"
        )
        retrieval_method = _text(value["retrieval_method"], "retrieval_method")
        if retrieval_method not in _RETRIEVAL_METHODS:
            raise RealArtifactContractError(f"unsupported retrieval_method: {retrieval_method}")
        if source_class == "VGI" and retrieval_method != "BOUNDED_QUERY":
            raise RealArtifactContractError(
                "VGI source artifacts require BOUNDED_QUERY acquisition"
            )
        if source_class == "MODEL" and retrieval_method != "MODEL_COMPUTATION":
            raise RealArtifactContractError(
                "MODEL source artifacts require MODEL_COMPUTATION acquisition"
            )
        if source_class == "SYNTHETIC" and retrieval_method != "SYNTHETIC_FIXTURE":
            raise RealArtifactContractError(
                "SYNTHETIC source artifacts require SYNTHETIC_FIXTURE acquisition"
            )
        if source_class == "OFFICIAL" and (
            (data_class == "REAL" and retrieval_method != "OFFICIAL_DOWNLOAD")
            or (
                data_class != "REAL"
                and retrieval_method not in {"OFFICIAL_DOWNLOAD", "METADATA_CAPTURE"}
            )
        ):
            raise RealArtifactContractError(
                "OFFICIAL acquisition method contradicts the artifact data class"
            )
        retrieval_query_path = _optional_repo_relative_path(
            value["retrieval_query_path"], "retrieval_query_path"
        )
        retrieval_query_sha256_value = value["retrieval_query_sha256"]
        if retrieval_query_sha256_value is None:
            retrieval_query_sha256 = None
        else:
            retrieval_query_sha256 = _text(
                retrieval_query_sha256_value, "retrieval_query_sha256"
            )
            if not _SHA256.fullmatch(retrieval_query_sha256):
                raise RealArtifactContractError(
                    "retrieval_query_sha256 must be lowercase 64-hex text or null"
                )
        snapshot_at = value["snapshot_at"]
        snapshot_reason = value["snapshot_reason"]
        if retrieval_method == "BOUNDED_QUERY":
            if retrieval_query_path is None or retrieval_query_sha256 is None:
                raise RealArtifactContractError(
                    "BOUNDED_QUERY requires retrieval_query_path and retrieval_query_sha256"
                )
            snapshot_text = _utc_second(snapshot_at, "snapshot_at")
            if snapshot_reason is not None:
                raise RealArtifactContractError("snapshot_reason must be null when snapshot_at is known")
            snapshot_at = snapshot_text
            snapshot_reason = None
        else:
            if (retrieval_query_path is None) != (retrieval_query_sha256 is None):
                raise RealArtifactContractError(
                    "retrieval_query_path and retrieval_query_sha256 must be both null or both known"
                )
            if snapshot_at is None:
                snapshot_reason = _text(snapshot_reason, "snapshot_reason")
            else:
                snapshot_at = _utc_second(snapshot_at, "snapshot_at")
                if snapshot_reason is not None:
                    raise RealArtifactContractError("snapshot_reason must be null when snapshot_at is known")

        valid_as_of, valid_as_of_reason = _optional_text_with_reason(
            value["valid_as_of"], value["valid_as_of_reason"], "valid_as_of"
        )
        if valid_as_of is not None:
            valid_as_of = _iso_date(valid_as_of, "valid_as_of")
        vertical_datum, vertical_datum_reason = _optional_text_with_reason(
            value["vertical_datum"], value["vertical_datum_reason"], "vertical_datum"
        )
        axis_order = _text(value["axis_order"], "axis_order")
        if axis_order not in _AXIS_ORDERS:
            raise RealArtifactContractError(f"unsupported axis_order: {axis_order}")
        horizontal_unit = _text(value["horizontal_unit"], "horizontal_unit")
        if horizontal_unit not in _HORIZONTAL_UNITS:
            raise RealArtifactContractError(
                f"unsupported horizontal_unit: {horizontal_unit}"
            )
        source_crs = _text(value["source_crs"], "source_crs")
        processing_crs = _text(value["processing_crs"], "processing_crs")
        output_crs = _text(value["output_crs"], "output_crs")
        if data_class == "REAL" and any(
            crs == "UNKNOWN" or not re.fullmatch(r"EPSG:[0-9]+", crs)
            for crs in (source_crs, processing_crs, output_crs)
        ):
            raise RealArtifactContractError("REAL geometry requires explicit EPSG CRS identifiers")
        if output_crs == "EPSG:4326" and (
            axis_order != "longitude_latitude" or horizontal_unit != "degree"
        ):
            raise RealArtifactContractError("EPSG:4326 output requires lon/lat axis and degree units")

        return cls(
            city_id=_text(value["city_id"], "city_id"),
            artifact_id=_text(value["artifact_id"], "artifact_id"),
            artifact_path=_repo_relative_path(value["artifact_path"], "artifact_path"),
            artifact_role=artifact_role,
            source_id=_text(value["source_id"], "source_id"),
            source_url=source_url,
            source_reference=source_reference,
            source_class=source_class,
            data_class=data_class,
            accessed_at=_iso_date(value["accessed_at"], "accessed_at"),
            valid_as_of=valid_as_of,
            valid_as_of_reason=valid_as_of_reason,
            license=license_text,
            license_terms_url=license_terms_url,
            license_review_status=license_review,
            redistribution_status=redistribution,
            redistribution_obligations=obligations,
            sha256=sha256,
            source_artifact_path=source_artifact_path,
            source_sha256=source_sha256,
            retrieval_method=retrieval_method,
            retrieval_query_path=retrieval_query_path,
            retrieval_query_sha256=retrieval_query_sha256,
            snapshot_at=snapshot_at,
            snapshot_reason=snapshot_reason,
            source_revision=_text(value["source_revision"], "source_revision"),
            source_crs=source_crs,
            processing_crs=processing_crs,
            output_crs=output_crs,
            axis_order=axis_order,
            horizontal_unit=horizontal_unit,
            vertical_datum=vertical_datum,
            vertical_datum_reason=vertical_datum_reason,
            transform_history=_text_tuple(
                value["transform_history"], "transform_history"
            ),
            source_feature_id=_text(value["source_feature_id"], "source_feature_id"),
            stable_feature_id=_text(value["stable_feature_id"], "stable_feature_id"),
            revision_id=_text(value["revision_id"], "revision_id"),
            lineage=_text_tuple(value["lineage"], "lineage"),
            geometry_status=geometry_status,
        )

    def as_mapping(self) -> Mapping[str, object]:
        """Return a detached, immutable mapping using the exact schema fields."""
        value: dict[str, object] = {
            field: getattr(self, field) for field in REAL_ARTIFACT_V2_FIELDS
        }
        value["transform_history"] = tuple(self.transform_history)
        value["lineage"] = tuple(self.lineage)
        value["redistribution_obligations"] = tuple(self.redistribution_obligations)
        return MappingProxyType(value)


def _is_reparse_point(path: Path) -> bool:
    attributes = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and attributes & flag)


_VERIFIED_INDEX_TOKEN = object()
_VALIDATED_GEOMETRY_INDEX_TOKEN = object()


@dataclass(frozen=True, slots=True)
class VerifiedArtifactIndex:
    """Manifest metadata bound to contained artifact, source, and query bytes.

    This hash-bound index is not a geometry-connection capability and makes no
    claim that files are committed in Git.  Final integration/RC gates verify
    version control separately.
    """

    records: tuple[RealArtifactLineage, ...]
    trusted_root: Path
    _records_by_artifact: Mapping[str, tuple[RealArtifactLineage, ...]]
    _token: object

    def __post_init__(self) -> None:
        if self._token is not _VERIFIED_INDEX_TOKEN:
            raise RealArtifactContractError("VerifiedArtifactIndex must be created by the loader")

    def records_for(self, artifact_id: str) -> tuple[RealArtifactLineage, ...]:
        records = self._records_by_artifact.get(artifact_id)
        if records is None:
            raise RealArtifactContractError(f"unresolved artifact_id: {artifact_id}")
        return records

    def sources_for(self, source_id: str) -> tuple[RealArtifactLineage, ...]:
        records = tuple(record for record in self.records if record.source_id == source_id)
        if not records:
            raise RealArtifactContractError(f"unresolved source_id: {source_id}")
        return records


@dataclass(frozen=True, slots=True)
class ValidatedGeometryIndex:
    """Immutable canonical geometry snapshots safe for deterministic derivation."""

    artifact_index: VerifiedArtifactIndex
    _payload_bytes_by_artifact: Mapping[str, bytes]
    _feature_ids_by_artifact: Mapping[str, tuple[str, ...]]
    _token: object

    def __post_init__(self) -> None:
        if self._token is not _VALIDATED_GEOMETRY_INDEX_TOKEN:
            raise RealArtifactContractError(
                "ValidatedGeometryIndex must be created by the validated geometry loader"
            )

    @property
    def records(self) -> tuple[RealArtifactLineage, ...]:
        return self.artifact_index.records

    @property
    def trusted_root(self) -> Path:
        return self.artifact_index.trusted_root

    def records_for(self, artifact_id: str) -> tuple[RealArtifactLineage, ...]:
        if artifact_id not in self._payload_bytes_by_artifact:
            raise RealArtifactContractError(
                f"artifact_id is not validated connectable geometry: {artifact_id}"
            )
        return self.artifact_index.records_for(artifact_id)

    def feature_ids_for(self, artifact_id: str) -> tuple[str, ...]:
        feature_ids = self._feature_ids_by_artifact.get(artifact_id)
        if feature_ids is None:
            raise RealArtifactContractError(
                f"artifact_id is not validated connectable geometry: {artifact_id}"
            )
        return feature_ids

    def payload_bytes_for(self, artifact_id: str) -> bytes:
        payload = self._payload_bytes_by_artifact.get(artifact_id)
        if payload is None:
            raise RealArtifactContractError(
                f"artifact_id is not validated connectable geometry: {artifact_id}"
            )
        return payload

    def payload_for(self, artifact_id: str) -> dict[str, Any]:
        payload = self.payload_bytes_for(artifact_id)
        return _parse_strict_json_bytes(payload, f"artifact {artifact_id}")

    def sources_for(self, source_id: str) -> tuple[RealArtifactLineage, ...]:
        return self.artifact_index.sources_for(source_id)

def _reject_duplicate_json_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise RealArtifactContractError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _reject_nonfinite_json_constant(token: str) -> None:
    raise RealArtifactContractError(f"non-finite JSON constant: {token}")


def _parse_strict_json_bytes(payload: bytes, name: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_json_members,
            parse_constant=_reject_nonfinite_json_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RealArtifactContractError(f"{name} is not strict UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise RealArtifactContractError(f"{name} must be a JSON object")
    return value


def _contained_regular_file(root: Path, relative: str, name: str) -> Path:
    root_resolved = root.resolve(strict=True)
    if not root_resolved.is_dir() or root_resolved.is_symlink() or _is_reparse_point(root_resolved):
        raise RealArtifactContractError("trusted_root must be a regular directory")
    candidate = root_resolved.joinpath(*PurePosixPath(relative).parts)
    current = root_resolved
    for part in PurePosixPath(relative).parts:
        current = current / part
        if not current.exists():
            raise RealArtifactContractError(f"{name} does not exist: {relative}")
        if current.is_symlink() or _is_reparse_point(current):
            raise RealArtifactContractError(f"{name} must not traverse a symlink or reparse point")
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as error:
        raise RealArtifactContractError(f"{name} escapes trusted_root") from error
    if not resolved.is_file():
        raise RealArtifactContractError(f"{name} must be a regular file")
    return resolved


def _read_bounded_file(path: Path, name: str, maximum_bytes: int) -> bytes:
    size = path.stat().st_size
    if size <= 0 or size > maximum_bytes:
        raise RealArtifactContractError(
            f"{name} is empty or exceeds the {maximum_bytes}-byte safety limit"
        )
    payload = path.read_bytes()
    if not payload or len(payload) > maximum_bytes:
        raise RealArtifactContractError(
            f"{name} changed size during bounded read"
        )
    return payload


def load_real_artifact_manifest(
    path: str | Path,
    *,
    trusted_root: str | Path,
    expected_city_id: str,
) -> VerifiedArtifactIndex:
    """Load v2 lineage and bind normalized/source/query hashes to contained bytes."""
    manifest = Path(path)
    if manifest.is_symlink() or not manifest.is_file() or _is_reparse_point(manifest):
        raise RealArtifactContractError("real artifact manifest must be a regular file")
    root = Path(trusted_root).resolve(strict=True)
    try:
        manifest.resolve(strict=True).relative_to(root)
    except ValueError as error:
        raise RealArtifactContractError(
            "real artifact manifest must be contained by trusted_root"
        ) from error
    size = manifest.stat().st_size
    if size <= 0 or size > MAX_REAL_ARTIFACT_MANIFEST_BYTES:
        raise RealArtifactContractError("real artifact manifest is empty or oversized")
    try:
        document = json.loads(
            manifest.read_text(encoding="utf-8-sig"),
            object_pairs_hook=_reject_duplicate_json_members,
            parse_constant=lambda token: (_ for _ in ()).throw(
                RealArtifactContractError(f"non-finite JSON constant: {token}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RealArtifactContractError("real artifact manifest is not valid UTF-8 JSON") from error
    if not isinstance(document, dict) or set(document) != {"schema_version", "city_id", "artifacts"}:
        raise RealArtifactContractError("real artifact manifest top-level keys must be exact")
    if document["schema_version"] != REAL_ARTIFACT_SCHEMA_VERSION:
        raise RealArtifactContractError("unsupported real artifact manifest schema version")
    if document["city_id"] != expected_city_id:
        raise RealArtifactContractError("manifest city_id does not match the requested city")
    raw_records = document["artifacts"]
    if not isinstance(raw_records, list) or not raw_records:
        raise RealArtifactContractError("real artifact manifest artifacts must be non-empty")
    if len(raw_records) > MAX_REAL_ARTIFACT_RECORDS:
        raise RealArtifactContractError("real artifact manifest exceeds the record limit")
    records = tuple(RealArtifactLineage.from_mapping(item) for item in raw_records)
    if any(record.city_id != expected_city_id for record in records):
        raise RealArtifactContractError("artifact record crosses the manifest city boundary")
    stable_ids = [record.stable_feature_id for record in records]
    source_ids = [(record.source_id, record.source_feature_id) for record in records]
    if len(stable_ids) != len(set(stable_ids)) or len(source_ids) != len(set(source_ids)):
        raise RealArtifactContractError("duplicate stable or source feature identity")
    if stable_ids != sorted(stable_ids):
        raise RealArtifactContractError("real artifact manifest must use canonical stable-id order")
    groups: dict[str, list[RealArtifactLineage]] = {}
    for record in records:
        groups.setdefault(record.artifact_id, []).append(record)
    artifact_paths = [members[0].artifact_path for members in groups.values()]
    if len(artifact_paths) != len(set(artifact_paths)):
        raise RealArtifactContractError(
            "different artifact IDs must not share one artifact_path"
        )
    immutable_groups: dict[str, tuple[RealArtifactLineage, ...]] = {}
    artifact_consistency_fields = (
        "city_id",
        "artifact_path",
        "artifact_role",
        "sha256",
        "source_artifact_path",
        "source_id",
        "source_url",
        "source_reference",
        "source_class",
        "data_class",
        "accessed_at",
        "valid_as_of",
        "valid_as_of_reason",
        "license",
        "license_terms_url",
        "license_review_status",
        "redistribution_status",
        "redistribution_obligations",
        "source_sha256",
        "retrieval_method",
        "retrieval_query_path",
        "retrieval_query_sha256",
        "snapshot_at",
        "snapshot_reason",
        "source_revision",
        "source_crs",
        "processing_crs",
        "output_crs",
        "axis_order",
        "horizontal_unit",
        "vertical_datum",
        "vertical_datum_reason",
        "transform_history",
        "geometry_status",
    )
    for artifact_id, members in groups.items():
        first = members[0]
        for member in members[1:]:
            if any(getattr(member, field) != getattr(first, field) for field in artifact_consistency_fields):
                raise RealArtifactContractError(
                    f"artifact_id {artifact_id} has contradictory artifact/source metadata"
                )
        artifact = _contained_regular_file(root, first.artifact_path, "artifact_path")
        artifact_bytes = _read_bounded_file(
            artifact, "artifact_path", MAX_NORMALIZED_ARTIFACT_BYTES
        )
        actual_sha256 = hashlib.sha256(artifact_bytes).hexdigest()
        if actual_sha256 != first.sha256:
            raise RealArtifactContractError(
                f"artifact sha256 mismatch for {artifact_id}: expected {first.sha256}, got {actual_sha256}"
            )
        source_artifact = _contained_regular_file(
            root, first.source_artifact_path, "source_artifact_path"
        )
        source_bytes = _read_bounded_file(
            source_artifact, "source_artifact_path", MAX_SOURCE_ARTIFACT_BYTES
        )
        actual_source_sha256 = hashlib.sha256(source_bytes).hexdigest()
        if actual_source_sha256 != first.source_sha256:
            raise RealArtifactContractError(
                f"source sha256 mismatch for {artifact_id}: "
                f"expected {first.source_sha256}, got {actual_source_sha256}"
            )
        if first.retrieval_query_path is not None:
            query = _contained_regular_file(
                root, first.retrieval_query_path, "retrieval_query_path"
            )
            query_bytes = _read_bounded_file(
                query, "retrieval_query_path", MAX_RETRIEVAL_QUERY_BYTES
            )
            actual_query_sha256 = hashlib.sha256(query_bytes).hexdigest()
            if actual_query_sha256 != first.retrieval_query_sha256:
                raise RealArtifactContractError(
                    f"query sha256 mismatch for {artifact_id}: "
                    f"expected {first.retrieval_query_sha256}, got {actual_query_sha256}"
                )
        immutable_groups[artifact_id] = tuple(members)
    return VerifiedArtifactIndex(
        records=records,
        trusted_root=root,
        _records_by_artifact=MappingProxyType(immutable_groups),
        _token=_VERIFIED_INDEX_TOKEN,
    )


def _coordinate_pair(value: object, name: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise RealArtifactContractError(f"{name} coordinate must be a two-number pair")
    lon, lat = value
    if any(isinstance(item, bool) or not isinstance(item, Real) for item in (lon, lat)):
        raise RealArtifactContractError(f"{name} coordinate must contain real numbers")
    lon_float, lat_float = float(lon), float(lat)
    if not math.isfinite(lon_float) or not math.isfinite(lat_float):
        raise RealArtifactContractError(f"{name} coordinate must be finite")
    if not -180.0 <= lon_float <= 180.0 or not -90.0 <= lat_float <= 90.0:
        raise RealArtifactContractError(f"{name} coordinate is outside EPSG:4326 range")
    return lon_float, lat_float


def _validate_line_string(value: object, name: str) -> None:
    if not isinstance(value, list) or len(value) < 2:
        raise RealArtifactContractError(f"{name} LineString needs at least two coordinates")
    coordinates = tuple(_coordinate_pair(item, name) for item in value)
    if len(set(coordinates)) < 2:
        raise RealArtifactContractError(f"{name} LineString has zero length")


def _segments_intersect(
    first_start: tuple[float, float],
    first_end: tuple[float, float],
    second_start: tuple[float, float],
    second_end: tuple[float, float],
) -> bool:
    def orientation(
        start: tuple[float, float],
        end: tuple[float, float],
        point: tuple[float, float],
    ) -> float:
        return (end[0] - start[0]) * (point[1] - start[1]) - (
            end[1] - start[1]
        ) * (point[0] - start[0])

    first_a = orientation(first_start, first_end, second_start)
    first_b = orientation(first_start, first_end, second_end)
    second_a = orientation(second_start, second_end, first_start)
    second_b = orientation(second_start, second_end, first_end)
    epsilon = 1e-15
    if any(abs(value) <= epsilon for value in (first_a, first_b, second_a, second_b)):
        # Non-adjacent touching or collinear segments make the ring non-simple.
        return not (
            max(first_start[0], first_end[0]) < min(second_start[0], second_end[0])
            or max(second_start[0], second_end[0]) < min(first_start[0], first_end[0])
            or max(first_start[1], first_end[1]) < min(second_start[1], second_end[1])
            or max(second_start[1], second_end[1]) < min(first_start[1], first_end[1])
        )
    return (first_a > 0) != (first_b > 0) and (second_a > 0) != (second_b > 0)


def _validate_ring(
    value: object, name: str
) -> tuple[tuple[float, float], ...]:
    if not isinstance(value, list) or len(value) < 4:
        raise RealArtifactContractError(f"{name} polygon ring needs at least four coordinates")
    coordinates = tuple(_coordinate_pair(item, name) for item in value)
    if coordinates[0] != coordinates[-1] or len(set(coordinates[:-1])) < 3:
        raise RealArtifactContractError(f"{name} polygon ring must be closed and non-degenerate")
    signed_double_area = sum(
        start[0] * end[1] - end[0] * start[1]
        for start, end in zip(coordinates, coordinates[1:])
    )
    if abs(signed_double_area) <= 1e-15:
        raise RealArtifactContractError(f"{name} polygon ring has zero area")
    edge_count = len(coordinates) - 1
    for first in range(edge_count):
        for second in range(first + 1, edge_count):
            if second in {first, first + 1} or (first == 0 and second == edge_count - 1):
                continue
            if _segments_intersect(
                coordinates[first],
                coordinates[first + 1],
                coordinates[second],
                coordinates[second + 1],
            ):
                raise RealArtifactContractError(f"{name} polygon ring self-intersects")
    return coordinates


def _ring_edges(
    ring: tuple[tuple[float, float], ...],
) -> tuple[tuple[tuple[float, float], tuple[float, float]], ...]:
    return tuple(zip(ring, ring[1:]))


def _rings_intersect(
    first: tuple[tuple[float, float], ...],
    second: tuple[tuple[float, float], ...],
) -> bool:
    return any(
        _segments_intersect(first_start, first_end, second_start, second_end)
        for first_start, first_end in _ring_edges(first)
        for second_start, second_end in _ring_edges(second)
    )


def _point_in_ring(
    point: tuple[float, float], ring: tuple[tuple[float, float], ...]
) -> bool:
    """Return strict interior membership after boundary intersections were rejected."""

    x, y = point
    inside = False
    for start, end in _ring_edges(ring):
        if (start[1] > y) == (end[1] > y):
            continue
        crossing_x = (end[0] - start[0]) * (y - start[1]) / (
            end[1] - start[1]
        ) + start[0]
        if x < crossing_x:
            inside = not inside
    return inside


def _validate_polygon(
    value: object, name: str
) -> tuple[tuple[tuple[float, float], ...], ...]:
    if not isinstance(value, list) or not value:
        raise RealArtifactContractError(f"{name} Polygon must be non-empty")
    rings = tuple(_validate_ring(ring, f"{name}[{index}]") for index, ring in enumerate(value))
    shell, holes = rings[0], rings[1:]
    for index, hole in enumerate(holes, start=1):
        if _rings_intersect(shell, hole) or not _point_in_ring(hole[0], shell):
            raise RealArtifactContractError(
                f"{name}[{index}] hole must be strictly inside the exterior ring"
            )
    for first in range(len(holes)):
        for second in range(first + 1, len(holes)):
            if (
                _rings_intersect(holes[first], holes[second])
                or _point_in_ring(holes[first][0], holes[second])
                or _point_in_ring(holes[second][0], holes[first])
            ):
                raise RealArtifactContractError(
                    f"{name} polygon holes overlap, intersect, or nest"
                )
    return rings


def _validate_geometry(value: object, name: str) -> None:
    if not isinstance(value, dict) or set(value) != {"type", "coordinates"}:
        raise RealArtifactContractError(f"{name} geometry keys must be exact")
    geometry_type = value["type"]
    coordinates = value["coordinates"]
    if geometry_type == "Point":
        _coordinate_pair(coordinates, name)
    elif geometry_type == "LineString":
        _validate_line_string(coordinates, name)
    elif geometry_type == "MultiLineString":
        if not isinstance(coordinates, list) or not coordinates:
            raise RealArtifactContractError(f"{name} MultiLineString must be non-empty")
        for index, line in enumerate(coordinates):
            _validate_line_string(line, f"{name}[{index}]")
    elif geometry_type == "Polygon":
        _validate_polygon(coordinates, name)
    elif geometry_type == "MultiPolygon":
        if not isinstance(coordinates, list) or not coordinates:
            raise RealArtifactContractError(f"{name} MultiPolygon must be non-empty")
        polygons = tuple(
            _validate_polygon(polygon, f"{name}[{polygon_index}]")
            for polygon_index, polygon in enumerate(coordinates)
        )
        for first in range(len(polygons)):
            for second in range(first + 1, len(polygons)):
                first_shell, second_shell = polygons[first][0], polygons[second][0]
                if (
                    _rings_intersect(first_shell, second_shell)
                    or _point_in_ring(first_shell[0], second_shell)
                    or _point_in_ring(second_shell[0], first_shell)
                ):
                    raise RealArtifactContractError(
                        f"{name} MultiPolygon members overlap or intersect"
                    )
    else:
        raise RealArtifactContractError(f"unsupported {name} geometry type: {geometry_type}")


def _validate_feature_properties(
    properties: Mapping[str, object],
    record: RealArtifactLineage,
    name: str,
) -> None:
    if record.artifact_role == "CORRIDOR_GEOMETRY":
        expected = _FEATURE_LINEAGE_KEYS | _CORRIDOR_FEATURE_PROPERTIES
        if set(properties) != expected:
            raise RealArtifactContractError(
                f"{name} corridor properties must be exact"
            )
        for field in ("bridge", "tunnel"):
            value = properties[field]
            reason = properties[f"{field}_reason"]
            if value == "UNKNOWN":
                _text(reason, f"{name}.{field}_reason")
            elif type(value) is bool:
                if reason is not None:
                    raise RealArtifactContractError(
                        f"{name}.{field}_reason must be null when {field} is known"
                    )
            else:
                raise RealArtifactContractError(
                    f"{name}.{field} must be true, false, or UNKNOWN"
                )
        for field in ("layer", "level"):
            value = properties[field]
            reason = properties[f"{field}_reason"]
            if value is None:
                _text(reason, f"{name}.{field}_reason")
            elif isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(float(value)):
                raise RealArtifactContractError(
                    f"{name}.{field} must be a finite number or null"
                )
            elif reason is not None:
                raise RealArtifactContractError(
                    f"{name}.{field}_reason must be null when {field} is known"
                )
    elif record.artifact_role == "OFFICIAL_HAZARD_GEOMETRY":
        expected = _FEATURE_LINEAGE_KEYS | _HAZARD_FEATURE_PROPERTIES
        if set(properties) != expected:
            raise RealArtifactContractError(
                f"{name} hazard properties must be exact"
            )
        _text(properties["hazard_type"], f"{name}.hazard_type")
        _optional_text_with_reason(
            properties["hazard_category"],
            properties["hazard_category_reason"],
            f"{name}.hazard_category",
        )
        hazard_value = properties["hazard_value"]
        if hazard_value is None:
            if properties["hazard_value_unit"] is not None:
                raise RealArtifactContractError(
                    f"{name}.hazard_value_unit must be null when value is unknown"
                )
            _text(properties["hazard_value_reason"], f"{name}.hazard_value_reason")
        else:
            if (
                isinstance(hazard_value, bool)
                or not isinstance(hazard_value, Real)
                or not math.isfinite(float(hazard_value))
            ):
                raise RealArtifactContractError(
                    f"{name}.hazard_value must be a finite number or null"
                )
            _text(properties["hazard_value_unit"], f"{name}.hazard_value_unit")
            if properties["hazard_value_reason"] is not None:
                raise RealArtifactContractError(
                    f"{name}.hazard_value_reason must be null when value is known"
                )


def validate_real_feature_collection(
    value: object,
    artifact_index: VerifiedArtifactIndex,
    *,
    artifact_id: str,
) -> dict[str, Any]:
    """Validate canonical GeoJSON and exact links to a hash-verified artifact."""
    if not isinstance(value, dict) or set(value) != {"type", "features"}:
        raise RealArtifactContractError("FeatureCollection top-level keys must be exact")
    if value["type"] != "FeatureCollection" or not isinstance(value["features"], list):
        raise RealArtifactContractError("real geometry must be a FeatureCollection")
    features = value["features"]
    if not features:
        raise RealArtifactContractError("real FeatureCollection must be non-empty")
    lineages = artifact_index.records_for(artifact_id)
    by_stable_id = {record.stable_feature_id: record for record in lineages}
    if len(by_stable_id) != len(lineages):
        raise RealArtifactContractError("lineage contains duplicate stable_feature_id")
    feature_ids: list[str] = []
    for index, feature in enumerate(features):
        if not isinstance(feature, dict) or set(feature) != _FEATURE_KEYS:
            raise RealArtifactContractError(f"feature[{index}] keys must be exact")
        if feature["type"] != "Feature":
            raise RealArtifactContractError(f"feature[{index}].type must be Feature")
        properties = feature["properties"]
        if not isinstance(properties, dict) or not _FEATURE_LINEAGE_KEYS <= set(properties):
            raise RealArtifactContractError(f"feature[{index}] is missing lineage properties")
        extra_properties = set(properties) - _ALLOWED_FEATURE_PROPERTIES
        if extra_properties:
            raise RealArtifactContractError(
                f"feature[{index}] contains unsupported properties: {sorted(extra_properties)}"
            )
        stable_id = _text(properties["stable_feature_id"], "stable_feature_id")
        if feature["id"] != stable_id:
            raise RealArtifactContractError(f"feature[{index}] id contradicts stable_feature_id")
        record = by_stable_id.get(stable_id)
        if record is None:
            raise RealArtifactContractError(f"feature[{index}] has unresolved lineage")
        expected = record.as_mapping()
        for field in _FEATURE_LINEAGE_KEYS:
            actual = properties[field]
            if field == "lineage" and isinstance(actual, list):
                actual = tuple(actual)
            if actual != expected[field]:
                raise RealArtifactContractError(
                    f"feature[{index}] lineage field {field} contradicts manifest"
                )
        if record.output_crs != "EPSG:4326" or record.axis_order != "longitude_latitude":
            raise RealArtifactContractError("GeoJSON lineage must declare EPSG:4326 lon/lat output")
        if record.horizontal_unit != "degree":
            raise RealArtifactContractError("EPSG:4326 GeoJSON must use degree horizontal units")
        if record.geometry_status != "SOURCE_TRACEABLE_REAL":
            raise RealArtifactContractError("only source-traceable REAL geometry can be connected")
        _validate_feature_properties(properties, record, f"feature[{index}]")
        _validate_geometry(feature["geometry"], f"feature[{index}]")
        geometry_type = feature["geometry"]["type"]
        if record.artifact_role == "OFFICIAL_HAZARD_GEOMETRY" and geometry_type not in {
            "Polygon",
            "MultiPolygon",
        }:
            raise RealArtifactContractError("official hazard geometry must be polygonal")
        if record.artifact_role == "CORRIDOR_GEOMETRY" and geometry_type not in {
            "LineString",
            "MultiLineString",
        }:
            raise RealArtifactContractError("corridor geometry must be linear")
        feature_ids.append(stable_id)
    if len(feature_ids) != len(set(feature_ids)):
        raise RealArtifactContractError("FeatureCollection contains duplicate stable IDs")
    if feature_ids != sorted(feature_ids):
        raise RealArtifactContractError("FeatureCollection must use canonical stable-id order")
    if set(feature_ids) != set(by_stable_id):
        raise RealArtifactContractError("FeatureCollection and lineage identities must match exactly")
    canonical = _canonical_json_bytes(value, sort_features=False)
    expected_hash = lineages[0].sha256
    if hashlib.sha256(canonical).hexdigest() != expected_hash:
        raise RealArtifactContractError("FeatureCollection bytes do not match the verified artifact sha256")
    return deepcopy(value)


def load_validated_geometry_manifest(
    path: str | Path,
    *,
    trusted_root: str | Path,
    expected_city_id: str,
) -> ValidatedGeometryIndex:
    """Issue an immutable geometry capability only after strict content validation."""

    artifact_index = load_real_artifact_manifest(
        path,
        trusted_root=trusted_root,
        expected_city_id=expected_city_id,
    )
    payloads: dict[str, bytes] = {}
    feature_ids: dict[str, tuple[str, ...]] = {}
    artifact_ids = tuple(dict.fromkeys(record.artifact_id for record in artifact_index.records))
    for artifact_id in artifact_ids:
        records = artifact_index.records_for(artifact_id)
        role = records[0].artifact_role
        if role not in {"CORRIDOR_GEOMETRY", "OFFICIAL_HAZARD_GEOMETRY"}:
            continue
        artifact_path = _contained_regular_file(
            artifact_index.trusted_root,
            records[0].artifact_path,
            "artifact_path",
        )
        payload_bytes = _read_bounded_file(
            artifact_path, "artifact_path", MAX_NORMALIZED_ARTIFACT_BYTES
        )
        payload = _parse_strict_json_bytes(payload_bytes, f"artifact {artifact_id}")
        validated = validate_real_feature_collection(
            payload,
            artifact_index,
            artifact_id=artifact_id,
        )
        payloads[artifact_id] = bytes(payload_bytes)
        feature_ids[artifact_id] = tuple(
            str(feature["id"]) for feature in validated["features"]
        )
    if not payloads:
        raise RealArtifactContractError(
            "manifest contains no validated corridor or official-hazard geometry"
        )
    return ValidatedGeometryIndex(
        artifact_index=artifact_index,
        _payload_bytes_by_artifact=MappingProxyType(payloads),
        _feature_ids_by_artifact=MappingProxyType(feature_ids),
        _token=_VALIDATED_GEOMETRY_INDEX_TOKEN,
    )


@dataclass(frozen=True, slots=True)
class QuarantinedGeometry:
    """Reasoned evidence that an invalid source feature was not connected."""

    artifact_id: str
    source_id: str
    source_feature_id: str
    stable_feature_id: str
    revision_id: str
    reason_code: str
    reason: str
    input_sha256: str


@dataclass(frozen=True, slots=True)
class GeometryPartition:
    """Diagnostic partition for one hash-bound artifact.

    ``accepted`` is immutable but is not a connection capability.  Accepted
    features must be remanifested, hash-bound, and loaded through
    ``load_validated_geometry_manifest`` before model use.
    """

    input_count: int
    accepted: Mapping[str, object]
    quarantined: tuple[QuarantinedGeometry, ...]

    @property
    def accepted_count(self) -> int:
        return len(self.accepted["features"])  # type: ignore[arg-type]

    @property
    def quarantined_count(self) -> int:
        return len(self.quarantined)


def partition_real_feature_collection(
    value: object,
    artifact_index: VerifiedArtifactIndex,
    *,
    artifact_id: str,
) -> GeometryPartition:
    """Quarantine invalid geometry while treating provenance defects as fatal."""
    if not isinstance(value, dict) or set(value) != {"type", "features"}:
        raise RealArtifactContractError("FeatureCollection top-level keys must be exact")
    if value["type"] != "FeatureCollection" or not isinstance(value["features"], list):
        raise RealArtifactContractError("real geometry must be a FeatureCollection")
    lineages = artifact_index.records_for(artifact_id)
    try:
        input_hash = hashlib.sha256(
            _canonical_json_bytes(value, sort_features=False)
        ).hexdigest()
    except (TypeError, ValueError) as error:
        raise RealArtifactContractError(
            "geometry partition input is not canonical finite JSON"
        ) from error
    if input_hash != lineages[0].sha256:
        raise RealArtifactContractError(
            "geometry partition input does not match the hash-bound artifact"
        )
    if any(
        record.data_class != "REAL"
        or record.geometry_status != "SOURCE_TRACEABLE_REAL"
        or record.output_crs != "EPSG:4326"
        or record.axis_order != "longitude_latitude"
        or record.horizontal_unit != "degree"
        for record in lineages
    ):
        raise RealArtifactContractError(
            "geometry partition requires source-traceable REAL EPSG:4326 lon/lat records"
        )
    by_stable_id = {record.stable_feature_id: record for record in lineages}
    features = value["features"]
    identities: list[str] = []
    accepted: list[dict[str, object]] = []
    quarantined: list[QuarantinedGeometry] = []
    for index, feature in enumerate(features):
        if not isinstance(feature, dict) or set(feature) != _FEATURE_KEYS:
            raise RealArtifactContractError(f"feature[{index}] keys must be exact")
        properties = feature.get("properties")
        if not isinstance(properties, dict) or not _FEATURE_LINEAGE_KEYS <= set(properties):
            raise RealArtifactContractError(f"feature[{index}] is missing lineage properties")
        extra_properties = set(properties) - _ALLOWED_FEATURE_PROPERTIES
        if extra_properties:
            raise RealArtifactContractError(
                f"feature[{index}] contains unsupported properties: {sorted(extra_properties)}"
            )
        stable_id = _text(properties["stable_feature_id"], "stable_feature_id")
        if feature.get("id") != stable_id or stable_id not in by_stable_id:
            raise RealArtifactContractError(f"feature[{index}] has unresolved lineage identity")
        record = by_stable_id[stable_id]
        expected = record.as_mapping()
        for field in _FEATURE_LINEAGE_KEYS:
            actual = properties[field]
            if field == "lineage" and isinstance(actual, list):
                actual = tuple(actual)
            if actual != expected[field]:
                raise RealArtifactContractError(
                    f"feature[{index}] lineage field {field} contradicts manifest"
                )
        identities.append(stable_id)
        try:
            _validate_feature_properties(properties, record, f"feature[{index}]")
            _validate_geometry(feature["geometry"], f"feature[{index}]")
            geometry_type = feature["geometry"]["type"]
            if record.artifact_role == "OFFICIAL_HAZARD_GEOMETRY" and geometry_type not in {
                "Polygon",
                "MultiPolygon",
            }:
                raise RealArtifactContractError("official hazard geometry must be polygonal")
            if record.artifact_role == "CORRIDOR_GEOMETRY" and geometry_type not in {
                "LineString",
                "MultiLineString",
            }:
                raise RealArtifactContractError("corridor geometry must be linear")
        except RealArtifactContractError as error:
            input_bytes = json.dumps(
                feature,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=True,
            ).encode("utf-8")
            quarantined.append(
                QuarantinedGeometry(
                    artifact_id=artifact_id,
                    source_id=record.source_id,
                    source_feature_id=record.source_feature_id,
                    stable_feature_id=record.stable_feature_id,
                    revision_id=record.revision_id,
                    reason_code="INVALID_GEOMETRY",
                    reason=str(error),
                    input_sha256=hashlib.sha256(input_bytes).hexdigest(),
                )
            )
        else:
            accepted.append(deepcopy(feature))
    if len(identities) != len(set(identities)):
        raise RealArtifactContractError("FeatureCollection contains duplicate stable IDs")
    if set(identities) != set(by_stable_id):
        raise RealArtifactContractError("FeatureCollection and lineage identities must match exactly")
    accepted.sort(key=lambda feature: str(feature["id"]))
    quarantined.sort(key=lambda item: item.stable_feature_id)
    result = GeometryPartition(
        input_count=len(features),
        accepted=_freeze_json(
            {"type": "FeatureCollection", "features": accepted}
        ),
        quarantined=tuple(quarantined),
    )
    if result.input_count != result.accepted_count + result.quarantined_count:
        raise RealArtifactContractError("geometry partition conservation failed")
    return result


def _freeze_json(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _normalize_json_number(value: object) -> object:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise RealArtifactContractError("canonical JSON rejects non-finite numbers")
        return 0.0 if value == 0.0 else value
    if isinstance(value, list):
        return [_normalize_json_number(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_json_number(item) for key, item in value.items()}
    return value


def _canonical_json_bytes(value: object, *, sort_features: bool) -> bytes:
    if not isinstance(value, dict) or set(value) != {"type", "features"}:
        raise RealArtifactContractError("FeatureCollection top-level keys must be exact")
    if value.get("type") != "FeatureCollection" or not isinstance(value["features"], list):
        raise RealArtifactContractError("canonical input must be a FeatureCollection")
    normalized = _normalize_json_number(deepcopy(value))
    features = normalized["features"]
    if any(not isinstance(feature, dict) or not isinstance(feature.get("id"), str) for feature in features):
        raise RealArtifactContractError("canonical features require text ids")
    if sort_features:
        features.sort(key=lambda feature: feature["id"])
    elif [feature["id"] for feature in features] != sorted(feature["id"] for feature in features):
        raise RealArtifactContractError("FeatureCollection must use canonical stable-id order")
    return (
        json.dumps(
            normalized,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def canonical_feature_collection_bytes(
    value: object,
    artifact_index: VerifiedArtifactIndex,
    *,
    artifact_id: str,
) -> bytes:
    """Validate then return deterministic UTF-8/LF bytes for a verified artifact."""
    canonical = _canonical_json_bytes(value, sort_features=True)
    canonical_value = json.loads(canonical)
    validate_real_feature_collection(
        canonical_value,
        artifact_index,
        artifact_id=artifact_id,
    )
    return canonical
