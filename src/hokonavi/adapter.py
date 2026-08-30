"""Deterministic, synthetic-only Hokonavi 2024 adapter prototype.

The adapter preserves reviewed source facts, records explicit information
loss, and keeps AblePath design data in a separately validated sidecar.
It does not read real network data or calculate profile/scenario values.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation
import json
import math
from numbers import Real
from pathlib import Path
import re
from typing import Mapping

import yaml


class HokonaviAdapterError(ValueError):
    """Raised when data contradicts the bounded adapter contract."""


_IN_OUT = {1: "OUTDOOR", 2: "BOUNDARY", 3: "INDOOR"}
_DIRECTION = {1: "BIDIRECTIONAL", 2: "FORWARD", 3: "REVERSE", 99: "UNKNOWN"}
_ROUTE_STRUCTURE = {
    1: "PHYSICALLY_SEPARATED",
    2: "NOT_PHYSICALLY_SEPARATED",
    3: "CROSSWALK",
    4: "UNMARKED_ROAD_CROSSING",
    99: "UNKNOWN",
}
_ROUTE_TYPE = {
    1: "NO_ASSOCIATED_ATTRIBUTE",
    2: "MOVING_WALKWAY",
    3: "RAILROAD_CROSSING",
    4: "ELEVATOR",
    5: "ESCALATOR",
    6: "STAIRS",
    7: "RAMP",
    99: "UNKNOWN",
}
_METHOD = {"1": "FIELD_SURVEY", "2": "TRACK_LOG"}
_CLASS_CODES = {1, 2, 3, 4, 5, 99}
_ELEVATOR_CODES = {1, 3, 99}
_LINK_PATTERN = re.compile(r"^link([1-9]|[1-9][0-9])_id$")

_MAPPING_REACHABILITY = {
    "OUTPUT": [
        "NODE_ID", "NODE_LAT", "NODE_LON", "NODE_GEOMETRY", "LINK_ID",
        "LINK_FROM", "LINK_TO", "LINK_GEOMETRY", "LINK_DISTANCE", "CRS_METADATA",
    ],
    "OUTPUT_WITH_LOSS": [
        "NODE_LEVEL", "NODE_TYPE", "NODE_CONNECTED_LINKS", "LINK_DIRECTION",
        "ROUTE_STRUCTURE", "ROUTE_TYPE", "STATIC_WIDTH_CLASS", "STATIC_WIDTH_VALUE",
        "LONGITUDINAL_SLOPE_CLASS", "LONGITUDINAL_SLOPE_VALUE", "STEP_CLASS",
        "STEP_VALUE", "STAIRS", "RAMP", "ELEVATOR", "SOURCE_METHOD",
        "UPDATE_DATE", "UNKNOWN_SEMANTICS",
    ],
    "SIDECAR": [
        "NODE_ELEVATION", "ESCALATOR", "RANK", "M7_REMAINING_WIDTH",
        "OBSERVATION", "EVIDENCE", "PROFILE_STATE", "SCENARIO_STATE",
        "BEFORE_AFTER", "OPERATION_STATUS",
    ],
    "REJECT_OR_EXTERNAL_SIDECAR": ["PROVENANCE"],
    "REJECT_NOT_APPLICABLE": ["FACILITY_DATASET"],
}

_SOURCE_TOP_KEYS = {"type", "fixture_status", "crs_metadata", "features"}
_SOURCE_CRS_KEYS = {"name", "coordinate_representation"}
_FEATURE_KEYS = {"type", "geometry", "properties"}
_SOURCE_NODE_KEYS = {
    "fixture_status", "entity", "node_id", "lat", "lon", "floor", "in_out",
}
_SOURCE_LINK_KEYS = {
    "fixture_status", "entity", "link_id", "start_id", "end_id", "distance",
    "rank", "r_method", "maint_date", "rt_struct", "route_type", "direction",
    "width", "w_min", "vtcl_slope", "vSlope_max", "lev_diff", "levDif_max",
    "stair", "elevator",
}
_INTERNAL_TOP_KEYS = {
    "fixture_status", "crs_metadata", "mapping_reachability", "nodes", "edges",
}
_INTERNAL_NODE_KEYS = {
    "node_id", "latitude", "longitude", "geometry", "level", "node_type",
    "in_out_code", "incident_edge_ids", "source_sidecar",
}
_INTERNAL_EDGE_KEYS = {
    "edge_id", "from_node", "to_node", "geometry", "length_m",
    "travel_direction", "travel_direction_code", "route_structure",
    "route_structure_code", "route_type", "route_type_code",
    "clear_width_static_class", "clear_width_static_m",
    "clear_width_static_measurement", "hokonavi_rank",
    "longitudinal_slope_class", "slope_estimate_percent", "slope_measurement",
    "step_class", "step_height_cm", "step_measurement", "connector", "connector_sidecar", "validity",
    "source_value_provenance", "source_sidecar",
}

_NODE_BASE_LOSSES = {
    "LOSS-CODEBOOK-MISMATCH",
    "LOSS-CONNECTIVITY-REPRESENTATION",
    "LOSS-LEVEL-DOMAIN",
}
_EDGE_BASE_LOSSES = {
    "LOSS-ABLEPATH-CORE-ABSENT",
    "LOSS-CODEBOOK-MISMATCH",
    "LOSS-RANK-NOT-PROFILE",
    "LOSS-SLOPE-PRECISION",
    "LOSS-SLOPE-QUANTIZATION",
    "LOSS-SOURCE-METHOD-GRANULARITY",
    "LOSS-STEP-PRECISION",
    "LOSS-STEP-QUANTIZATION",
    "LOSS-VALIDITY-SEMANTICS",
    "LOSS-WIDTH-PRECISION",
    "LOSS-WIDTH-QUANTIZATION",
}

_SIDECAR_PATH = Path(__file__).resolve().parents[2] / "schemas" / "hokonavi_2024_sidecar.schema.json"
_MAPPING_PATH = Path(__file__).resolve().parents[2] / "schemas" / "hokonavi_2024_mapping.yaml"
_SIDECAR_EDGE_KEYS = {
    "m7", "observation", "evidence", "validity", "profile", "scenario",
    "provenance", "before_after", "operation_status",
}
_PROVENANCE_KEYS = {"source_role", "source_id", "crs", "method", "applied_constant_ids"}
_OBSERVATION_KEYS = {
    "observation_id", "attribute", "raw_value", "unit", "method", "device",
    "observed_at", "observer_role", "direction", "weather", "photo", "accuracy",
    "review_status",
}
_EVIDENCE_KEYS = {
    "source_class", "acquisition_method", "verification_level", "validity_status",
    "authority_scope",
}
_SOURCE_CLASSES = {"OFFICIAL", "VGI", "IMAGE", "MODEL", "FIELD", "OPERATOR"}
_ACQUISITION_METHODS = {"DOWNLOAD", "VISUAL_AUDIT", "TAPE", "INCLINOMETER", "LIDAR", "INTERVIEW"}
_VERIFICATION_LEVELS = {"UNREVIEWED", "SINGLE_REVIEWED", "DOUBLE_REVIEWED", "ADJUDICATED"}
_VALIDITY_STATUSES = {"CURRENT", "STALE", "EXPIRED", "UNKNOWN"}
_AUTHORITY_SCOPES = {"geometry", "dimension", "operation", "hazard"}
_PROFILE_STATES = {"PASS", "CONDITIONAL", "FAIL", "UNKNOWN"}
_SCENARIO_STATES = {"OPEN", "NARROWED", "CLOSED", "UNKNOWN"}
_COMPUTATION_STATUSES = {"COMPUTED", "NOT_COMPUTED"}
_VARIANTS = {"mean_case", "sensitivity_high_case"}


def canonical_json_bytes(value: object) -> bytes:
    """Return canonical UTF-8 JSON bytes and reject non-finite values."""

    try:
        payload = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as error:
        raise HokonaviAdapterError(f"value is not canonical JSON: {error}") from error
    return (payload + "\n").encode("utf-8")


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise HokonaviAdapterError(f"{name} must be a mapping")
    return value


def _list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise HokonaviAdapterError(f"{name} must be a list")
    return value


def _exact_keys(
    value: Mapping[str, object],
    required: set[str],
    name: str,
    *,
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    missing = required - set(value)
    unexpected = set(value) - required - optional
    if missing or unexpected:
        raise HokonaviAdapterError(
            f"{name} has unsupported schema; missing={sorted(missing)}, "
            f"unexpected={sorted(unexpected)}"
        )


def _text(value: object, name: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise HokonaviAdapterError(f"{name} must be non-empty text")
    return value


def _finite(value: object, name: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise HokonaviAdapterError(f"{name} must be a finite number")
    number = float(value)
    if not math.isfinite(number) or (minimum is not None and number < minimum):
        raise HokonaviAdapterError(f"{name} is outside the reviewed numeric domain")
    return number


def _optional_finite(value: object, name: str) -> float | None:
    if value is None:
        return None
    return _finite(value, name, minimum=0)


def _integer_or_none(value: object, name: str) -> int | None:
    if value is None:
        return None
    if type(value) is not int or value < 0:
        raise HokonaviAdapterError(f"{name} must be a non-negative integer or null")
    return value


def _one_decimal_or_none(value: object, name: str) -> float | None:
    number = _optional_finite(value, name)
    if number is None:
        return None
    try:
        decimal_value = Decimal(str(value))
    except InvalidOperation as error:
        raise HokonaviAdapterError(f"{name} is not a decimal value") from error
    if decimal_value.as_tuple().exponent < -1:
        raise HokonaviAdapterError(f"{name} must use 0.1m resolution")
    return number


def _code(value: object, codebook: Mapping[int, str], name: str) -> int:
    if type(value) is not int or value not in codebook:
        raise HokonaviAdapterError(f"unsupported {name}: {value!r}")
    return value


def _geometry(value: object, expected_type: str, name: str) -> dict[str, object]:
    geometry = _mapping(value, name)
    _exact_keys(geometry, {"type", "coordinates"}, name)
    if geometry["type"] != expected_type:
        raise HokonaviAdapterError(f"{name} must be {expected_type}")
    coordinates = _list(geometry["coordinates"], f"{name}.coordinates")
    pairs = [coordinates] if expected_type == "Point" else coordinates
    if expected_type == "LineString" and len(pairs) < 2:
        raise HokonaviAdapterError(f"{name} requires at least two points")
    for pair in pairs:
        if not isinstance(pair, list) or len(pair) != 2:
            raise HokonaviAdapterError(f"{name} coordinates must be [longitude, latitude]")
        longitude = _finite(pair[0], f"{name}.longitude")
        latitude = _finite(pair[1], f"{name}.latitude")
        if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
            raise HokonaviAdapterError(f"{name} coordinate is outside lon/lat bounds")
    return deepcopy(dict(geometry))


def _source_provenance(raw: object, normalized: object) -> dict[str, object]:
    if raw == 99 or raw == "99":
        return {"kind": "SOURCE_CODE_99", "raw": raw, "normalized": "UNKNOWN"}
    return {"kind": "SOURCE_VALUE", "raw": raw, "normalized": normalized}


def _start_time_provenance(properties: Mapping[str, object]) -> dict[str, object]:
    if "start_time" not in properties:
        return {"kind": "MISSING_ATTRIBUTE", "normalized": "UNKNOWN"}
    raw = properties["start_time"]
    if not isinstance(raw, str):
        raise HokonaviAdapterError("start_time must be text when present")
    if raw == "99":
        return {"kind": "SOURCE_CODE_99", "raw": raw, "normalized": "UNKNOWN"}
    if raw == "":
        return {"kind": "SEMANTIC_BLANK", "raw": raw, "normalized": "NO_TIME_RESTRICTION"}
    if not re.fullmatch(r"(?:[01][0-9]|2[0-3])[0-5][0-9]", raw):
        raise HokonaviAdapterError("start_time must be HHMM, blank, 99, or missing")
    return {"kind": "SOURCE_VALUE", "raw": raw, "normalized": raw}


def _validate_date(value: object, name: str) -> str:
    text = _text(value, name)
    assert text is not None
    try:
        date.fromisoformat(text)
    except ValueError as error:
        raise HokonaviAdapterError(f"{name} must be an ISO calendar date") from error
    return text


def _validate_provenance(value: object, name: str) -> dict[str, object]:
    provenance = _mapping(value, name)
    _exact_keys(provenance, _PROVENANCE_KEYS, name)
    if provenance["source_role"] != "ABLEPATH_DESIGN":
        raise HokonaviAdapterError(f"{name}.source_role must be ABLEPATH_DESIGN")
    for key in ("source_id", "crs", "method"):
        _text(provenance[key], f"{name}.{key}")
    constant_ids = _list(provenance["applied_constant_ids"], f"{name}.applied_constant_ids")
    if any(not isinstance(item, str) or not item for item in constant_ids):
        raise HokonaviAdapterError(f"{name}.applied_constant_ids must contain text")
    if constant_ids != sorted(set(constant_ids)):
        raise HokonaviAdapterError(f"{name}.applied_constant_ids must be sorted and unique")
    return deepcopy(dict(provenance))


def _validate_observations(value: object, name: str) -> list[object]:
    records = _list(value, name)
    ids: list[str] = []
    for index, raw in enumerate(records):
        record_name = f"{name}[{index}]"
        record = _mapping(raw, record_name)
        _exact_keys(record, _OBSERVATION_KEYS, record_name)
        observation_id = _text(record["observation_id"], f"{record_name}.observation_id")
        assert observation_id is not None
        ids.append(observation_id)
        for key in ("attribute", "method", "observed_at", "observer_role", "review_status"):
            _text(record[key], f"{record_name}.{key}")
        for key in ("unit", "device", "direction", "weather", "photo"):
            _text(record[key], f"{record_name}.{key}", nullable=True)
        raw_value = record["raw_value"]
        if isinstance(raw_value, float) and not math.isfinite(raw_value):
            raise HokonaviAdapterError(f"{record_name}.raw_value must be finite")
        if not isinstance(raw_value, (str, int, float, bool, type(None))):
            raise HokonaviAdapterError(f"{record_name}.raw_value has unsupported type")
        if record["accuracy"] is not None:
            _finite(record["accuracy"], f"{record_name}.accuracy", minimum=0)
    if ids != sorted(set(ids)):
        raise HokonaviAdapterError(f"{name} must use sorted unique observation_id values")
    return deepcopy(records)


def _validate_evidence(value: object, name: str) -> list[object]:
    records = _list(value, name)
    allowed = (
        ("source_class", _SOURCE_CLASSES),
        ("acquisition_method", _ACQUISITION_METHODS),
        ("verification_level", _VERIFICATION_LEVELS),
        ("validity_status", _VALIDITY_STATUSES),
        ("authority_scope", _AUTHORITY_SCOPES),
    )
    for index, raw in enumerate(records):
        record_name = f"{name}[{index}]"
        record = _mapping(raw, record_name)
        _exact_keys(record, _EVIDENCE_KEYS, record_name)
        for key, values in allowed:
            if record[key] not in values:
                raise HokonaviAdapterError(f"{record_name}.{key} is outside the reviewed enum")
    return deepcopy(records)


def _validate_computed_records(
    value: object,
    name: str,
    *,
    kind: str,
) -> list[object]:
    records = _list(value, name)
    seen: list[tuple[str, ...]] = []
    for index, raw in enumerate(records):
        record_name = f"{name}[{index}]"
        record = _mapping(raw, record_name)
        if kind == "profile":
            keys = {"profile_id", "scenario_id", "computation_status", "profile_state"}
            _exact_keys(record, keys, record_name)
            profile_id = _text(record["profile_id"], f"{record_name}.profile_id")
            scenario_id = _text(record["scenario_id"], f"{record_name}.scenario_id")
            seen.append((str(profile_id), str(scenario_id)))
            state_key = "profile_state"
            states = _PROFILE_STATES
        else:
            keys = {"scenario_id", "computation_status", "edge_state"}
            _exact_keys(record, keys, record_name)
            scenario_id = _text(record["scenario_id"], f"{record_name}.scenario_id")
            seen.append((str(scenario_id),))
            state_key = "edge_state"
            states = _SCENARIO_STATES
        status = record["computation_status"]
        if status not in _COMPUTATION_STATUSES:
            raise HokonaviAdapterError(f"{record_name}.computation_status is invalid")
        state = record[state_key]
        if status == "COMPUTED" and state not in states:
            raise HokonaviAdapterError(f"{record_name}.{state_key} is invalid")
        if status == "NOT_COMPUTED" and state is not None:
            raise HokonaviAdapterError(f"{record_name}.{state_key} must be null when not computed")
    if seen != sorted(set(seen)):
        raise HokonaviAdapterError(f"{name} identifiers must be sorted and unique")
    return deepcopy(records)


def _validate_m7(value: object, name: str) -> list[object]:
    records = _list(value, name)
    seen: list[tuple[str, str]] = []
    required = {
        "scenario_id", "variant", "remaining_clear_width_m", "hazard_data_status",
        "official_closure", "provenance",
    }
    for index, raw in enumerate(records):
        record_name = f"{name}[{index}]"
        record = _mapping(raw, record_name)
        _exact_keys(record, required, record_name)
        scenario_id = _text(record["scenario_id"], f"{record_name}.scenario_id")
        if record["variant"] not in _VARIANTS:
            raise HokonaviAdapterError(f"{record_name}.variant is invalid")
        seen.append((str(scenario_id), str(record["variant"])))
        width = _optional_finite(record["remaining_clear_width_m"], f"{record_name}.remaining_clear_width_m")
        if record["hazard_data_status"] not in {"KNOWN", "UNKNOWN"}:
            raise HokonaviAdapterError(f"{record_name}.hazard_data_status is invalid")
        if record["hazard_data_status"] == "KNOWN" and width is None:
            raise HokonaviAdapterError(f"{record_name} known hazard data requires a width")
        closure = record["official_closure"]
        if closure is not None and type(closure) is not bool:
            raise HokonaviAdapterError(f"{record_name}.official_closure must be bool or null")
        if record["hazard_data_status"] == "UNKNOWN" and (
            width is not None or closure is not None
        ):
            raise HokonaviAdapterError(
                f"{record_name} UNKNOWN hazard data requires null width and closure"
            )
        _validate_provenance(record["provenance"], f"{record_name}.provenance")
    if seen != sorted(set(seen)):
        raise HokonaviAdapterError(f"{name} scenario/variant pairs must be sorted and unique")
    return deepcopy(records)


def validate_sidecar(value: object, *, edge_ids: set[str]) -> dict[str, object]:
    """Validate and canonicalize the exact AblePath sidecar v1 shape."""

    try:
        schema = json.loads(_SIDECAR_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HokonaviAdapterError(f"sidecar schema cannot be loaded: {error}") from error
    if schema.get("$id") != "https://ablepath.example/schemas/hokonavi_2024_sidecar-1.0.0.json":
        raise HokonaviAdapterError("sidecar schema identity changed")
    sidecar = _mapping(value, "ablepath_sidecar")
    _exact_keys(sidecar, {"schema_version", "source_role", "edges"}, "ablepath_sidecar")
    if sidecar["schema_version"] != "1.0.0":
        raise HokonaviAdapterError("ablepath_sidecar must use schema_version 1.0.0")
    if sidecar["source_role"] != "ABLEPATH_DESIGN":
        raise HokonaviAdapterError("ablepath_sidecar.source_role must be ABLEPATH_DESIGN")
    edges = _mapping(sidecar["edges"], "ablepath_sidecar.edges")
    unknown_ids = set(edges) - edge_ids
    if unknown_ids:
        raise HokonaviAdapterError(f"sidecar references unknown edge IDs: {sorted(unknown_ids)}")
    for edge_id in sorted(edges):
        _text(edge_id, "sidecar edge ID")
        name = f"ablepath_sidecar.edges[{edge_id}]"
        payload = _mapping(edges[edge_id], name)
        _exact_keys(payload, {"provenance"}, name, optional=_SIDECAR_EDGE_KEYS - {"provenance"})
        _validate_provenance(payload["provenance"], f"{name}.provenance")
        if "m7" in payload:
            _validate_m7(payload["m7"], f"{name}.m7")
        if "observation" in payload:
            _validate_observations(payload["observation"], f"{name}.observation")
        if "evidence" in payload:
            _validate_evidence(payload["evidence"], f"{name}.evidence")
        if "validity" in payload:
            validity = _mapping(payload["validity"], f"{name}.validity")
            _exact_keys(validity, {"valid_from", "valid_to"}, f"{name}.validity")
            _text(validity["valid_from"], f"{name}.validity.valid_from")
            _text(validity["valid_to"], f"{name}.validity.valid_to", nullable=True)
        if "profile" in payload:
            _validate_computed_records(payload["profile"], f"{name}.profile", kind="profile")
        if "scenario" in payload:
            _validate_computed_records(payload["scenario"], f"{name}.scenario", kind="scenario")
        if "before_after" in payload:
            records = _list(payload["before_after"], f"{name}.before_after")
            phases: list[str] = []
            for index, raw in enumerate(records):
                record_name = f"{name}.before_after[{index}]"
                record = _mapping(raw, record_name)
                _exact_keys(record, {"intervention_phase"}, record_name)
                if record["intervention_phase"] not in {"BEFORE", "AFTER"}:
                    raise HokonaviAdapterError(f"{record_name}.intervention_phase is invalid")
                phases.append(str(record["intervention_phase"]))
            if phases != sorted(set(phases)):
                raise HokonaviAdapterError(f"{name}.before_after must be sorted and unique")
        if "operation_status" in payload:
            records = _list(payload["operation_status"], f"{name}.operation_status")
            scenario_ids: list[str] = []
            for index, raw in enumerate(records):
                record_name = f"{name}.operation_status[{index}]"
                record = _mapping(raw, record_name)
                _exact_keys(record, {"scenario_id", "official_closure", "hazard_data_status"}, record_name)
                scenario_id = _text(record["scenario_id"], f"{record_name}.scenario_id")
                scenario_ids.append(str(scenario_id))
                closure = record["official_closure"]
                if closure is not None and type(closure) is not bool:
                    raise HokonaviAdapterError(f"{record_name}.official_closure must be bool or null")
                if record["hazard_data_status"] not in {"KNOWN", "UNKNOWN"}:
                    raise HokonaviAdapterError(f"{record_name}.hazard_data_status is invalid")
                if record["hazard_data_status"] == "UNKNOWN" and closure is not None:
                    raise HokonaviAdapterError(
                        f"{record_name} UNKNOWN operation data requires null closure"
                    )
            if scenario_ids != sorted(set(scenario_ids)):
                raise HokonaviAdapterError(f"{name}.operation_status must be sorted and unique")
    return json.loads(canonical_json_bytes(dict(sidecar)))


def _edge_losses(edge: Mapping[str, object]) -> list[str]:
    losses = set(_EDGE_BASE_LOSSES)
    if edge.get("route_type_code") in {4, 6, 7}:
        losses.add("LOSS-CONNECTOR-SEMANTICS")
    provenance = _mapping(edge.get("source_value_provenance"), "source_value_provenance")
    if any(
        _mapping(provenance[field], f"source_value_provenance.{field}").get("kind")
        == "SOURCE_CODE_99"
        for field in ("direction", "width", "vtcl_slope", "lev_diff", "rt_struct", "route_type", "elevator")
    ):
        losses.add("LOSS-UNKNOWN-ENCODING")
    return sorted(losses)


def _exact_loss_ids(value: object, expected: list[str], name: str) -> None:
    actual = _list(value, name)
    if actual != expected:
        raise HokonaviAdapterError(
            f"{name} must be the exact sorted applicable loss_ids; "
            f"expected={expected}, actual={actual}"
        )


def _mapping_loss_ids() -> dict[str, str]:
    try:
        contract = yaml.safe_load(_MAPPING_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise HokonaviAdapterError(f"mapping contract cannot be loaded: {error}") from error
    mappings = contract.get("mappings") if isinstance(contract, dict) else None
    if not isinstance(mappings, list):
        raise HokonaviAdapterError("mapping contract has no mappings list")
    result: dict[str, str] = {}
    for raw in mappings:
        mapping = _mapping(raw, "mapping contract item")
        if mapping.get("status") != "FULL":
            mapping_id = _text(mapping.get("id"), "mapping contract id")
            loss_id = _text(mapping.get("loss_id"), f"mapping {mapping_id} loss_id")
            result[str(mapping_id)] = str(loss_id)
    reached = {item for values in _MAPPING_REACHABILITY.values() for item in values}
    if reached != {str(_mapping(item, "mapping item").get("id")) for item in mappings}:
        raise HokonaviAdapterError("runtime mapping reachability differs from mapping contract")
    return dict(sorted(result.items()))


def _connector(route_type: int, stair: object, elevator: object) -> dict[str, object]:
    if route_type == 99:
        if stair is not None or elevator != 99:
            raise HokonaviAdapterError(
                "UNKNOWN route_type requires unknown connector values"
            )
        return {
            "stairs": None,
            "stair_count": None,
            "is_ramp": None,
            "is_elevator": None,
            "elevator_code": 99,
        }
    if route_type == 6:
        if type(stair) is not int or stair <= 0:
            raise HokonaviAdapterError("stair route requires a positive stair count")
    elif stair is not None:
        raise HokonaviAdapterError("non-stair route cannot carry a stair count")
    if type(elevator) is not int or elevator not in _ELEVATOR_CODES:
        raise HokonaviAdapterError("elevator code is outside the reviewed prototype subset")
    if route_type == 4 and elevator == 1:
        raise HokonaviAdapterError("elevator route contradicts elevator=1 (none)")
    if route_type != 4 and elevator != 1:
        raise HokonaviAdapterError("non-elevator route contradicts elevator code")
    return {
        "stairs": route_type == 6,
        "stair_count": stair,
        "is_ramp": route_type == 7,
        "is_elevator": route_type == 4,
        "elevator_code": elevator,
    }


def import_hokonavi_2024(
    document: Mapping[str, object],
    *,
    ablepath_sidecar: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Import a reviewed synthetic network without inventing semantics."""

    source = _mapping(document, "Hokonavi network")
    _exact_keys(source, _SOURCE_TOP_KEYS, "Hokonavi network")
    if source["type"] != "FeatureCollection":
        raise HokonaviAdapterError("network must be a FeatureCollection")
    fixture_status = _text(source["fixture_status"], "fixture_status")
    if fixture_status != "SYNTHETIC":
        raise HokonaviAdapterError("bounded prototype requires fixture_status=SYNTHETIC")
    crs = _mapping(source["crs_metadata"], "crs_metadata")
    _exact_keys(crs, _SOURCE_CRS_KEYS, "crs_metadata")
    if crs != {"name": "JGD2011", "coordinate_representation": "decimal_degrees"}:
        raise HokonaviAdapterError("source CRS must be JGD2011 decimal degrees")

    node_features: list[tuple[Mapping[str, object], dict[str, object]]] = []
    link_features: list[tuple[Mapping[str, object], dict[str, object]]] = []
    for index, raw_feature in enumerate(_list(source["features"], "features")):
        feature = _mapping(raw_feature, f"features[{index}]")
        _exact_keys(feature, _FEATURE_KEYS, f"features[{index}]")
        if feature["type"] != "Feature":
            raise HokonaviAdapterError("every network member must be a Feature")
        properties = _mapping(feature["properties"], f"features[{index}].properties")
        if properties.get("fixture_status") != fixture_status:
            raise HokonaviAdapterError("feature/source synthetic marker mismatch")
        if properties.get("entity") == "node":
            optional = {"elevation"} | {key for key in properties if _LINK_PATTERN.fullmatch(key)}
            _exact_keys(properties, _SOURCE_NODE_KEYS, f"features[{index}].properties", optional=optional)
            node_features.append((properties, _geometry(feature["geometry"], "Point", f"features[{index}].geometry")))
        elif properties.get("entity") == "link":
            _exact_keys(properties, _SOURCE_LINK_KEYS, f"features[{index}].properties", optional={"start_time"})
            link_features.append((properties, _geometry(feature["geometry"], "LineString", f"features[{index}].geometry")))
        else:
            raise HokonaviAdapterError("mixed or unknown entity")

    node_ids = [_text(properties["node_id"], "node_id") for properties, _ in node_features]
    link_ids = [_text(properties["link_id"], "link_id") for properties, _ in link_features]
    if len(node_ids) != len(set(node_ids)):
        raise HokonaviAdapterError("duplicate node ID")
    if len(link_ids) != len(set(link_ids)):
        raise HokonaviAdapterError("duplicate link ID")
    if set(node_ids) & set(link_ids):
        raise HokonaviAdapterError("node/link ID collision")
    node_id_set = set(node_ids)

    incidents: dict[str, set[str]] = {str(node_id): set() for node_id in node_ids}
    for properties, _ in link_features:
        edge_id = str(_text(properties["link_id"], "link_id"))
        start = str(_text(properties["start_id"], f"{edge_id}.start_id"))
        end = str(_text(properties["end_id"], f"{edge_id}.end_id"))
        if start not in node_id_set or end not in node_id_set:
            raise HokonaviAdapterError("dangling endpoint")
        incidents[start].add(edge_id)
        incidents[end].add(edge_id)

    nodes: list[dict[str, object]] = []
    node_coordinates: dict[str, list[object]] = {}
    for properties, geometry in node_features:
        node_id = str(properties["node_id"])
        latitude = _finite(properties["lat"], f"{node_id}.lat")
        longitude = _finite(properties["lon"], f"{node_id}.lon")
        if geometry["coordinates"] != [longitude, latitude]:
            raise HokonaviAdapterError(f"{node_id} properties contradict Point geometry")
        level = properties["floor"]
        _finite(level, f"{node_id}.floor")
        in_out = _code(properties["in_out"], _IN_OUT, f"{node_id}.in_out")
        numbered_links = sorted(
            (
                int(_LINK_PATTERN.fullmatch(key).group(1)),
                str(_text(value, f"{node_id}.{key}")),
            )
            for key, value in properties.items()
            if _LINK_PATTERN.fullmatch(key)
        )
        numbered_slots = [slot for slot, _ in numbered_links]
        if numbered_slots != list(range(1, len(numbered_slots) + 1)):
            raise HokonaviAdapterError(
                f"{node_id} numbered incident link columns must be contiguous from link1_id"
            )
        declared = [edge_id for _, edge_id in numbered_links]
        if len(declared) != len(set(declared)):
            raise HokonaviAdapterError(f"{node_id} repeats an incident link ID")
        if set(declared) != incidents[node_id]:
            raise HokonaviAdapterError(f"{node_id} incident links contradict endpoints")
        losses = set(_NODE_BASE_LOSSES)
        source_sidecar: dict[str, object] = {"source_role": "SOURCE_FACT"}
        if "elevation" in properties:
            source_sidecar["elevation_m"] = _finite(properties["elevation"], f"{node_id}.elevation")
            losses.add("LOSS-ABLEPATH-CORE-ABSENT")
        source_sidecar["loss_ids"] = sorted(losses)
        node_coordinates[node_id] = [longitude, latitude]
        nodes.append({
            "node_id": node_id,
            "latitude": latitude,
            "longitude": longitude,
            "geometry": geometry,
            "level": level,
            "node_type": _IN_OUT[in_out],
            "in_out_code": in_out,
            "incident_edge_ids": declared,
            "source_sidecar": source_sidecar,
        })

    edges: list[dict[str, object]] = []
    for properties, geometry in link_features:
        edge_id = str(properties["link_id"])
        start = str(properties["start_id"])
        end = str(properties["end_id"])
        coordinates = geometry["coordinates"]
        if coordinates[0] != node_coordinates[start] or coordinates[-1] != node_coordinates[end]:
            raise HokonaviAdapterError(f"{edge_id} geometry endpoints contradict start/end")
        direction = _code(properties["direction"], _DIRECTION, f"{edge_id}.direction")
        structure = _code(properties["rt_struct"], _ROUTE_STRUCTURE, f"{edge_id}.rt_struct")
        route_type = _code(properties["route_type"], _ROUTE_TYPE, f"{edge_id}.route_type")
        width = properties["width"]
        slope_class = properties["vtcl_slope"]
        step_class = properties["lev_diff"]
        for value, name in ((width, "width"), (slope_class, "vtcl_slope"), (step_class, "lev_diff")):
            if type(value) is not int or value not in _CLASS_CODES:
                raise HokonaviAdapterError(f"unsupported {edge_id}.{name}: {value!r}")
        static_width = _one_decimal_or_none(properties["w_min"], f"{edge_id}.w_min")
        slope_value = _integer_or_none(properties["vSlope_max"], f"{edge_id}.vSlope_max")
        step_value = _integer_or_none(properties["levDif_max"], f"{edge_id}.levDif_max")
        if width == 99 and static_width is not None:
            raise HokonaviAdapterError("UNKNOWN width class cannot carry w_min")
        if slope_class == 99 and slope_value is not None:
            raise HokonaviAdapterError("UNKNOWN slope class cannot carry vSlope_max")
        if step_class == 99 and step_value is not None:
            raise HokonaviAdapterError("UNKNOWN step class cannot carry levDif_max")
        connector = _connector(route_type, properties["stair"], properties["elevator"])
        r_method = properties["r_method"]
        if not isinstance(r_method, str) or len(r_method) != 3 or any(character not in _METHOD for character in r_method):
            raise HokonaviAdapterError("r_method must contain three reviewed method codes")
        maint_date = _validate_date(properties["maint_date"], f"{edge_id}.maint_date")
        rank = _text(properties["rank"], f"{edge_id}.rank")
        if rank is None or not re.fullmatch(r"[A-Z0-9]{3}", rank):
            raise HokonaviAdapterError(f"{edge_id}.rank must be a three-character source code")
        provenance = {
            "start_time": _start_time_provenance(properties),
            "direction": _source_provenance(direction, _DIRECTION[direction]),
            "width": _source_provenance(width, "UNKNOWN" if width == 99 else width),
            "vtcl_slope": _source_provenance(slope_class, "UNKNOWN" if slope_class == 99 else slope_class),
            "lev_diff": _source_provenance(step_class, "UNKNOWN" if step_class == 99 else step_class),
            "rt_struct": _source_provenance(structure, _ROUTE_STRUCTURE[structure]),
            "route_type": _source_provenance(route_type, _ROUTE_TYPE[route_type]),
            "elevator": _source_provenance(properties["elevator"], "UNKNOWN" if properties["elevator"] == 99 else properties["elevator"]),
        }
        edge: dict[str, object] = {
            "edge_id": edge_id,
            "from_node": start,
            "to_node": end,
            "geometry": geometry,
            "length_m": _finite(properties["distance"], f"{edge_id}.distance", minimum=0.000000001),
            "travel_direction": _DIRECTION[direction],
            "travel_direction_code": direction,
            "route_structure": _ROUTE_STRUCTURE[structure],
            "route_structure_code": structure,
            "route_type": _ROUTE_TYPE[route_type],
            "route_type_code": route_type,
            "clear_width_static_class": "UNKNOWN" if width == 99 else width,
            "clear_width_static_m": static_width,
            "clear_width_static_measurement": {"source_field": "w_min", "unit": "m", "resolution_m": 0.1},
            "hokonavi_rank": rank,
            "longitudinal_slope_class": "UNKNOWN" if slope_class == 99 else slope_class,
            "slope_estimate_percent": slope_value,
            "slope_measurement": {"source_field": "vSlope_max", "unit": "percent", "precision": "integer"},
            "step_class": "UNKNOWN" if step_class == 99 else step_class,
            "step_height_cm": step_value,
            "step_measurement": {"source_field": "levDif_max", "unit": "cm", "precision": "integer"},
            "connector": connector,
            "connector_sidecar": {
                "stair_count": connector["stair_count"],
                "elevator_code": connector["elevator_code"],
            },
            "validity": {"maint_date": maint_date},
            "source_value_provenance": provenance,
            "source_sidecar": {
                "source_role": "SOURCE_FACT",
                "hokonavi_r_method_raw": r_method,
                "source_method": {
                    "width": _METHOD[r_method[0]],
                    "longitudinal_slope": _METHOD[r_method[1]],
                    "step": _METHOD[r_method[2]],
                },
                "loss_ids": [],
            },
        }
        source_unknown = {
            name: value
            for name, value in (
                ("direction", direction),
                ("width", width),
                ("vtcl_slope", slope_class),
                ("lev_diff", step_class),
            )
            if value == 99
        }
        if source_unknown:
            edge["source_unknown"] = source_unknown
        edge["source_sidecar"]["loss_ids"] = _edge_losses(edge)
        edges.append(edge)

    nodes.sort(key=lambda item: str(item["node_id"]))
    edges.sort(key=lambda item: str(item["edge_id"]))
    result: dict[str, object] = {
        "fixture_status": fixture_status,
        "crs_metadata": {
            "name": "JGD2011",
            "axis_order": ["longitude", "latitude"],
        },
        "mapping_reachability": deepcopy(_MAPPING_REACHABILITY),
        "nodes": nodes,
        "edges": edges,
    }
    if ablepath_sidecar is not None:
        result["ablepath_sidecar"] = validate_sidecar(ablepath_sidecar, edge_ids=set(str(value) for value in link_ids))
    canonical_json_bytes(result)
    return result


def _validate_internal_node(node: Mapping[str, object]) -> dict[str, object]:
    _exact_keys(node, _INTERNAL_NODE_KEYS, "node")
    code = _code(node["in_out_code"], _IN_OUT, "node.in_out_code")
    if node["node_type"] != _IN_OUT[code]:
        raise HokonaviAdapterError("node_type contradicts in_out_code")
    geometry = _geometry(node["geometry"], "Point", "node.geometry")
    latitude = _finite(node["latitude"], "node.latitude")
    longitude = _finite(node["longitude"], "node.longitude")
    if geometry["coordinates"] != [longitude, latitude]:
        raise HokonaviAdapterError("node coordinates contradict geometry")
    source = _mapping(node["source_sidecar"], "node.source_sidecar")
    _exact_keys(source, {"source_role", "loss_ids"}, "node.source_sidecar", optional={"elevation_m"})
    if source["source_role"] != "SOURCE_FACT":
        raise HokonaviAdapterError("node source role must be SOURCE_FACT")
    expected_losses = set(_NODE_BASE_LOSSES)
    if "elevation_m" in source:
        _finite(source["elevation_m"], "node.elevation_m")
        expected_losses.add("LOSS-ABLEPATH-CORE-ABSENT")
    _exact_loss_ids(source["loss_ids"], sorted(expected_losses), "node.source_sidecar.loss_ids")
    return geometry


def _validate_internal_edge(edge: Mapping[str, object]) -> None:
    _exact_keys(edge, _INTERNAL_EDGE_KEYS, "edge", optional={"source_unknown"})
    direction = _code(edge["travel_direction_code"], _DIRECTION, "edge.travel_direction_code")
    structure = _code(edge["route_structure_code"], _ROUTE_STRUCTURE, "edge.route_structure_code")
    route_type = _code(edge["route_type_code"], _ROUTE_TYPE, "edge.route_type_code")
    if edge["travel_direction"] != _DIRECTION[direction]:
        raise HokonaviAdapterError("travel direction label contradicts source code")
    if edge["route_structure"] != _ROUTE_STRUCTURE[structure]:
        raise HokonaviAdapterError("route structure label contradicts source code")
    if edge["route_type"] != _ROUTE_TYPE[route_type]:
        raise HokonaviAdapterError("route type label contradicts source code")
    width_code = 99 if edge["clear_width_static_class"] == "UNKNOWN" else edge["clear_width_static_class"]
    slope_code = 99 if edge["longitudinal_slope_class"] == "UNKNOWN" else edge["longitudinal_slope_class"]
    step_code = 99 if edge["step_class"] == "UNKNOWN" else edge["step_class"]
    for value, name in ((width_code, "width"), (slope_code, "vtcl_slope"), (step_code, "lev_diff")):
        if type(value) is not int or value not in _CLASS_CODES:
            raise HokonaviAdapterError(f"edge {name} class is invalid")
    _one_decimal_or_none(edge["clear_width_static_m"], "edge.clear_width_static_m")
    _integer_or_none(edge["slope_estimate_percent"], "edge.slope_estimate_percent")
    _integer_or_none(edge["step_height_cm"], "edge.step_height_cm")
    if edge["clear_width_static_measurement"] != {"source_field": "w_min", "unit": "m", "resolution_m": 0.1}:
        raise HokonaviAdapterError("static width measurement metadata changed")
    if edge["slope_measurement"] != {"source_field": "vSlope_max", "unit": "percent", "precision": "integer"}:
        raise HokonaviAdapterError("slope measurement metadata changed")
    if edge["step_measurement"] != {"source_field": "levDif_max", "unit": "cm", "precision": "integer"}:
        raise HokonaviAdapterError("step measurement metadata changed")
    connector = _mapping(edge["connector"], "edge.connector")
    _exact_keys(connector, {"stairs", "stair_count", "is_ramp", "is_elevator", "elevator_code"}, "edge.connector")
    expected_connector = _connector(route_type, connector["stair_count"], connector["elevator_code"])
    if dict(connector) != expected_connector:
        raise HokonaviAdapterError("connector values contradict route_type")
    connector_sidecar = _mapping(edge["connector_sidecar"], "edge.connector_sidecar")
    expected_connector_sidecar = {
        "stair_count": connector["stair_count"],
        "elevator_code": connector["elevator_code"],
    }
    if dict(connector_sidecar) != expected_connector_sidecar:
        raise HokonaviAdapterError("connector sidecar contradicts connector values")
    expected_source_unknown = {
        name: value
        for name, value in (
            ("direction", direction),
            ("width", width_code),
            ("vtcl_slope", slope_code),
            ("lev_diff", step_code),
        )
        if value == 99
    }
    if edge.get("source_unknown") != (expected_source_unknown or None):
        raise HokonaviAdapterError("source_unknown must exactly mirror source code 99 values")
    validity = _mapping(edge["validity"], "edge.validity")
    _exact_keys(validity, {"maint_date"}, "edge.validity")
    _validate_date(validity["maint_date"], "edge.validity.maint_date")
    source = _mapping(edge["source_sidecar"], "edge.source_sidecar")
    _exact_keys(source, {"source_role", "hokonavi_r_method_raw", "source_method", "loss_ids"}, "edge.source_sidecar")
    if source["source_role"] != "SOURCE_FACT":
        raise HokonaviAdapterError("edge source role must be SOURCE_FACT")
    r_method = source["hokonavi_r_method_raw"]
    if not isinstance(r_method, str) or len(r_method) != 3 or any(character not in _METHOD for character in r_method):
        raise HokonaviAdapterError("edge r_method is invalid")
    expected_methods = {
        "width": _METHOD[r_method[0]],
        "longitudinal_slope": _METHOD[r_method[1]],
        "step": _METHOD[r_method[2]],
    }
    if source["source_method"] != expected_methods:
        raise HokonaviAdapterError("edge source methods contradict r_method")
    provenance = _mapping(edge["source_value_provenance"], "edge.source_value_provenance")
    expected_provenance = {
        "direction": _source_provenance(direction, _DIRECTION[direction]),
        "width": _source_provenance(width_code, "UNKNOWN" if width_code == 99 else width_code),
        "vtcl_slope": _source_provenance(slope_code, "UNKNOWN" if slope_code == 99 else slope_code),
        "lev_diff": _source_provenance(step_code, "UNKNOWN" if step_code == 99 else step_code),
        "rt_struct": _source_provenance(structure, _ROUTE_STRUCTURE[structure]),
        "route_type": _source_provenance(route_type, _ROUTE_TYPE[route_type]),
        "elevator": _source_provenance(connector["elevator_code"], "UNKNOWN" if connector["elevator_code"] == 99 else connector["elevator_code"]),
    }
    _exact_keys(provenance, {"start_time", *expected_provenance}, "edge.source_value_provenance")
    for key, expected in expected_provenance.items():
        if provenance[key] != expected:
            raise HokonaviAdapterError(f"edge provenance for {key} contradicts source value")
    start_time = _mapping(provenance["start_time"], "edge.start_time provenance")
    kind = start_time.get("kind")
    if kind == "MISSING_ATTRIBUTE":
        _exact_keys(start_time, {"kind", "normalized"}, "edge.start_time provenance")
        if start_time["normalized"] != "UNKNOWN":
            raise HokonaviAdapterError("missing start_time must remain UNKNOWN")
    elif kind in {"SOURCE_CODE_99", "SEMANTIC_BLANK", "SOURCE_VALUE"}:
        _exact_keys(start_time, {"kind", "raw", "normalized"}, "edge.start_time provenance")
        if _start_time_provenance({"start_time": start_time["raw"]}) != dict(start_time):
            raise HokonaviAdapterError("start_time provenance is inconsistent")
    else:
        raise HokonaviAdapterError("start_time provenance kind is invalid")
    _exact_loss_ids(source["loss_ids"], _edge_losses(edge), "edge.source_sidecar.loss_ids")
    _geometry(edge["geometry"], "LineString", "edge.geometry")
    _finite(edge["length_m"], "edge.length_m", minimum=0.000000001)


def export_hokonavi_2024(
    internal: Mapping[str, object],
    *,
    include_sidecar: bool,
) -> dict[str, object]:
    """Export source fields and preserve all AblePath-only data externally."""

    if type(include_sidecar) is not bool:
        raise HokonaviAdapterError("include_sidecar must be boolean")
    value = _mapping(internal, "internal network")
    _exact_keys(value, _INTERNAL_TOP_KEYS, "internal network", optional={"ablepath_sidecar"})
    expected_crs = {
        "name": "JGD2011",
        "axis_order": ["longitude", "latitude"],
    }
    if value["crs_metadata"] != expected_crs:
        raise HokonaviAdapterError("internal CRS metadata changed")
    if value["mapping_reachability"] != _MAPPING_REACHABILITY:
        raise HokonaviAdapterError("mapping reachability contract changed")
    if value["fixture_status"] != "SYNTHETIC":
        raise HokonaviAdapterError("bounded prototype requires fixture_status=SYNTHETIC")
    nodes = _list(value["nodes"], "internal.nodes")
    edges = _list(value["edges"], "internal.edges")
    edge_ids = {str(_mapping(edge, "edge").get("edge_id")) for edge in edges}
    sidecar_value = value.get("ablepath_sidecar")
    if sidecar_value is not None and not include_sidecar:
        raise HokonaviAdapterError("AblePath-only data requires an external sidecar")
    validated_sidecar = None
    if sidecar_value is not None:
        validated_sidecar = validate_sidecar(sidecar_value, edge_ids=edge_ids)

    features: list[dict[str, object]] = []
    for raw_node in sorted(nodes, key=lambda item: str(_mapping(item, "node").get("node_id"))):
        node = _mapping(raw_node, "node")
        geometry = _validate_internal_node(node)
        properties: dict[str, object] = {
            "fixture_status": "SYNTHETIC",
            "entity": "node",
            "node_id": node["node_id"],
            "lat": node["latitude"],
            "lon": node["longitude"],
            "floor": node["level"],
            "in_out": node["in_out_code"],
        }
        source = _mapping(node["source_sidecar"], "node.source_sidecar")
        if "elevation_m" in source:
            properties["elevation"] = source["elevation_m"]
        for index, edge_id in enumerate(_list(node["incident_edge_ids"], "node.incident_edge_ids"), start=1):
            properties[f"link{index}_id"] = edge_id
        features.append({"type": "Feature", "geometry": geometry, "properties": properties})

    for raw_edge in sorted(edges, key=lambda item: str(_mapping(item, "edge").get("edge_id"))):
        edge = _mapping(raw_edge, "edge")
        _validate_internal_edge(edge)
        connector = _mapping(edge["connector"], "edge.connector")
        source = _mapping(edge["source_sidecar"], "edge.source_sidecar")
        validity = _mapping(edge["validity"], "edge.validity")
        provenance = _mapping(edge["source_value_provenance"], "edge.source_value_provenance")
        width_code = 99 if edge["clear_width_static_class"] == "UNKNOWN" else edge["clear_width_static_class"]
        slope_code = 99 if edge["longitudinal_slope_class"] == "UNKNOWN" else edge["longitudinal_slope_class"]
        step_code = 99 if edge["step_class"] == "UNKNOWN" else edge["step_class"]
        properties = {
            "fixture_status": "SYNTHETIC",
            "entity": "link",
            "link_id": edge["edge_id"],
            "start_id": edge["from_node"],
            "end_id": edge["to_node"],
            "distance": edge["length_m"],
            "rank": edge["hokonavi_rank"],
            "r_method": source["hokonavi_r_method_raw"],
            "maint_date": validity["maint_date"],
            "rt_struct": edge["route_structure_code"],
            "route_type": edge["route_type_code"],
            "direction": edge["travel_direction_code"],
            "width": width_code,
            "w_min": edge["clear_width_static_m"],
            "vtcl_slope": slope_code,
            "vSlope_max": edge["slope_estimate_percent"],
            "lev_diff": step_code,
            "levDif_max": edge["step_height_cm"],
            "stair": connector["stair_count"],
            "elevator": connector["elevator_code"],
        }
        start_time = _mapping(provenance["start_time"], "edge.start_time provenance")
        if start_time["kind"] != "MISSING_ATTRIBUTE":
            properties["start_time"] = start_time["raw"]
        features.append({"type": "Feature", "geometry": deepcopy(edge["geometry"]), "properties": properties})

    network = {
        "type": "FeatureCollection",
        "fixture_status": "SYNTHETIC",
        "crs_metadata": {"name": "JGD2011", "coordinate_representation": "decimal_degrees"},
        "features": features,
    }
    import_hokonavi_2024(network, ablepath_sidecar=validated_sidecar)
    loss_by_entity = {
        str(node["node_id"]): list(_mapping(node["source_sidecar"], "node.source_sidecar")["loss_ids"])
        for node in nodes
    }
    loss_by_entity.update({
        str(edge["edge_id"]): list(_mapping(edge["source_sidecar"], "edge.source_sidecar")["loss_ids"])
        for edge in edges
    })
    output = {
        "network": network,
        "ablepath_sidecar": deepcopy(validated_sidecar) if include_sidecar else None,
        "information_loss": {
            "status": "PARTIAL_WITH_EXPLICIT_LOSS",
            "loss_ids_by_entity": dict(sorted(loss_by_entity.items())),
            "loss_ids_by_mapping": _mapping_loss_ids(),
            "mapping_status_counts": {
                "FULL": 10,
                "PARTIAL": 18,
                "SIDECAR_REQUIRED": 10,
                "UNMAPPED": 1,
                "NOT_APPLICABLE": 1,
            },
        },
    }
    canonical_json_bytes(output)
    return output
