"""[software_correctness] Fail-closed validators for the M7 V2 candidate input contracts.

This module decides, *before* the frozen M7 core is ever considered, whether an
evidence record is (a) a well-formed record and (b) eligible to become M7
production input. It never imports or calls the frozen residual-width core, it
never mutates its inputs, and it never invents a value: every rejection is
reported as an explicit, greppable ``E_*`` error code.

Two distinct verdicts are returned by every validator:

``ValidationResult.ok`` / ``ValidationResult.errors``
    Whether the record is structurally and semantically well formed under the
    contract. A record can be perfectly valid and still be permanently
    ineligible (the ``PROXY_NOT_SETBACK`` worked example is exactly that).

``ValidationResult.eligibility``
    ``{"eligible": bool, "reason": str}`` - whether the record may enter M7
    production. Fail-closed: anything not explicitly allowed is ineligible, and
    a record with ``ok=False`` is always ineligible.

Metric CRS handling is deliberately split the same way: a geographic CRS is a
hard record error (``E_CRS_GEOGRAPHIC``, a prohibited derivation), while a
well-formed projected CRS outside :data:`PROJECTED_CRS_ALLOWLIST` is a record
that is valid but not eligible (``E_CRS_NOT_ALLOWLISTED``).

This module is pure, deterministic and stdlib-only. ``jsonschema`` is used for
schema validation when importable, but every fail-closed rule below is
implemented explicitly in Python and is never delegated to JSON Schema.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # pragma: no cover - exercised by whichever branch the environment has
    import jsonschema as _jsonschema
except ImportError:  # pragma: no cover
    _jsonschema = None

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"

SCHEMA_NAMES = {
    "setback": "m7_setback_evidence_v2.schema.json",
    "damage_state": "m7_damage_state_evidence_v2.schema.json",
    "debris_presence": "m7_debris_presence_evidence_v2.schema.json",
    "scenario_realization": "m7_scenario_realization_v1.schema.json",
}

RECORD_KINDS = ("setback", "damage_state", "debris_presence",
                "scenario_realization", "height")

#: Projected metric CRS codes accepted for M7 setback geometry.
PROJECTED_CRS_ALLOWLIST = {"EPSG:6674", "EPSG:6677"}

#: Geographic (angular) CRS codes that are never valid for a metric distance.
GEOGRAPHIC_CRS_DENYLIST = {"EPSG:4326", "EPSG:4612", "EPSG:6668", "EPSG:6697"}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CRS_RE = re.compile(r"^EPSG:[0-9]+$")

#: M7 core categorical damage states (mirrors candidate_network.M7_DAMAGE_STATES).
M7_CORE_DAMAGE_STATES = {"COLLAPSED", "DAMAGED"}

#: Intensity measures that are hazard exposure only and can never be mapped.
HAZARD_EXPOSURE_ONLY_MEASURES = {
    "PGA",
    "PGV",
    "SA",
    "SI",
    "JMA_INSTRUMENTAL_SEISMIC_INTENSITY",
    "INUNDATION_DEPTH",
    "LANDSLIDE_ZONE_OVERLAP",
    "LIQUEFACTION_ZONE_OVERLAP",
    "HAZARD_EXPOSURE_ONLY",
}

PROBABILITY_SUM_TOLERANCE = 1e-6

#: Declared damage-state vocabularies, keyed "<damage_taxonomy_id>@<version>".
#: A distribution whose taxonomy is not registered here cannot have its keys
#: checked, so it is never eligible either way (a distribution is never a state).
DECLARED_TAXONOMY_STATES = {
    "JP-MLIT-BUILDING-DAMAGE-CLASS@2024.1": frozenset({
        "NO_DAMAGE",
        "PARTIAL_DAMAGE",
        "HALF_COLLAPSE",
        "LARGE_SCALE_HALF_COLLAPSE",
        "COMPLETE_COLLAPSE",
    }),
}

#: lod1HeightType provenance codes and their M7 disposition.
HEIGHT_METHOD_FLAGS = {
    "2": "POINT_CLOUD_MEDIAN",
    "6": "AERIAL_PHOTOGRAMMETRY_MAX",
}
HEIGHT_UNIFORM_CODE = "0"
HEIGHT_STOREY_ESTIMATE_CODE = "9"
HEIGHT_SENTINEL_VALUE = -9999


class M7EvidenceContractError(ValueError):
    """Raised for programming errors in the use of this module."""


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validating one evidence record against its V2 contract."""

    ok: bool
    errors: list[str] = field(default_factory=list)
    eligibility: dict = field(default_factory=dict)


_INELIGIBLE_INVALID = "E_RECORD_INVALID"


def _ineligible(reason: str) -> dict:
    return {"eligible": False, "reason": reason}


def _eligible(reason: str) -> dict:
    return {"eligible": True, "reason": reason}


# --------------------------------------------------------------------------
# schema loading / structural validation
# --------------------------------------------------------------------------

_SCHEMA_CACHE: dict[str, dict] = {}


def _is_finite_real(value: Any) -> bool:
    """Return true only for finite JSON-style real numbers, never booleans."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def load_schema(name: str) -> dict:
    """Load one M7 contract schema by short name or by file name."""
    if not isinstance(name, str) or not name:
        raise M7EvidenceContractError("schema name must be a non-empty string")
    filename = SCHEMA_NAMES.get(name, name)
    if not filename.endswith(".schema.json"):
        raise M7EvidenceContractError(f"unknown schema name: {name}")
    if filename in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[filename]
    path = SCHEMA_DIR / filename
    if not path.is_file():
        raise M7EvidenceContractError(f"schema file not found: {filename}")
    schema = json.loads(path.read_text(encoding="utf-8"))
    _SCHEMA_CACHE[filename] = schema
    return schema


def _type_ok(value: Any, expected: Any) -> bool:
    names = expected if isinstance(expected, list) else [expected]
    for name in names:
        if name == "null" and value is None:
            return True
        if name == "boolean" and isinstance(value, bool):
            return True
        if name == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if name == "number" and _is_finite_real(value):
            return True
        if name == "string" and isinstance(value, str):
            return True
        if name == "object" and isinstance(value, dict):
            return True
        if name == "array" and isinstance(value, list):
            return True
    return False


def _structural_check(schema: dict, instance: Any, root: dict, path: str,
                      errors: list[str]) -> None:
    """Minimal structural JSON Schema check for the subset used by M7 schemas."""
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise M7EvidenceContractError(f"unsupported $ref: {ref}")
        _structural_check(root["$defs"][ref.split("/")[-1]], instance, root, path,
                          errors)
        return
    for subschema in schema.get("allOf", []):
        _structural_check(subschema, instance, root, path, errors)
    if "if" in schema:
        probe: list[str] = []
        _structural_check(schema["if"], instance, root, path, probe)
        branch = "then" if not probe else "else"
        if branch in schema:
            _structural_check(schema[branch], instance, root, path, errors)
    if "const" in schema and instance != schema["const"]:
        errors.append(f"E_SCHEMA_INVALID:{path}:const")
        return
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"E_SCHEMA_INVALID:{path}:enum")
        return
    if "type" in schema and not _type_ok(instance, schema["type"]):
        errors.append(f"E_SCHEMA_INVALID:{path}:type")
        return
    if isinstance(instance, str):
        pattern = schema.get("pattern")
        if pattern is not None and re.search(pattern, instance) is None:
            errors.append(f"E_SCHEMA_INVALID:{path}:pattern")
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"E_SCHEMA_INVALID:{path}:minLength")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"E_SCHEMA_INVALID:{path}:minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"E_SCHEMA_INVALID:{path}:maximum")
    if isinstance(instance, list) and "items" in schema:
        for index, item in enumerate(instance):
            _structural_check(schema["items"], item, root, f"{path}[{index}]", errors)
    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"E_SCHEMA_INVALID:{path}.{name}:required")
        if len(instance) < schema.get("minProperties", 0):
            errors.append(f"E_SCHEMA_INVALID:{path}:minProperties")
        extra = schema.get("additionalProperties")
        names_schema = schema.get("propertyNames")
        for key, value in instance.items():
            child = f"{path}.{key}"
            if names_schema is not None:
                _structural_check(names_schema, key, root, f"{child}:name", errors)
            if key in properties:
                _structural_check(properties[key], value, root, child, errors)
            elif extra is False:
                errors.append(f"E_SCHEMA_INVALID:{child}:additionalProperties")
            elif isinstance(extra, dict):
                _structural_check(extra, value, root, child, errors)


def _schema_errors(schema_name: str, record: Any) -> list[str]:
    schema = load_schema(schema_name)
    if _jsonschema is not None:
        validator = _jsonschema.Draft202012Validator(schema)
        return [
            "E_SCHEMA_INVALID:"
            + ("/".join(str(part) for part in error.absolute_path) or "<root>")
            + f":{error.validator}"
            for error in sorted(validator.iter_errors(record),
                                key=lambda err: list(err.absolute_path))
        ]
    errors: list[str] = []
    _structural_check(schema, record, schema, "<root>", errors)
    return errors


def _require_mapping(record: Any) -> list[str]:
    if not isinstance(record, dict):
        return ["E_NOT_A_MAPPING"]
    return []


def _sha_errors(record: dict, fields: tuple[str, ...], null_allowed: bool,
                code_prefix: str) -> list[str]:
    """Check SHA-256 receipt fields; null is allowed only for UNKNOWN records."""
    errors: list[str] = []
    for name in fields:
        value = record.get(name)
        if value is None:
            if not null_allowed:
                errors.append(f"{code_prefix}_SHA256_MISSING:{name}")
            continue
        if not isinstance(value, str) or SHA256_RE.match(value) is None:
            errors.append(f"E_SHA256_MALFORMED:{name}")
    return errors


def _identity_errors(record: dict, fields: tuple[str, ...],
                     null_allowed: bool) -> list[str]:
    errors: list[str] = []
    for name in fields:
        value = record.get(name)
        if value is None or value == "":
            if not null_allowed:
                errors.append(f"E_SOURCE_IDENTITY_MISSING:{name}")
        elif not isinstance(value, str):
            errors.append(f"E_SOURCE_IDENTITY_MISSING:{name}")
    return errors


# --------------------------------------------------------------------------
# setback
# --------------------------------------------------------------------------


def _setback_errors(record: dict) -> list[str]:
    errors: list[str] = []
    setback_status = record.get("setback_status")
    boundary_role = record.get("boundary_role")
    evidence_status = record.get("evidence_status")
    geometry_role = record.get("building_geometry_role")
    method = record.get("measurement_or_derivation_method")
    setback_value = record.get("setback_value_m")

    if setback_value is not None and not _is_finite_real(setback_value):
        errors.append("E_SETBACK_VALUE_INVALID")

    # A proxy record is a record only; it can never claim eligibility.
    if setback_status == "PROXY_NOT_SETBACK" and evidence_status == "ACCEPTED":
        errors.append("E_PROXY_NOT_SETBACK_PROMOTED")
    if boundary_role == "CANDIDATE_CENTERLINE_PROXY":
        if setback_status != "PROXY_NOT_SETBACK":
            errors.append("E_CENTERLINE_PROXY_AS_SETBACK")
        if evidence_status == "ACCEPTED":
            errors.append("E_PROXY_NOT_SETBACK_PROMOTED")
    if geometry_role == "CENTROID_FORBIDDEN":
        errors.append("E_CENTROID_FORBIDDEN_ROLE")
    if isinstance(method, str) and "centroid" in method.casefold():
        errors.append("E_CENTROID_METHOD")
    if boundary_role == "UNKNOWN" and evidence_status == "ACCEPTED":
        errors.append("E_BOUNDARY_ROLE_UNKNOWN_PROMOTED")

    receipts_may_be_null = setback_status in {"PROXY_NOT_SETBACK", "UNKNOWN"}
    errors.extend(_sha_errors(
        record, ("boundary_sha256", "building_sha256"), receipts_may_be_null, "E"))
    errors.extend(_identity_errors(
        record,
        ("boundary_source_id", "boundary_revision_id", "building_source_id",
         "building_revision_id"),
        receipts_may_be_null,
    ))

    start = record.get("station_start_m")
    end = record.get("station_end_m")
    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
        if start > end:
            errors.append("E_STATION_ORDER_INVALID")

    crs = record.get("metric_crs")
    if not isinstance(crs, str) or CRS_RE.match(crs) is None:
        errors.append("E_CRS_MALFORMED")
    elif crs in GEOGRAPHIC_CRS_DENYLIST:
        errors.append("E_CRS_GEOGRAPHIC")
    return errors


def _setback_eligibility(record: dict) -> dict:
    setback_status = record.get("setback_status")
    boundary_role = record.get("boundary_role")
    if setback_status == "PROXY_NOT_SETBACK" or boundary_role == "CANDIDATE_CENTERLINE_PROXY":
        return _ineligible("E_SETBACK_PROXY_NEVER_ELIGIBLE")
    if setback_status == "UNKNOWN" or boundary_role == "UNKNOWN":
        return _ineligible("E_SETBACK_UNKNOWN_NEVER_ELIGIBLE")
    if setback_status == "RESEARCH_DERIVED_EXPERIMENTAL":
        return _ineligible("E_SETBACK_EXPERIMENTAL_NOT_PRODUCTION")
    if boundary_role == "OFFICIAL_ROAD_BOUNDARY_PROXY":
        return _ineligible("E_ROAD_BOUNDARY_OFFSET_CONTRACT_NOT_FROZEN")
    if setback_status not in {"OBSERVED_FIELD", "OFFICIAL_BOUNDARY_DERIVED"}:
        return _ineligible("E_SETBACK_STATUS_NOT_ELIGIBLE")
    if record.get("building_geometry_role") not in {"FRONTAGE_LINE", "FOOTPRINT_EDGE"}:
        return _ineligible("E_SETBACK_GEOMETRY_ROLE_NOT_ELIGIBLE")
    if record.get("evidence_status") != "ACCEPTED":
        return _ineligible("E_SETBACK_EVIDENCE_NOT_ACCEPTED")
    if record.get("coverage_status") != "COMPLETE":
        return _ineligible("E_SIDE_COVERAGE_INCOMPLETE")
    crs = record.get("metric_crs")
    if crs not in PROJECTED_CRS_ALLOWLIST:
        return _ineligible("E_CRS_NOT_ALLOWLISTED")
    if setback_status == "OFFICIAL_BOUNDARY_DERIVED":
        if not record.get("transform_id") or not record.get("transform_version"):
            return _ineligible("E_SETBACK_TRANSFORM_NOT_FROZEN")
    setback_value = record.get("setback_value_m")
    if not _is_finite_real(setback_value):
        return _ineligible("E_SETBACK_VALUE_MISSING")
    return _eligible("ELIGIBLE_CANDIDATE_ACCEPTED_RECEIPT")


def validate_setback_evidence(record: Any) -> ValidationResult:
    """[software_correctness] Validate one M7 setback evidence record (V2)."""
    return _validate("setback", record)


# --------------------------------------------------------------------------
# damage state
# --------------------------------------------------------------------------


def _damage_errors(record: dict) -> list[str]:
    errors: list[str] = []
    kind = record.get("evidence_kind")
    mapping = record.get("mapping_to_m7_core")
    mapping_status = record.get("mapping_status")
    intensity = record.get("intensity_measure_type")
    probabilities = record.get("damage_state_probabilities")

    if mapping is not None and mapping not in M7_CORE_DAMAGE_STATES:
        errors.append("E_MAPPING_NOT_CORE_STATE")

    # Hazard exposure can never become a categorical building damage state.
    if intensity in HAZARD_EXPOSURE_ONLY_MEASURES:
        if mapping is not None:
            errors.append("E_EXPOSURE_MAPPED_TO_DAMAGE")
        if mapping_status not in {"MAPPING_FORBIDDEN_EXPOSURE_ONLY", "NOT_MAPPED"}:
            errors.append("E_EXPOSURE_MAPPING_STATUS_INVALID")

    if kind == "MODEL_PROBABILITY_DISTRIBUTION":
        if mapping is not None:
            errors.append("E_DISTRIBUTION_MAPPED_TO_CATEGORICAL")
        if record.get("realized_state") is not None:
            errors.append("E_DISTRIBUTION_REALIZED_STATE_SET")
        if not isinstance(probabilities, dict) or not probabilities:
            errors.append("E_PROBABILITIES_MISSING")

    if isinstance(probabilities, dict) and probabilities:
        probability_values_valid = all(
            _is_finite_real(value)
            and 0.0 <= value <= 1.0
            for value in probabilities.values()
        )
        if not probability_values_valid:
            errors.append("E_PROBABILITY_VALUE_INVALID")
        elif abs(sum(probabilities.values()) - 1.0) > PROBABILITY_SUM_TOLERANCE:
            errors.append("E_PROBABILITIES_NOT_NORMALISED")
        key = f"{record.get('damage_taxonomy_id')}@{record.get('damage_taxonomy_version')}"
        declared = DECLARED_TAXONOMY_STATES.get(key)
        if declared is not None and not set(probabilities) <= declared:
            errors.append("E_PROBABILITY_KEY_NOT_IN_TAXONOMY")
        if not record.get("damage_taxonomy_id") or not record.get(
                "damage_taxonomy_version"):
            errors.append("E_TAXONOMY_VERSION_MISSING")

    if kind == "UNKNOWN" and mapping is not None:
        errors.append("E_UNKNOWN_COERCED_TO_DAMAGED")

    if mapping is not None:
        if mapping_status != "MAPPED_EXPLICIT":
            errors.append("E_MAPPING_STATUS_INCONSISTENT")
        if not record.get("damage_taxonomy_version") or not record.get(
                "damage_taxonomy_id"):
            errors.append("E_TAXONOMY_VERSION_MISSING")
        if kind in {"OBSERVED_POST_EVENT", "OFFICIAL_ASSET_LEVEL_SCENARIO"}:
            # A written mapping may await its receipt, but a rejected record
            # can never carry one. Acceptance itself is an eligibility gate.
            if record.get("validation_status") == "REJECTED":
                errors.append("E_MAPPING_WITHOUT_ACCEPTED_BASIS")
        elif kind == "MODEL_REALIZATION_EXPERIMENTAL":
            if not isinstance(record.get("realization_seed"), int) or isinstance(
                    record.get("realization_seed"), bool):
                errors.append("E_REALIZATION_SEED_MISSING")
            if not record.get("realization_id"):
                errors.append("E_REALIZATION_ID_MISSING")
            if not record.get("realization_method"):
                errors.append("E_REALIZATION_METHOD_MISSING")
        else:
            errors.append("E_MAPPING_WITHOUT_ACCEPTED_BASIS")

    if record.get("realized_state") is not None and kind not in {
            "OBSERVED_POST_EVENT", "OFFICIAL_ASSET_LEVEL_SCENARIO",
            "MODEL_REALIZATION_EXPERIMENTAL"}:
        errors.append("E_REALIZED_STATE_NOT_ALLOWED")

    unknown_kind = kind == "UNKNOWN"
    errors.extend(_sha_errors(record, ("source_sha256",), unknown_kind, "E"))
    errors.extend(_identity_errors(record, ("source_id", "revision_id"), unknown_kind))
    return errors


def _damage_eligibility(record: dict) -> dict:
    kind = record.get("evidence_kind")
    if kind == "UNKNOWN":
        return _ineligible("E_DAMAGE_UNKNOWN_NEVER_ELIGIBLE")
    if kind == "MODEL_PROBABILITY_DISTRIBUTION":
        return _ineligible("E_DAMAGE_DISTRIBUTION_NEVER_ELIGIBLE")
    if kind == "MODEL_REALIZATION_EXPERIMENTAL":
        return _ineligible("E_DAMAGE_EXPERIMENTAL_NOT_PRODUCTION")
    if record.get("mapping_status") != "MAPPED_EXPLICIT" or record.get(
            "mapping_to_m7_core") is None:
        return _ineligible("E_DAMAGE_NOT_MAPPED")
    if record.get("validation_status") != "ACCEPTED":
        return _ineligible("E_DAMAGE_NOT_ACCEPTED")
    if not record.get("damage_taxonomy_version"):
        return _ineligible("E_TAXONOMY_VERSION_MISSING")
    return _eligible("ELIGIBLE_ACCEPTED_EXPLICIT_MAPPING")


def validate_damage_state_evidence(record: Any) -> ValidationResult:
    """[software_correctness] Validate one M7 damage-state evidence record (V2)."""
    return _validate("damage_state", record)


# --------------------------------------------------------------------------
# debris presence
# --------------------------------------------------------------------------


def _debris_errors(record: dict) -> list[str]:
    errors: list[str] = []
    kind = record.get("debris_evidence_kind")
    mapping = record.get("mapping_to_m7_core")
    observed = record.get("observed_debris_present")
    realized = record.get("realized_debris_present")

    if kind == "CONDITIONAL_PROBABILITY" and mapping is not None:
        errors.append("E_PROBABILITY_THRESHOLD_TO_BOOL")
    if record.get("probability_of_presence") is not None and mapping is not None \
            and observed is None and realized is None:
        errors.append("E_PROBABILITY_THRESHOLD_TO_BOOL")
    if kind == "UNKNOWN" and mapping is not None:
        errors.append("E_UNKNOWN_COERCED_TO_FALSE")

    basis_present = observed is not None or realized is not None
    if mapping is not None and record.get("extent_model_id") and not basis_present:
        errors.append("E_EXTENT_USED_AS_PRESENCE")

    if kind in {"OBSERVED", "OFFICIAL_ASSET_LEVEL_SCENARIO"}:
        if mapping is not None:
            if not isinstance(observed, bool):
                errors.append("E_DEBRIS_MAPPING_WITHOUT_ACCEPTED_BASIS")
            if record.get("validation_status") == "REJECTED":
                errors.append("E_DEBRIS_MAPPING_WITHOUT_ACCEPTED_BASIS")
            if mapping != observed:
                errors.append("E_DEBRIS_MAPPING_CONTRADICTS_BASIS")
    elif kind == "EXPERIMENTAL_STOCHASTIC_REALIZATION":
        seed = record.get("realization_seed")
        if not isinstance(seed, int) or isinstance(seed, bool):
            errors.append("E_DEBRIS_REALIZATION_SEED_MISSING")
        if not record.get("realization_id"):
            errors.append("E_DEBRIS_REALIZATION_ID_MISSING")
        if not record.get("probability_model_id") or not record.get(
                "probability_model_version"):
            errors.append("E_DEBRIS_PROBABILITY_MODEL_MISSING")
    elif mapping is not None:
        errors.append("E_DEBRIS_MAPPING_WITHOUT_ACCEPTED_BASIS")

    if realized is not None and kind != "EXPERIMENTAL_STOCHASTIC_REALIZATION":
        errors.append("E_REALIZED_FLAG_NOT_ALLOWED")
    if observed is not None and kind not in {"OBSERVED", "OFFICIAL_ASSET_LEVEL_SCENARIO"}:
        errors.append("E_OBSERVED_FLAG_NOT_ALLOWED")
    if mapping is not None and not record.get("damage_state_evidence_id"):
        errors.append("E_DEBRIS_WITHOUT_DAMAGE_STATE_LINK")

    unknown_kind = kind == "UNKNOWN"
    errors.extend(_sha_errors(record, ("source_sha256",), unknown_kind, "E"))
    errors.extend(_identity_errors(record, ("source_id", "revision_id"), unknown_kind))
    return errors


def _debris_eligibility(record: dict) -> dict:
    kind = record.get("debris_evidence_kind")
    if kind == "UNKNOWN":
        return _ineligible("E_DEBRIS_UNKNOWN_NEVER_ELIGIBLE")
    if kind == "CONDITIONAL_PROBABILITY":
        return _ineligible("E_DEBRIS_PROBABILITY_NEVER_ELIGIBLE")
    if kind == "EXPERIMENTAL_STOCHASTIC_REALIZATION":
        return _ineligible("E_DEBRIS_EXPERIMENTAL_NOT_PRODUCTION")
    if not isinstance(record.get("mapping_to_m7_core"), bool):
        return _ineligible("E_DEBRIS_NOT_MAPPED")
    if record.get("validation_status") != "ACCEPTED":
        return _ineligible("E_DEBRIS_NOT_ACCEPTED")
    if not isinstance(record.get("observed_debris_present"), bool):
        return _ineligible("E_DEBRIS_MAPPING_WITHOUT_ACCEPTED_BASIS")
    return _eligible("ELIGIBLE_ACCEPTED_OBSERVED_BOOLEAN")


def validate_debris_presence_evidence(record: Any) -> ValidationResult:
    """[software_correctness] Validate one M7 debris-presence evidence record (V2)."""
    return _validate("debris_presence", record)


# --------------------------------------------------------------------------
# scenario realization
# --------------------------------------------------------------------------


def _scenario_errors(record: dict) -> list[str]:
    errors: list[str] = []
    if record.get("experimental_only") is not True:
        errors.append("E_SCENARIO_EXPERIMENTAL_ONLY_FALSE")
    if record.get("production_eligible") is not False:
        errors.append("E_SCENARIO_PRODUCTION_ELIGIBLE_TRUE")
    seed = record.get("seed")
    if not isinstance(seed, int) or isinstance(seed, bool):
        errors.append("E_SEED_MISSING")
    generator = record.get("random_generator")
    if not isinstance(generator, str) or not generator:
        errors.append("E_RANDOM_GENERATOR_MISSING")
    for name in ("damage_distribution_sha256", "realization_sha256"):
        value = record.get(name)
        if not isinstance(value, str) or SHA256_RE.match(value) is None:
            errors.append(f"E_SHA256_MALFORMED:{name}")
    for name in ("hazard_model", "exposure_model", "building_taxonomy_mapping",
                 "fragility_model", "debris_probability_model"):
        model = record.get(name)
        if not isinstance(model, dict):
            errors.append(f"E_SOURCE_IDENTITY_MISSING:{name}")
            continue
        if not model.get("model_id") or not model.get("model_version"):
            errors.append(f"E_SOURCE_IDENTITY_MISSING:{name}")
        sha = model.get("source_sha256")
        if sha is not None and (not isinstance(sha, str)
                                or SHA256_RE.match(sha) is None):
            errors.append(f"E_SHA256_MALFORMED:{name}.source_sha256")
    return errors


def _scenario_eligibility(record: dict) -> dict:
    return _ineligible("E_SCENARIO_NEVER_PRODUCTION_ELIGIBLE")


def validate_scenario_realization(record: Any) -> ValidationResult:
    """[software_correctness] Validate one M7 scenario realization record (V1)."""
    return _validate("scenario_realization", record)


# --------------------------------------------------------------------------
# height provenance
# --------------------------------------------------------------------------


def _height_errors(record: dict) -> list[str]:
    """Height policy per reports/M7_HEIGHT_PROVENANCE_DECISION.json."""
    errors: list[str] = []
    status = record.get("height_status")
    code = record.get("height_provenance_lod1HeightType")
    value = record.get("official_height_m")

    if code is not None and not isinstance(code, str):
        code = str(code)

    if status == "INVALID_SENTINEL" or value == HEIGHT_SENTINEL_VALUE:
        errors.append("E_HEIGHT_INVALID_SENTINEL")
    elif code == HEIGHT_UNIFORM_CODE:
        errors.append("E_HEIGHT_UNIFORM_VALUE_NOT_EVIDENCE")
    elif code == HEIGHT_STOREY_ESTIMATE_CODE:
        errors.append("E_HEIGHT_STOREY_ESTIMATE_NOT_ELIGIBLE")
    elif code in HEIGHT_METHOD_FLAGS:
        flag = record.get("height_method_flag")
        if flag is None:
            errors.append("E_HEIGHT_METHOD_FLAG_MISSING")
        elif flag != HEIGHT_METHOD_FLAGS[code]:
            errors.append("E_HEIGHT_METHOD_FLAG_NOT_DISTINCT")
        if not _is_finite_real(value):
            errors.append("E_HEIGHT_VALUE_MISSING")
        elif value <= 0:
            errors.append("E_HEIGHT_VALUE_MISSING")
    else:
        errors.append("E_HEIGHT_PROVENANCE_CODE_UNKNOWN")
    return errors


def _height_eligibility(record: dict) -> dict:
    """No height class is production eligible: M7_HEIGHT_POLICY_READY is false."""
    code = record.get("height_provenance_lod1HeightType")
    if code is not None and not isinstance(code, str):
        code = str(code)
    if record.get("height_status") == "INVALID_SENTINEL" or record.get(
            "official_height_m") == HEIGHT_SENTINEL_VALUE:
        return _ineligible("E_HEIGHT_INVALID_SENTINEL")
    if code == HEIGHT_UNIFORM_CODE:
        return _ineligible("E_HEIGHT_UNIFORM_VALUE_NOT_EVIDENCE")
    if code == HEIGHT_STOREY_ESTIMATE_CODE:
        return _ineligible("E_HEIGHT_STOREY_ESTIMATE_NOT_ELIGIBLE")
    if code in HEIGHT_METHOD_FLAGS:
        return _ineligible("E_HEIGHT_CANDIDATE_ONLY_NOT_FROZEN")
    return _ineligible("E_HEIGHT_PROVENANCE_CODE_UNKNOWN")


def validate_height_evidence(record: Any) -> ValidationResult:
    """[source_conformance] Validate one PLATEAU height provenance record."""
    errors = _require_mapping(record)
    if errors:
        return ValidationResult(False, errors, _ineligible(_INELIGIBLE_INVALID))
    for name in ("official_height_m", "height_status",
                 "height_provenance_lod1HeightType"):
        if name not in record:
            errors.append(f"E_MISSING_FIELD:{name}")
    if errors:
        return ValidationResult(False, errors, _ineligible(_INELIGIBLE_INVALID))
    errors = _height_errors(record)
    eligibility = (_height_eligibility(record) if not errors
                   else _ineligible(errors[0].split(":")[0]))
    return ValidationResult(not errors, errors, eligibility)


# --------------------------------------------------------------------------
# side coverage
# --------------------------------------------------------------------------


def validate_side_coverage(area: Any) -> ValidationResult:
    """[software_correctness] A side may be promoted only with a COMPLETE receipt.

    ``PACKAGE_COMPLETE_*`` is an acquisition-package receipt, not an M7 side
    coverage receipt, and is explicitly insufficient.
    """
    errors = _require_mapping(area)
    if errors:
        return ValidationResult(False, errors, _ineligible(_INELIGIBLE_INVALID))
    status = area.get("coverage_status")
    if not isinstance(status, str) or not status:
        return ValidationResult(
            False, ["E_MISSING_FIELD:coverage_status"],
            _ineligible("E_SIDE_COVERAGE_NOT_COMPLETE_RECEIPT"))
    if status == "COMPLETE":
        return ValidationResult(True, [], _eligible("SIDE_COVERAGE_COMPLETE"))
    if status.startswith("PACKAGE_COMPLETE"):
        return ValidationResult(
            True, [], _ineligible("E_SIDE_COVERAGE_NOT_COMPLETE_RECEIPT"))
    return ValidationResult(True, [], _ineligible("E_SIDE_COVERAGE_INCOMPLETE"))


# --------------------------------------------------------------------------
# dispatch
# --------------------------------------------------------------------------

_RULES = {
    "setback": (_setback_errors, _setback_eligibility),
    "damage_state": (_damage_errors, _damage_eligibility),
    "debris_presence": (_debris_errors, _debris_eligibility),
    "scenario_realization": (_scenario_errors, _scenario_eligibility),
}


def _validate(record_kind: str, record: Any) -> ValidationResult:
    errors = _require_mapping(record)
    if errors:
        return ValidationResult(False, errors, _ineligible(_INELIGIBLE_INVALID))
    errors = _schema_errors(record_kind, record)
    errors.extend(_RULES[record_kind][0](record))
    if errors:
        return ValidationResult(False, errors, _ineligible(_INELIGIBLE_INVALID))
    return ValidationResult(True, [], _RULES[record_kind][1](record))


def m7_eligibility(record_kind: str, record: Any) -> dict:
    """Return ``{"eligible": bool, "reason": str}`` for one record, fail-closed."""
    if record_kind not in RECORD_KINDS:
        raise M7EvidenceContractError(f"E_UNKNOWN_RECORD_KIND:{record_kind}")
    if record_kind == "height":
        return validate_height_evidence(record).eligibility
    return _validate(record_kind, record).eligibility
