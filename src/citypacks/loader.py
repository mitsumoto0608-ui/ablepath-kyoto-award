"""Fail-closed loader for the overnight v1 city-pack envelope."""

from __future__ import annotations

from copy import deepcopy
import math
from numbers import Real
import os
from pathlib import Path
import re
import stat
from typing import Any

import yaml


SUPPORTED_CITYPACK_MAJOR = 1
MAX_CITY_DOCUMENT_BYTES = 1_000_000
_VERSION_TRIPLET = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_READINESS_KEYS = {
    "facility_status",
    "entrance_status",
    "capacity_status",
    "operation_status",
    "demand_status",
    "origin_status",
    "profile_status",
    "kpi_status",
    "m6_status",
}
_KPI_KEYS = {
    "physically_reachable",
    "accommodated",
    "overflow_waiting",
    "unreachable",
    "unknown_affected_upper_bound",
}
_GEO_FIELDS = {
    "schema_version",
    "source_crs",
    "processing_crs",
    "output_crs",
    "horizontal_unit",
    "vertical_unit",
    "axis_order",
    "coordinate_precision",
    "transform_history",
    "geometry_status",
    "source_feature_id",
    "stable_feature_id",
    "revision_id",
    "lineage",
}
_CITY_REQUIRED = {
    "schema_version",
    "citypack_schema_version",
    "hazard_schema_version",
    "viewer_data_schema_version",
    "city_id",
    "data_status",
    "official_metadata_status",
    "schema_compatibility",
    "readiness",
    "kpis",
    "geospatial_contract",
    "completion_levels",
}
_CITY_ALLOWED = _CITY_REQUIRED | {
    "display_name",
    "country",
    "municipality",
    "corridor_name",
    "center_lon",
    "center_lat",
    "center_data_class",
    "center_value_class",
    "default_zoom",
    "plateau_city_code",
    "supported_hazards",
    "last_verified_at",
    "source_manifest_path",
    "scenario_disclaimer",
    "official_data_targets",
}
_GEOSPATIAL_ALLOWED = _GEO_FIELDS | {
    "source_horizontal_unit",
    "processing_horizontal_unit",
    "output_horizontal_unit",
    "processing_axis_order",
    "processing_crs_note",
}
_COMPLETION_KEYS = {
    "ENGINEERING_UI_COMPLETE",
    "DATA_STAGING_COMPLETE",
    "REAL_GEOMETRY_CONNECTED",
    "MODEL_CONNECTED",
    "ADMIN_VALIDATED",
    "overall",
}
_DATA_CLASSES = {
    "REAL",
    "OFFICIAL_METADATA_ONLY",
    "MODEL_DERIVED",
    "SYNTHETIC_DEMO",
    "UNKNOWN",
}
_READINESS_STATUSES = _DATA_CLASSES | {"NOT_COMPUTED", "READY", "KNOWN"}
MAX_YAML_DEPTH = 64
MAX_YAML_NODES = 10_000


class CityPackContractError(ValueError):
    """Raised when a city pack cannot be interpreted without guessing."""


def require_supported_major(
    version: object,
    *,
    contract_name: str,
    supported_major: int = SUPPORTED_CITYPACK_MAJOR,
) -> tuple[int, int, int]:
    """Parse semantic version text and reject every unsupported major."""
    if not isinstance(version, str) or not _VERSION_TRIPLET.fullmatch(version):
        raise CityPackContractError(
            f"{contract_name} version must be a numeric version triplet such as "
            f"{supported_major}.0.0; got {version!r}"
        )
    major, minor, patch = (int(part) for part in version.split("-", 1)[0].split("+", 1)[0].split("."))
    if major != supported_major:
        raise CityPackContractError(
            f"unsupported {contract_name} schema major {major}; supported major "
            f"{supported_major}. Record a migration requirement; do not reinterpret "
            "the document implicitly."
        )
    return major, minor, patch


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CityPackContractError(f"{name} must be a mapping")
    return value


def _nonempty_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CityPackContractError(f"{name} must be non-empty text")
    return value


def _finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(float(value)):
        raise CityPackContractError(f"{name} must be a finite number")
    return float(value)


def _nonempty_text_or_list(value: object, name: str) -> None:
    if isinstance(value, str):
        _nonempty_text(value, name)
        return
    if isinstance(value, list) and value and all(
        isinstance(item, str) and item.strip() for item in value
    ):
        return
    raise CityPackContractError(f"{name} must be non-empty text or a non-empty text list")


def _validate_document(document: dict[str, Any]) -> None:
    keys = set(document)
    if keys != _CITY_REQUIRED and (missing := _CITY_REQUIRED - keys):
        raise CityPackContractError(f"city.yaml missing required keys: {sorted(missing)}")
    extra = keys - _CITY_ALLOWED
    if extra:
        raise CityPackContractError(f"city.yaml contains unsupported keys: {sorted(extra)}")
    for version_key in (
        "schema_version",
        "citypack_schema_version",
        "hazard_schema_version",
        "viewer_data_schema_version",
    ):
        if version_key not in document:
            raise CityPackContractError(f"missing required version: {version_key}")
        require_supported_major(document[version_key], contract_name=version_key)

    _nonempty_text(document.get("city_id"), "city_id")
    for name in (
        "display_name",
        "country",
        "municipality",
        "corridor_name",
        "center_data_class",
        "center_value_class",
        "plateau_city_code",
        "last_verified_at",
        "source_manifest_path",
        "scenario_disclaimer",
    ):
        if name in document:
            _nonempty_text(document[name], name)
    for name in ("center_lon", "center_lat", "default_zoom"):
        if name in document:
            _finite_number(document[name], name)
    if "supported_hazards" in document:
        supported = document["supported_hazards"]
        if (
            not isinstance(supported, list)
            or any(not isinstance(item, str) or not item.strip() for item in supported)
            or len(supported) != len(set(supported))
        ):
            raise CityPackContractError(
                "supported_hazards must be a unique list of non-empty text"
            )
    if "official_data_targets" in document:
        _mapping(document["official_data_targets"], "official_data_targets")
    if document.get("data_status") not in _DATA_CLASSES:
        raise CityPackContractError("data_status uses an unsupported evidence class")
    if document.get("official_metadata_status") != "OFFICIAL_METADATA_ONLY":
        raise CityPackContractError(
            "official_metadata_status must be OFFICIAL_METADATA_ONLY for metadata-only sources"
        )
    compatibility = _mapping(document.get("schema_compatibility"), "schema_compatibility")
    expected_compatibility = {
        "supported_major": SUPPORTED_CITYPACK_MAJOR,
        "unsupported_major_policy": "REJECT_WITH_ACTIONABLE_ERROR",
        "migration_policy": "RECORD_REQUIRED_MIGRATION_NO_IMPLICIT_CONVERSION",
    }
    if compatibility != expected_compatibility:
        raise CityPackContractError(
            "schema_compatibility must explicitly reject unsupported majors and "
            "record migrations without implicit conversion"
        )

    readiness = _mapping(document.get("readiness"), "readiness")
    if set(readiness) != _READINESS_KEYS:
        raise CityPackContractError(
            "readiness keys must be exact: "
            f"missing={sorted(_READINESS_KEYS - set(readiness))}, "
            f"extra={sorted(set(readiness) - _READINESS_KEYS)}"
        )
    for name in _READINESS_KEYS:
        if not isinstance(readiness[name], str) or readiness[name] not in _READINESS_STATUSES:
            raise CityPackContractError(
                f"readiness.{name} must use a declared readiness/evidence status"
            )
    if readiness["profile_status"] != "NOT_COMPUTED":
        raise CityPackContractError(
            "profile_status must remain NOT_COMPUTED while M6/profile evaluation is unavailable"
        )
    if readiness["m6_status"] != "NOT_COMPUTED":
        raise CityPackContractError("m6_status must remain NOT_COMPUTED")
    if readiness["kpi_status"] != "NOT_COMPUTED":
        raise CityPackContractError("kpi_status must remain NOT_COMPUTED")

    kpis = _mapping(document.get("kpis"), "kpis")
    if set(kpis) != _KPI_KEYS:
        raise CityPackContractError(
            "kpis keys must be the exact five V4 KPI cards: "
            f"missing={sorted(_KPI_KEYS - set(kpis))}, extra={sorted(set(kpis) - _KPI_KEYS)}"
        )
    prerequisites = (
        "facility_status",
        "entrance_status",
        "capacity_status",
        "operation_status",
        "demand_status",
        "origin_status",
        "profile_status",
    )
    missing_prerequisite = any(readiness[key] not in {"READY", "KNOWN"} for key in prerequisites)
    for kpi_name, raw_entry in kpis.items():
        entry = _mapping(raw_entry, f"kpis.{kpi_name}")
        if set(entry) != {"value", "reason"}:
            raise CityPackContractError(
                f"kpis.{kpi_name} must contain exactly value and reason"
            )
        if missing_prerequisite and entry["value"] is not None:
            raise CityPackContractError(
                f"kpis.{kpi_name}.value must be null while readiness prerequisites are missing"
            )
        if entry["value"] is None:
            _nonempty_text(entry["reason"], f"kpis.{kpi_name}.reason")

    geospatial = _mapping(document.get("geospatial_contract"), "geospatial_contract")
    missing_geo = _GEO_FIELDS.difference(geospatial)
    if missing_geo:
        raise CityPackContractError(
            f"geospatial_contract missing V4 fields: {sorted(missing_geo)}"
        )
    extra_geo = set(geospatial) - _GEOSPATIAL_ALLOWED
    if extra_geo:
        raise CityPackContractError(
            f"geospatial_contract contains unsupported keys: {sorted(extra_geo)}"
        )
    require_supported_major(
        geospatial["schema_version"], contract_name="geospatial_contract"
    )
    for name in (
        "source_crs",
        "processing_crs",
        "output_crs",
        "horizontal_unit",
        "vertical_unit",
        "geometry_status",
        "source_feature_id",
        "stable_feature_id",
        "revision_id",
    ):
        _nonempty_text(geospatial[name], f"geospatial_contract.{name}")
    precision = geospatial["coordinate_precision"]
    if isinstance(precision, bool) or not isinstance(precision, int) or precision < 0:
        raise CityPackContractError(
            "geospatial_contract.coordinate_precision must be a non-negative integer"
        )
    for name in ("axis_order", "transform_history", "lineage"):
        _nonempty_text_or_list(geospatial[name], f"geospatial_contract.{name}")
    for name in (
        "source_horizontal_unit",
        "processing_horizontal_unit",
        "output_horizontal_unit",
        "processing_crs_note",
    ):
        if name in geospatial:
            _nonempty_text(geospatial[name], f"geospatial_contract.{name}")
    if "processing_axis_order" in geospatial:
        _nonempty_text_or_list(
            geospatial["processing_axis_order"],
            "geospatial_contract.processing_axis_order",
        )

    completion = _mapping(document.get("completion_levels"), "completion_levels")
    if set(completion) != _COMPLETION_KEYS:
        raise CityPackContractError("completion_levels must contain the exact five levels and overall")
    for name in _COMPLETION_KEYS - {"overall"}:
        if type(completion[name]) is not bool:
            raise CityPackContractError(f"completion_levels.{name} must be bool")
    if completion["overall"] not in {"PARTIAL_COMPLETE", "DEMO_COMPLETE"}:
        raise CityPackContractError("completion_levels.overall is unsupported")


class _NoAliasUniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects aliases and duplicate mapping keys."""

    def compose_node(self, parent: object, index: object) -> yaml.Node:
        if self.check_event(yaml.AliasEvent):
            raise CityPackContractError("YAML aliases are not accepted in city.yaml")
        return super().compose_node(parent, index)

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict:
        seen: set[object] = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=False)
            try:
                duplicate = key in seen
            except TypeError as exc:
                raise CityPackContractError("city.yaml mapping keys must be scalar") from exc
            if duplicate:
                raise CityPackContractError(f"duplicate YAML key is not accepted: {key!r}")
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


def _enforce_structure_limits(value: object) -> None:
    stack: list[tuple[object, int]] = [(value, 1)]
    node_count = 0
    while stack:
        current, depth = stack.pop()
        node_count += 1
        if node_count > MAX_YAML_NODES:
            raise CityPackContractError("city.yaml exceeds the node-count limit")
        if depth > MAX_YAML_DEPTH:
            raise CityPackContractError("city.yaml exceeds the nesting-depth limit")
        if isinstance(current, dict):
            stack.extend((item, depth + 1) for pair in current.items() for item in pair)
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)


def _is_reparse_point(path: Path) -> bool:
    details = os.lstat(path)
    attributes = getattr(details, "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _reject_link_components(path: Path) -> None:
    """Inspect existing unresolved path components before canonicalization."""
    candidate = path.absolute()
    while True:
        if candidate.exists() or candidate.is_symlink():
            if candidate.is_symlink() or _is_reparse_point(candidate):
                raise CityPackContractError(
                    f"city-pack path component may not be a symlink or reparse point: {candidate.name}"
                )
        if candidate.parent == candidate:
            return
        candidate = candidate.parent


def load_citypack(
    pack_directory: str | Path,
    *,
    trusted_root: str | Path,
) -> dict[str, Any]:
    """Load and validate ``city.yaml`` without migration or caller-visible aliases."""
    raw_root = Path(trusted_root)
    raw_pack = Path(pack_directory)
    _reject_link_components(raw_root)
    _reject_link_components(raw_pack)
    root = raw_root.resolve(strict=True)
    pack = raw_pack.resolve(strict=True)
    try:
        pack.relative_to(root)
    except ValueError as exc:
        raise CityPackContractError("city pack must be contained by trusted_root") from exc
    city_document = pack / "city.yaml"
    if not city_document.is_file():
        raise CityPackContractError(f"city.yaml not found in city pack: {pack}")
    for candidate in (pack, city_document):
        if candidate.is_symlink() or _is_reparse_point(candidate):
            raise CityPackContractError("city-pack paths may not be symlinks or reparse points")
    try:
        with city_document.open("rb") as handle:
            size = os.fstat(handle.fileno()).st_size
            if size <= 0 or size > MAX_CITY_DOCUMENT_BYTES:
                raise CityPackContractError(
                    f"city.yaml size {size} is outside the accepted "
                    f"1..{MAX_CITY_DOCUMENT_BYTES} byte range"
                )
            payload = handle.read(MAX_CITY_DOCUMENT_BYTES + 1)
        document = yaml.load(payload.decode("utf-8"), Loader=_NoAliasUniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError, RecursionError) as exc:
        raise CityPackContractError(f"cannot parse city.yaml safely: {exc}") from exc
    _enforce_structure_limits(document)
    mapping = _mapping(document, "city.yaml")
    _validate_document(mapping)
    return deepcopy(mapping)
