"""Build the additive Arashiyama real-data lane from retained source bytes.

The bounded OSM response is small and redistributable under ODbL obligations,
so its exact bytes are retained inside the city package.  The much larger MLIT
A31b archive remains outside Git; only a bounded, source-checksummed preparation
is emitted.  No accessibility, operation, closure, or M7 value is inferred.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
import shutil
import zipfile


CITY_ID = "kyoto_arashiyama"
BBOX = (135.6748, 35.0087, 135.6802, 35.0153)
OSM_RAW_NAME = "osm_arashiyama_20260829.raw.json"
OSM_QUERY_NAME = "osm_arashiyama_20260829.overpassql"
FLOOD_ZIP_NAME = "A31b-25_10_5235_GEOJSON.zip"
FLOOD_MEMBER = "20_想定最大規模/A31b-20-25_10_5235.geojson"
EXPECTED_OSM_SHA256 = "1cde93d68bebf633989e825cbd5ac1e772cee81508043f44beb311250a1e8013"
EXPECTED_QUERY_SHA256 = "b5c52b3ea7542261159b5764956aa9662673c0422b3509dc59e4866f00c14603"
EXPECTED_FLOOD_SHA256 = "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c"
FLOOD_SOURCE_ID = "mlit-ksj-a31b-2025-5235-max"
FLOOD_PREVIEW_REVISION = "mlit-a31b-2025-5235-max-preview-v2"
OVERLAP_PREVIEW_REVISION = "arashiyama-a31b-osm-overlap-preview-v2"
EXPECTED_LEGACY_FLOOD_PREVIEW_SHA256 = "49ce418868f10c2e385912b86cd72f5c41fd3ca8387c26cfd55ec0eef5d14e32"
EXPECTED_CANONICAL_FLOOD_PREVIEW_SHA256 = "2136fb313319bf1b8500edd409a80c5bef8e5cbae9e412a5cd1c663ecfeefa5b"


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _write_json(path: Path, value: object) -> str:
    payload = _canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _inside(coordinate: list[float]) -> bool:
    lon, lat = coordinate
    return BBOX[0] <= lon <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]


def _known_bool(tags: dict[str, str], key: str) -> tuple[bool | str, str | None]:
    raw = tags.get(key)
    if raw in {"yes", "true", "1"}:
        return True, None
    if raw in {"no", "false", "0"}:
        return False, None
    if raw is None:
        return "UNKNOWN", f"OSM way has no {key} tag"
    return "UNKNOWN", f"OSM {key} tag is not a supported boolean: {raw}"


def _known_number(tags: dict[str, str], key: str) -> tuple[float | int | None, str | None]:
    raw = tags.get(key)
    if raw is None:
        return None, f"OSM way has no {key} tag"
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None, f"OSM {key} tag is not a single numeric value: {raw}"
    if not math.isfinite(value):
        return None, f"OSM {key} tag is not finite"
    return (int(value) if value.is_integer() else value), None


def _osm_segments(
    raw: dict, *, source_sha256: str, query_sha256: str
) -> tuple[list[dict], list[dict], list[dict]]:
    corridor: list[dict] = []
    graph_edges: list[dict] = []
    node_coordinates: dict[str, list[float]] = {}
    for element in sorted(raw.get("elements", []), key=lambda item: item.get("id", 0)):
        if element.get("type") != "way" or "geometry" not in element:
            continue
        way_id = int(element["id"])
        tags = dict(element.get("tags", {}))
        osm_node_ids = element.get("nodes", [])
        geometry = [
            [round(float(item["lon"]), 7), round(float(item["lat"]), 7)]
            for item in element["geometry"]
        ]
        if len(osm_node_ids) != len(geometry):
            continue
        bridge, bridge_reason = _known_bool(tags, "bridge")
        tunnel, tunnel_reason = _known_bool(tags, "tunnel")
        layer, layer_reason = _known_number(tags, "layer")
        level, level_reason = _known_number(tags, "level")
        for segment_index in range(len(geometry) - 1):
            coordinates = [geometry[segment_index], geometry[segment_index + 1]]
            if not all(_inside(coordinate) for coordinate in coordinates):
                continue
            if coordinates[0] == coordinates[1]:
                continue
            from_id = f"kyoto-arashiyama:osm-node-{int(osm_node_ids[segment_index]):012d}"
            to_id = f"kyoto-arashiyama:osm-node-{int(osm_node_ids[segment_index + 1]):012d}"
            node_coordinates[from_id] = coordinates[0]
            node_coordinates[to_id] = coordinates[1]
            endpoint_node_ids = sorted(
                (int(osm_node_ids[segment_index]), int(osm_node_ids[segment_index + 1]))
            )
            stable_id = (
                f"kyoto-arashiyama:osm-way-{way_id:012d}:"
                f"nodes-{endpoint_node_ids[0]:012d}-{endpoint_node_ids[1]:012d}"
            )
            source_feature_id = f"way/{way_id}#segment/{segment_index}"
            lineage = [
                "OpenStreetMap way and original node IDs",
                "fixed-time bounded Overpass response retained as exact bytes",
                "consecutive source-node segmentation; no crossing-node invention",
            ]
            shared = {
                "artifact_id": "arashiyama-osm-corridor-v1",
                "city_id": CITY_ID,
                "data_class": "REAL",
                "geometry_status": "SOURCE_TRACEABLE_REAL",
                "lineage": lineage,
                "revision_id": "osm-2026-08-29-v1",
                "source_class": "VGI",
                "source_feature_id": source_feature_id,
                "source_id": "openstreetmap-overpass-arashiyama-20260829",
                "stable_feature_id": stable_id,
            }
            corridor.append(
                {
                    "geometry": {"coordinates": coordinates, "type": "LineString"},
                    "id": stable_id,
                    "properties": {
                        **shared,
                        "bridge": bridge,
                        "bridge_reason": bridge_reason,
                        "layer": layer,
                        "layer_reason": layer_reason,
                        "level": level,
                        "level_reason": level_reason,
                        "tunnel": tunnel,
                        "tunnel_reason": tunnel_reason,
                    },
                    "type": "Feature",
                }
            )
            graph_edges.append(
                {
                    "geometry": {"coordinates": coordinates, "type": "LineString"},
                    "id": stable_id,
                    "properties": {
                        "accessibility_reason": "No field-verified width, gradient, step, or surface evidence",
                        "accessibility_state": "UNKNOWN",
                        "bridge": bridge,
                        "bridge_reason": bridge_reason,
                        "data_class": "REAL",
                        "edge_id": stable_id,
                        "foot": tags.get("foot"),
                        "foot_reason": None if tags.get("foot") is not None else "OSM way has no foot tag",
                        "from_node": from_id,
                        "geometry_status": "SOURCE_TRACEABLE_REAL",
                        "highway": tags.get("highway"),
                        "layer": layer,
                        "layer_reason": layer_reason,
                        "level": level,
                        "level_reason": level_reason,
                        "name": tags.get("bridge:name") or tags.get("name"),
                        "name_reason": None if tags.get("bridge:name") or tags.get("name") else "OSM way has no bridge:name or name tag",
                        "name:en": tags.get("bridge:name:en") or tags.get("name:en"),
                        "name:en_reason": None if tags.get("bridge:name:en") or tags.get("name:en") else "OSM way has no bridge:name:en or name:en tag",
                        "operation_reason": "No official time-specific passage or closure record is connected",
                        "operation_status": "UNKNOWN",
                        "osm_access_tag": tags.get("access"),
                        "osm_access_tag_reason": None if tags.get("access") is not None else "OSM way has no access tag",
                        "osm_width_tag": tags.get("width"),
                        "osm_width_tag_reason": None if tags.get("width") is not None else "OSM way has no width tag",
                        "lineage": lineage,
                        "retrieval_query_sha256": query_sha256,
                        "revision_id": "osm-2026-08-29-v1",
                        "running_slope": None,
                        "running_slope_reason": "No field measurement; OSM incline is not converted to a verified running slope",
                        "source_class": "VGI",
                        "source_feature_id": source_feature_id,
                        "source_id": "openstreetmap-overpass-arashiyama-20260829",
                        "source_sha256": source_sha256,
                        "source_tags": tags,
                        "stable_feature_id": stable_id,
                        "step_height_m": None,
                        "step_height_reason": "No field-verified step-height measurement",
                        "to_node": to_id,
                        "topology_status": "CANDIDATE",
                        "tunnel": tunnel,
                        "tunnel_reason": tunnel_reason,
                        "width_m": None,
                        "width_reason": "OSM width tag, if present, is retained separately and not promoted to verified clear width",
                    },
                    "type": "Feature",
                }
            )
    nodes = [
        {
            "geometry": {"coordinates": coordinate, "type": "Point"},
            "id": node_id,
            "properties": {
                "data_class": "REAL",
                "geometry_status": "SOURCE_TRACEABLE_REAL",
                "lineage": [
                    "OpenStreetMap original node ID and coordinate",
                    "fixed-time bounded Overpass response retained as exact bytes",
                    "node retained because it is an endpoint of a retained candidate segment",
                ],
                "node_id": node_id,
                "retrieval_query_sha256": query_sha256,
                "revision_id": "osm-2026-08-29-v1",
                "source_class": "VGI",
                "source_feature_id": f"node/{int(node_id.rsplit('-', 1)[1])}",
                "source_id": "openstreetmap-overpass-arashiyama-20260829",
                "source_sha256": source_sha256,
                "stable_feature_id": node_id,
                "topology_status": "CANDIDATE",
            },
            "type": "Feature",
        }
        for node_id, coordinate in sorted(node_coordinates.items())
    ]
    corridor.sort(key=lambda feature: feature["id"])
    graph_edges.sort(key=lambda feature: feature["properties"]["edge_id"])
    return corridor, nodes, graph_edges


def _manifest_records(corridor: list[dict], artifact_sha: str, source_sha: str, query_sha: str) -> list[dict]:
    common = {
        "accessed_at": "2026-08-30",
        "artifact_id": "arashiyama-osm-corridor-v1",
        "artifact_path": "geography/corridor.real.geojson",
        "artifact_role": "CORRIDOR_GEOMETRY",
        "axis_order": "longitude_latitude",
        "city_id": CITY_ID,
        "data_class": "REAL",
        "geometry_status": "SOURCE_TRACEABLE_REAL",
        "horizontal_unit": "degree",
        "license": "Open Data Commons Open Database License (ODbL) 1.0",
        "license_review_status": "AGENT_REVIEWED_HUMAN_PENDING",
        "license_terms_url": "https://www.openstreetmap.org/copyright",
        "output_crs": "EPSG:4326",
        "processing_crs": "EPSG:4326",
        "redistribution_obligations": [
            "Attribute OpenStreetMap contributors",
            "Provide ODbL notice and database/source availability as applicable",
            "Apply ODbL share-alike obligations to a derived database when applicable",
        ],
        "redistribution_status": "PERMITTED_WITH_OBLIGATIONS",
        "retrieval_method": "BOUNDED_QUERY",
        "retrieval_query_path": f"sources/{OSM_QUERY_NAME}",
        "retrieval_query_sha256": query_sha,
        "revision_id": "osm-2026-08-29-v1",
        "sha256": artifact_sha,
        "snapshot_at": "2026-08-29T00:00:00Z",
        "snapshot_reason": None,
        "source_artifact_path": f"sources/{OSM_RAW_NAME}",
        "source_class": "VGI",
        "source_crs": "EPSG:4326",
        "source_id": "openstreetmap-overpass-arashiyama-20260829",
        "source_reference": None,
        "source_revision": "Overpass historical snapshot requested for 2026-08-29T00:00:00Z",
        "source_sha256": source_sha,
        "source_url": "https://overpass-api.de/api/interpreter",
        "transform_history": [
            "Retain exact fixed-time bounded Overpass JSON response",
            "Select highway ways returned by the retained query",
            "Split only at consecutive original OSM node IDs",
            "Keep segments whose two source nodes are inside the declared bbox",
            "Round source lon/lat to seven decimal places for deterministic GeoJSON",
        ],
        "valid_as_of": "2026-08-29",
        "valid_as_of_reason": None,
        "vertical_datum": None,
        "vertical_datum_reason": "The 2D OSM corridor extract contains no verified elevation coordinate",
    }
    records = []
    for feature in corridor:
        props = feature["properties"]
        records.append(
            {
                **common,
                "lineage": props["lineage"],
                "source_feature_id": props["source_feature_id"],
                "stable_feature_id": props["stable_feature_id"],
            }
        )
    return records


def _topology_qa(nodes: list[dict], edges: list[dict]) -> dict:
    node_ids = [item["properties"]["node_id"] for item in nodes]
    edge_ids = [item["properties"]["edge_id"] for item in edges]
    degrees = Counter()
    for edge in edges:
        degrees[edge["properties"]["from_node"]] += 1
        degrees[edge["properties"]["to_node"]] += 1
    dangling_node_ids = sorted(
        node_id for node_id in node_ids if degrees[node_id] == 1
    )
    return {
        "counts": {
            "dangling_endpoint_nodes": len(dangling_node_ids),
            "duplicate_edge_ids": len(edge_ids) - len(set(edge_ids)),
            "duplicate_node_ids": len(node_ids) - len(set(node_ids)),
            "edges": len(edges),
            "geometric_crossings_promoted_to_nodes": 0,
            "nodes": len(nodes),
            "self_loops": sum(
                edge["properties"]["from_node"] == edge["properties"]["to_node"]
                for edge in edges
            ),
            "zero_length_edges": sum(
                edge["geometry"]["coordinates"][0] == edge["geometry"]["coordinates"][-1]
                for edge in edges
            ),
        },
        "graph_status": "CANDIDATE",
        "issue_register_status": "OPEN",
        "issues": [
            {
                "feature_id": node_id,
                "issue_id": f"arashiyama-topology:dangling:{node_id}",
                "issue_type": "DANGLING_ENDPOINT",
                "owner": "FIELD_QA",
                "qa_code": "UNEXPECTED_DANGLE",
                "reason": "Degree-one candidate node requires corridor-boundary or field-connectivity review",
                "severity": "REVIEW_REQUIRED",
                "status": "OPEN",
            }
            for node_id in dangling_node_ids
        ],
        "method": "Endpoint identity uses retained OSM node IDs; geometric crossings are not promoted",
        "not_computed": {
            "disconnected_verified_destinations": {
                "reason": "No field-verified destination/entrance nodes are connected",
                "status": "NOT_COMPUTED",
            },
            "field_verified_connectivity": {
                "reason": "Candidate topology has not been checked on site",
                "status": "NOT_COMPUTED",
            },
            "geometric_crossing_review": {
                "reason": "No grade-separated/crossing conflation review has been performed beyond retained OSM IDs/tags",
                "status": "NOT_COMPUTED",
            },
        },
    }


def _polygonal_mapping(geometry):
    from shapely.geometry import mapping

    if geometry.geom_type in {"Polygon", "MultiPolygon"}:
        return mapping(geometry)
    polygons = [part for part in getattr(geometry, "geoms", ()) if part.geom_type == "Polygon"]
    if not polygons:
        return None
    from shapely.geometry import MultiPolygon

    return mapping(MultiPolygon(polygons))


def _flood_clip(source_zip: Path) -> tuple[list[dict], list[dict]]:
    import ijson
    from pyproj import Transformer
    from shapely.geometry import box, shape
    from shapely.ops import transform

    transformer = Transformer.from_crs("EPSG:6668", "EPSG:4326", always_xy=True)
    clip_box = box(*BBOX)
    features: list[dict] = []
    quarantine: list[dict] = []
    with zipfile.ZipFile(source_zip) as archive, archive.open(FLOOD_MEMBER) as handle:
        for source_index, source in enumerate(ijson.items(handle, "features.item")):
            try:
                source_geometry = shape(source["geometry"])
            except Exception as error:
                quarantine.append({"reason": f"GEOMETRY_PARSE_ERROR:{type(error).__name__}", "source_feature_index": source_index})
                continue
            if source_geometry.is_empty:
                continue
            minx, miny, maxx, maxy = source_geometry.bounds
            if maxx < BBOX[0] or minx > BBOX[2] or maxy < BBOX[1] or miny > BBOX[3]:
                continue
            if not source_geometry.is_valid:
                quarantine.append({"reason": "INVALID_SOURCE_GEOMETRY", "source_feature_index": source_index})
                continue
            output_geometry = transform(transformer.transform, source_geometry).intersection(clip_box)
            if output_geometry.is_empty:
                continue
            polygonal = _polygonal_mapping(output_geometry)
            if polygonal is None:
                quarantine.append({"reason": "NON_POLYGONAL_CLIP_RESULT", "source_feature_index": source_index})
                continue
            stable_id = f"kyoto-arashiyama:a31b-5235-max:{source_index:08d}"
            depth_rank = source.get("properties", {}).get("A31b_201")
            features.append(
                {
                    "geometry": polygonal,
                    "id": stable_id,
                    "properties": {
                        "connection_status": "NOT_CONNECTED",
                        "data_class": "OFFICIAL_METADATA_ONLY",
                        "depth_rank_code": depth_rank,
                        "geometry_status": "PREPARED_NOT_CONNECTED",
                        "hazard_type": "FLOOD",
                        "inundation_depth_m": None,
                        "inundation_depth_reason": "A31b_201 is retained as an official category code and is not converted to a measured depth",
                        "official_closure": None,
                        "official_closure_reason": "The hazard polygon is not an official road-closure record",
                        "scenario_state": "UNKNOWN",
                        "scenario_state_reason": "Hazard overlap alone must not create a closure or passage state",
                        "output_axis_order": "longitude_latitude",
                        "output_crs": "EPSG:4326",
                        "revision_id": FLOOD_PREVIEW_REVISION,
                        "source_class": "OFFICIAL",
                        "source_axis_order": "x_y_as_stored_in_geojson",
                        "source_crs": "EPSG:6668",
                        "source_feature_id": f"A31b-20-25_10_5235#feature/{source_index}",
                        "source_id": FLOOD_SOURCE_ID,
                        "source_sha256": EXPECTED_FLOOD_SHA256,
                        "stable_feature_id": stable_id,
                        "transform_history": [
                            "Read checksum-bound A31b GeoJSON member from retained ZIP",
                            "Transform EPSG:6668 x/y coordinates to EPSG:4326 longitude/latitude with always_xy",
                            "Intersect polygonal geometry with the declared Arashiyama bbox",
                        ],
                    },
                    "type": "Feature",
                }
            )
    features.sort(key=lambda feature: feature["id"])
    return features, quarantine


def _overlap_rows(edges: list[dict], hazards: list[dict]) -> list[dict[str, object]]:
    from shapely.geometry import shape

    hazard_shapes = [(shape(feature["geometry"]), feature) for feature in hazards]
    rows = []
    for edge in edges:
        line = shape(edge["geometry"])
        overlapping = [feature for geometry, feature in hazard_shapes if line.intersects(geometry)]
        ranks = sorted({str(feature["properties"]["depth_rank_code"]) for feature in overlapping})
        rows.append(
            {
                "connection_status": "NOT_CONNECTED",
                "data_class": "MODEL_DERIVED",
                "depth_rank_codes": "|".join(ranks),
                "edge_id": edge["properties"]["edge_id"],
                "hazard_overlap_status": "OVERLAPS" if overlapping else "NO_OVERLAP",
                "hazard_capability_status": "NOT_CONNECTED",
                "inundation_depth_m": "",
                "inundation_depth_reason": "A31b category codes are not converted to measured depth",
                "official_closure": "",
                "official_closure_reason": "The hazard polygon is not an official road-closure record",
                "scenario_state": "UNKNOWN",
                "source_class": "MODEL",
            }
        )
    return sorted(rows, key=lambda row: str(row["edge_id"]))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    return _sha256(path)


def _rebind_retained_preview(pack: Path, edges: list[dict]) -> None:
    """Rebind the quarantined preview to rebuilt edge IDs without connecting it."""
    flood_path = pack / "hazards" / "flood_a31b_2025.prepared.geojson"
    if not flood_path.is_file():
        raise RuntimeError("RETAINED_PREVIEW_REBIND_BLOCKED: prepared flood preview is unavailable")
    retained_sha = _sha256(flood_path)
    if retained_sha not in {
        EXPECTED_LEGACY_FLOOD_PREVIEW_SHA256,
        EXPECTED_CANONICAL_FLOOD_PREVIEW_SHA256,
    }:
        raise RuntimeError("RETAINED_PREVIEW_REBIND_BLOCKED: retained preview checksum mismatch")
    payload = json.loads(flood_path.read_text(encoding="utf-8"))
    hazards = payload.get("features", [])
    if not hazards:
        raise RuntimeError("RETAINED_PREVIEW_REBIND_BLOCKED: prepared flood preview is empty")
    for feature in hazards:
        properties = feature["properties"]
        properties.update(
            {
                "output_axis_order": "longitude_latitude",
                "output_crs": "EPSG:4326",
                "revision_id": FLOOD_PREVIEW_REVISION,
                "source_axis_order": "x_y_as_stored_in_geojson",
                "source_crs": "EPSG:6668",
                "source_id": FLOOD_SOURCE_ID,
                "source_sha256": EXPECTED_FLOOD_SHA256,
                "transform_history": [
                    "Read checksum-bound A31b GeoJSON member from retained ZIP",
                    "Transform EPSG:6668 x/y coordinates to EPSG:4326 longitude/latitude with always_xy",
                    "Intersect polygonal geometry with the declared Arashiyama bbox",
                ],
            }
        )
    hazards.sort(key=lambda feature: feature["id"])
    flood_sha = _write_json(flood_path, {"features": hazards, "type": "FeatureCollection"})
    overlap_path = pack / "hazards" / "edge_hazard_overlap.real.csv"
    with overlap_path.open(encoding="utf-8", newline="") as handle:
        retained_rows = list(csv.DictReader(handle))
    edge_by_source_feature = {
        edge["properties"]["source_feature_id"]: edge["properties"]["edge_id"]
        for edge in edges
    }
    current_edge_ids = set(edge_by_source_feature.values())
    rebound_rows = []
    for row in retained_rows:
        previous_edge_id = row["edge_id"]
        if previous_edge_id in current_edge_ids:
            rebound_edge_id = previous_edge_id
        else:
            prefix = "kyoto-arashiyama:osm-way-"
            if not previous_edge_id.startswith(prefix) or ":segment-" not in previous_edge_id:
                raise RuntimeError("RETAINED_PREVIEW_REBIND_BLOCKED: unrecognized legacy edge ID")
            way_text, segment_text = previous_edge_id[len(prefix) :].split(":segment-", 1)
            source_feature_id = f"way/{int(way_text)}#segment/{int(segment_text)}"
            if source_feature_id not in edge_by_source_feature:
                raise RuntimeError("RETAINED_PREVIEW_REBIND_BLOCKED: legacy edge has no rebuilt counterpart")
            rebound_edge_id = edge_by_source_feature[source_feature_id]
        row["edge_id"] = rebound_edge_id
        row["official_closure"] = ""
        row["official_closure_reason"] = (
            "The hazard polygon is not an official road-closure record"
        )
        rebound_rows.append(row)
    if len(rebound_rows) != len(edges) or {row["edge_id"] for row in rebound_rows} != current_edge_ids:
        raise RuntimeError("RETAINED_PREVIEW_REBIND_BLOCKED: edge coverage is not exact")
    rebound_rows.sort(key=lambda row: row["edge_id"])
    overlap_sha = _write_csv(overlap_path, rebound_rows)
    graph_path = pack / "graph" / "walk_edges.real.geojson"
    sidecar_path = pack / "hazards" / "edge_hazard_overlap.real.manifest.json"
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    sidecar["inputs"] = sorted(
        [
            {"path": "graph/walk_edges.real.geojson", "sha256": _sha256(graph_path)},
            {"path": "hazards/flood_a31b_2025.prepared.geojson", "sha256": flood_sha},
        ],
        key=lambda item: item["path"],
    )
    sidecar["output"] = {
        "path": "hazards/edge_hazard_overlap.real.csv",
        "sha256": overlap_sha,
    }
    sidecar["revision_id"] = OVERLAP_PREVIEW_REVISION
    _write_json(sidecar_path, sidecar)
    preparation_path = pack / "sources" / "flood_a31b_2025.preparation.json"
    preparation = json.loads(preparation_path.read_text(encoding="utf-8"))
    preparation["artifact_sha256"] = flood_sha
    preparation["revision_id"] = FLOOD_PREVIEW_REVISION
    preparation["source_id"] = FLOOD_SOURCE_ID
    _write_json(preparation_path, preparation)


def _prepare_optional_flood_preview(pack: Path, raw_root: Path, edges: list[dict]) -> None:
    """Prepare an explicitly unconnected preview with optional external GIS tools."""
    flood_external = raw_root / FLOOD_ZIP_NAME
    if not flood_external.is_file() or _sha256(flood_external) != EXPECTED_FLOOD_SHA256:
        raise RuntimeError(
            "OPTIONAL_PREPARATION_BLOCKED: checksum-bound A31b archive is unavailable"
        )
    try:
        hazards, quarantine = _flood_clip(flood_external)
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "OPTIONAL_PREPARATION_BLOCKED: ijson, shapely, and pyproj are external preparation tools"
        ) from error
    if not hazards:
        raise RuntimeError("bounded official flood preparation produced no polygon")
    flood_artifact = pack / "hazards" / "flood_a31b_2025.prepared.geojson"
    flood_sha = _write_json(flood_artifact, {"features": hazards, "type": "FeatureCollection"})
    stale_connected_name = pack / "hazards" / "flood_a31b_2025.official.geojson"
    stale_connected_name.unlink(missing_ok=True)
    _write_json(pack / "hazards" / "flood_a31b_2025.quarantine.json", {"records": quarantine})
    overlap_path = pack / "hazards" / "edge_hazard_overlap.real.csv"
    overlap_sha = _write_csv(overlap_path, _overlap_rows(edges, hazards))
    graph_path = pack / "graph" / "walk_edges.real.geojson"
    _write_json(
        pack / "hazards" / "edge_hazard_overlap.real.manifest.json",
        {
            "connection_status": "NOT_CONNECTED",
            "data_class": "MODEL_DERIVED",
            "inputs": sorted(
                [
                    {"path": "graph/walk_edges.real.geojson", "sha256": _sha256(graph_path)},
                    {"path": "hazards/flood_a31b_2025.prepared.geojson", "sha256": flood_sha},
                ],
                key=lambda item: item["path"],
            ),
            "lineage": [
                "checksum-bound candidate graph geometry",
                "checksum-bound optional A31b prepared preview",
                "Shapely intersects predicate in EPSG:4326; output is model-derived and unconnected",
                "edge rows sorted by edge_id before hashing",
            ],
            "output": {"path": "hazards/edge_hazard_overlap.real.csv", "sha256": overlap_sha},
            "revision_id": OVERLAP_PREVIEW_REVISION,
            "source_class": "MODEL",
        },
    )
    _write_json(
        pack / "sources" / "flood_a31b_2025.preparation.json",
        {
            "accessed_at": "2026-08-30",
            "artifact_path": "hazards/flood_a31b_2025.prepared.geojson",
            "artifact_sha256": flood_sha,
            "catalog_url": "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-A31b-2025.html",
            "data_class": "OFFICIAL_METADATA_ONLY",
            "dataset": "National Land Numerical Information A31b Flood Inundation Assumption Area 2025, maximum scale",
            "geometry_status": "PREPARED_NOT_CONNECTED",
            "license": "Creative Commons Attribution 4.0 International",
            "license_review_status": "AGENT_REVIEWED_HUMAN_PENDING",
            "license_terms_url": "https://creativecommons.org/licenses/by/4.0/legalcode",
            "lineage": [
                "Official A31b 2025 maximum-scale member retained in a checksum-bound external archive",
                "invalid overlapping source geometry quarantined without repair",
                "bounded clip prepared for review but not issued as a shared-v2 capability",
            ],
            "output_crs": "EPSG:4326",
            "processing_crs": "EPSG:4326",
            "raw_retention": "EXTERNAL_ONLY_FULL_ARCHIVE",
            "redistribution_obligations": ["Attribute the Ministry of Land, Infrastructure, Transport and Tourism source"],
            "redistribution_status": "PERMITTED_WITH_OBLIGATIONS",
            "revision_id": FLOOD_PREVIEW_REVISION,
            "runtime_dependencies": ["ijson", "pyproj", "shapely"],
            "runtime_status": "OPTIONAL_PREPARATION",
            "shared_v2_connection_reason": "The 55 MB full official archive is deliberately not copied into Git; shared v2 requires contained exact source bytes",
            "shared_v2_connection_status": "NOT_CONNECTED",
            "source_archive_member": FLOOD_MEMBER,
            "source_class": "OFFICIAL",
            "source_crs": "EPSG:6668",
            "source_feature_id": "A31b-20-25_10_5235#bounded-preparation",
            "source_id": FLOOD_SOURCE_ID,
            "source_sha256": EXPECTED_FLOOD_SHA256,
            "source_url": "https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip",
            "transform_history": [
                "Stream the maximum-scale GeoJSON member from the checksum-bound archive",
                "Quarantine invalid overlapping source geometry without repair",
                "Transform EPSG:6668 to EPSG:4326 with always_xy axis order",
                "Intersect polygonal geometry with the declared Arashiyama bbox",
                "Retain A31b_201 only as a categorical depth-rank code",
            ],
            "valid_as_of": None,
            "valid_as_of_reason": "The catalogue identifies the 2025 edition but does not state one exact validity day",
            "vertical_datum": None,
            "vertical_datum_reason": "The prepared 2D polygon layer contains no verified vertical coordinate",
        },
    )


def build(
    pack: Path,
    raw_root: Path,
    *,
    optional_official_preview: bool = False,
    rebind_retained_preview: bool = False,
) -> None:
    osm_external = raw_root / OSM_RAW_NAME
    if _sha256(osm_external) != EXPECTED_OSM_SHA256:
        raise RuntimeError("bounded OSM source checksum mismatch")
    osm_internal = pack / "sources" / OSM_RAW_NAME
    shutil.copyfile(osm_external, osm_internal)
    raw = json.loads(osm_internal.read_text(encoding="utf-8"))
    query_sha = _sha256(pack / "sources" / OSM_QUERY_NAME)
    if query_sha != EXPECTED_QUERY_SHA256:
        raise RuntimeError("bounded OSM query checksum mismatch")
    corridor, nodes, edges = _osm_segments(
        raw, source_sha256=EXPECTED_OSM_SHA256, query_sha256=query_sha
    )
    if not corridor or not edges or not nodes:
        raise RuntimeError("bounded OSM extraction produced an empty graph")
    corridor_sha = _write_json(
        pack / "geography" / "corridor.real.geojson",
        {"features": corridor, "type": "FeatureCollection"},
    )
    nodes_sha = _write_json(pack / "graph" / "walk_nodes.real.geojson", {"features": nodes, "type": "FeatureCollection"})
    edges_sha = _write_json(pack / "graph" / "walk_edges.real.geojson", {"features": edges, "type": "FeatureCollection"})
    qa_sha = _write_json(pack / "graph" / "topology_qa.real.json", _topology_qa(nodes, edges))
    _write_json(
        pack / "graph" / "graph_provenance.real.json",
        {
            "axis_order": "longitude_latitude",
            "capability_status": "SOURCE_TRACEABLE_CANDIDATE",
            "horizontal_unit": "degree",
            "lineage": [
                "fixed-time bounded Overpass response retained as exact bytes",
                "candidate segments split only at consecutive original OSM node IDs",
                "graph output hashes bind the delivered candidate nodes, edges, and QA",
            ],
            "outputs": [
                {"path": "graph/topology_qa.real.json", "sha256": qa_sha},
                {"path": "graph/walk_edges.real.geojson", "sha256": edges_sha},
                {"path": "graph/walk_nodes.real.geojson", "sha256": nodes_sha},
            ],
            "output_crs": "EPSG:4326",
            "processing_crs": "EPSG:4326",
            "retrieval_query_path": f"sources/{OSM_QUERY_NAME}",
            "retrieval_query_sha256": query_sha,
            "revision_id": "osm-2026-08-29-v1",
            "source_artifact_path": f"sources/{OSM_RAW_NAME}",
            "source_crs": "EPSG:4326",
            "source_id": "openstreetmap-overpass-arashiyama-20260829",
            "source_sha256": EXPECTED_OSM_SHA256,
            "topology_status": "CANDIDATE",
            "transform_history": [
                "Retain exact fixed-time bounded Overpass JSON response",
                "Select highway ways returned by the retained query",
                "Split only at consecutive original OSM node IDs",
                "Identify stable physical segments by OSM way ID plus unordered endpoint node pair",
                "Keep segments whose two source nodes are inside the declared bbox",
                "Round source longitude/latitude to seven decimal places",
            ],
        },
    )
    records = _manifest_records(corridor, corridor_sha, EXPECTED_OSM_SHA256, query_sha)
    manifest_path = pack / "sources" / "realdata_manifest.json"
    manifest_sha = _write_json(manifest_path, {"artifacts": records, "city_id": CITY_ID, "schema_version": "2.0.0"})
    _write_json(
        pack / "sources" / "realdata_fileset.json",
        {
            "capability_id": "arashiyama-osm-corridor-v1",
            "connection_status": "CONNECTED",
            "exact_fileset": [
                {"path": "geography/corridor.real.geojson", "role": "NORMALIZED_GEOMETRY", "sha256": corridor_sha},
                {"path": f"sources/{OSM_QUERY_NAME}", "role": "RETRIEVAL_QUERY", "sha256": query_sha},
                {"path": f"sources/{OSM_RAW_NAME}", "role": "EXACT_SOURCE_RESPONSE", "sha256": EXPECTED_OSM_SHA256},
                {"path": "sources/realdata_manifest.json", "role": "V2_LINEAGE_MANIFEST", "sha256": manifest_sha},
            ],
            "source_class": "VGI",
        },
    )

    _write_json(
        pack / "sources" / "optional_preparation_status.json",
        {
            "connection_status": "NOT_CONNECTED",
            "optional_command_flag": "--optional-official-preview",
            "reason": "Official flood preview preparation requires external ijson, shapely, and pyproj tools that are not declared project runtime dependencies",
            "runtime_dependencies": ["ijson", "pyproj", "shapely"],
            "runtime_dependencies_declared_by_project": False,
            "status": "OPTIONAL_PREPARATION",
        },
    )
    if optional_official_preview:
        _prepare_optional_flood_preview(pack, raw_root, edges)
    elif rebind_retained_preview:
        _rebind_retained_preview(pack, edges)
    _write_json(
        pack / "sources" / "plateau_kyoto_2025.metadata.json",
        {
            "accessed_at": "2026-08-30",
            "arashiyama_geometry_coverage_verified": False,
            "citygml_or_tiles_retained": False,
            "data_class": "OFFICIAL_METADATA_ONLY",
            "dataset_page": "https://www.geospatial.jp/ckan/dataset/plateau-26100-kyoto-shi-2025",
            "dataset_title": "PLATEAU Kyoto City 2025",
            "geometry_connection_status": "NOT_CONNECTED",
            "license": None,
            "license_reason": "Dataset terms were not retained and reviewed within this bounded lane",
            "license_review_status": "AGENT_REVIEWED_HUMAN_PENDING",
            "lineage": ["Official catalogue metadata capture only; no CityGML or 3D Tiles payload retained"],
            "metadata_connection_status": "CONNECTED",
            "official_city_page": "https://www.city.kyoto.lg.jp/tokei/page/0000312935.html",
            "output_crs": None,
            "output_crs_reason": "No geometry payload is connected",
            "processing_crs": None,
            "processing_crs_reason": "No geometry transformation was performed",
            "reason": "The multi-gigabyte CityGML/tiles payload was not downloaded; Arashiyama tile coverage was not independently verified",
            "redistribution_status": "UNKNOWN",
            "redistribution_status_reason": "Human review of the dataset-specific payload terms remains pending",
            "revision_id": "plateau-kyoto-2025-metadata-v1",
            "source_class": "OFFICIAL",
            "source_crs": None,
            "source_crs_reason": "No CityGML or tiles payload was retained",
            "source_feature_id": "plateau-26100-kyoto-shi-2025",
            "source_id": "plateau-26100-kyoto-shi-2025",
            "source_sha256": None,
            "source_sha256_reason": "No exact catalogue response or geometry payload was retained",
            "source_url": "https://www.geospatial.jp/ckan/dataset/plateau-26100-kyoto-shi-2025",
            "transform_history": ["METADATA_CAPTURE_ONLY"],
            "valid_as_of": None,
            "valid_as_of_reason": "The catalogue edition is 2025 but no exact validity day was retained",
            "vertical_datum": None,
            "vertical_datum_reason": "No geometry payload is connected",
        },
    )
    _write_json(
        pack / "sources" / "kyoto_inner_flood.metadata.json",
        {
            "accessed_at": "2026-08-30",
            "data_class": "OFFICIAL_METADATA_ONLY",
            "geometry_connection_status": "NOT_CONNECTED",
            "license": None,
            "license_reason": "The official page was identified but dataset-specific redistribution terms for machine geometry were not available",
            "lineage": ["Official Kyoto City page metadata only; no machine-readable inner-flood geometry was found or retained"],
            "output_crs": None,
            "output_crs_reason": "No geometry payload is connected",
            "processing_crs": None,
            "processing_crs_reason": "No geometry transformation was performed",
            "redistribution_status": "UNKNOWN",
            "redistribution_status_reason": "No redistributable machine-readable payload was identified",
            "revision_id": "kyoto-inner-flood-metadata-2026-06-01-v1",
            "source_class": "OFFICIAL",
            "source_crs": None,
            "source_crs_reason": "No machine-readable geometry was retained",
            "source_feature_id": "kyoto-city-inner-flood-page-0000349757",
            "source_id": "kyoto-city-inner-flood-page-0000349757",
            "source_sha256": None,
            "source_sha256_reason": "No exact response bytes were retained",
            "source_url": "https://www.city.kyoto.lg.jp/suido/page/0000349757.html",
            "transform_history": ["METADATA_CAPTURE_ONLY"],
            "valid_as_of": "2026-06-01",
            "valid_as_of_reason": None,
            "vertical_datum": None,
            "vertical_datum_reason": "No geometry payload is connected",
        },
    )
    _write_json(
        pack / "sources" / "retention_receipt.json",
        {
            "external_location": "ablepath-raw/kyoto_arashiyama",
            "external_sources": {
                FLOOD_ZIP_NAME: {
                    "repository_copy": None,
                    "repository_copy_reason": "Full 55 MB official archive is retained outside Git",
                    "retention_verified_this_run": optional_official_preview,
                    "sha256": EXPECTED_FLOOD_SHA256,
                },
                OSM_RAW_NAME: {"repository_copy": f"sources/{OSM_RAW_NAME}", "sha256": EXPECTED_OSM_SHA256},
            },
            "repository_includes_bounded_osm_raw": True,
            "repository_omits_full_a31b_archive": True,
        },
    )
    preview_prepared = all(
        (pack / relative).is_file()
        for relative in (
            "hazards/edge_hazard_overlap.real.manifest.json",
            "hazards/flood_a31b_2025.prepared.geojson",
            "sources/flood_a31b_2025.preparation.json",
        )
    )
    _write_json(
        pack / "realdata_status.json",
        {
            "ADMIN_VALIDATED": False,
            "CANDIDATE_GRAPH_CONNECTED": True,
            "CANDIDATE_GRAPH_CONNECTED_SCOPE": "CITYPACK_ARTIFACT_FILES_ONLY",
            "CANDIDATE_GRAPH_CONNECTED_TO_MODEL": False,
            "KPI_CONNECTED": False,
            "M6_CONNECTED": False,
            "M7_CONNECTED": False,
            "MODEL_CONNECTED": False,
            "OFFICIAL_HAZARD_GEOMETRY_CONNECTED": False,
            "OFFICIAL_HAZARD_GEOMETRY_CONNECTION_REASON": "The checksum-bound official source archive is outside the shared-v2 trust root",
            "OFFICIAL_HAZARD_DATA_CLASS": "OFFICIAL_METADATA_ONLY",
            "OFFICIAL_HAZARD_GEOMETRY_PREPARED": preview_prepared,
            "PLATEAU_3D_CONNECTED": False,
            "PLATEAU_METADATA_CONNECTED": True,
            "REAL_GEOMETRY_CONNECTED": True,
            "REAL_GEOMETRY_CONNECTED_SCOPE": "CITYPACK_VALIDATED_ARTIFACT_CAPABILITY",
            "REAL_GEOMETRY_CONNECTED_TO_VIEWER": False,
            "kpis": {
                "accessible_route_share": {"reason": "Width, slope, steps, surface, and entrance evidence are not field verified", "value": None},
                "additional_allocatable_people_upper_bound": {"reason": "M6/profile allocation is not computed", "value": None},
                "m7_residual_width_route_share": {"reason": "No candidate edge has the complete real M7 input set", "value": None},
                "officially_open_route_share": {"reason": "No time-specific official passage/closure records are connected", "value": None},
            },
            "notes": [
                "REAL means source-traceable geometry, not safe, accessible, or administratively validated",
                "The A31b clip is prepared exposure geometry only; overlap never creates closure",
                "The legacy synthetic demo remains separate and unchanged",
            ],
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument(
        "--optional-official-preview",
        action="store_true",
        help="Run unconnected A31b preview preparation with external ijson/shapely/pyproj tooling",
    )
    parser.add_argument(
        "--rebind-retained-preview",
        action="store_true",
        help="Rebind the already quarantined preview to rebuilt candidate edge IDs without connecting it",
    )
    arguments = parser.parse_args()
    build(
        arguments.pack.resolve(),
        arguments.raw_root.resolve(),
        optional_official_preview=arguments.optional_official_preview,
        rebind_retained_preview=arguments.rebind_retained_preview,
    )


if __name__ == "__main__":
    main()
