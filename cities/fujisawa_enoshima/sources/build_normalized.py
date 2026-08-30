"""Build the bounded Fujisawa/Enoshima real-data artifacts deterministically.

External inputs are treated as untrusted data.  This script reads only explicit
paths, selects a fixed corridor, preserves raw feature identity, and never
infers width, slope, steps, entrances, capacity, operation, or passability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any


CITY_ID = "fujisawa_enoshima"
SNAPSHOT_AT = "2026-08-30T00:00:00Z"
OSM_WAY_IDS = (27423903, 27423906)
A40_BBOX = (139.4800, 35.3018, 139.4842, 35.3082)
OSM_MAX_BYTES = 2_000_000
A40_PREVIEW_MAX_BYTES = 5_000_000
PLATEAU_MAX_BYTES = 16_000_000
MAX_FEATURES = 20_000
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _reject_nonfinite(token: str) -> object:
    raise ValueError(f"non-finite JSON constant: {token}")


def _read_json(path: Path, *, max_bytes: int) -> dict[str, Any]:
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"JSON input size {size} exceeds limit {max_bytes}: {path.name}")
    value = json.loads(
        path.read_text(encoding="utf-8-sig"),
        object_pairs_hook=_reject_duplicate_pairs,
        parse_constant=_reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _write_json(path: Path, value: object) -> str:
    payload = _canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require_sha256(value: str, name: str) -> str:
    normalized = value.lower()
    if not SHA256_PATTERN.fullmatch(normalized):
        raise ValueError(f"{name} must be a lowercase SHA-256")
    return normalized


def _finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _finite_tag_number(value: object, name: str) -> float:
    if isinstance(value, str):
        if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", value):
            raise ValueError(f"{name} must be a finite decimal tag")
        value = float(value)
    return _finite_number(value, name)


def _osm_yes_no_unknown(value: object, name: str) -> bool | str:
    if value is None:
        return "UNKNOWN"
    if value == "yes":
        return True
    if value == "no":
        return False
    raise ValueError(f"{name} must be exact OSM yes/no when present")


def _round_coordinates(value: object) -> object:
    if isinstance(value, list):
        if len(value) == 2 and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
            longitude = _finite_number(value[0], "longitude")
            latitude = _finite_number(value[1], "latitude")
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                raise ValueError("coordinate is outside longitude/latitude bounds")
            return [round(longitude, 7), round(latitude, 7)]
        return [_round_coordinates(item) for item in value]
    raise ValueError("geometry coordinates must be nested arrays")


def _geometry_bbox(geometry: dict[str, Any]) -> tuple[float, float, float, float]:
    points: list[list[float]] = []

    def visit(value: object) -> None:
        if isinstance(value, list):
            if len(value) == 2 and all(isinstance(item, (int, float)) for item in value):
                points.append([float(value[0]), float(value[1])])
            else:
                for item in value:
                    visit(item)

    visit(geometry["coordinates"])
    if not points:
        raise ValueError("empty geometry")
    return (
        min(point[0] for point in points),
        min(point[1] for point in points),
        max(point[0] for point in points),
        max(point[1] for point in points),
    )


def _bbox_intersects(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> bool:
    return not (
        first[2] < second[0]
        or first[0] > second[2]
        or first[3] < second[1]
        or first[1] > second[3]
    )


def _bbox_contains(
    outer: tuple[float, float, float, float],
    inner: tuple[float, float, float, float],
) -> bool:
    return (
        inner[0] >= outer[0]
        and inner[1] >= outer[1]
        and inner[2] <= outer[2]
        and inner[3] <= outer[3]
    )


def _select_a40_preview_features(
    document: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    """Return intersecting A40 polygons with content-derived, order-stable IDs."""

    if document.get("type") != "FeatureCollection":
        raise ValueError("A40 preview input must be a FeatureCollection")
    features = document.get("features")
    if not isinstance(features, list):
        raise ValueError("A40 preview features must be an array")
    if len(features) > MAX_FEATURES:
        raise ValueError(f"A40 preview feature count exceeds limit {MAX_FEATURES}")

    selected: dict[str, dict[str, Any]] = {}
    for feature in features:
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            raise ValueError("A40 preview contains a non-Feature item")
        geometry = feature.get("geometry")
        properties = feature.get("properties")
        if not isinstance(geometry, dict) or geometry.get("type") != "Polygon":
            raise ValueError("A40 preview supports Polygon geometry only")
        if not isinstance(properties, dict):
            raise ValueError("A40 preview feature properties must be an object")
        normalized = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": _round_coordinates(geometry.get("coordinates")),
            },
            "properties": properties,
        }
        if not _bbox_intersects(A40_BBOX, _geometry_bbox(normalized["geometry"])):
            continue
        source_id = f"sha256:{_canonical_sha256(normalized)}"
        if source_id in selected:
            raise ValueError(f"duplicate A40 preview feature: {source_id}")
        selected[source_id] = normalized

    if not selected:
        raise ValueError("A40 preview selection is empty")
    return sorted(selected.items())


def _stable_token(value: object, *, length: int = 16) -> str:
    return _canonical_sha256(value)[:length].upper()


def _topology_counts(
    node_features: list[dict[str, Any]], edge_features: list[dict[str, Any]]
) -> dict[str, int]:
    node_ids = [item["properties"]["node_id"] for item in node_features]
    edge_ids = [item["properties"]["edge_id"] for item in edge_features]
    adjacency = {node_id: set() for node_id in node_ids}
    self_loops = 0
    zero_length_edges = 0
    for edge in edge_features:
        properties = edge["properties"]
        start = properties["from_node"]
        end = properties["to_node"]
        if start not in adjacency or end not in adjacency:
            raise ValueError(f"edge references missing node: {properties['edge_id']}")
        self_loops += start == end
        coordinates = edge["geometry"]["coordinates"]
        zero_length_edges += coordinates[0] == coordinates[-1]
        adjacency[start].add(end)
        adjacency[end].add(start)

    components = 0
    unseen = set(adjacency)
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            for neighbor in adjacency[stack.pop()]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
    return {
        "nodes": len(node_features),
        "edges": len(edge_features),
        "duplicate_node_ids": len(node_ids) - len(set(node_ids)),
        "duplicate_edge_ids": len(edge_ids) - len(set(edge_ids)),
        "dangling_endpoint_nodes": sum(len(neighbors) == 1 for neighbors in adjacency.values()),
        "self_loops": self_loops,
        "zero_length_edges": zero_length_edges,
        "connected_components": components,
    }


def _lineage_properties(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: record[key]
        for key in (
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
        )
    }


def _record(
    *,
    artifact_id: str,
    artifact_path: str,
    artifact_role: str,
    source_id: str,
    source_url: str,
    source_class: str,
    license_name: str,
    license_terms_url: str,
    obligations: list[str],
    artifact_sha256: str,
    source_artifact_path: str,
    source_sha256: str,
    retrieval_method: str,
    retrieval_query_path: str | None,
    retrieval_query_sha256: str | None,
    snapshot_at: str | None,
    snapshot_reason: str | None,
    source_revision: str,
    source_crs: str,
    processing_crs: str,
    transform_history: list[str],
    source_feature_id: str,
    stable_feature_id: str,
    lineage: list[str],
) -> dict[str, Any]:
    return {
        "city_id": CITY_ID,
        "artifact_id": artifact_id,
        "artifact_path": artifact_path,
        "artifact_role": artifact_role,
        "source_id": source_id,
        "source_url": source_url,
        "source_reference": None,
        "source_class": source_class,
        "data_class": "REAL",
        "accessed_at": "2026-08-30",
        "valid_as_of": "2026-08-30" if source_class == "VGI" else None,
        "valid_as_of_reason": None
        if source_class == "VGI"
        else "A40 basis year 2020 does not identify one observation date",
        "license": license_name,
        "license_terms_url": license_terms_url,
        "license_review_status": "AGENT_REVIEWED_HUMAN_PENDING",
        "redistribution_status": "PERMITTED_WITH_OBLIGATIONS",
        "redistribution_obligations": obligations,
        "sha256": artifact_sha256,
        "source_artifact_path": source_artifact_path,
        "source_sha256": source_sha256,
        "retrieval_method": retrieval_method,
        "retrieval_query_path": retrieval_query_path,
        "retrieval_query_sha256": retrieval_query_sha256,
        "snapshot_at": snapshot_at,
        "snapshot_reason": snapshot_reason,
        "source_revision": source_revision,
        "source_crs": source_crs,
        "processing_crs": processing_crs,
        "output_crs": "EPSG:4326",
        "axis_order": "longitude_latitude",
        "horizontal_unit": "degree",
        "vertical_datum": None,
        "vertical_datum_reason": "2D source geometry has no registered vertical datum",
        "transform_history": transform_history,
        "source_feature_id": source_feature_id,
        "stable_feature_id": stable_feature_id,
        "revision_id": "20260830-r1",
        "lineage": lineage,
        "geometry_status": "SOURCE_TRACEABLE_REAL",
    }


def build(
    city: Path,
    a40_path: Path,
    a40_zip_sha256: str,
    plateau_path: Path | None,
    plateau_sha256: str | None,
) -> None:
    osm_raw_path = city / "sources" / "osm-corridor.raw.json"
    query_path = city / "sources" / "osm-corridor.overpassql"
    a40_zip_sha256 = _require_sha256(a40_zip_sha256, "A40 ZIP SHA-256")
    if plateau_sha256 is not None:
        plateau_sha256 = _require_sha256(plateau_sha256, "PLATEAU catalog SHA-256")
    osm = _read_json(osm_raw_path, max_bytes=OSM_MAX_BYTES)
    elements = osm.get("elements")
    if not isinstance(elements, list) or len(elements) > MAX_FEATURES:
        raise ValueError("OSM elements must be a bounded array")
    ways = {
        int(item["id"]): item
        for item in elements
        if isinstance(item, dict) and item.get("type") == "way" and item.get("id") in OSM_WAY_IDS
    }
    if set(ways) != set(OSM_WAY_IDS):
        raise ValueError(f"missing fixed OSM ways: {sorted(set(OSM_WAY_IDS) - set(ways))}")

    corridor_records: list[dict[str, Any]] = []
    corridor_features: list[dict[str, Any]] = []
    for way_id in OSM_WAY_IDS:
        way = ways[way_id]
        points = way.get("geometry")
        if not isinstance(points, list) or len(points) < 2 or len(points) > MAX_FEATURES:
            raise ValueError(f"OSM way/{way_id} geometry must be a bounded line")
        geometry = {
            "type": "LineString",
            "coordinates": [
                _round_coordinates([point.get("lon"), point.get("lat")])
                if isinstance(point, dict)
                else (_ for _ in ()).throw(ValueError(f"OSM way/{way_id} point must be an object"))
                for point in points
            ],
        }
        stable_id = f"fujisawa-enoshima:corridor:osm-way-{way_id}"
        record = _record(
            artifact_id="fujisawa-osm-corridor-v1",
            artifact_path="geography/corridor.real.geojson",
            artifact_role="CORRIDOR_GEOMETRY",
            source_id="osm-overpass-fujisawa-20260830",
            source_url="https://www.openstreetmap.org/copyright",
            source_class="VGI",
            license_name="ODbL-1.0",
            license_terms_url="https://opendatacommons.org/licenses/odbl/1-0/",
            obligations=["attribute OpenStreetMap contributors", "ODbL database/share-alike obligations"],
            artifact_sha256="PENDING",
            source_artifact_path="sources/osm-corridor.raw.json",
            source_sha256=_sha256(osm_raw_path),
            retrieval_method="BOUNDED_QUERY",
            retrieval_query_path="sources/osm-corridor.overpassql",
            retrieval_query_sha256=_sha256(query_path),
            snapshot_at=SNAPSHOT_AT,
            snapshot_reason=None,
            source_revision=f"OSM snapshot {SNAPSHOT_AT}",
            source_crs="EPSG:4326",
            processing_crs="EPSG:4326",
            transform_history=["fixed-time bounded Overpass query", "selected fixed corridor way IDs", "rounded coordinates to 7 decimals"],
            source_feature_id=f"way/{way_id}",
            stable_feature_id=stable_id,
            lineage=[f"OpenStreetMap way/{way_id}", "bounded candidate corridor selection; no field verification"],
        )
        tags = way.get("tags", {})
        if not isinstance(tags, dict):
            raise ValueError(f"OSM way/{way_id} tags must be an object")
        bridge = _osm_yes_no_unknown(tags.get("bridge"), "bridge")
        tunnel = _osm_yes_no_unknown(tags.get("tunnel"), "tunnel")
        layer = _finite_tag_number(tags["layer"], "layer") if "layer" in tags else None
        level = _finite_tag_number(tags["level"], "level") if "level" in tags else None
        properties = _lineage_properties(record)
        properties.update(
            {
                "bridge": bridge,
                "bridge_reason": None if bridge != "UNKNOWN" else "OSM bridge tag absent",
                "tunnel": tunnel,
                "tunnel_reason": None if tunnel != "UNKNOWN" else "OSM tunnel tag absent",
                "layer": layer,
                "layer_reason": None if layer is not None else "OSM layer tag absent",
                "level": level,
                "level_reason": None if level is not None else "OSM level tag absent",
            }
        )
        corridor_records.append(record)
        corridor_features.append({"type": "Feature", "id": stable_id, "geometry": geometry, "properties": properties})

    corridor_features.sort(key=lambda item: item["id"])
    corridor_document = {"type": "FeatureCollection", "features": corridor_features}
    corridor_sha = _write_json(city / "geography" / "corridor.real.geojson", corridor_document)
    for record in corridor_records:
        record["sha256"] = corridor_sha

    graph_nodes: dict[tuple[float, float], str] = {}
    graph_edges: list[dict[str, Any]] = []
    for way_id in OSM_WAY_IDS:
        source_feature = next(
            feature
            for feature in corridor_features
            if feature["properties"]["source_feature_id"] == f"way/{way_id}"
        )
        coordinates = source_feature["geometry"]["coordinates"]
        source_properties = source_feature["properties"]
        for coordinate in coordinates:
            key = (coordinate[0], coordinate[1])
            graph_nodes.setdefault(
                key,
                f"FJ-OSM-N-{_stable_token({'coordinate': [key[0], key[1]]})}",
            )
        for start, end in zip(coordinates, coordinates[1:]):
            segment_identity = {
                "source_way_id": way_id,
                "start": start,
                "end": end,
            }
            edge_token = _stable_token(segment_identity)
            graph_edges.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [start, end]},
                    "properties": {
                        "edge_id": f"FJ-OSM-E-{edge_token}",
                        "from_node": graph_nodes[(start[0], start[1])],
                        "to_node": graph_nodes[(end[0], end[1])],
                        "data_status": "REAL_VGI_CANDIDATE",
                        "geometry_status": "SOURCE_TRACEABLE_REAL",
                        "source_class": "VGI",
                        "source_feature_id": f"way/{way_id}#segment-sha256/{_canonical_sha256(segment_identity)}",
                        "stable_feature_id": f"fujisawa-enoshima:edge:osm-{edge_token.lower()}",
                        "revision_id": "20260830-r1",
                        "lineage": [f"OpenStreetMap way/{way_id}", "consecutive source geometry vertices"],
                        "bridge": source_properties["bridge"],
                        "bridge_reason": source_properties["bridge_reason"],
                        "tunnel": source_properties["tunnel"],
                        "tunnel_reason": source_properties["tunnel_reason"],
                        "level": source_properties["level"],
                        "level_reason": source_properties["level_reason"],
                        "layer": source_properties["layer"],
                        "layer_reason": source_properties["layer_reason"],
                        "width_m": None,
                        "width_m_reason": "No reviewed source width or field measurement is connected",
                        "slope": None,
                        "slope_reason": "No reviewed source slope or field measurement is connected",
                        "step_status": "UNKNOWN",
                        "step_status_reason": "OSM step semantics are not established for this segment",
                        "accessibility_state": "UNKNOWN",
                        "accessibility_state_reason": "M6/profile and field validation are not connected",
                        "official_closure": None,
                        "official_closure_reason": "No current official closure feed is connected",
                        "operation_status": "UNKNOWN",
                        "operation_status_reason": "No current operator status feed is connected",
                        "length_m": None,
                        "length_m_reason": "Geodesic length derivation is not reviewed or connected",
                        "topology_status": "CANDIDATE",
                    },
                }
            )
    graph_edges.sort(key=lambda item: item["properties"]["edge_id"])
    node_features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [coordinate[0], coordinate[1]]},
            "properties": {
                "node_id": node_id,
                "data_status": "REAL_VGI_CANDIDATE",
                "geometry_status": "SOURCE_TRACEABLE_REAL",
                "source_class": "VGI",
                "source_feature_id": f"osm-coordinate/{coordinate[0]:.7f},{coordinate[1]:.7f}",
                "stable_feature_id": f"fujisawa-enoshima:node:{node_id.lower()}",
                "revision_id": "20260830-r1",
                "lineage": ["exact shared OSM source vertex; no nearest-neighbour join"],
                "node_role": "candidate_graph_vertex",
                "entrance_status": "UNKNOWN",
                "entrance_status_reason": "Candidate graph vertex is not a field-verified entrance",
            },
        }
        for coordinate, node_id in sorted(graph_nodes.items(), key=lambda item: item[1])
    ]
    graph_metadata = {
        "schema_version": "2.0.0",
        "source_crs": "EPSG:4326",
        "processing_crs": "EPSG:4326",
        "output_crs": "EPSG:4326",
        "horizontal_unit": "degree",
        "vertical_unit": "UNKNOWN",
        "axis_order": "longitude_latitude",
        "coordinate_precision": 7,
        "transform_history": ["segmented only at exact OSM geometry vertices; no inferred joins"],
        "geometry_status": "SOURCE_TRACEABLE_REAL",
        "source_feature_id": "way/27423903+way/27423906",
        "stable_feature_id": "FUJISAWA-ENOSHIMA-CANDIDATE-GRAPH-V1",
        "revision_id": "20260830-r1",
        "lineage": ["fixed-time bounded OSM source", "candidate graph; no field or administrative validation"],
        "topology_status": "CANDIDATE",
    }
    _write_json(city / "graph" / "candidate_walk_nodes.real.geojson", {"type": "FeatureCollection", "metadata": graph_metadata, "features": node_features})
    _write_json(city / "graph" / "candidate_walk_edges.real.geojson", {"type": "FeatureCollection", "metadata": graph_metadata, "features": graph_edges})

    a40 = _read_json(a40_path, max_bytes=A40_PREVIEW_MAX_BYTES)
    selected = _select_a40_preview_features(a40)
    source_clip = {
        "type": "FeatureCollection",
        "metadata": {
            "source_name": "A40-20_14_GML.zip operator-supplied derivative",
            "source_crs": "EPSG:6668",
            "output_crs": "UNVERIFIED_NOT_RELABELLED",
            "selection_bbox": list(A40_BBOX),
            "selection_method": "feature bbox intersects the fixed preview bbox",
            "connection_status": "NOT_CONNECTED",
            "original_source_trust_bound": False,
            "original_source_trust_reason": "The original official ZIP is not retained in the task staging contract; an operator-provided SHA string cannot bind this derivative to that ZIP.",
            "license_review_status": "HUMAN_PENDING",
            "coverage_complete": False,
            "coverage_reason": "Intersection selection from a derivative does not prove complete official source coverage.",
        },
        "features": [
            {
                "type": "Feature",
                "id": source_id,
                "geometry": feature["geometry"],
                "properties": feature.get("properties", {}),
            }
            for source_id, feature in selected
        ],
    }
    source_clip_path = city / "sources" / "a40-tsunami-source.clip.geojson"
    source_clip_sha = _write_json(source_clip_path, source_clip)

    hazard_features: list[dict[str, Any]] = []
    for source_id, feature in selected:
        stable_id = f"fujisawa-enoshima:hazard-preview:{source_id.removeprefix('sha256:')}"
        hazard_features.append(
            {
                "type": "Feature",
                "id": stable_id,
                "geometry": feature["geometry"],
                "properties": {
                "city_id": CITY_ID,
                "source_id": "mlit-ksj-a40-20-14-unbound-preview",
                "source_class": "OFFICIAL_DERIVED_PREVIEW",
                "data_class": "DERIVED_PREVIEW_NOT_CONNECTED",
                "source_feature_id": source_id,
                "stable_feature_id": stable_id,
                "revision_id": "20260830-r2",
                "geometry_status": "DERIVED_PREVIEW_NOT_CONNECTED",
                "lineage": ["operator-provided A40 derivative", "content-derived preview selection; original ZIP not trust-bound"],
                "hazard_type": "TSUNAMI_INUNDATION_ASSUMPTION",
                "hazard_category": None,
                "hazard_category_reason": "A40 depth category withheld from decision logic pending human/A1 review",
                "hazard_value": None,
                "hazard_value_unit": None,
                "hazard_value_reason": "No numeric depth imported into this lane",
                "official_closure": None,
                "official_closure_reason": "No current official closure feed is connected",
                "operation_status": "UNKNOWN",
                "operation_status_reason": "No current operator status feed is connected",
                "arrival_time_min": None,
                "arrival_time_reason": "No reviewed tsunami arrival-time source is connected",
                },
            }
        )
    hazard_features.sort(key=lambda item: item["id"])
    _write_json(
        city / "hazards" / "official-tsunami.real.geojson",
        {
            "type": "FeatureCollection",
            "metadata": {
                "connection_status": "NOT_CONNECTED",
                "coverage_complete": False,
                "coverage_reason": "The original official ZIP, CRS transformation, license interpretation, and corridor coverage have not been independently verified.",
                "source_crs": "EPSG:6668",
                "output_crs": "UNVERIFIED_NOT_RELABELLED",
                "original_source_trust_bound": False,
                "original_source_trust_reason": "Only an operator-provided derivative and separately asserted ZIP SHA are available; byte lineage to the original ZIP is unproven.",
                "license_review_status": "HUMAN_PENDING",
            },
            "features": hazard_features,
        },
    )

    records = sorted(corridor_records, key=lambda item: item["stable_feature_id"])
    _write_json(
        city / "sources" / "real-artifacts-v2.json",
        {"schema_version": "2.0.0", "city_id": CITY_ID, "artifacts": records},
    )

    plateau_bytes: int | None = None
    if plateau_path is not None:
        if plateau_sha256 is None:
            raise ValueError("PLATEAU catalog SHA-256 is required with a catalog path")
        plateau = _read_json(plateau_path, max_bytes=PLATEAU_MAX_BYTES)
        datasets = plateau.get("datasets")
        if not isinstance(datasets, list) or len(datasets) > MAX_FEATURES:
            raise ValueError("PLATEAU datasets must be a bounded array")
        selected_plateau = sorted(
            [
                {
                    key: item.get(key)
                    for key in ("city_code", "type_en", "year", "format", "lod", "texture", "url", "composite_url")
                }
                for item in datasets
                if isinstance(item, dict)
                and item.get("city_code") == "14205"
                and item.get("year") == 2025
                and item.get("type_en") in {"bldg", "brid", "tran"}
            ],
            key=lambda item: (str(item["type_en"]), str(item["lod"]), str(item["texture"])),
        )
        plateau_bytes = plateau_path.stat().st_size
        _write_json(
            city / "sources" / "plateau_metadata.json",
            {
                "source_class": "OFFICIAL_METADATA_ONLY",
                "source_url": "https://api.plateauview.mlit.go.jp/datacatalog/plateau-datasets",
                "accessed_at": "2026-08-30",
                "raw_catalog_sha256": plateau_sha256,
                "city_code": "14205",
                "records": selected_plateau,
                "connection_status": "METADATA_RECORDED_UNBOUND_NOT_CONNECTED",
                "reason": "This lane records operator-retrieved official URLs, but raw catalog bytes, Cesium loading, CORS, extent coverage, and UI connection are not independently verified here.",
            },
        )
    _write_json(
        city / "sources" / "external-source-checksums.json",
        {
            "schema_version": "1.0.0",
            "sources": [
                {
                    "path_hint": "Git-external A40-20_14_GML.zip",
                    "source_url": "https://nlftp.mlit.go.jp/ksj/gml/data/A40/A40-20/A40-20_14_GML.zip",
                    "sha256": a40_zip_sha256,
                    "bytes": 29821436,
                    "retention": "Git-external operator-local raw store",
                    "verification_status": "UNBOUND_OPERATOR_ASSERTION_NOT_CONNECTION_AUTHORITY",
                    "connection_authority": False,
                    "license_review_status": "HUMAN_PENDING",
                    "redistribution_status": "UNKNOWN",
                },
                {
                    "path_hint": "Git-external PLATEAU catalog snapshot",
                    "source_url": "https://api.plateauview.mlit.go.jp/datacatalog/plateau-datasets",
                    "sha256": plateau_sha256,
                    "bytes": plateau_bytes,
                    "bytes_reason": None
                    if plateau_bytes is not None
                    else "Raw PLATEAU catalog was not supplied to this rebuild; byte count is UNKNOWN.",
                    "retention": "Git-external operator-local raw store",
                    "verification_status": "UNBOUND_OPERATOR_ASSERTION_NOT_CONNECTION_AUTHORITY",
                    "connection_authority": False,
                    "license_review_status": "HUMAN_PENDING",
                    "redistribution_status": "UNKNOWN",
                },
            ],
        },
    )

    topology_counts = _topology_counts(node_features, graph_edges)
    _write_json(
        city / "graph" / "candidate_topology_qa.real.json",
        {
            "schema_version": "2.0.0",
            "graph_status": "CANDIDATE",
            "data_class": "REAL_VGI_CANDIDATE",
            "counts": topology_counts,
            "geometric_crossing_policy": "NO_NODE_WITHOUT_SHARED_SOURCE_VERTEX",
            "grade_separation": {"bridge_source_way": "way/27423903", "bridge": True, "layer": 1},
            "disconnected_destinations": {"status": "NOT_COMPUTED", "reason": "No field-verified facility entrance is connected."},
            "unsplit_hazard_boundaries": {"status": "NOT_COMPUTED", "reason": "Hazard overlap adapter is outside this city-lane writer ownership; no closure is inferred."},
            "promotion_status": "BLOCKED_FIELD_AND_ADMIN_REVIEW",
            "promotion_reason": "Widths, slopes, steps, entrances, access, and operational conditions remain UNKNOWN.",
        },
    )
    bridge_coordinates = ways[27423903]["geometry"]
    _write_json(
        city / "geography" / "corridor_landmarks.json",
        {
            "schema_version": "1.0.0",
            "source_class": "VGI",
            "geometry_status": "SOURCE_TRACEABLE_REAL",
            "landmarks": [
                {"landmark_id": "KATASE_COAST", "label": "片瀬海岸側接続点（候補）", "source_feature_id": "way/27423903", "coordinate": [bridge_coordinates[0]["lon"], bridge_coordinates[0]["lat"]], "geometry_status": "SOURCE_TRACEABLE_REAL", "entrance_status": "UNKNOWN", "entrance_status_reason": "Task-scope anchor is not a field-verified entrance"},
                {"landmark_id": "BENTEN_BRIDGE", "label": "江の島弁天橋（OSM bridge tag候補）", "source_feature_id": "way/27423903", "coordinate": [bridge_coordinates[len(bridge_coordinates) // 2]["lon"], bridge_coordinates[len(bridge_coordinates) // 2]["lat"]], "geometry_status": "SOURCE_TRACEABLE_REAL", "entrance_status": "UNKNOWN", "entrance_status_reason": "Task-scope anchor is not a field-verified entrance"},
                {"landmark_id": "ENOSHIMA_ENTRANCE", "label": "江の島入口側接続点（候補）", "source_feature_id": "way/27423903", "coordinate": [bridge_coordinates[-1]["lon"], bridge_coordinates[-1]["lat"]], "geometry_status": "SOURCE_TRACEABLE_REAL", "entrance_status": "UNKNOWN", "entrance_status_reason": "Task-scope anchor is not a field-verified entrance"},
            ],
            "limitations": "Labels describe task-scope anchors on VGI geometry; they are not field-verified entrances or passability claims.",
        },
    )

    geometry_status_by_path = {
        "geography/corridor.real.geojson": "SOURCE_TRACEABLE_REAL",
        "geography/corridor_landmarks.json": "SOURCE_TRACEABLE_REAL_VGI_ANCHORS",
        "graph/candidate_walk_nodes.real.geojson": "SOURCE_TRACEABLE_REAL_CANDIDATE",
        "graph/candidate_walk_edges.real.geojson": "SOURCE_TRACEABLE_REAL_CANDIDATE",
        "graph/candidate_topology_qa.real.json": "SOURCE_TRACEABLE_REAL_CANDIDATE_QA",
        "hazards/official-tsunami.real.geojson": "OFFICIAL_DERIVED_PREVIEW_NOT_CONNECTED",
        "sources/a40-tsunami-source.clip.geojson": "OFFICIAL_DERIVED_SOURCE_PREVIEW_NOT_CONNECTED",
        "sources/osm-corridor.raw.json": "VGI_RETAINED_RAW_GEOMETRY",
        "graph/walk_nodes.geojson": "SYNTHETIC_DEMO",
        "graph/walk_edges.geojson": "SYNTHETIC_DEMO",
        "graph/topology_qa.json": "SYNTHETIC_DEMO_CANDIDATE",
        "pois/pois.csv": "SYNTHETIC_DEMO",
        "hazards/edge_states.csv": "SYNTHETIC_DEMO",
        "viewer/city_config.json": "SYNTHETIC_DEMO_AND_METADATA_ONLY",
    }
    artifacts = []
    for path in sorted(city.rglob("*")):
        if not path.is_file() or path.name in {
            ".gitattributes",
            "README.md",
            "artifact_manifest.json",
        }:
            continue
        relative = path.relative_to(city).as_posix()
        if "__pycache__" in path.parts:
            continue
        artifacts.append(
            {
                "path": relative,
                "schema_version": "1.0.0",
                "geometry_status": geometry_status_by_path.get(relative, "NON_GEOMETRY_OR_METADATA_ONLY"),
            }
        )
    _write_json(
        city / "artifact_manifest.json",
        {
            "schema_version": "1.0.0",
            "city_id": CITY_ID,
            "source_crs": "MIXED_EPSG_4326_AND_UNVERIFIED_A40_DERIVATIVE",
            "processing_crs": "MIXED_SEE_PER_ARTIFACT_METADATA",
            "output_crs": "MIXED_EPSG_4326_AND_UNVERIFIED_NOT_RELABELLED",
            "horizontal_unit": "degree",
            "vertical_unit": "UNKNOWN",
            "axis_order": "longitude_latitude",
            "coordinate_precision": 7,
            "transform_history": ["Legacy synthetic artifacts retained separately", "Only reviewed VGI corridor artifacts are hash-bound by sources/real-artifacts-v2.json", "A40 derivative is preview-only until original ZIP, CRS conversion, license, and coverage are reviewed"],
            "geometry_status": "MIXED_REAL_VGI_CANDIDATE_A40_PREVIEW_NOT_CONNECTED_AND_SYNTHETIC",
            "source_feature_id": "MULTI_SOURCE_SEE_REAL_ARTIFACTS_V2",
            "stable_feature_id": "FJ-ARTIFACT-MANIFEST",
            "revision_id": "20260830-r2",
            "lineage": ["Fujisawa Phase 2 lane; VGI candidate, official-derived preview, model, and synthetic axes remain separate"],
            "artifacts": artifacts,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", type=Path, required=True)
    parser.add_argument("--a40-geojson", type=Path, required=True)
    parser.add_argument("--a40-zip-sha256", required=True)
    parser.add_argument("--plateau-catalog", type=Path)
    parser.add_argument("--plateau-catalog-sha256")
    args = parser.parse_args()
    build(args.city, args.a40_geojson, args.a40_zip_sha256, args.plateau_catalog, args.plateau_catalog_sha256)


if __name__ == "__main__":
    main()
