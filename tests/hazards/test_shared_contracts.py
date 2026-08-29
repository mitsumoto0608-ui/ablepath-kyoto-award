"""Tests for the versioned, profile-independent overnight hazard contracts."""

from __future__ import annotations

import copy
import csv
import json
from dataclasses import FrozenInstanceError
import math
from numbers import Real
from pathlib import Path
import re

import pytest
import yaml

from src.citypacks import loader as loader_module
from src.citypacks.loader import CityPackContractError, load_citypack, require_supported_major
from src.citypacks.source_manifest import (
    ARASHIYAMA_V1_FIELDS,
    FUJISAWA_V1_FIELDS,
    KIYOMIZU_V1_FIELDS,
    SourceManifestContractError,
    load_source_manifest,
)
from src.hazards.contracts import (
    EdgeHazardObservation,
    EdgeScenarioPhysics,
    HazardContractError,
    HazardScenario,
    validate_dense_observations,
)


ROOT = Path(__file__).resolve().parents[2]


def _schema_accepts(instance: object, schema: dict, root: dict | None = None) -> bool:
    """Evaluate the dependency-free JSON Schema subset used by shipped contracts."""
    root = schema if root is None else root
    if "$ref" in schema:
        target: object = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]  # type: ignore[index]
        return _schema_accepts(instance, target, root)  # type: ignore[arg-type]
    if "allOf" in schema and not all(
        _schema_accepts(instance, item, root) for item in schema["allOf"]
    ):
        return False
    if "anyOf" in schema and not any(
        _schema_accepts(instance, item, root) for item in schema["anyOf"]
    ):
        return False
    if "oneOf" in schema and sum(
        _schema_accepts(instance, item, root) for item in schema["oneOf"]
    ) != 1:
        return False
    if "not" in schema and _schema_accepts(instance, schema["not"], root):
        return False
    if "if" in schema:
        branch = "then" if _schema_accepts(instance, schema["if"], root) else "else"
        if branch in schema and not _schema_accepts(instance, schema[branch], root):
            return False

    expected_types = schema.get("type")
    if expected_types is not None:
        expected = {expected_types} if isinstance(expected_types, str) else set(expected_types)

        def matches_type(name: str) -> bool:
            return {
                "object": isinstance(instance, dict),
                "array": isinstance(instance, list),
                "string": isinstance(instance, str),
                "number": isinstance(instance, Real)
                and not isinstance(instance, bool)
                and math.isfinite(float(instance)),
                "integer": isinstance(instance, int) and not isinstance(instance, bool),
                "boolean": type(instance) is bool,
                "null": instance is None,
            }[name]

        if not any(matches_type(name) for name in expected):
            return False
    serialized = json.dumps(instance, ensure_ascii=False, sort_keys=True)
    if "const" in schema and serialized != json.dumps(
        schema["const"], ensure_ascii=False, sort_keys=True
    ):
        return False
    if "enum" in schema and serialized not in {
        json.dumps(item, ensure_ascii=False, sort_keys=True) for item in schema["enum"]
    }:
        return False
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            return False
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            return False
    if isinstance(instance, Real) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            return False
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            return False
        if schema.get("uniqueItems") and len({
            json.dumps(item, ensure_ascii=False, sort_keys=True) for item in instance
        }) != len(instance):
            return False
        if "items" in schema and not all(
            _schema_accepts(item, schema["items"], root) for item in instance
        ):
            return False
    if isinstance(instance, dict):
        if len(instance) < schema.get("minProperties", 0):
            return False
        if not set(schema.get("required", ())) <= set(instance):
            return False
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(instance) - set(properties):
            return False
        if any(
            key in properties and not _schema_accepts(value, properties[key], root)
            for key, value in instance.items()
        ):
            return False
    return True


def _city_document() -> dict:
    return {
        "schema_version": "1.0.0",
        "citypack_schema_version": "1.0.0",
        "hazard_schema_version": "1.0.0",
        "viewer_data_schema_version": "1.0.0",
        "city_id": "fixture_city",
        "data_status": "SYNTHETIC_DEMO",
        "official_metadata_status": "OFFICIAL_METADATA_ONLY",
        "schema_compatibility": {
            "supported_major": 1,
            "unsupported_major_policy": "REJECT_WITH_ACTIONABLE_ERROR",
            "migration_policy": "RECORD_REQUIRED_MIGRATION_NO_IMPLICIT_CONVERSION",
        },
        "readiness": {
            "facility_status": "UNKNOWN",
            "entrance_status": "UNKNOWN",
            "capacity_status": "UNKNOWN",
            "operation_status": "UNKNOWN",
            "demand_status": "UNKNOWN",
            "origin_status": "UNKNOWN",
            "profile_status": "NOT_COMPUTED",
            "kpi_status": "NOT_COMPUTED",
            "m6_status": "NOT_COMPUTED",
        },
        "kpis": {
            "physically_reachable": {"value": None, "reason": "TOPOLOGY_UNAVAILABLE"},
            "accommodated": {"value": None, "reason": "CAPACITY_UNAVAILABLE"},
            "overflow_waiting": {"value": None, "reason": "DEMAND_UNAVAILABLE"},
            "unreachable": {"value": None, "reason": "PROFILE_NOT_COMPUTED"},
            "unknown_affected_upper_bound": {"value": None, "reason": "DEMAND_UNAVAILABLE"},
        },
        "geospatial_contract": {
            "schema_version": "1.0.0",
            "source_crs": "EPSG:4326",
            "processing_crs": "EPSG:6674",
            "output_crs": "EPSG:4326",
            "horizontal_unit": "degree",
            "vertical_unit": "UNKNOWN",
            "axis_order": "lon_lat",
            "coordinate_precision": 6,
            "transform_history": "NOT_EXECUTED_SYNTHETIC_FIXTURE",
            "geometry_status": "SYNTHETIC_DEMO_CANDIDATE",
            "source_feature_id": "FIXTURE_CITY_V1",
            "stable_feature_id": "FIXTURE_CITY",
            "revision_id": "r1",
            "lineage": "FIXTURE_VALUE",
        },
        "completion_levels": {
            "ENGINEERING_UI_COMPLETE": False,
            "DATA_STAGING_COMPLETE": True,
            "REAL_GEOMETRY_CONNECTED": False,
            "MODEL_CONNECTED": False,
            "ADMIN_VALIDATED": False,
            "overall": "PARTIAL_COMPLETE",
        },
    }


def test_citypack_loader_accepts_supported_major_without_reinterpreting_data(tmp_path: Path) -> None:
    """[software_correctness] Supported v1 data is returned as an isolated copy."""
    pack = tmp_path / "fixture_city"
    pack.mkdir()
    source = _city_document()
    (pack / "city.yaml").write_text(yaml.safe_dump(source), encoding="utf-8", newline="\n")
    loaded = load_citypack(pack, trusted_root=tmp_path)
    assert loaded == source
    loaded["city_id"] = "mutated"
    assert load_citypack(pack, trusted_root=tmp_path)["city_id"] == "fixture_city"


@pytest.mark.parametrize("version", ["2.0.0", "0.9.0", "invalid", "1"])
def test_citypack_loader_rejects_unsupported_or_malformed_versions(version: str) -> None:
    """[software_correctness] Unknown majors fail with an actionable migration message."""
    with pytest.raises(CityPackContractError, match="supported major 1|version triplet"):
        require_supported_major(version, contract_name="citypack")


def test_citypack_loader_rejects_kpi_or_profile_false_green(tmp_path: Path) -> None:
    """[source_conformance] Missing prerequisites cannot become zero KPI or computed profile."""
    for mutation in (
        lambda doc: doc["kpis"]["physically_reachable"].update(value=0),
        lambda doc: doc["kpis"]["physically_reachable"].update(reason=""),
        lambda doc: doc["readiness"].update(profile_status="PASS"),
        lambda doc: doc["readiness"].update(m6_status="KNOWN"),
        lambda doc: doc.update(kpis={}),
        lambda doc: doc.update(unversioned_extension=True),
        lambda doc: doc["readiness"].update(unversioned_extension="UNKNOWN"),
        lambda doc: doc["geospatial_contract"].update(unversioned_extension="UNKNOWN"),
    ):
        document = _city_document()
        mutation(document)
        pack = tmp_path / f"pack-{len(list(tmp_path.iterdir()))}"
        pack.mkdir()
        (pack / "city.yaml").write_text(yaml.safe_dump(document), encoding="utf-8", newline="\n")
        with pytest.raises(CityPackContractError):
            load_citypack(pack, trusted_root=tmp_path)


def test_citypack_loader_rejects_duplicate_keys_aliases_and_untrusted_paths(tmp_path: Path) -> None:
    """[software_correctness] Untrusted YAML cannot override keys, expand aliases, or escape its root."""
    duplicate_pack = tmp_path / "duplicate"
    duplicate_pack.mkdir()
    duplicate_payload = yaml.safe_dump(_city_document()) + "city_id: duplicate\n"
    (duplicate_pack / "city.yaml").write_text(duplicate_payload, encoding="utf-8", newline="\n")
    with pytest.raises(CityPackContractError, match="duplicate YAML key"):
        load_citypack(duplicate_pack, trusted_root=tmp_path)

    alias_pack = tmp_path / "alias"
    alias_pack.mkdir()
    (alias_pack / "city.yaml").write_text(
        'schema_version: &version "1.0.0"\ncitypack_schema_version: *version\n',
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(CityPackContractError, match="aliases"):
        load_citypack(alias_pack, trusted_root=tmp_path)

    other_root = tmp_path / "trusted"
    other_root.mkdir()
    with pytest.raises(CityPackContractError, match="trusted_root"):
        load_citypack(duplicate_pack, trusted_root=other_root)


@pytest.mark.parametrize("reparse_name", ["trusted", "city.yaml"])
def test_citypack_loader_rejects_reparse_components_without_platform_privileges(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, reparse_name: str
) -> None:
    """[software_correctness] Root and file reparse points fail before canonicalization."""
    trusted = tmp_path / "trusted"
    pack = trusted / "fixture"
    pack.mkdir(parents=True)
    (pack / "city.yaml").write_text(
        yaml.safe_dump(_city_document()), encoding="utf-8", newline="\n"
    )
    monkeypatch.setattr(
        loader_module,
        "_is_reparse_point",
        lambda path: path.name == reparse_name,
    )
    with pytest.raises(CityPackContractError, match="symlink.*reparse point"):
        load_citypack(pack, trusted_root=trusted)


def test_hazard_scenario_preserves_static_unknown_defaults() -> None:
    """[source_conformance] A static scenario carries source status and never invents elapsed time."""
    scenario = HazardScenario.from_mapping(
        {
            "scenario_id": "RAIN_HEAVY",
            "hazard_type": "FLOOD",
            "source_status": "OFFICIAL_METADATA_ONLY",
            "official_or_assumption": "ABLEPATH_DESIGN",
            "elapsed_time_sec": None,
            "coverage_complete": False,
            "default_edge_state": "UNKNOWN",
            "disclaimer": "静的比較であり道路閉鎖を示さない",
            "source_ids": ["official-metadata-1"],
        }
    )
    assert scenario.elapsed_time_sec is None
    assert scenario.default_edge_state == "UNKNOWN"
    assert scenario.coverage_complete is False
    with pytest.raises(FrozenInstanceError):
        scenario.default_edge_state = "PASS"  # type: ignore[misc]


def test_hazard_scenario_rejects_unclassified_evidence_authority() -> None:
    """[source_conformance] Evidence authority cannot be an arbitrary unreviewed label."""
    with pytest.raises(HazardContractError, match="official_or_assumption"):
        HazardScenario.from_mapping(
            {
                "scenario_id": "S1",
                "hazard_type": "FLOOD",
                "source_status": "OFFICIAL_METADATA_ONLY",
                "official_or_assumption": "TRUST_ME",
                "elapsed_time_sec": None,
                "coverage_complete": False,
                "default_edge_state": "UNKNOWN",
                "disclaimer": "静的比較",
                "source_ids": ["source-1"],
            }
        )


@pytest.mark.parametrize(
    ("source_status", "source_ids"),
    [("SYNTHETIC_DEMO", ["source-1"]), ("OFFICIAL_METADATA_ONLY", [])],
)
def test_hazard_scenario_rejects_false_official_authority(
    source_status: str, source_ids: list[str]
) -> None:
    """[source_conformance] OFFICIAL needs official/real status and traceable source IDs."""
    with pytest.raises(HazardContractError, match="OFFICIAL authority"):
        HazardScenario.from_mapping(
            {
                "scenario_id": "S1",
                "hazard_type": "FLOOD",
                "source_status": source_status,
                "official_or_assumption": "OFFICIAL",
                "elapsed_time_sec": None,
                "coverage_complete": False,
                "default_edge_state": "UNKNOWN",
                "disclaimer": "静的比較",
                "source_ids": source_ids,
            }
        )


def test_observation_keeps_overlap_closure_and_unknown_orthogonal() -> None:
    """[software_correctness] Overlap true does not imply closure or a safe/open state."""
    observation = EdgeHazardObservation.from_mapping(
        {
            "edge_id": "E1",
            "scenario_id": "S1",
            "overlap": True,
            "overlap_length_m": 12.5,
            "max_depth_m": None,
            "mean_depth_m": None,
            "official_closure": None,
            "hazard_data_status": "UNKNOWN",
            "source_ids": ["source-1"],
        }
    )
    assert observation.overlap is True
    assert observation.official_closure is None
    assert observation.hazard_data_status == "UNKNOWN"


@pytest.mark.parametrize(
    ("field", "value"),
    [("hazard_data_status", "OPEN"), ("official_closure", "UNKNOWN"), ("overlap", "YES")],
)
def test_observation_rejects_unsafe_enum_or_type_coercion(field: str, value: object) -> None:
    """[software_correctness] Unknown and tri-state fields are never truthiness-coerced."""
    row = {
        "edge_id": "E1",
        "scenario_id": "S1",
        "overlap": None,
        "overlap_length_m": None,
        "max_depth_m": None,
        "mean_depth_m": None,
        "official_closure": None,
        "hazard_data_status": "UNKNOWN",
        "source_ids": [],
    }
    row[field] = value
    with pytest.raises(HazardContractError):
        EdgeHazardObservation.from_mapping(row)


@pytest.mark.parametrize(
    "mutation",
    [
        {"overlap": None, "overlap_length_m": 1.0},
        {"overlap": None, "max_depth_m": 0.2},
        {"overlap": False, "overlap_length_m": 1.0},
        {"overlap": False, "max_depth_m": 0.2},
        {"overlap": True, "max_depth_m": 0.2, "mean_depth_m": 0.3},
        {"hazard_data_status": "KNOWN"},
    ],
)
def test_observation_rejects_physically_contradictory_rows(mutation: dict) -> None:
    """[software_correctness] Contradictory geometry/depth/status combinations fail closed."""
    row = {
        "edge_id": "E1",
        "scenario_id": "S1",
        "overlap": None,
        "overlap_length_m": None,
        "max_depth_m": None,
        "mean_depth_m": None,
        "official_closure": None,
        "hazard_data_status": "UNKNOWN",
        "source_ids": [],
    }
    row.update(mutation)
    with pytest.raises(HazardContractError):
        EdgeHazardObservation.from_mapping(row)


def test_edge_physics_is_profile_independent_and_finite() -> None:
    """[software_correctness] Physical values remain finite floats with explicit provenance only."""
    physics = EdgeScenarioPhysics.from_mapping(
        {
            "edge_id": "E1",
            "scenario_id": "S1",
            "base_clear_width_m": 3,
            "remaining_clear_width_m": 0,
            "physical_values": {"debris_intrusion_left_m": 3.27},
            "provenance": {
                "data_class": "SYNTHETIC_DEMO",
                "source_ids": ["fixture"],
                "method": "M7 residual width",
                "model": "M7",
                "applied_constant_ids": ["MOYA_DEBRIS_SLOPE"],
            },
        }
    )
    assert type(physics.base_clear_width_m) is float
    assert type(physics.remaining_clear_width_m) is float
    assert physics.remaining_clear_width_m == 0.0
    assert not hasattr(physics, "profile_state")


def test_edge_physics_is_deeply_immutable_and_rejects_profile_state() -> None:
    """[software_correctness] Input aliases cannot mutate provenance and M6/state keys are rejected."""
    source_ids = ["fixture"]
    raw = {
        "edge_id": "E1",
        "scenario_id": "S1",
        "base_clear_width_m": 3.0,
        "remaining_clear_width_m": 2.0,
        "physical_values": {"max_depth_m": None},
        "provenance": {
            "data_class": "SYNTHETIC_DEMO",
            "source_ids": source_ids,
            "method": "static fixture",
            "model": "NONE",
        },
    }
    physics = EdgeScenarioPhysics.from_mapping(raw)
    source_ids.append("MUTATED")
    assert physics.provenance["source_ids"] == ("fixture",)
    with pytest.raises(AttributeError):
        physics.provenance["source_ids"].append("MUTATED")  # type: ignore[union-attr]
    raw["physical_values"] = {"profile_state": 1.0}
    with pytest.raises(HazardContractError, match="non-physical"):
        EdgeScenarioPhysics.from_mapping(raw)
    raw["physical_values"] = {"max_depth_m": None}
    raw["provenance"]["model"] = "M6"
    with pytest.raises(HazardContractError, match="outside EdgeScenarioPhysics"):
        EdgeScenarioPhysics.from_mapping(raw)
    raw["provenance"]["model"] = "M60 flood physics"
    assert EdgeScenarioPhysics.from_mapping(raw).provenance["model"] == "M60 flood physics"


def test_dense_observation_matrix_rejects_missing_duplicate_and_orphan_pairs() -> None:
    """[software_correctness] Every scenario-edge pair appears exactly once."""
    expected = [
        {"scenario_id": "S1", "edge_id": "E1"},
        {"scenario_id": "S1", "edge_id": "E2"},
        {"scenario_id": "S2", "edge_id": "E1"},
        {"scenario_id": "S2", "edge_id": "E2"},
    ]
    validate_dense_observations(["S1", "S2"], ["E1", "E2"], expected)
    for mutant in (
        expected[:-1],
        expected + [expected[0]],
        expected + [{"scenario_id": "ORPHAN", "edge_id": "E1"}],
    ):
        with pytest.raises(HazardContractError):
            validate_dense_observations(["S1", "S2"], ["E1", "E2"], mutant)


def test_dense_observation_matrix_has_cardinality_and_error_output_bounds() -> None:
    """[software_correctness] Untrusted cardinality cannot force unbounded products or logs."""
    with pytest.raises(HazardContractError, match="bounded contract"):
        validate_dense_observations([f"S{i}" for i in range(129)], ["E1"], [])
    with pytest.raises(HazardContractError, match="at least one item"):
        validate_dense_observations([], ["E1"], [])


def test_json_contract_schemas_are_versioned_and_parseable() -> None:
    """[software_correctness] Shipped JSON contracts declare version and reject extra ambiguity."""
    schema_dir = ROOT / "schemas" / "hazards"
    names = {
        "hazard-scenario.schema.json",
        "edge-hazard-observation.schema.json",
        "edge-scenario-physics.schema.json",
        "citypack-envelope.schema.json",
    }
    assert {path.name for path in schema_dir.glob("*.schema.json")} == names
    for name in names:
        schema = json.loads((schema_dir / name).read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["x-ablepath-schema-version"] == "1.0.0"
        assert schema["additionalProperties"] is False
        assert schema["required"]
        assert set(schema["required"]) <= set(schema["properties"])
    city_schema = json.loads((schema_dir / "citypack-envelope.schema.json").read_text(encoding="utf-8"))
    for nested in ("schema_compatibility", "readiness", "kpis", "geospatial_contract", "completion_levels"):
        assert city_schema["properties"][nested]["additionalProperties"] is False
    readiness = city_schema["properties"]["readiness"]["properties"]
    for name in (
        "facility_status", "entrance_status", "capacity_status",
        "operation_status", "demand_status", "origin_status",
    ):
        assert readiness[name] == {"$ref": "#/$defs/readinessStatus"}
    geospatial = city_schema["properties"]["geospatial_contract"]["properties"]
    for name in ("axis_order", "transform_history", "lineage", "processing_axis_order"):
        assert geospatial[name] == {"$ref": "#/$defs/nonEmptyTextOrList"}
    scenario_schema = json.loads((schema_dir / "hazard-scenario.schema.json").read_text(encoding="utf-8"))
    official_rule = scenario_schema["allOf"][0]
    assert official_rule["if"]["properties"]["official_or_assumption"] == {"const": "OFFICIAL"}
    assert official_rule["then"]["properties"]["source_ids"] == {"minItems": 1}


def test_json_schema_structural_subset_and_runtime_share_representable_mutants(
    tmp_path: Path,
) -> None:
    """[software_correctness] Representable mutants match; named relational rules remain runtime-only."""
    schema_dir = ROOT / "schemas" / "hazards"
    schemas = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in schema_dir.glob("*.schema.json")
    }

    city_schema = schemas["citypack-envelope.schema.json"]
    assert _schema_accepts(_city_document(), city_schema)
    for name, value in (("display_name", 7), ("supported_hazards", ["EQ", "EQ"])):
        document = _city_document()
        document[name] = value
        assert not _schema_accepts(document, city_schema)
        pack = tmp_path / f"city-{name}"
        pack.mkdir()
        (pack / "city.yaml").write_text(
            yaml.safe_dump(document), encoding="utf-8", newline="\n"
        )
        with pytest.raises(CityPackContractError):
            load_citypack(pack, trusted_root=tmp_path)
    document = _city_document()
    document["geospatial_contract"]["processing_axis_order"] = None
    assert not _schema_accepts(document, city_schema)
    pack = tmp_path / "city-processing-axis"
    pack.mkdir()
    (pack / "city.yaml").write_text(
        yaml.safe_dump(document), encoding="utf-8", newline="\n"
    )
    with pytest.raises(CityPackContractError):
        load_citypack(pack, trusted_root=tmp_path)

    scenario = {
        "scenario_id": "S1",
        "hazard_type": "FLOOD",
        "source_status": "OFFICIAL_METADATA_ONLY",
        "official_or_assumption": "OFFICIAL",
        "elapsed_time_sec": None,
        "coverage_complete": False,
        "default_edge_state": "UNKNOWN",
        "disclaimer": "静的比較",
        "source_ids": ["source-1"],
    }
    scenario_schema = schemas["hazard-scenario.schema.json"]
    assert _schema_accepts(scenario, scenario_schema)
    HazardScenario.from_mapping(scenario)
    false_official = copy.deepcopy(scenario)
    false_official.update(source_status="SYNTHETIC_DEMO", source_ids=[])
    assert not _schema_accepts(false_official, scenario_schema)
    with pytest.raises(HazardContractError):
        HazardScenario.from_mapping(false_official)

    observation = {
        "edge_id": "E1",
        "scenario_id": "S1",
        "overlap": None,
        "overlap_length_m": None,
        "max_depth_m": None,
        "mean_depth_m": None,
        "official_closure": None,
        "hazard_data_status": "UNKNOWN",
        "source_ids": [],
    }
    observation_schema = schemas["edge-hazard-observation.schema.json"]
    assert _schema_accepts(observation, observation_schema)
    EdgeHazardObservation.from_mapping(observation)
    for mutation in (
        {"max_depth_m": 0.2},
        {"overlap": False, "max_depth_m": 0.2},
        {"hazard_data_status": "KNOWN"},
    ):
        invalid = copy.deepcopy(observation)
        invalid.update(mutation)
        assert not _schema_accepts(invalid, observation_schema)
        with pytest.raises(HazardContractError):
            EdgeHazardObservation.from_mapping(invalid)
    runtime_validation = observation_schema["x-ablepath-runtime-validation"]
    assert runtime_validation == {
        "authority": "src.hazards.contracts.EdgeHazardObservation.from_mapping",
        "schema_scope": "STRUCTURAL_SUBSET",
        "required_rules": ["mean_depth_m must not exceed max_depth_m"],
    }
    relational_mutant = copy.deepcopy(observation)
    relational_mutant.update(overlap=True, max_depth_m=0.2, mean_depth_m=0.3)
    assert _schema_accepts(relational_mutant, observation_schema)
    with pytest.raises(HazardContractError, match="mean_depth_m"):
        EdgeHazardObservation.from_mapping(relational_mutant)

    physics = {
        "edge_id": "E1",
        "scenario_id": "S1",
        "base_clear_width_m": 3.0,
        "remaining_clear_width_m": 2.0,
        "physical_values": {"max_depth_m": None},
        "provenance": {
            "data_class": "SYNTHETIC_DEMO",
            "source_ids": ["fixture"],
            "method": "static fixture",
            "model": "M7",
        },
    }
    physics_schema = schemas["edge-scenario-physics.schema.json"]
    assert _schema_accepts(physics, physics_schema)
    EdgeScenarioPhysics.from_mapping(physics)
    invalid_physics = copy.deepcopy(physics)
    invalid_physics["provenance"]["model"] = "M6"
    assert not _schema_accepts(invalid_physics, physics_schema)
    with pytest.raises(HazardContractError):
        EdgeScenarioPhysics.from_mapping(invalid_physics)
    invalid_physics["provenance"]["model"] = "m6-profile"
    assert not _schema_accepts(invalid_physics, physics_schema)
    with pytest.raises(HazardContractError):
        EdgeScenarioPhysics.from_mapping(invalid_physics)
    physics["provenance"]["model"] = "M60"
    assert _schema_accepts(physics, physics_schema)
    EdgeScenarioPhysics.from_mapping(physics)


@pytest.mark.parametrize(
    ("fields", "dialect", "truth_updates"),
    [
        (
            KIYOMIZU_V1_FIELDS,
            "kiyomizu-v1.0.0",
            {
                "source_class": "OFFICIAL_METADATA_ONLY",
                "evidence_class": "OFFICIAL_METADATA_ONLY",
                "data_status": "OFFICIAL_METADATA_ONLY",
                "source_url": "https://example.invalid/source",
            },
        ),
        (
            ARASHIYAMA_V1_FIELDS,
            "arashiyama-v1.0.0",
            {
                "record_kind": "OFFICIAL_METADATA",
                "data_class": "OFFICIAL_METADATA_ONLY",
                "source_url": "https://example.invalid/source",
                "artifact_schema_version": "1.0.0",
            },
        ),
        (
            FUJISAWA_V1_FIELDS,
            "fujisawa-v1.0.0",
            {
                "source_class": "OFFICIAL_METADATA_ONLY",
                "url": "https://example.invalid/source",
                "schema_version": "1.0.0",
            },
        ),
    ],
)
def test_source_manifest_dialects_normalize_without_truth_promotion(
    tmp_path: Path,
    fields: tuple[str, ...],
    dialect: str,
    truth_updates: dict[str, str],
) -> None:
    """[source_conformance] Exact legacy v1 headers map to one immutable truth model."""
    path = tmp_path / f"{dialect}.csv"
    row = {name: "" for name in fields}
    row.update(
        dataset_id="source-1",
        freshness_status="UNKNOWN",
        download_status="METADATA_ONLY",
        **truth_updates,
    )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)
    records = load_source_manifest(path)
    assert len(records) == 1
    assert records[0].schema_version == "1.0.0"
    assert records[0].dialect_id == dialect
    assert records[0].record_kind == "OFFICIAL_METADATA"
    assert records[0].data_class == "OFFICIAL_METADATA_ONLY"
    with pytest.raises(TypeError):
        records[0].raw["data_class"] = "REAL"  # type: ignore[index]
    for unsupported_class in ("SYNTHETIC_DEMO", "UNKNOWN", "MODEL_DERIVED"):
        invalid_row = dict(row)
        if dialect == "kiyomizu-v1.0.0":
            invalid_row.update(
                source_class=unsupported_class,
                evidence_class=unsupported_class,
                data_status=unsupported_class,
            )
        elif dialect == "arashiyama-v1.0.0":
            invalid_row["data_class"] = unsupported_class
        else:
            invalid_row["source_class"] = unsupported_class
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerow(invalid_row)
        with pytest.raises(SourceManifestContractError, match="data_class"):
            load_source_manifest(path)


def test_source_manifest_adapter_rejects_unknown_schema_truth_and_duplicates(
    tmp_path: Path,
) -> None:
    """[software_correctness] Unknown headers/classes/majors and duplicate IDs fail closed."""
    path = tmp_path / "manifest.csv"

    def write(fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    base = {name: "" for name in ARASHIYAMA_V1_FIELDS}
    base.update(
        dataset_id="source-1",
        record_kind="OFFICIAL_METADATA",
        data_class="OFFICIAL_METADATA_ONLY",
        source_url="https://example.invalid/source",
        freshness_status="UNKNOWN",
        download_status="METADATA_ONLY",
        artifact_schema_version="1.0.0",
    )
    write(ARASHIYAMA_V1_FIELDS + ("unexpected",), [{**base, "unexpected": "x"}])
    with pytest.raises(SourceManifestContractError, match="unsupported.*header"):
        load_source_manifest(path)
    invalid = dict(base, data_class="REALISH")
    write(ARASHIYAMA_V1_FIELDS, [invalid])
    with pytest.raises(SourceManifestContractError, match="data_class"):
        load_source_manifest(path)
    for data_class, record_kind in (
        ("UNKNOWN", "OFFICIAL_METADATA"),
        ("SYNTHETIC_DEMO", "OFFICIAL_METADATA"),
        ("MODEL_DERIVED", "OFFICIAL_METADATA"),
        ("OFFICIAL_METADATA_ONLY", "VGI_METADATA"),
        ("VGI_METADATA_ONLY", "OFFICIAL_METADATA"),
    ):
        invalid = dict(base, data_class=data_class, record_kind=record_kind)
        write(ARASHIYAMA_V1_FIELDS, [invalid])
        with pytest.raises(SourceManifestContractError, match="data_class|contradicts"):
            load_source_manifest(path)
    invalid = dict(base, artifact_schema_version="2.0.0")
    write(ARASHIYAMA_V1_FIELDS, [invalid])
    with pytest.raises(SourceManifestContractError, match="unsupported.*schema"):
        load_source_manifest(path)
    write(ARASHIYAMA_V1_FIELDS, [base, base])
    with pytest.raises(SourceManifestContractError, match="duplicate.*dataset_id"):
        load_source_manifest(path)
