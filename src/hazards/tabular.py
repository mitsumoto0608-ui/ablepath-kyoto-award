"""Strict v1 loaders for staged city hazard-table dialects.

Pack-specific audit columns remain available in an immutable raw mapping. The
loader validates the exact ordered CSV header and the semantics used by the
current UNKNOWN-only adapter. Any future physical value or dialect change
requires a new reviewed adapter rather than coercion.
"""

from __future__ import annotations

from collections.abc import Mapping
import csv
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from .contracts import EdgeHazardObservation, HazardContractError


KIYOMIZU_EDGE_V1_FIELDS = (
    "schema_version", "edge_id", "scenario_id", "data_status",
    "damage_state", "debris_present", "base_clear_width_m",
    "debris_intrusion_left_m", "debris_intrusion_right_m",
    "remaining_clear_width_m", "official_closure", "hazard_data_status",
    "profile_status", "reason", "source_ids", "source_feature_id",
    "stable_feature_id", "revision_id", "lineage",
)
ARASHIYAMA_EDGE_V1_FIELDS = (
    "scenario_id", "edge_id", "hazard_type", "data_class",
    "hazard_overlap_status", "inundation_depth_m", "official_closure",
    "operational_rule_status", "scenario_state", "source_dataset_ids",
    "notes", "source_feature_id", "stable_feature_id", "revision_id",
    "lineage",
)
FUJISAWA_EDGE_V1_FIELDS = (
    "schema_version", "hazard_schema_version", "scenario_id", "edge_id",
    "data_status", "physical_state", "physical_state_reason",
    "operational_state", "operational_state_reason", "arrival_time_min",
    "inundation_depth_m", "closure_time_min", "source_dataset_ids",
    "snapshot_mode", "source_crs", "processing_crs", "output_crs",
    "horizontal_unit", "vertical_unit", "axis_order",
    "coordinate_precision", "transform_history", "geometry_status",
    "source_feature_id", "stable_feature_id", "revision_id", "lineage",
)
_DIALECTS = {
    KIYOMIZU_EDGE_V1_FIELDS: "KIYOMIZU_EDGE_UNKNOWN_V1",
    ARASHIYAMA_EDGE_V1_FIELDS: "ARASHIYAMA_EDGE_UNKNOWN_V1",
    FUJISAWA_EDGE_V1_FIELDS: "FUJISAWA_EDGE_UNKNOWN_V1",
}
MAX_TABLE_BYTES = 2 * 1024 * 1024
MAX_TABLE_ROWS = 200_000


@dataclass(frozen=True, slots=True)
class AdaptedEdgeObservation:
    """A normalized observation plus immutable source-row provenance."""

    dialect_id: str
    observation: EdgeHazardObservation
    raw: Mapping[str, str]


def _row(raw: object, dialect_hint: str | None = None) -> tuple[dict[str, str], str]:
    if not isinstance(raw, Mapping):
        raise HazardContractError("hazard table row must be a mapping")
    if any(not isinstance(key, str) or not isinstance(value, str) for key, value in raw.items()):
        raise HazardContractError("hazard table row keys and values must be strings")
    data = dict(raw)
    matching = [name for fields, name in _DIALECTS.items() if set(fields) == set(data)]
    if len(matching) != 1 or (dialect_hint is not None and matching[0] != dialect_hint):
        raise HazardContractError(
            "unsupported hazard table fields; an explicit versioned adapter is required"
        )
    return data, matching[0]


def _is(data: Mapping[str, str], key: str, expected: str) -> None:
    if data[key] != expected:
        raise HazardContractError(f"{key} must be {expected!r} in the reviewed v1 dialect")


def _one_of(data: Mapping[str, str], key: str, expected: set[str]) -> None:
    if data[key] not in expected:
        raise HazardContractError(f"{key} must be one of {sorted(expected)}")


def _blank(data: Mapping[str, str], *keys: str) -> None:
    populated = [key for key in keys if data[key].strip()]
    if populated:
        raise HazardContractError(
            f"physical values {populated} require a new reviewed adapter; v1 is UNKNOWN-only"
        )


def _nonempty(data: Mapping[str, str], *keys: str) -> None:
    missing = [key for key in keys if not data[key].strip()]
    if missing:
        raise HazardContractError(f"required audit fields are empty: {missing}")


def _ids(value: str, separator: str) -> list[str]:
    if not value.strip():
        return []
    items = [item.strip() for item in value.split(separator)]
    if any(not item for item in items) or len(items) != len(set(items)):
        raise HazardContractError("source IDs must be non-empty and unique")
    return items


def adapt_edge_observation_row(
    raw: object, *, dialect_hint: str | None = None
) -> AdaptedEdgeObservation:
    """Normalize one exact-field UNKNOWN-only row without inventing physics."""
    data, dialect = _row(raw, dialect_hint)
    _nonempty(
        data, "edge_id", "scenario_id", "source_feature_id",
        "stable_feature_id", "revision_id", "lineage",
    )
    if dialect == "KIYOMIZU_EDGE_UNKNOWN_V1":
        _is(data, "schema_version", "1.0.0")
        _is(data, "data_status", "SYNTHETIC_DEMO")
        _is(data, "damage_state", "UNKNOWN")
        _is(data, "hazard_data_status", "UNKNOWN")
        _is(data, "profile_status", "NOT_COMPUTED")
        _is(data, "revision_id", "fixture-v1")
        _is(data, "lineage", "FIXTURE_VALUE|ABLEPATH_DESIGN_SCENARIO_EDGE")
        _nonempty(data, "reason")
        _blank(
            data, "debris_present", "base_clear_width_m",
            "debris_intrusion_left_m", "debris_intrusion_right_m",
            "remaining_clear_width_m", "official_closure",
        )
        source_ids = _ids(data["source_ids"], "|")
    elif dialect == "ARASHIYAMA_EDGE_UNKNOWN_V1":
        _one_of(data, "hazard_type", {"RAIN", "FLOOD"})
        _is(data, "data_class", "SYNTHETIC_DEMO")
        _is(data, "hazard_overlap_status", "NOT_COMPUTED")
        _is(data, "official_closure", "UNKNOWN")
        _is(data, "operational_rule_status", "UNKNOWN")
        _is(data, "scenario_state", "UNKNOWN")
        _is(data, "source_feature_id", "FIXTURE_ARASHIYAMA_EDGE_STATE_V1")
        _is(data, "revision_id", "r1")
        _is(data, "lineage", "ABLEPATH_DESIGN synthetic scenario-edge matrix")
        _nonempty(data, "notes")
        _blank(data, "inundation_depth_m")
        source_ids = _ids(data["source_dataset_ids"], ";")
    else:
        for key in ("schema_version", "hazard_schema_version"):
            _is(data, key, "1.0.0")
        _is(data, "data_status", "SYNTHETIC_DEMO")
        _is(data, "physical_state", "UNKNOWN")
        _is(data, "operational_state", "UNKNOWN")
        _is(data, "snapshot_mode", "STATIC_SNAPSHOT_COMPARISON")
        _is(data, "source_crs", "EPSG:4326")
        _is(data, "processing_crs", "EPSG:6677")
        _is(data, "output_crs", "EPSG:4326")
        _is(data, "horizontal_unit", "degree_output_metre_processing")
        _is(data, "vertical_unit", "UNKNOWN")
        _is(data, "axis_order", "longitude_latitude")
        _is(data, "coordinate_precision", "6")
        _is(data, "transform_history", "NOT_TRANSFORMED_FIXTURE_ONLY")
        _is(data, "geometry_status", "SYNTHETIC_DEMO")
        _is(data, "revision_id", "1")
        _is(data, "lineage", "FIXTURE_VALUE|STATIC_SCENARIO_METADATA_ONLY")
        _nonempty(data, "physical_state_reason", "operational_state_reason")
        _blank(data, "arrival_time_min", "inundation_depth_m", "closure_time_min")
        source_ids = _ids(data["source_dataset_ids"], "|")

    observation = EdgeHazardObservation.from_mapping(
        {
            "edge_id": data["edge_id"],
            "scenario_id": data["scenario_id"],
            "overlap": None,
            "overlap_length_m": None,
            "max_depth_m": None,
            "mean_depth_m": None,
            "official_closure": None,
            "hazard_data_status": "UNKNOWN",
            "source_ids": source_ids,
        }
    )
    return AdaptedEdgeObservation(
        dialect_id=dialect,
        observation=observation,
        raw=MappingProxyType(dict(data)),
    )


def load_edge_observation_table(path: Path) -> tuple[AdaptedEdgeObservation, ...]:
    """Load a bounded CSV after validating its exact ordered v1 header."""
    if not isinstance(path, Path) or not path.is_file() or path.is_symlink():
        raise HazardContractError("hazard table path must be a regular non-symlink file")
    if path.stat().st_size > MAX_TABLE_BYTES:
        raise HazardContractError("hazard table exceeds the 2 MiB input limit")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = tuple(reader.fieldnames or ())
        try:
            dialect = _DIALECTS[header]
        except KeyError as exc:
            raise HazardContractError(
                "unsupported or duplicate hazard table header; exact order is required"
            ) from exc
        records: list[AdaptedEdgeObservation] = []
        for index, row in enumerate(reader, start=1):
            if index > MAX_TABLE_ROWS:
                raise HazardContractError("hazard table exceeds the row limit")
            records.append(adapt_edge_observation_row(row, dialect_hint=dialect))
    if not records:
        raise HazardContractError("hazard table must contain at least one row")
    return tuple(records)


__all__ = [
    "ARASHIYAMA_EDGE_V1_FIELDS",
    "AdaptedEdgeObservation",
    "FUJISAWA_EDGE_V1_FIELDS",
    "KIYOMIZU_EDGE_V1_FIELDS",
    "adapt_edge_observation_row",
    "load_edge_observation_table",
]
