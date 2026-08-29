"""Small immutable contracts shared by the three overnight city packs.

These objects describe scenario physics and evidence only. They intentionally do
not implement M6/profile evaluation, routing, facility operation, or closure
inference.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
import math
from numbers import Real
import re
from types import MappingProxyType
from typing import Any, Mapping, Sequence


_DATA_STATUSES = {
    "REAL",
    "OFFICIAL_METADATA_ONLY",
    "MODEL_DERIVED",
    "SYNTHETIC_DEMO",
    "UNKNOWN",
}
_EDGE_STATES = {"PASS", "CONDITIONAL", "FAIL", "UNKNOWN"}
_HAZARD_DATA_STATUSES = {"KNOWN", "UNKNOWN"}
_EVIDENCE_AUTHORITIES = {
    "OFFICIAL",
    "SOURCE_FACT",
    "ABLEPATH_DESIGN",
    "DESIGN_ASSUMPTION",
    "UNKNOWN",
}
_PHYSICAL_VALUE_KEYS = {
    "debris_intrusion_left_m",
    "debris_intrusion_right_m",
    "overlap_length_m",
    "max_depth_m",
    "mean_depth_m",
    "arrival_time_sec",
    "elapsed_time_sec",
}
_PROVENANCE_REQUIRED = {"data_class", "source_ids", "method", "model"}
_PROVENANCE_ALLOWED = _PROVENANCE_REQUIRED | {"applied_constant_ids", "notes"}
MAX_SCENARIOS = 128
MAX_EDGES = 10_000
MAX_OBSERVATIONS = 200_000
MAX_ERROR_PAIRS = 20


class HazardContractError(ValueError):
    """Raised when hazard input would require coercion or an invented value."""


def _exact_keys(value: object, required: set[str], name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise HazardContractError(f"{name} must be a mapping")
    keys = set(value)
    if keys != required:
        raise HazardContractError(
            f"{name} keys must be exactly {sorted(required)}; "
            f"missing={sorted(required - keys)}, extra={sorted(keys - required)}"
        )
    return value


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HazardContractError(f"{name} must be non-empty text")
    return value


def _nullable_float(value: object, name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise HazardContractError(f"{name} must be a real number or null")
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise HazardContractError(f"{name} must be finite and non-negative")
    return number


def _tri_bool(value: object, name: str) -> bool | None:
    if value is None or type(value) is bool:
        return value
    raise HazardContractError(f"{name} must be true, false, or null")


def _source_ids(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise HazardContractError("source_ids must be a list of non-empty strings")
    if len(value) != len(set(value)):
        raise HazardContractError("source_ids must not contain duplicates")
    return tuple(value)


def _freeze(value: object) -> object:
    """Return a detached recursively immutable representation."""
    detached = deepcopy(value)
    if isinstance(detached, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in detached.items()})
    if isinstance(detached, (list, tuple)):
        return tuple(_freeze(item) for item in detached)
    if isinstance(detached, (set, frozenset)):
        return frozenset(_freeze(item) for item in detached)
    return detached


@dataclass(frozen=True, slots=True)
class HazardScenario:
    scenario_id: str
    hazard_type: str
    source_status: str
    official_or_assumption: str
    elapsed_time_sec: float | None
    coverage_complete: bool
    default_edge_state: str
    disclaimer: str
    source_ids: tuple[str, ...]

    @classmethod
    def from_mapping(cls, raw: object) -> "HazardScenario":
        required = {
            "scenario_id",
            "hazard_type",
            "source_status",
            "official_or_assumption",
            "elapsed_time_sec",
            "coverage_complete",
            "default_edge_state",
            "disclaimer",
            "source_ids",
        }
        data = _exact_keys(raw, required, "HazardScenario")
        source_status = _text(data["source_status"], "source_status")
        if source_status not in _DATA_STATUSES:
            raise HazardContractError(f"unsupported source_status: {source_status}")
        edge_state = _text(data["default_edge_state"], "default_edge_state")
        if edge_state not in _EDGE_STATES:
            raise HazardContractError(f"unsupported default_edge_state: {edge_state}")
        if type(data["coverage_complete"]) is not bool:
            raise HazardContractError("coverage_complete must be bool")
        authority = _text(data["official_or_assumption"], "official_or_assumption")
        if authority not in _EVIDENCE_AUTHORITIES:
            raise HazardContractError(f"unsupported official_or_assumption: {authority}")
        source_ids = _source_ids(data["source_ids"])
        if authority == "OFFICIAL" and (
            source_status not in {"REAL", "OFFICIAL_METADATA_ONLY"} or not source_ids
        ):
            raise HazardContractError(
                "OFFICIAL authority requires REAL/OFFICIAL_METADATA_ONLY status and source IDs"
            )
        return cls(
            scenario_id=_text(data["scenario_id"], "scenario_id"),
            hazard_type=_text(data["hazard_type"], "hazard_type"),
            source_status=source_status,
            official_or_assumption=authority,
            elapsed_time_sec=_nullable_float(data["elapsed_time_sec"], "elapsed_time_sec"),
            coverage_complete=data["coverage_complete"],
            default_edge_state=edge_state,
            disclaimer=_text(data["disclaimer"], "disclaimer"),
            source_ids=source_ids,
        )


@dataclass(frozen=True, slots=True)
class EdgeHazardObservation:
    edge_id: str
    scenario_id: str
    overlap: bool | None
    overlap_length_m: float | None
    max_depth_m: float | None
    mean_depth_m: float | None
    official_closure: bool | None
    hazard_data_status: str
    source_ids: tuple[str, ...]

    @classmethod
    def from_mapping(cls, raw: object) -> "EdgeHazardObservation":
        required = {
            "edge_id",
            "scenario_id",
            "overlap",
            "overlap_length_m",
            "max_depth_m",
            "mean_depth_m",
            "official_closure",
            "hazard_data_status",
            "source_ids",
        }
        data = _exact_keys(raw, required, "EdgeHazardObservation")
        status = _text(data["hazard_data_status"], "hazard_data_status")
        if status not in _HAZARD_DATA_STATUSES:
            raise HazardContractError("hazard_data_status must be KNOWN or UNKNOWN")
        overlap = _tri_bool(data["overlap"], "overlap")
        overlap_length = _nullable_float(data["overlap_length_m"], "overlap_length_m")
        max_depth = _nullable_float(data["max_depth_m"], "max_depth_m")
        mean_depth = _nullable_float(data["mean_depth_m"], "mean_depth_m")
        if overlap is None and any(
            value is not None for value in (overlap_length, max_depth, mean_depth)
        ):
            raise HazardContractError(
                "overlap_length_m and depth observations require a known overlap value"
            )
        if overlap is False and overlap_length not in {None, 0.0}:
            raise HazardContractError("overlap=false contradicts positive overlap_length_m")
        if overlap is False and any(value not in {None, 0.0} for value in (max_depth, mean_depth)):
            raise HazardContractError("overlap=false contradicts positive depth")
        if mean_depth is not None and max_depth is not None and mean_depth > max_depth:
            raise HazardContractError("mean_depth_m cannot exceed max_depth_m")
        if status == "KNOWN" and all(
            value is None for value in (overlap, overlap_length, max_depth, mean_depth)
        ):
            raise HazardContractError("KNOWN hazard data requires at least one physical observation")
        return cls(
            edge_id=_text(data["edge_id"], "edge_id"),
            scenario_id=_text(data["scenario_id"], "scenario_id"),
            overlap=overlap,
            overlap_length_m=overlap_length,
            max_depth_m=max_depth,
            mean_depth_m=mean_depth,
            official_closure=_tri_bool(data["official_closure"], "official_closure"),
            hazard_data_status=status,
            source_ids=_source_ids(data["source_ids"]),
        )


@dataclass(frozen=True, slots=True)
class EdgeScenarioPhysics:
    edge_id: str
    scenario_id: str
    base_clear_width_m: float | None
    remaining_clear_width_m: float | None
    physical_values: Mapping[str, float | None]
    provenance: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, raw: object) -> "EdgeScenarioPhysics":
        required = {
            "edge_id",
            "scenario_id",
            "base_clear_width_m",
            "remaining_clear_width_m",
            "physical_values",
            "provenance",
        }
        data = _exact_keys(raw, required, "EdgeScenarioPhysics")
        physical = data["physical_values"]
        provenance = data["provenance"]
        if not isinstance(physical, Mapping) or not physical:
            raise HazardContractError("physical_values must be a non-empty mapping")
        if not isinstance(provenance, Mapping) or not provenance:
            raise HazardContractError("provenance must be a non-empty mapping")
        physical_keys = set(physical)
        if not physical_keys <= _PHYSICAL_VALUE_KEYS:
            raise HazardContractError(
                f"physical_values contains non-physical or unsupported keys: "
                f"{sorted(physical_keys - _PHYSICAL_VALUE_KEYS)}"
            )
        provenance_keys = set(provenance)
        if not _PROVENANCE_REQUIRED <= provenance_keys or not provenance_keys <= _PROVENANCE_ALLOWED:
            raise HazardContractError(
                "provenance requires data_class/source_ids/method/model and accepts "
                "only applied_constant_ids/notes as optional fields"
            )
        data_class = _text(provenance["data_class"], "provenance.data_class")
        if data_class not in _DATA_STATUSES:
            raise HazardContractError("provenance.data_class is unsupported")
        normalized_provenance = {
            "data_class": data_class,
            "source_ids": _source_ids(provenance["source_ids"]),
            "method": _text(provenance["method"], "provenance.method"),
            "model": _text(provenance["model"], "provenance.model"),
        }
        forbidden_model_tokens = {"M6", "PROFILE", "ACCESSIBILITY", "ROUTE", "STATE"}
        model_tokens = set(re.findall(r"[A-Z0-9]+", normalized_provenance["model"].upper()))
        if model_tokens & forbidden_model_tokens:
            raise HazardContractError(
                "profile/accessibility/route/state models are outside EdgeScenarioPhysics"
            )
        if "applied_constant_ids" in provenance:
            normalized_provenance["applied_constant_ids"] = _source_ids(
                provenance["applied_constant_ids"]
            )
        if "notes" in provenance:
            normalized_provenance["notes"] = _text(provenance["notes"], "provenance.notes")
        converted = {
            _text(key, "physical_values key"): _nullable_float(value, f"physical_values.{key}")
            for key, value in physical.items()
        }
        return cls(
            edge_id=_text(data["edge_id"], "edge_id"),
            scenario_id=_text(data["scenario_id"], "scenario_id"),
            base_clear_width_m=_nullable_float(data["base_clear_width_m"], "base_clear_width_m"),
            remaining_clear_width_m=_nullable_float(
                data["remaining_clear_width_m"], "remaining_clear_width_m"
            ),
            physical_values=_freeze(converted),  # type: ignore[arg-type]
            provenance=_freeze(normalized_provenance),  # type: ignore[arg-type]
        )


def validate_dense_observations(
    scenario_ids: Sequence[str],
    edge_ids: Sequence[str],
    rows: Sequence[Mapping[str, object]],
) -> None:
    """Require exactly one observation for every scenario-edge pair."""
    scenarios = tuple(_text(value, "scenario_id") for value in scenario_ids)
    edges = tuple(_text(value, "edge_id") for value in edge_ids)
    if len(scenarios) > MAX_SCENARIOS or len(edges) > MAX_EDGES:
        raise HazardContractError("scenario or edge cardinality exceeds the bounded contract")
    if not scenarios or not edges:
        raise HazardContractError("scenario_ids and edge_ids must each contain at least one item")
    expected_count = len(scenarios) * len(edges)
    if expected_count > MAX_OBSERVATIONS or len(rows) > MAX_OBSERVATIONS:
        raise HazardContractError("observation matrix exceeds the bounded contract")
    if len(scenarios) != len(set(scenarios)) or len(edges) != len(set(edges)):
        raise HazardContractError("scenario_ids and edge_ids must be unique")
    expected = {(scenario_id, edge_id) for scenario_id in scenarios for edge_id in edges}
    pairs: list[tuple[str, str]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise HazardContractError(f"observation row {index} must be a mapping")
        pairs.append(
            (
                _text(row.get("scenario_id"), f"rows[{index}].scenario_id"),
                _text(row.get("edge_id"), f"rows[{index}].edge_id"),
            )
        )
    counts = Counter(pairs)
    duplicate = sorted(pair for pair, count in counts.items() if count != 1)
    actual = set(pairs)
    if len(rows) != expected_count or actual != expected or duplicate:
        missing_sample = sorted(expected - actual)[:MAX_ERROR_PAIRS]
        orphan_sample = sorted(actual - expected)[:MAX_ERROR_PAIRS]
        duplicate_sample = duplicate[:MAX_ERROR_PAIRS]
        raise HazardContractError(
            "scenario-edge observation matrix is not dense and unique: "
            f"expected_count={expected_count}, actual_count={len(rows)}, "
            f"missing_sample={missing_sample}, orphan_sample={orphan_sample}, "
            f"duplicate_sample={duplicate_sample}"
        )
