"""Contract tests for Phase 2 official-geometry overlap observations."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from src.hazards import (
    EDGE_HAZARD_OBSERVATION_V2_FIELDS,
    EdgeHazardObservationV2,
    HazardContractError,
    HazardScenario,
    derive_edge_hazard_observation_v2,
)
from src.citypacks import (
    ValidatedGeometryIndex,
    VerifiedArtifactIndex,
    load_real_artifact_manifest,
    load_validated_geometry_manifest,
)


ROOT = Path(__file__).resolve().parents[2]


def _schema_constraint_accepts(value: object, constraint: dict[str, object]) -> bool:
    """Evaluate the small JSON-Schema keyword subset used by the v2 fixture."""

    if "const" in constraint and value != constraint["const"]:
        return False
    if "enum" in constraint and value not in constraint["enum"]:
        return False
    expected_type = constraint.get("type")
    types = expected_type if isinstance(expected_type, list) else [expected_type]
    if expected_type is not None:
        type_matches = {
            "null": value is None,
            "boolean": type(value) is bool,
            "number": type(value) in {int, float},
            "string": isinstance(value, str),
            "array": isinstance(value, list),
        }
        if not any(type_matches.get(str(item), False) for item in types):
            return False
    if isinstance(value, str) and len(value) < int(constraint.get("minLength", 0)):
        return False
    if isinstance(value, list):
        if len(value) < int(constraint.get("minItems", 0)):
            return False
        if "maxItems" in constraint and len(value) > int(constraint["maxItems"]):
            return False
        if constraint.get("uniqueItems") is True and len(value) != len(set(value)):
            return False
    if type(value) in {int, float} and "minimum" in constraint:
        if float(value) < float(constraint["minimum"]):
            return False
    return True


def _v2_schema_accepts(schema: dict[str, object], instance: dict[str, object]) -> bool:
    """Evaluate required/base/conditional semantics without a new dependency."""

    required = schema["required"]
    properties = schema["properties"]
    if not isinstance(required, list) or not isinstance(properties, dict):
        return False
    if set(instance) != set(required) or set(instance) != set(properties):
        return False
    if any(
        not _schema_constraint_accepts(instance[name], constraint)
        for name, constraint in properties.items()
        if isinstance(constraint, dict)
    ):
        return False
    for branch in schema["allOf"]:
        condition = branch.get("if", {}).get("properties", {})
        applies = all(
            _schema_constraint_accepts(instance[name], constraint)
            for name, constraint in condition.items()
        )
        if applies:
            constraints = branch.get("then", {}).get("properties", {})
            if any(
                not _schema_constraint_accepts(instance[name], constraint)
                for name, constraint in constraints.items()
            ):
                return False
    return True


def _artifact_record(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "city_id": "kyoto_arashiyama",
        "artifact_id": "arashiyama-osm-corridor-v1",
        "artifact_path": "geography/corridor.real.geojson",
        "artifact_role": "CORRIDOR_GEOMETRY",
        "source_id": "osm-bounded-20260829",
        "source_url": "https://www.openstreetmap.org/copyright",
        "source_reference": None,
        "source_class": "VGI",
        "data_class": "REAL",
        "accessed_at": "2026-08-30",
        "valid_as_of": "2026-08-29",
        "valid_as_of_reason": None,
        "license": "ODbL-1.0",
        "license_terms_url": "https://opendatacommons.org/licenses/odbl/1-0/",
        "license_review_status": "AGENT_REVIEWED_HUMAN_PENDING",
        "redistribution_status": "PERMITTED_WITH_OBLIGATIONS",
        "redistribution_obligations": ["attribution", "share-alike database terms"],
        "sha256": "a" * 64,
        "source_artifact_path": "sources/osm-source.raw.json",
        "source_sha256": "b" * 64,
        "retrieval_method": "BOUNDED_QUERY",
        "retrieval_query_path": "sources/osm-corridor.overpassql",
        "retrieval_query_sha256": hashlib.sha256(b"fixture bounded query\n").hexdigest(),
        "snapshot_at": "2026-08-29T00:00:00Z",
        "snapshot_reason": None,
        "source_revision": "OSM snapshot 2026-08-29T00:00:00Z",
        "source_crs": "EPSG:4326",
        "processing_crs": "EPSG:4326",
        "output_crs": "EPSG:4326",
        "axis_order": "longitude_latitude",
        "horizontal_unit": "degree",
        "vertical_datum": None,
        "vertical_datum_reason": "2D source geometry has no vertical datum",
        "transform_history": ["bounded extract; no coordinate transform"],
        "source_feature_id": "way/1",
        "stable_feature_id": "kyoto-arashiyama:edge:osm-way-1",
        "revision_id": "osm-20260829-r1",
        "lineage": ["bounded source feature", "no implicit topology join"],
        "geometry_status": "SOURCE_TRACEABLE_REAL",
    }
    value.update(updates)
    return value


def _feature(record: dict[str, object], geometry: dict[str, object]) -> dict[str, object]:
    properties: dict[str, object] = {
        "city_id": record["city_id"],
        "artifact_id": record["artifact_id"],
        "source_id": record["source_id"],
        "source_class": record["source_class"],
        "data_class": record["data_class"],
        "source_feature_id": record["source_feature_id"],
        "stable_feature_id": record["stable_feature_id"],
        "revision_id": record["revision_id"],
        "lineage": record["lineage"],
        "geometry_status": record["geometry_status"],
    }
    if record["artifact_role"] == "CORRIDOR_GEOMETRY":
        properties.update(
            {
                "bridge": "UNKNOWN",
                "bridge_reason": "source tag absent in fixture",
                "tunnel": "UNKNOWN",
                "tunnel_reason": "source tag absent in fixture",
                "layer": None,
                "layer_reason": "source tag absent in fixture",
                "level": None,
                "level_reason": "source tag absent in fixture",
            }
        )
    else:
        properties.update(
            {
                "hazard_type": "FLOOD",
                "hazard_category": None,
                "hazard_category_reason": "category semantics not reviewed",
                "hazard_value": None,
                "hazard_value_unit": None,
                "hazard_value_reason": "source fixture has no numeric value",
            }
        )
    return {
        "type": "Feature",
        "id": record["stable_feature_id"],
        "geometry": geometry,
        "properties": properties,
    }


def _verified_artifact_index(
    tmp_path: Path,
    *,
    hazard_coordinates: list[list[list[float]]] | None = None,
    edge_geometry: dict[str, object] | None = None,
    hazard_geometry: dict[str, object] | None = None,
) -> ValidatedGeometryIndex:
    root = tmp_path / "city-root"
    (root / "geography").mkdir(parents=True)
    (root / "hazards").mkdir()
    (root / "sources").mkdir()
    (root / "sources" / "osm-corridor.overpassql").write_text(
        "fixture bounded query\n", encoding="utf-8", newline="\n"
    )
    edge = _artifact_record()
    hazard = _artifact_record(
        artifact_id="official-flood-polygons-v1",
        artifact_path="hazards/official-flood.real.geojson",
        artifact_role="OFFICIAL_HAZARD_GEOMETRY",
        source_id="official-flood-geometry",
        source_url="https://www.city.kyoto.lg.jp/example/flood",
        source_class="OFFICIAL",
        source_artifact_path="sources/official-source.raw.json",
        license="Kyoto-City-Open-Data-Terms",
        license_terms_url="https://www.city.kyoto.lg.jp/example/terms",
        retrieval_method="OFFICIAL_DOWNLOAD",
        retrieval_query_path=None,
        retrieval_query_sha256=None,
        snapshot_at=None,
        snapshot_reason="official download has no historical query endpoint",
        source_revision="official revision 2026-08-01",
        source_feature_id="flood/45",
        stable_feature_id="kyoto-arashiyama:hazard:flood-45",
        revision_id="official-20260801-r1",
        lineage=["official polygon feature", "category semantics not inferred"],
    )
    payloads = {
        str(edge["artifact_path"]): {
            "type": "FeatureCollection",
            "features": [
                _feature(
                    edge,
                    edge_geometry or {
                        "type": "LineString",
                        "coordinates": [[135.676, 35.011], [135.677, 35.012]],
                    },
                )
            ],
        },
        str(hazard["artifact_path"]): {
            "type": "FeatureCollection",
            "features": [
                _feature(
                    hazard,
                    hazard_geometry or {
                        "type": "Polygon",
                        "coordinates": hazard_coordinates or [
                            [
                                [135.675, 35.010],
                                [135.678, 35.010],
                                [135.678, 35.013],
                                [135.675, 35.010],
                            ]
                        ],
                    },
                )
            ],
        },
    }
    records: list[dict[str, object]] = []
    for record in (edge, hazard):
        source_bytes = (
            json.dumps(
                {"fixture_source_id": record["source_id"]},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
        (root / str(record["source_artifact_path"])).write_bytes(source_bytes)
        payload_bytes = (
            json.dumps(
                payloads[str(record["artifact_path"])],
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
        path = root / str(record["artifact_path"])
        path.write_bytes(payload_bytes)
        records.append(
            {
                **record,
                "sha256": hashlib.sha256(payload_bytes).hexdigest(),
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
            }
        )
    manifest = root / "sources" / "real-artifacts-v2.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "2.0.0",
                "city_id": "kyoto_arashiyama",
                "artifacts": sorted(records, key=lambda item: str(item["stable_feature_id"])),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
        newline="\n",
    )
    return load_validated_geometry_manifest(
        manifest,
        trusted_root=root,
        expected_city_id="kyoto_arashiyama",
    )


def _scenario(
    scenario_id: str,
    *,
    hazard_type: str = "FLOOD",
    source_ids: list[str] | None = None,
    source_status: str = "REAL",
    authority: str = "OFFICIAL",
    coverage_complete: bool = False,
    default_edge_state: str = "UNKNOWN",
    elapsed_time_sec: float | None = None,
) -> HazardScenario:
    return HazardScenario.from_mapping(
        {
            "scenario_id": scenario_id,
            "hazard_type": hazard_type,
            "source_status": source_status,
            "official_or_assumption": authority,
            "elapsed_time_sec": elapsed_time_sec,
            "coverage_complete": coverage_complete,
            "default_edge_state": default_edge_state,
            "disclaimer": "static geometry predicate; no safety or closure guarantee",
            "source_ids": (
                source_ids
                if source_ids is not None
                else ["official-flood-geometry"]
            ),
        }
    )


def _unknown_scenario() -> HazardScenario:
    return _scenario(
        "flood-static-snapshot",
        source_ids=[],
        source_status="UNKNOWN",
        authority="UNKNOWN",
    )


def _unknown(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": "2.0.0",
        "edge_id": "kyoto-arashiyama:edge:osm-way-1",
        "scenario_id": "flood-static-snapshot",
        "hazard_type": "FLOOD",
        "scenario_source_status": "UNKNOWN",
        "scenario_authority": "UNKNOWN",
        "scenario_coverage_complete": False,
        "scenario_default_edge_state": "UNKNOWN",
        "scenario_source_ids": [],
        "scenario_elapsed_time_sec": None,
        "overlap": None,
        "overlap_length_m": None,
        "max_depth_m": None,
        "mean_depth_m": None,
        "coverage_status": "UNKNOWN",
        "official_closure": None,
        "hazard_data_status": "UNKNOWN",
        "data_class": "UNKNOWN",
        "source_ids": ["osm-bounded-20260829"],
        "hazard_geometry_artifact_ids": [],
        "edge_geometry_artifact_ids": ["arashiyama-osm-corridor-v1"],
        "official_closure_source_ids": [],
        "intersecting_hazard_feature_ids": [],
        "source_feature_ids": ["way/1"],
        "revision_ids": ["osm-20260829-r1"],
        "method": "not computed because official hazard geometry is unavailable",
        "lineage": ["official metadata only", "no spatial intersection performed"],
    }
    value.update(updates)
    return value


def _known_overlap(**updates: object) -> dict[str, object]:
    value = _unknown(
        overlap=True,
        overlap_length_m=12.5,
        max_depth_m=1.2,
        mean_depth_m=0.7,
        coverage_status="PARTIAL",
        hazard_data_status="KNOWN",
        data_class="MODEL_DERIVED",
        scenario_source_status="REAL",
        scenario_authority="OFFICIAL",
        scenario_coverage_complete=False,
        scenario_default_edge_state="UNKNOWN",
        scenario_source_ids=["official-flood-geometry"],
        scenario_elapsed_time_sec=None,
        source_ids=["official-flood-geometry", "osm-bounded-20260829"],
        hazard_geometry_artifact_ids=["official-flood-polygons-v1"],
        edge_geometry_artifact_ids=["arashiyama-osm-corridor-v1"],
        source_feature_ids=["flood/45", "way/1"],
        revision_ids=["official-20260801-r1", "osm-20260829-r1"],
        method="deterministic line/polygon intersection",
        lineage=["official polygon input", "VGI edge input", "model-derived overlap"],
    )
    value.update(updates)
    return value


def test_unknown_observation_preserves_nulls_and_input_immutability(tmp_path: Path) -> None:
    """[source_conformance] Missing official geometry remains UNKNOWN, never false or zero."""

    raw = _unknown()
    before = copy.deepcopy(raw)
    observation = EdgeHazardObservationV2.from_mapping(
        raw,
        artifact_index=_verified_artifact_index(tmp_path),
        scenario=_unknown_scenario(),
    )
    assert raw == before
    assert observation.hazard_data_status == "UNKNOWN"
    assert observation.overlap is None
    assert observation.overlap_length_m is None
    assert observation.max_depth_m is None
    assert observation.mean_depth_m is None
    assert observation.official_closure is None
    assert observation.data_class == "UNKNOWN"
    assert observation.scenario_source_ids == ()
    assert set(observation.as_mapping()) == set(EDGE_HAZARD_OBSERVATION_V2_FIELDS)
    with pytest.raises(TypeError):
        observation.as_mapping()["overlap"] = False  # type: ignore[index]


@pytest.mark.parametrize(
    "updates",
    [
        {"edge_id": "kyoto-arashiyama:edge:not-in-artifact"},
        {"edge_geometry_artifact_ids": []},
    ],
)
def test_unknown_observation_resolves_exactly_one_edge_identity(
    tmp_path: Path, updates: dict[str, object]
) -> None:
    """[source_conformance] UNKNOWN physics does not permit unknown edge provenance."""

    with pytest.raises(HazardContractError, match="edge_id|exactly one edge"):
        EdgeHazardObservationV2.from_mapping(
            _unknown(**updates),
            artifact_index=_verified_artifact_index(tmp_path),
            scenario=_unknown_scenario(),
        )


def test_known_overlap_is_model_derived_and_does_not_infer_closure(tmp_path: Path) -> None:
    """[source_conformance] Official polygon input does not make the intersection official policy."""

    observation = derive_edge_hazard_observation_v2(
        artifact_index=_verified_artifact_index(tmp_path),
        edge_id="kyoto-arashiyama:edge:osm-way-1",
        scenario=_scenario("flood-static-snapshot"),
        edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
        hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
    )
    assert observation.overlap is True
    assert observation.coverage_status == "PARTIAL"
    assert observation.hazard_data_status == "KNOWN"
    assert observation.data_class == "MODEL_DERIVED"
    assert observation.overlap_length_m is None
    assert observation.max_depth_m is None
    assert observation.mean_depth_m is None
    assert observation.official_closure is None
    assert observation.official_closure_source_ids == ()
    assert observation.scenario_source_ids == ("official-flood-geometry",)
    assert observation.intersecting_hazard_feature_ids == (
        "kyoto-arashiyama:hazard:flood-45",
    )


@pytest.mark.parametrize(
    "updates",
    [
        {"overlap": False},
        {"overlap_length_m": 0.0},
        {"max_depth_m": 0.0},
        {"mean_depth_m": 0.0},
        {"official_closure": False},
        {"hazard_data_status": "KNOWN"},
        {"data_class": "OFFICIAL"},
    ],
)
def test_unknown_rejects_physical_or_policy_defaults(
    tmp_path: Path, updates: dict[str, object]
) -> None:
    """[source_conformance] UNKNOWN cannot become false, zero, open, or official data."""

    with pytest.raises(HazardContractError):
        EdgeHazardObservationV2.from_mapping(
            _unknown(**updates),
            artifact_index=_verified_artifact_index(tmp_path),
            scenario=_unknown_scenario(),
        )


def test_no_intersection_without_coverage_authority_stays_unknown(tmp_path: Path) -> None:
    """[source_conformance] Polygon absence cannot self-assert complete official coverage."""

    far_polygon = [
        [
            [136.0, 36.0],
            [136.1, 36.0],
            [136.1, 36.1],
            [136.0, 36.0],
        ]
    ]
    observation = derive_edge_hazard_observation_v2(
        artifact_index=_verified_artifact_index(
            tmp_path, hazard_coordinates=far_polygon
        ),
        edge_id="kyoto-arashiyama:edge:osm-way-1",
        scenario=_scenario("flood-static-snapshot"),
        edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
        hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
    )
    assert observation.hazard_data_status == "UNKNOWN"
    assert observation.coverage_status == "UNKNOWN"
    assert observation.overlap is None
    assert observation.official_closure is None

    serialized = json.loads(json.dumps(dict(observation.as_mapping())))
    reloaded = EdgeHazardObservationV2.from_mapping(
        serialized,
        artifact_index=_verified_artifact_index(
            tmp_path / "round-trip", hazard_coordinates=far_polygon
        ),
        scenario=_scenario("flood-static-snapshot"),
    )
    assert reloaded == observation


def test_serialized_unknown_rebinds_scenario_to_official_hazard_artifact(
    tmp_path: Path,
) -> None:
    """[source_conformance] UNKNOWN cannot relabel a referenced official artifact."""

    far_polygon = [
        [[136.0, 36.0], [136.1, 36.0], [136.1, 36.1], [136.0, 36.0]]
    ]
    index = _verified_artifact_index(tmp_path, hazard_coordinates=far_polygon)
    observation = derive_edge_hazard_observation_v2(
        artifact_index=index,
        edge_id="kyoto-arashiyama:edge:osm-way-1",
        scenario=_scenario("flood-static-snapshot"),
        edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
        hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
    )
    serialized = json.loads(json.dumps(dict(observation.as_mapping())))

    relabelled = copy.deepcopy(serialized)
    relabelled["hazard_type"] = "TSUNAMI"
    with pytest.raises(HazardContractError, match="hazard_type must exactly match"):
        EdgeHazardObservationV2.from_mapping(
            relabelled,
            artifact_index=index,
            scenario=_scenario("flood-static-snapshot", hazard_type="TSUNAMI"),
        )

    unrelated = copy.deepcopy(serialized)
    unrelated["scenario_source_ids"] = ["unrelated-official-source"]
    with pytest.raises(HazardContractError, match="scenario source_ids"):
        EdgeHazardObservationV2.from_mapping(
            unrelated,
            artifact_index=index,
            scenario=_scenario(
                "flood-static-snapshot",
                source_ids=["unrelated-official-source"],
            ),
        )


def test_unknown_rejects_elapsed_time_even_when_scenario_matches(tmp_path: Path) -> None:
    """[source_conformance] Static v2 observations cannot smuggle in a T+n claim."""

    with pytest.raises(HazardContractError, match="scenario_elapsed_time_sec=null"):
        EdgeHazardObservationV2.from_mapping(
            _unknown(scenario_elapsed_time_sec=1.0),
            artifact_index=_verified_artifact_index(tmp_path),
            scenario=_scenario(
                "flood-static-snapshot",
                source_ids=[],
                source_status="UNKNOWN",
                authority="UNKNOWN",
                elapsed_time_sec=1.0,
            ),
        )


def test_derivation_respects_holes_and_all_multi_geometry_members(tmp_path: Path) -> None:
    """[software_correctness] Hole and later multi-members cannot be skipped by the predicate."""

    shell = [
        [135.675, 35.010],
        [135.678, 35.010],
        [135.678, 35.013],
        [135.675, 35.013],
        [135.675, 35.010],
    ]
    hole = [
        [135.6755, 35.0105],
        [135.6775, 35.0105],
        [135.6775, 35.0125],
        [135.6755, 35.0125],
        [135.6755, 35.0105],
    ]
    hole_result = derive_edge_hazard_observation_v2(
        artifact_index=_verified_artifact_index(
            tmp_path / "hole",
            hazard_geometry={"type": "Polygon", "coordinates": [shell, hole]},
        ),
        edge_id="kyoto-arashiyama:edge:osm-way-1",
        scenario=_scenario("hole"),
        edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
        hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
    )
    assert hole_result.hazard_data_status == "UNKNOWN"

    multi_line_result = derive_edge_hazard_observation_v2(
        artifact_index=_verified_artifact_index(
            tmp_path / "multi-line",
            edge_geometry={
                "type": "MultiLineString",
                "coordinates": [
                    [[136.0, 36.0], [136.1, 36.1]],
                    [[135.676, 35.011], [135.677, 35.012]],
                ],
            },
        ),
        edge_id="kyoto-arashiyama:edge:osm-way-1",
        scenario=_scenario("multi-line"),
        edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
        hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
    )
    assert multi_line_result.overlap is True

    multi_polygon_result = derive_edge_hazard_observation_v2(
        artifact_index=_verified_artifact_index(
            tmp_path / "multi-polygon",
            hazard_geometry={
                "type": "MultiPolygon",
                "coordinates": [
                    [[[136.0, 36.0], [136.1, 36.0], [136.1, 36.1], [136.0, 36.0]]],
                    [shell],
                ],
            },
        ),
        edge_id="kyoto-arashiyama:edge:osm-way-1",
        scenario=_scenario("multi-polygon"),
        edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
        hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
    )
    assert multi_polygon_result.overlap is True


def test_derivation_rejects_noncanonical_hazard_artifact_order(tmp_path: Path) -> None:
    """[software_correctness] Artifact input order cannot change deterministic provenance."""

    with pytest.raises(HazardContractError, match="canonical order"):
        derive_edge_hazard_observation_v2(
            artifact_index=_verified_artifact_index(tmp_path),
            edge_id="kyoto-arashiyama:edge:osm-way-1",
            scenario=_scenario("order"),
            edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
            hazard_geometry_artifact_ids=("z-artifact", "a-artifact"),
        )


def test_derivation_resolves_edge_id_and_uses_immutable_snapshot(tmp_path: Path) -> None:
    """[software_correctness] Edge identity is exact and later file changes cannot alter evidence."""

    index = _verified_artifact_index(tmp_path)
    with pytest.raises(HazardContractError, match="edge_id does not resolve"):
        derive_edge_hazard_observation_v2(
            artifact_index=index,
            edge_id="kyoto-arashiyama:edge:not-in-artifact",
            scenario=_scenario("bad-edge"),
            edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
            hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
        )

    (index.trusted_root / "hazards" / "official-flood.real.geojson").write_text(
        "{}\n", encoding="utf-8", newline="\n"
    )
    observation = derive_edge_hazard_observation_v2(
        artifact_index=index,
        edge_id="kyoto-arashiyama:edge:osm-way-1",
        scenario=_scenario("immutable-snapshot"),
        edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
        hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
    )
    assert observation.overlap is True


def test_derivation_binds_scenario_hazard_type_and_official_sources(tmp_path: Path) -> None:
    """[source_conformance] A real polygon cannot be relabelled as another hazard scenario."""

    index = _verified_artifact_index(tmp_path)
    with pytest.raises(HazardContractError, match="hazard_type must exactly match"):
        derive_edge_hazard_observation_v2(
            artifact_index=index,
            edge_id="kyoto-arashiyama:edge:osm-way-1",
            scenario=_scenario("wrong-type", hazard_type="TSUNAMI"),
            edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
            hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
        )

    unsafe_scenarios = (
        _scenario(
            "assumption",
            source_status="SYNTHETIC_DEMO",
            authority="DESIGN_ASSUMPTION",
        ),
        _scenario("coverage-overclaim", coverage_complete=True),
        _scenario("state-overclaim", default_edge_state="PASS"),
        _scenario("time-overclaim", elapsed_time_sec=3600.0),
        _scenario("unsorted-sources", source_ids=["z-source", "a-source"]),
    )
    for unsafe in unsafe_scenarios:
        with pytest.raises(HazardContractError, match="REAL/OFFICIAL scenario provenance"):
            derive_edge_hazard_observation_v2(
                artifact_index=index,
                edge_id="kyoto-arashiyama:edge:osm-way-1",
                scenario=unsafe,
                edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
                hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
            )
    with pytest.raises(HazardContractError, match="scenario source_ids"):
        derive_edge_hazard_observation_v2(
            artifact_index=index,
            edge_id="kyoto-arashiyama:edge:osm-way-1",
            scenario=_scenario("wrong-source", source_ids=["unrelated-source"]),
            edge_geometry_artifact_id="arashiyama-osm-corridor-v1",
            hazard_geometry_artifact_ids=("official-flood-polygons-v1",),
        )


def test_official_closure_requires_separate_authority_adapter(tmp_path: Path) -> None:
    """[source_conformance] A polygon overlap is never itself a closure authority."""

    artifact_index = _verified_artifact_index(tmp_path)
    with pytest.raises(HazardContractError, match="authority adapter"):
        EdgeHazardObservationV2.from_mapping(
            _known_overlap(official_closure=True),
            artifact_index=artifact_index,
            scenario=_scenario("flood-static-snapshot"),
        )
    with pytest.raises(HazardContractError, match="authority adapter"):
        EdgeHazardObservationV2.from_mapping(
            _known_overlap(
                official_closure=True,
                official_closure_source_ids=["official-flood-geometry"],
            ),
            artifact_index=artifact_index,
            scenario=_scenario("flood-static-snapshot"),
        )


@pytest.mark.parametrize(
    "updates",
    [
        {"source_ids": []},
        {"hazard_geometry_artifact_ids": []},
        {"edge_geometry_artifact_ids": []},
        {"overlap": None},
        {"max_depth_m": -0.1},
        {"mean_depth_m": 1.3},
        {"overlap_length_m": -0.1},
        {"hazard_geometry_artifact_ids": ["synthetic-or-missing-1"]},
        {"source_feature_ids": ["way/from-another-source"]},
        {"revision_ids": ["unrelated-revision"]},
        {"edge_id": "kyoto-arashiyama:edge:not-in-artifact"},
        {"extra": "not allowed"},
    ],
)
def test_known_observation_rejects_untraceable_or_contradictory_values(
    tmp_path: Path,
    updates: dict[str, object]
) -> None:
    """[software_correctness] KNOWN needs traceable finite relationally valid evidence."""

    with pytest.raises(HazardContractError):
        EdgeHazardObservationV2.from_mapping(
            _known_overlap(**updates),
            artifact_index=_verified_artifact_index(tmp_path),
            scenario=_scenario("flood-static-snapshot"),
        )


def test_hash_only_index_and_self_asserted_known_mapping_are_rejected(
    tmp_path: Path,
) -> None:
    """[source_conformance] KNOWN is emitted only by deterministic geometry derivation."""

    validated = _verified_artifact_index(tmp_path)
    metadata_only = load_real_artifact_manifest(
        validated.trusted_root / "sources" / "real-artifacts-v2.json",
        trusted_root=validated.trusted_root,
        expected_city_id="kyoto_arashiyama",
    )
    assert isinstance(metadata_only, VerifiedArtifactIndex)
    with pytest.raises(HazardContractError, match="validated immutable geometry derivation"):
        EdgeHazardObservationV2.from_mapping(
            _known_overlap(),
            artifact_index=metadata_only,
            scenario=_scenario("flood-static-snapshot"),
        )
    with pytest.raises(HazardContractError, match="validated immutable geometry derivation"):
        EdgeHazardObservationV2.from_mapping(
            _known_overlap(),
            artifact_index=validated,
            scenario=_scenario("flood-static-snapshot"),
        )


def test_v2_hazard_schema_declares_exact_runtime_fields() -> None:
    """[source_conformance] The published schema exposes no hidden policy field."""

    schema = json.loads(
        (ROOT / "schemas" / "realdata" / "edge-hazard-observation-v2.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(EDGE_HAZARD_OBSERVATION_V2_FIELDS)
    assert set(schema["properties"]) == set(EDGE_HAZARD_OBSERVATION_V2_FIELDS)
    assert len(schema["allOf"]) == 3
    assert schema["x-ablepath-runtime-validation"]
    assert schema["properties"]["scenario_elapsed_time_sec"] == {"type": "null"}
    known = schema["allOf"][1]["then"]["properties"]
    assert known["overlap"] == {"const": True}
    assert known["coverage_status"] == {"const": "PARTIAL"}
    assert known["overlap_length_m"] == {"type": "null"}
    assert known["max_depth_m"] == {"type": "null"}
    assert known["mean_depth_m"] == {"type": "null"}
    assert known["scenario_source_status"] == {"const": "REAL"}
    assert known["scenario_authority"] == {"const": "OFFICIAL"}
    assert known["scenario_coverage_complete"] == {"const": False}
    assert not ({"state", "hazard_state", "profile_state", "route_state"} & set(schema["properties"]))


def test_v2_hazard_schema_branches_reject_semantic_mutants() -> None:
    """[software_correctness] UNKNOWN/KNOWN schema branches kill unsafe field mutants."""

    schema = json.loads(
        (ROOT / "schemas" / "realdata" / "edge-hazard-observation-v2.schema.json").read_text(
            encoding="utf-8"
        )
    )
    unknown = _unknown()
    known = _known_overlap(
        overlap_length_m=None,
        max_depth_m=None,
        mean_depth_m=None,
        intersecting_hazard_feature_ids=["kyoto-arashiyama:hazard:flood-45"],
    )
    assert _v2_schema_accepts(schema, unknown)
    assert _v2_schema_accepts(schema, known)

    unknown_mutants = (
        {"overlap": False},
        {"overlap_length_m": 0.0},
        {"coverage_status": "PARTIAL"},
        {"data_class": "MODEL_DERIVED"},
        {"scenario_elapsed_time_sec": 1.0},
        {"intersecting_hazard_feature_ids": ["invented-feature"]},
    )
    known_mutants = (
        {"overlap": False},
        {"coverage_status": "COMPLETE"},
        {"data_class": "UNKNOWN"},
        {"scenario_source_status": "UNKNOWN"},
        {"scenario_authority": "UNKNOWN"},
        {"scenario_coverage_complete": True},
        {"scenario_default_edge_state": "PASS"},
        {"scenario_elapsed_time_sec": 1.0},
        {"scenario_source_ids": []},
        {"source_ids": []},
        {"hazard_geometry_artifact_ids": []},
        {"edge_geometry_artifact_ids": []},
        {"intersecting_hazard_feature_ids": []},
        {"source_feature_ids": []},
        {"revision_ids": []},
    )
    for updates in unknown_mutants:
        assert not _v2_schema_accepts(schema, {**unknown, **updates})
    for updates in known_mutants:
        assert not _v2_schema_accepts(schema, {**known, **updates})
