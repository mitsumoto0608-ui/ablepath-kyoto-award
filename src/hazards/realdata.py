"""Phase 2 contract for derived edge/official-hazard geometry intersections."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from numbers import Real
from types import MappingProxyType
from typing import Mapping

from src.citypacks.realdata import (
    RealArtifactContractError,
    ValidatedGeometryIndex,
    VerifiedArtifactIndex,
)

from .contracts import HazardContractError, HazardScenario


EDGE_HAZARD_OBSERVATION_V2_FIELDS = (
    "schema_version",
    "edge_id",
    "scenario_id",
    "hazard_type",
    "scenario_source_status",
    "scenario_authority",
    "scenario_coverage_complete",
    "scenario_default_edge_state",
    "scenario_source_ids",
    "scenario_elapsed_time_sec",
    "overlap",
    "overlap_length_m",
    "max_depth_m",
    "mean_depth_m",
    "coverage_status",
    "official_closure",
    "hazard_data_status",
    "data_class",
    "source_ids",
    "hazard_geometry_artifact_ids",
    "edge_geometry_artifact_ids",
    "official_closure_source_ids",
    "intersecting_hazard_feature_ids",
    "source_feature_ids",
    "revision_ids",
    "method",
    "lineage",
)

_COVERAGE = {"COMPLETE", "PARTIAL", "UNKNOWN"}
_HAZARD_STATUS = {"KNOWN", "UNKNOWN"}
_EDGE_HAZARD_TOKEN = object()


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HazardContractError(f"{name} must be non-empty text")
    return value


def _text_tuple(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise HazardContractError(f"{name} must be a text list")
    items = tuple(_text(item, f"{name}[]") for item in value)
    if len(items) != len(set(items)):
        raise HazardContractError(f"{name} must contain unique values")
    return items


def _identifier_tuple(value: object, name: str) -> tuple[str, ...]:
    items = _text_tuple(value, name)
    if items != tuple(sorted(items)):
        raise HazardContractError(f"{name} must use canonical sorted order")
    return items


def _optional_bool(value: object, name: str) -> bool | None:
    if value is not None and type(value) is not bool:
        raise HazardContractError(f"{name} must be true, false, or null")
    return value


def _optional_nonnegative_float(value: object, name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise HazardContractError(f"{name} must be a finite non-negative number or null")
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise HazardContractError(f"{name} must be a finite non-negative number or null")
    return result


@dataclass(frozen=True, slots=True)
class EdgeHazardObservationV2:
    """Immutable model-derived overlap with operational policy kept orthogonal."""

    schema_version: str
    edge_id: str
    scenario_id: str
    hazard_type: str
    scenario_source_status: str
    scenario_authority: str
    scenario_coverage_complete: bool
    scenario_default_edge_state: str
    scenario_source_ids: tuple[str, ...]
    scenario_elapsed_time_sec: float | None
    overlap: bool | None
    overlap_length_m: float | None
    max_depth_m: float | None
    mean_depth_m: float | None
    coverage_status: str
    official_closure: bool | None
    hazard_data_status: str
    data_class: str
    source_ids: tuple[str, ...]
    hazard_geometry_artifact_ids: tuple[str, ...]
    edge_geometry_artifact_ids: tuple[str, ...]
    official_closure_source_ids: tuple[str, ...]
    intersecting_hazard_feature_ids: tuple[str, ...]
    source_feature_ids: tuple[str, ...]
    revision_ids: tuple[str, ...]
    method: str
    lineage: tuple[str, ...]
    _token: object = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._token is not _EDGE_HAZARD_TOKEN:
            raise HazardContractError(
                "EdgeHazardObservationV2 must be created by a contract loader or trusted derivation"
            )

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, object],
        *,
        artifact_index: VerifiedArtifactIndex | ValidatedGeometryIndex,
        scenario: HazardScenario,
    ) -> "EdgeHazardObservationV2":
        """Validate exact v2 relationships without inventing policy or zero values."""
        if not isinstance(value, Mapping):
            raise HazardContractError("edge hazard observation v2 must be a mapping")
        keys = set(value)
        expected = set(EDGE_HAZARD_OBSERVATION_V2_FIELDS)
        if keys != expected:
            raise HazardContractError(
                "edge hazard observation v2 keys must be exact: "
                f"missing={sorted(expected - keys)}, extra={sorted(keys - expected)}"
            )
        if value["schema_version"] != "2.0.0":
            raise HazardContractError("unsupported edge hazard observation schema version")
        if not isinstance(scenario, HazardScenario):
            raise HazardContractError("observation loading requires a validated HazardScenario")
        coverage = _text(value["coverage_status"], "coverage_status")
        if coverage not in _COVERAGE:
            raise HazardContractError(f"unsupported coverage_status: {coverage}")
        hazard_status = _text(value["hazard_data_status"], "hazard_data_status")
        if hazard_status not in _HAZARD_STATUS:
            raise HazardContractError(f"unsupported hazard_data_status: {hazard_status}")
        data_class = _text(value["data_class"], "data_class")
        expected_data_class = "MODEL_DERIVED" if hazard_status == "KNOWN" else "UNKNOWN"
        if data_class != expected_data_class:
            raise HazardContractError(
                f"{hazard_status} hazard data requires data_class={expected_data_class}"
            )

        overlap = _optional_bool(value["overlap"], "overlap")
        overlap_length = _optional_nonnegative_float(
            value["overlap_length_m"], "overlap_length_m"
        )
        max_depth = _optional_nonnegative_float(value["max_depth_m"], "max_depth_m")
        mean_depth = _optional_nonnegative_float(value["mean_depth_m"], "mean_depth_m")
        closure = _optional_bool(value["official_closure"], "official_closure")

        source_ids = _identifier_tuple(value["source_ids"], "source_ids")
        hazard_artifacts = _identifier_tuple(
            value["hazard_geometry_artifact_ids"], "hazard_geometry_artifact_ids"
        )
        edge_artifacts = _identifier_tuple(
            value["edge_geometry_artifact_ids"], "edge_geometry_artifact_ids"
        )
        closure_sources = _identifier_tuple(
            value["official_closure_source_ids"], "official_closure_source_ids"
        )
        intersecting_hazard_features = _identifier_tuple(
            value["intersecting_hazard_feature_ids"],
            "intersecting_hazard_feature_ids",
        )
        source_features = _identifier_tuple(value["source_feature_ids"], "source_feature_ids")
        revisions = _identifier_tuple(value["revision_ids"], "revision_ids")
        lineage = _text_tuple(value["lineage"], "lineage")
        if not lineage:
            raise HazardContractError("lineage must be non-empty")
        edge_id = _text(value["edge_id"], "edge_id")
        scenario_id = _text(value["scenario_id"], "scenario_id")
        hazard_type = _text(value["hazard_type"], "hazard_type")
        scenario_source_status = _text(
            value["scenario_source_status"], "scenario_source_status"
        )
        scenario_authority = _text(value["scenario_authority"], "scenario_authority")
        scenario_coverage_complete = value["scenario_coverage_complete"]
        if type(scenario_coverage_complete) is not bool:
            raise HazardContractError("scenario_coverage_complete must be bool")
        scenario_default_edge_state = _text(
            value["scenario_default_edge_state"], "scenario_default_edge_state"
        )
        scenario_source_ids = _identifier_tuple(
            value["scenario_source_ids"], "scenario_source_ids"
        )
        scenario_elapsed_time_sec = _optional_nonnegative_float(
            value["scenario_elapsed_time_sec"], "scenario_elapsed_time_sec"
        )
        if (
            scenario_id != scenario.scenario_id
            or hazard_type != scenario.hazard_type
            or scenario_source_status != scenario.source_status
            or scenario_authority != scenario.official_or_assumption
            or scenario_coverage_complete != scenario.coverage_complete
            or scenario_default_edge_state != scenario.default_edge_state
            or scenario_source_ids != scenario.source_ids
            or scenario_elapsed_time_sec != scenario.elapsed_time_sec
        ):
            raise HazardContractError(
                "serialized observation scenario provenance contradicts HazardScenario"
            )
        if scenario_elapsed_time_sec is not None:
            raise HazardContractError(
                "v2 geometry observations require scenario_elapsed_time_sec=null"
            )
        if scenario_default_edge_state != "UNKNOWN":
            raise HazardContractError(
                "edge state integration is outside v2 geometry observation; default must be UNKNOWN"
            )
        method = _text(value["method"], "method")

        physical_values = (overlap, overlap_length, max_depth, mean_depth)
        if hazard_status == "UNKNOWN":
            if any(item is not None for item in physical_values):
                raise HazardContractError("UNKNOWN hazard data requires all physical values to be null")
            if coverage != "UNKNOWN":
                raise HazardContractError("UNKNOWN hazard data requires UNKNOWN evaluated coverage")
            if intersecting_hazard_features:
                raise HazardContractError(
                    "UNKNOWN hazard data cannot claim intersecting hazard features"
                )
        else:
            if overlap is None:
                raise HazardContractError("KNOWN hazard data requires boolean overlap")
            if not source_ids or not hazard_artifacts or not edge_artifacts:
                raise HazardContractError(
                    "KNOWN hazard data requires source, hazard-artifact, and edge-artifact IDs"
                )
            if overlap is False and coverage != "COMPLETE":
                raise HazardContractError("known no-overlap requires complete coverage")
            if coverage == "UNKNOWN":
                raise HazardContractError("KNOWN hazard data requires evaluated coverage")

        if overlap is False and any(
            item is not None for item in (overlap_length, max_depth, mean_depth)
        ):
            raise HazardContractError("no-overlap cannot carry length or depth values")
        if mean_depth is not None and max_depth is None:
            raise HazardContractError("mean_depth_m requires max_depth_m")
        if mean_depth is not None and max_depth is not None and mean_depth > max_depth:
            raise HazardContractError("mean_depth_m must not exceed max_depth_m")

        if closure is None and closure_sources:
            raise HazardContractError("closure sources require a non-null official_closure")
        if closure is not None:
            raise HazardContractError(
                "official closure requires a separate reviewed authority adapter; v2 keeps it null"
            )
        if hazard_status == "KNOWN":
            raise HazardContractError(
                "KNOWN hazard observations require validated immutable geometry derivation"
            )
        if len(edge_artifacts) != 1:
            raise HazardContractError(
                "each v2 observation must resolve exactly one edge geometry artifact"
            )

        referenced_artifact_ids = tuple(hazard_artifacts + edge_artifacts)
        if not isinstance(artifact_index, ValidatedGeometryIndex):
            raise HazardContractError(
                "geometry-referenced observations require ValidatedGeometryIndex"
            )
        try:
            resolved_artifacts = {
                artifact_id: artifact_index.records_for(artifact_id)
                for artifact_id in referenced_artifact_ids
            }
            referenced_records = tuple(
                record
                for artifact_id in referenced_artifact_ids
                for record in resolved_artifacts[artifact_id]
            )
        except RealArtifactContractError as error:
            raise HazardContractError(str(error)) from error
        for artifact_id in hazard_artifacts:
            for record in resolved_artifacts[artifact_id]:
                if not (
                    record.artifact_role == "OFFICIAL_HAZARD_GEOMETRY"
                    and record.source_class == "OFFICIAL"
                    and record.data_class == "REAL"
                    and record.geometry_status == "SOURCE_TRACEABLE_REAL"
                ):
                    raise HazardContractError(
                        f"hazard artifact {artifact_id} is not verified official REAL geometry"
                    )
        if hazard_artifacts:
            _validate_connectable_scenario(scenario)
            hazard_records = tuple(
                record
                for artifact_id in hazard_artifacts
                for record in resolved_artifacts[artifact_id]
            )
            expected_scenario_source_ids = tuple(
                sorted({record.source_id for record in hazard_records})
            )
            if scenario_source_ids != expected_scenario_source_ids:
                raise HazardContractError(
                    "scenario source_ids must exactly resolve through official hazard artifacts"
                )
            observed_hazard_types: set[str] = set()
            try:
                for artifact_id in hazard_artifacts:
                    payload = artifact_index.payload_for(artifact_id)
                    for feature in payload["features"]:
                        if not isinstance(feature, Mapping):
                            raise HazardContractError(
                                "resolved hazard feature is invalid"
                            )
                        properties = feature.get("properties")
                        if not isinstance(properties, Mapping):
                            raise HazardContractError(
                                "resolved hazard properties are invalid"
                            )
                        observed_hazard_types.add(
                            _text(
                                properties.get("hazard_type"),
                                "hazard feature hazard_type",
                            )
                        )
            except (KeyError, TypeError, RealArtifactContractError) as error:
                if isinstance(error, HazardContractError):
                    raise
                raise HazardContractError(str(error)) from error
            if observed_hazard_types != {hazard_type}:
                raise HazardContractError(
                    "scenario hazard_type must exactly match all official hazard features"
                )
        for artifact_id in edge_artifacts:
            for record in resolved_artifacts[artifact_id]:
                if not (
                    record.artifact_role == "CORRIDOR_GEOMETRY"
                    and record.source_class in {"OFFICIAL", "VGI"}
                    and record.data_class == "REAL"
                    and record.geometry_status == "SOURCE_TRACEABLE_REAL"
                ):
                    raise HazardContractError(
                        f"edge artifact {artifact_id} is not verified source-traceable geometry"
                    )
        if edge_artifacts and edge_id not in {
            feature_id
            for artifact_id in edge_artifacts
            for feature_id in artifact_index.feature_ids_for(artifact_id)
        }:
            raise HazardContractError("edge_id does not resolve through edge artifacts")
        expected_source_ids = {record.source_id for record in referenced_records}
        expected_feature_ids = {record.source_feature_id for record in referenced_records}
        expected_revision_ids = {record.revision_id for record in referenced_records}
        if set(source_ids) != expected_source_ids:
            raise HazardContractError("source_ids do not exactly resolve through artifact inputs")
        if set(source_features) != expected_feature_ids:
            raise HazardContractError(
                "source_feature_ids do not exactly resolve through artifact inputs"
            )
        if set(revisions) != expected_revision_ids:
            raise HazardContractError("revision_ids do not exactly resolve through artifact inputs")

        return cls(
            schema_version="2.0.0",
            edge_id=edge_id,
            scenario_id=scenario_id,
            hazard_type=hazard_type,
            scenario_source_status=scenario_source_status,
            scenario_authority=scenario_authority,
            scenario_coverage_complete=scenario_coverage_complete,
            scenario_default_edge_state=scenario_default_edge_state,
            scenario_source_ids=scenario_source_ids,
            scenario_elapsed_time_sec=scenario_elapsed_time_sec,
            overlap=overlap,
            overlap_length_m=overlap_length,
            max_depth_m=max_depth,
            mean_depth_m=mean_depth,
            coverage_status=coverage,
            official_closure=closure,
            hazard_data_status=hazard_status,
            data_class=data_class,
            source_ids=source_ids,
            hazard_geometry_artifact_ids=hazard_artifacts,
            edge_geometry_artifact_ids=edge_artifacts,
            official_closure_source_ids=closure_sources,
            intersecting_hazard_feature_ids=intersecting_hazard_features,
            source_feature_ids=source_features,
            revision_ids=revisions,
            method=method,
            lineage=lineage,
            _token=_EDGE_HAZARD_TOKEN,
        )

    def as_mapping(self) -> Mapping[str, object]:
        """Return an immutable detached mapping using the exact v2 surface."""
        value = {
            field: getattr(self, field) for field in EDGE_HAZARD_OBSERVATION_V2_FIELDS
        }
        for field in (
            "source_ids",
            "hazard_geometry_artifact_ids",
            "edge_geometry_artifact_ids",
            "official_closure_source_ids",
            "intersecting_hazard_feature_ids",
            "scenario_source_ids",
            "source_feature_ids",
            "revision_ids",
            "lineage",
        ):
            value[field] = tuple(value[field])
        return MappingProxyType(value)


def _orientation(
    start: tuple[float, float],
    end: tuple[float, float],
    point: tuple[float, float],
) -> float:
    return (end[0] - start[0]) * (point[1] - start[1]) - (
        end[1] - start[1]
    ) * (point[0] - start[0])


def _point_on_segment(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> bool:
    epsilon = 1e-15
    return abs(_orientation(start, end, point)) <= epsilon and (
        min(start[0], end[0]) - epsilon <= point[0] <= max(start[0], end[0]) + epsilon
        and min(start[1], end[1]) - epsilon <= point[1] <= max(start[1], end[1]) + epsilon
    )


def _segments_intersect(
    first_start: tuple[float, float],
    first_end: tuple[float, float],
    second_start: tuple[float, float],
    second_end: tuple[float, float],
) -> bool:
    first_a = _orientation(first_start, first_end, second_start)
    first_b = _orientation(first_start, first_end, second_end)
    second_a = _orientation(second_start, second_end, first_start)
    second_b = _orientation(second_start, second_end, first_end)
    if (first_a > 0) != (first_b > 0) and (second_a > 0) != (second_b > 0):
        return True
    return any(
        _point_on_segment(point, start, end)
        for point, start, end in (
            (second_start, first_start, first_end),
            (second_end, first_start, first_end),
            (first_start, second_start, second_end),
            (first_end, second_start, second_end),
        )
    )


def _pair(value: object) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise HazardContractError("validated geometry contains an invalid coordinate pair")
    x, y = value
    if any(isinstance(item, bool) or not isinstance(item, Real) for item in (x, y)):
        raise HazardContractError("validated geometry contains a non-numeric coordinate")
    return float(x), float(y)


def _ring(value: object) -> tuple[tuple[float, float], ...]:
    if not isinstance(value, list):
        raise HazardContractError("validated polygon ring must be a coordinate list")
    return tuple(_pair(item) for item in value)


def _point_in_ring(
    point: tuple[float, float], ring: tuple[tuple[float, float], ...]
) -> bool:
    if any(_point_on_segment(point, start, end) for start, end in zip(ring, ring[1:])):
        return True
    inside = False
    for start, end in zip(ring, ring[1:]):
        if (start[1] > point[1]) == (end[1] > point[1]):
            continue
        crossing_x = (end[0] - start[0]) * (point[1] - start[1]) / (
            end[1] - start[1]
        ) + start[0]
        if point[0] < crossing_x:
            inside = not inside
    return inside


def _point_in_polygon(
    point: tuple[float, float], polygon: tuple[tuple[tuple[float, float], ...], ...]
) -> bool:
    return _point_in_ring(point, polygon[0]) and not any(
        _point_in_ring(point, hole) for hole in polygon[1:]
    )


def _line_intersects_polygon(
    line: tuple[tuple[float, float], ...],
    polygon: tuple[tuple[tuple[float, float], ...], ...],
) -> bool:
    if any(_point_in_polygon(point, polygon) for point in line):
        return True
    return any(
        _segments_intersect(line_start, line_end, ring_start, ring_end)
        for line_start, line_end in zip(line, line[1:])
        for ring in polygon
        for ring_start, ring_end in zip(ring, ring[1:])
    )


def _line_parts(geometry: Mapping[str, object]) -> tuple[tuple[tuple[float, float], ...], ...]:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type == "LineString" and isinstance(coordinates, list):
        return (tuple(_pair(point) for point in coordinates),)
    if geometry_type == "MultiLineString" and isinstance(coordinates, list):
        return tuple(tuple(_pair(point) for point in line) for line in coordinates)
    raise HazardContractError("edge capability does not contain linear geometry")


def _polygon_parts(
    geometry: Mapping[str, object],
) -> tuple[tuple[tuple[tuple[float, float], ...], ...], ...]:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type == "Polygon" and isinstance(coordinates, list):
        return (tuple(_ring(ring) for ring in coordinates),)
    if geometry_type == "MultiPolygon" and isinstance(coordinates, list):
        return tuple(tuple(_ring(ring) for ring in polygon) for polygon in coordinates)
    raise HazardContractError("hazard capability does not contain polygonal geometry")


def _validate_connectable_scenario(scenario: HazardScenario) -> None:
    if (
        scenario.source_status != "REAL"
        or scenario.official_or_assumption != "OFFICIAL"
        or scenario.coverage_complete is not False
        or scenario.default_edge_state != "UNKNOWN"
        or scenario.elapsed_time_sec is not None
        or scenario.source_ids != tuple(sorted(scenario.source_ids))
    ):
        raise HazardContractError(
            "geometry derivation requires REAL/OFFICIAL scenario provenance, "
            "coverage_complete=false, default_edge_state=UNKNOWN, and elapsed_time_sec=null"
        )


def derive_edge_hazard_observation_v2(
    *,
    artifact_index: ValidatedGeometryIndex,
    edge_id: str,
    scenario: HazardScenario,
    edge_geometry_artifact_id: str,
    hazard_geometry_artifact_ids: tuple[str, ...],
) -> EdgeHazardObservationV2:
    """Derive a conservative line/polygon predicate from immutable validated bytes.

    An observed intersection is model-derived KNOWN/PARTIAL.  Absence of an
    intersection remains UNKNOWN because dataset coverage authority is not
    implied.  Length, depth, and official closure remain null.
    """

    if not isinstance(artifact_index, ValidatedGeometryIndex):
        raise HazardContractError("derivation requires ValidatedGeometryIndex")
    if not isinstance(scenario, HazardScenario):
        raise HazardContractError("derivation requires a validated HazardScenario")
    _validate_connectable_scenario(scenario)
    edge_id = _text(edge_id, "edge_id")
    scenario_id = _text(scenario.scenario_id, "scenario.scenario_id")
    hazard_type = _text(scenario.hazard_type, "scenario.hazard_type")
    edge_artifact_id = _text(edge_geometry_artifact_id, "edge_geometry_artifact_id")
    hazard_artifact_ids = tuple(
        _text(item, "hazard_geometry_artifact_ids[]")
        for item in hazard_geometry_artifact_ids
    )
    if not hazard_artifact_ids or len(hazard_artifact_ids) != len(set(hazard_artifact_ids)):
        raise HazardContractError("hazard_geometry_artifact_ids must be non-empty and unique")
    if hazard_artifact_ids != tuple(sorted(hazard_artifact_ids)):
        raise HazardContractError("hazard_geometry_artifact_ids must use canonical order")
    try:
        edge_records = artifact_index.records_for(edge_artifact_id)
        if edge_id not in artifact_index.feature_ids_for(edge_artifact_id):
            raise HazardContractError("edge_id does not resolve through the edge artifact")
        if any(record.artifact_role != "CORRIDOR_GEOMETRY" for record in edge_records):
            raise HazardContractError("edge artifact is not validated corridor geometry")
        hazard_records = tuple(
            record
            for artifact_id in hazard_artifact_ids
            for record in artifact_index.records_for(artifact_id)
        )
        if any(
            record.artifact_role != "OFFICIAL_HAZARD_GEOMETRY"
            or record.source_class != "OFFICIAL"
            or record.data_class != "REAL"
            for record in hazard_records
        ):
            raise HazardContractError("hazard artifacts must be validated official REAL geometry")
        hazard_source_ids = {record.source_id for record in hazard_records}
        if set(scenario.source_ids) != hazard_source_ids:
            raise HazardContractError(
                "scenario source_ids must exactly resolve through official hazard artifacts"
            )
        edge_payload = artifact_index.payload_for(edge_artifact_id)
        edge_feature = next(
            feature
            for feature in edge_payload["features"]
            if isinstance(feature, Mapping) and feature.get("id") == edge_id
        )
        edge_geometry = edge_feature["geometry"]
        if not isinstance(edge_geometry, Mapping):
            raise HazardContractError("resolved edge geometry is invalid")
        lines = _line_parts(edge_geometry)
        intersecting_hazard_feature_ids: list[str] = []
        observed_hazard_types: set[str] = set()
        for hazard_artifact_id in hazard_artifact_ids:
            hazard_payload = artifact_index.payload_for(hazard_artifact_id)
            for feature in hazard_payload["features"]:
                if not isinstance(feature, Mapping) or not isinstance(feature.get("geometry"), Mapping):
                    raise HazardContractError("resolved hazard geometry is invalid")
                properties = feature.get("properties")
                if not isinstance(properties, Mapping):
                    raise HazardContractError("resolved hazard properties are invalid")
                observed_hazard_types.add(
                    _text(properties.get("hazard_type"), "hazard feature hazard_type")
                )
                polygons = _polygon_parts(feature["geometry"])
                if any(
                    _line_intersects_polygon(line, polygon)
                    for line in lines
                    for polygon in polygons
                ):
                    intersecting_hazard_feature_ids.append(str(feature["id"]))
        if observed_hazard_types != {hazard_type}:
            raise HazardContractError(
                "scenario hazard_type must exactly match all official hazard features"
            )
    except (RealArtifactContractError, KeyError, StopIteration, TypeError) as error:
        if isinstance(error, HazardContractError):
            raise
        raise HazardContractError(str(error)) from error

    all_records = tuple(edge_records) + hazard_records
    source_ids = tuple(sorted({record.source_id for record in all_records}))
    source_feature_ids = tuple(sorted({record.source_feature_id for record in all_records}))
    revision_ids = tuple(sorted({record.revision_id for record in all_records}))
    intersecting_hazard_feature_ids_tuple = tuple(
        sorted(set(intersecting_hazard_feature_ids))
    )
    if intersecting_hazard_feature_ids_tuple:
        return EdgeHazardObservationV2(
            schema_version="2.0.0",
            edge_id=edge_id,
            scenario_id=scenario_id,
            hazard_type=hazard_type,
            scenario_source_status=scenario.source_status,
            scenario_authority=scenario.official_or_assumption,
            scenario_coverage_complete=scenario.coverage_complete,
            scenario_default_edge_state=scenario.default_edge_state,
            scenario_source_ids=scenario.source_ids,
            scenario_elapsed_time_sec=scenario.elapsed_time_sec,
            overlap=True,
            overlap_length_m=None,
            max_depth_m=None,
            mean_depth_m=None,
            coverage_status="PARTIAL",
            official_closure=None,
            hazard_data_status="KNOWN",
            data_class="MODEL_DERIVED",
            source_ids=source_ids,
            hazard_geometry_artifact_ids=hazard_artifact_ids,
            edge_geometry_artifact_ids=(edge_artifact_id,),
            official_closure_source_ids=(),
            intersecting_hazard_feature_ids=intersecting_hazard_feature_ids_tuple,
            source_feature_ids=source_feature_ids,
            revision_ids=revision_ids,
            method="deterministic EPSG:4326 line/polygon predicate; length and depth not computed",
            lineage=(
                "validated immutable corridor geometry",
                "validated immutable official hazard geometry",
                "model-derived intersection predicate",
            ),
            _token=_EDGE_HAZARD_TOKEN,
        )
    return EdgeHazardObservationV2(
        schema_version="2.0.0",
        edge_id=edge_id,
        scenario_id=scenario_id,
        hazard_type=hazard_type,
        scenario_source_status=scenario.source_status,
        scenario_authority=scenario.official_or_assumption,
        scenario_coverage_complete=scenario.coverage_complete,
        scenario_default_edge_state=scenario.default_edge_state,
        scenario_source_ids=scenario.source_ids,
        scenario_elapsed_time_sec=scenario.elapsed_time_sec,
        overlap=None,
        overlap_length_m=None,
        max_depth_m=None,
        mean_depth_m=None,
        coverage_status="UNKNOWN",
        official_closure=None,
        hazard_data_status="UNKNOWN",
        data_class="UNKNOWN",
        source_ids=source_ids,
        hazard_geometry_artifact_ids=hazard_artifact_ids,
        edge_geometry_artifact_ids=(edge_artifact_id,),
        official_closure_source_ids=(),
        intersecting_hazard_feature_ids=(),
        source_feature_ids=source_feature_ids,
        revision_ids=revision_ids,
        method="no intersection observed; official dataset coverage completeness is unverified",
        lineage=(
            "validated immutable corridor geometry",
            "validated immutable official hazard geometry",
            "no-overlap not asserted without coverage authority",
        ),
        _token=_EDGE_HAZARD_TOKEN,
    )
