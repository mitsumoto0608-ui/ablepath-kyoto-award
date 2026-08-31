"""Build deterministic Kiyomizu v2 artifacts from retained source bytes.

External files are untrusted data.  This script reads only explicitly supplied
paths and never follows instructions contained in source payloads.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable


CITY_ID = "kyoto_kiyomizu"
ARTIFACT_ID = "kiyomizu_osm_named_corridor_20260830"
SNAPSHOT_AT = "2026-08-30T00:00:00Z"
ACCESSED_AT = "2026-08-30"
CORRIDOR_BBOX = (135.7775, 34.9948, 135.7850, 35.0046)
CORRIDOR_NAMES = {
    "東大路通",
    "ねねの小径",
    "一年坂",
    "二年坂",
    "三年坂",
    "清水坂",
    "八坂通",
}


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


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


def _pretty_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2)
        + "\n"
    ).encode("utf-8")


def _pretty_hazard_metadata_bytes(value: object) -> bytes:
    """Preserve the reviewed hazard-metadata key order and final LF."""

    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=False, indent=2)
        + "\n"
    ).encode("utf-8")


def _build_hazard_preview_metadata(
    *,
    feature_count: int,
    source_zip_sha256: str,
    component_hashes: dict[str, dict[str, str]],
    preview_sha256: str,
) -> dict[str, Any]:
    """Return the deterministic, non-connectable official-preview contract."""

    normalized_component_hashes = {
        layer: {
            extension: component_hashes[layer][extension]
            for extension in sorted(component_hashes[layer])
        }
        for layer in sorted(component_hashes)
    }
    return {
        "accessed_at": ACCESSED_AT,
        "analysis_eligible": False,
        "axis_order": "longitude_latitude",
        "capability_status": "NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT",
        "city_id": CITY_ID,
        "connection_reason": "The citywide official ZIP is intentionally outside Git; v2 cannot bind contained raw bytes",
        "connection_status": "NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT",
        "data_class": "REAL",
        "data_class_scope": "SOURCE_GEOMETRY_NATURE_ONLY_NOT_CAPABILITY_ELIGIBILITY",
        "data_class_semantics": "REAL describes source geometry nature only; it does not grant validated capability eligibility",
        "edge_state_effect": "NONE",
        "external_raw_location": "REPOSITORY_EXTERNAL_PATH_NOT_VERSIONED",
        "feature_count": feature_count,
        "geometry_status": "SOURCE_TRACEABLE_REAL_PREVIEW",
        "horizontal_unit": "degree",
        "license": "Kyoto City Disaster Prevention Information Map GIS reuse terms",
        "license_terms_url": "https://www.bousaimap.city.kyoto.lg.jp/help/attention.html",
        "model_eligible": False,
        "official_closure": None,
        "official_closure_reason": "Zone overlap is not an operation record",
        "output_crs": "EPSG:4326",
        "preview_sha256": preview_sha256,
        "processing_crs": "EPSG:6668",
        "quarantine_scope": "ALL_FEATURES_IN_COMPANION_PREVIEW",
        "redistribution_status": "PERMITTED_WITH_ATTRIBUTION_AGENT_REVIEWED_HUMAN_PENDING",
        "required_attribution": "出典：京都市防災情報マップ",
        "schema_version": "2.0.0-preview",
        "selection_bbox_epsg4326": list(CORRIDOR_BBOX),
        "source_component_sha256": normalized_component_hashes,
        "source_class": "OFFICIAL",
        "source_crs": "EPSG:6668",
        "source_id": "kyoto_city_hazard_map_landslide_20260830",
        "source_url": "https://www.bousaimap.city.kyoto.lg.jp/GisDownload",
        "source_zip_sha256": source_zip_sha256.lower(),
        "transform_history": [
            "Selected source polygons whose source bbox intersects the fixed corridor bbox",
            "Transformed JGD2011 EPSG:6668 to EPSG:4326 using PROJ always_xy",
            "Did not clip polygon boundaries and did not infer operational closure",
        ],
        "trust_status": "HASH_REFERENCED_RAW_NOT_IN_TRUST_ROOT",
        "vertical_datum": None,
        "vertical_datum_reason": "2D polygon dataset",
        "viewer_eligible": False,
    }


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _osm_bool(tags: dict[str, str], key: str) -> tuple[bool | str, str | None]:
    value = tags.get(key)
    if value == "yes":
        return True, None
    if value == "no":
        return False, None
    if value is None:
        return "UNKNOWN", f"OSM_{key.upper()}_TAG_MISSING_AT_SNAPSHOT"
    return "UNKNOWN", f"OSM_{key.upper()}_TAG_NOT_BOOLEAN:{value}"


def _osm_number(tags: dict[str, str], key: str) -> tuple[float | None, str | None]:
    value = tags.get(key)
    if value is None:
        return None, f"OSM_{key.upper()}_TAG_MISSING_AT_SNAPSHOT"
    try:
        number = float(value)
    except ValueError:
        return None, f"OSM_{key.upper()}_TAG_NOT_SINGLE_NUMERIC:{value}"
    if not math.isfinite(number):
        return None, f"OSM_{key.upper()}_TAG_NONFINITE"
    return number, None


def _lineage(way_id: int) -> list[str]:
    return [
        f"OpenStreetMap way {way_id}",
        f"Overpass historical snapshot {SNAPSHOT_AT}",
        "Server-side exact bbox/name filter; no nearest-neighbour or planar-crossing join",
    ]


def _corridor_properties(way: dict[str, Any]) -> dict[str, Any]:
    way_id = int(way["id"])
    tags = dict(way.get("tags", {}))
    bridge, bridge_reason = _osm_bool(tags, "bridge")
    tunnel, tunnel_reason = _osm_bool(tags, "tunnel")
    layer, layer_reason = _osm_number(tags, "layer")
    level, level_reason = _osm_number(tags, "level")
    stable_id = f"KK-OSM-W{way_id}"
    return {
        "city_id": CITY_ID,
        "artifact_id": ARTIFACT_ID,
        "source_id": "openstreetmap_kiyomizu_named_corridor_20260830",
        "source_class": "VGI",
        "data_class": "REAL",
        "source_feature_id": f"osm-way-{way_id}",
        "stable_feature_id": stable_id,
        "revision_id": f"osm-snapshot-{SNAPSHOT_AT}",
        "lineage": _lineage(way_id),
        "geometry_status": "SOURCE_TRACEABLE_REAL",
        "bridge": bridge,
        "bridge_reason": bridge_reason,
        "tunnel": tunnel,
        "tunnel_reason": tunnel_reason,
        "layer": layer,
        "layer_reason": layer_reason,
        "level": level,
        "level_reason": level_reason,
    }


def _manifest_record(
    properties: dict[str, Any],
    *,
    artifact_sha256: str,
    source_sha256: str,
    query_sha256: str,
) -> dict[str, Any]:
    return {
        "city_id": CITY_ID,
        "artifact_id": ARTIFACT_ID,
        "artifact_path": "geography/real/corridor.osm.geojson",
        "artifact_role": "CORRIDOR_GEOMETRY",
        "source_id": properties["source_id"],
        "source_url": "https://www.openstreetmap.org/",
        "source_reference": None,
        "source_class": "VGI",
        "data_class": "REAL",
        "accessed_at": ACCESSED_AT,
        "valid_as_of": "2026-08-30",
        "valid_as_of_reason": None,
        "license": "Open Data Commons Open Database License (ODbL) 1.0",
        "license_terms_url": "https://opendatacommons.org/licenses/odbl/1-0/",
        "license_review_status": "AGENT_REVIEWED_HUMAN_PENDING",
        "redistribution_status": "PERMITTED_WITH_OBLIGATIONS",
        "redistribution_obligations": [
            "Attribute OpenStreetMap and its contributors",
            "Keep the ODbL notice and disclose derivative database terms where applicable",
        ],
        "sha256": artifact_sha256,
        "source_artifact_path": "sources/retained/osm_corridor_20260830.raw.json",
        "source_sha256": source_sha256,
        "retrieval_method": "BOUNDED_QUERY",
        "retrieval_query_path": "sources/queries/osm_corridor_20260830.overpassql",
        "retrieval_query_sha256": query_sha256,
        "snapshot_at": SNAPSHOT_AT,
        "snapshot_reason": None,
        "source_revision": f"OpenStreetMap historical snapshot {SNAPSHOT_AT}",
        "source_crs": "EPSG:4326",
        "processing_crs": "EPSG:4326",
        "output_crs": "EPSG:4326",
        "axis_order": "longitude_latitude",
        "horizontal_unit": "degree",
        "vertical_datum": None,
        "vertical_datum_reason": "OSM 2D way response supplies no vertical datum",
        "transform_history": [
            "Selected server-side by exact Overpass bbox/name/date query",
            "Copied OSM way-node longitude/latitude without coordinate transformation",
            "Canonicalized FeatureCollection by stable_feature_id",
        ],
        "source_feature_id": properties["source_feature_id"],
        "stable_feature_id": properties["stable_feature_id"],
        "revision_id": properties["revision_id"],
        "lineage": properties["lineage"],
        "geometry_status": "SOURCE_TRACEABLE_REAL",
    }


def _segment_intersection_candidates(edges: list[dict[str, Any]]) -> list[dict[str, str]]:
    def orientation(a: list[float], b: list[float], c: list[float]) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def proper_intersection(a: list[float], b: list[float], c: list[float], d: list[float]) -> bool:
        o1, o2 = orientation(a, b, c), orientation(a, b, d)
        o3, o4 = orientation(c, d, a), orientation(c, d, b)
        return (o1 > 0 > o2 or o2 > 0 > o1) and (o3 > 0 > o4 or o4 > 0 > o3)

    candidates: set[tuple[str, str]] = set()
    for index, first in enumerate(edges):
        first_props = first["properties"]
        first_nodes = set(first_props["source_node_ids"])
        first_coords = first["geometry"]["coordinates"]
        for second in edges[index + 1 :]:
            second_props = second["properties"]
            if first_props["source_way_id"] == second_props["source_way_id"]:
                continue
            if first_nodes.intersection(second_props["source_node_ids"]):
                continue
            second_coords = second["geometry"]["coordinates"]
            if any(
                proper_intersection(a, b, c, d)
                for a, b in zip(first_coords, first_coords[1:])
                for c, d in zip(second_coords, second_coords[1:])
            ):
                candidates.add(tuple(sorted((first["id"], second["id"]))))
    return [
        {"edge_a": first, "edge_b": second, "action": "REVIEW_NO_NODE_CREATED"}
        for first, second in sorted(candidates)
    ]


def _components(edges: list[dict[str, Any]]) -> list[list[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for feature in edges:
        props = feature["properties"]
        left, right = props["from_node"], props["to_node"]
        adjacency[left].add(right)
        adjacency[right].add(left)
    remaining = set(adjacency)
    result: list[list[str]] = []
    while remaining:
        seed = min(remaining)
        queue = deque([seed])
        component: set[str] = set()
        while queue:
            current = queue.popleft()
            if current in component:
                continue
            component.add(current)
            queue.extend(sorted(adjacency[current] - component))
        remaining -= component
        result.append(sorted(component))
    return sorted(result, key=lambda item: (item[0], len(item)))


def build_osm(pack: Path) -> None:
    raw_path = pack / "sources" / "retained" / "osm_corridor_20260830.raw.json"
    query_path = pack / "sources" / "queries" / "osm_corridor_20260830.overpassql"
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    node_by_id = {
        int(item["id"]): item for item in raw["elements"] if item.get("type") == "node"
    }
    ways = sorted(
        (item for item in raw["elements"] if item.get("type") == "way"),
        key=lambda item: int(item["id"]),
    )
    if len(ways) != 17 or {way.get("tags", {}).get("name") for way in ways} != CORRIDOR_NAMES:
        raise ValueError("retained OSM response does not match the fixed named-corridor contract")
    referenced = {int(node_id) for way in ways for node_id in way["nodes"]}
    if referenced != set(node_by_id):
        raise ValueError("retained OSM response has missing or unreferenced nodes")

    corridor_features: list[dict[str, Any]] = []
    for way in ways:
        properties = _corridor_properties(way)
        coordinates = [
            [float(node_by_id[int(node_id)]["lon"]), float(node_by_id[int(node_id)]["lat"])]
            for node_id in way["nodes"]
        ]
        corridor_features.append(
            {
                "type": "Feature",
                "id": properties["stable_feature_id"],
                "geometry": {"type": "LineString", "coordinates": coordinates},
                "properties": properties,
            }
        )
    corridor_features.sort(key=lambda feature: feature["id"])
    corridor_document = {"type": "FeatureCollection", "features": corridor_features}
    corridor_bytes = _canonical_bytes(corridor_document)
    corridor_sha = _sha256_bytes(corridor_bytes)
    _write(pack / "geography" / "real" / "corridor.osm.geojson", corridor_bytes)

    records = [
        _manifest_record(
            feature["properties"],
            artifact_sha256=corridor_sha,
            source_sha256=_sha256_file(raw_path),
            query_sha256=_sha256_file(query_path),
        )
        for feature in corridor_features
    ]
    manifest = {"schema_version": "2.0.0", "city_id": CITY_ID, "artifacts": records}
    _write(pack / "realdata" / "artifact_manifest.v2.json", _pretty_bytes(manifest))

    membership = Counter(int(node_id) for way in ways for node_id in way["nodes"])
    graph_edges: list[dict[str, Any]] = []
    graph_node_source_ids: set[int] = set()
    for way in ways:
        way_id = int(way["id"])
        source_nodes = [int(node_id) for node_id in way["nodes"]]
        cuts = [
            index
            for index, node_id in enumerate(source_nodes)
            if index in {0, len(source_nodes) - 1} or membership[node_id] > 1
        ]
        for segment_index, (start, end) in enumerate(zip(cuts, cuts[1:]), start=1):
            if end <= start:
                continue
            segment_nodes = source_nodes[start : end + 1]
            coordinates = [
                [float(node_by_id[node_id]["lon"]), float(node_by_id[node_id]["lat"])]
                for node_id in segment_nodes
            ]
            stable_id = f"KK-OSM-W{way_id}-S{segment_index:02d}"
            tags = dict(way.get("tags", {}))
            bridge, bridge_reason = _osm_bool(tags, "bridge")
            tunnel, tunnel_reason = _osm_bool(tags, "tunnel")
            layer, layer_reason = _osm_number(tags, "layer")
            level, level_reason = _osm_number(tags, "level")
            graph_node_source_ids.update((segment_nodes[0], segment_nodes[-1]))
            graph_edges.append(
                {
                    "type": "Feature",
                    "id": stable_id,
                    "geometry": {"type": "LineString", "coordinates": coordinates},
                    "properties": {
                        "schema_version": "2.0.0",
                        "city_id": CITY_ID,
                        "edge_id": stable_id,
                        "from_node": f"KK-OSM-N{segment_nodes[0]}",
                        "to_node": f"KK-OSM-N{segment_nodes[-1]}",
                        "source_id": "openstreetmap_kiyomizu_named_corridor_20260830",
                        "source_class": "VGI",
                        "data_class": "REAL",
                        "source_way_id": f"osm-way-{way_id}",
                        "source_node_ids": [f"osm-node-{node_id}" for node_id in segment_nodes],
                        "source_feature_id": f"osm-way-{way_id}:nodes-{start}-{end}",
                        "stable_feature_id": stable_id,
                        "revision_id": f"osm-snapshot-{SNAPSHOT_AT}",
                        "lineage": _lineage(way_id),
                        "geometry_status": "SOURCE_TRACEABLE_REAL",
                        "topology_status": "CANDIDATE",
                        "highway_tag": tags.get("highway"),
                        "name_tag": tags.get("name"),
                        "surface_tag": tags.get("surface"),
                        "access_tag": tags.get("access"),
                        "bridge": bridge,
                        "bridge_reason": bridge_reason,
                        "tunnel": tunnel,
                        "tunnel_reason": tunnel_reason,
                        "layer": layer,
                        "layer_reason": layer_reason,
                        "level": level,
                        "level_reason": level_reason,
                        "base_clear_width_m": None,
                        "base_clear_width_reason": "NOT_FIELD_MEASURED",
                        "running_slope": None,
                        "running_slope_reason": "NOT_FIELD_MEASURED",
                        "step_height_m": None,
                        "step_height_reason": "NOT_FIELD_MEASURED",
                        "operation_status": "UNKNOWN",
                        "operation_reason": "VGI_TAGS_DO_NOT_VERIFY_CURRENT_OR_EMERGENCY_OPERATION",
                        "accessibility_state": "UNKNOWN",
                        "accessibility_reason": "M6_NOT_COMPUTED_AND_REQUIRED_ATTRIBUTES_MISSING",
                    },
                }
            )
    graph_edges.sort(key=lambda feature: feature["id"])
    graph_nodes = []
    for source_id in sorted(graph_node_source_ids):
        node = node_by_id[source_id]
        stable_id = f"KK-OSM-N{source_id}"
        graph_nodes.append(
            {
                "type": "Feature",
                "id": stable_id,
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(node["lon"]), float(node["lat"])],
                },
                "properties": {
                    "schema_version": "2.0.0",
                    "city_id": CITY_ID,
                    "node_id": stable_id,
                    "source_id": "openstreetmap_kiyomizu_named_corridor_20260830",
                    "source_class": "VGI",
                    "data_class": "REAL",
                    "source_feature_id": f"osm-node-{source_id}",
                    "stable_feature_id": stable_id,
                    "revision_id": f"osm-snapshot-{SNAPSHOT_AT}",
                    "lineage": [
                        f"OpenStreetMap node {source_id}",
                        f"Referenced endpoint/shared node in snapshot {SNAPSHOT_AT}",
                    ],
                    "geometry_status": "SOURCE_TRACEABLE_REAL",
                    "topology_status": "CANDIDATE",
                    "entrance_status": "UNKNOWN",
                    "entrance_reason": "NO_OFFICIAL_OR_FIELD_ENTRANCE_EVIDENCE",
                },
            }
        )
    graph_nodes.sort(key=lambda feature: feature["id"])
    _write(
        pack / "graph" / "real" / "candidate_nodes.geojson",
        _pretty_bytes({"type": "FeatureCollection", "features": graph_nodes}),
    )
    _write(
        pack / "graph" / "real" / "candidate_edges.geojson",
        _pretty_bytes({"type": "FeatureCollection", "features": graph_edges}),
    )

    endpoint_counts = Counter(
        endpoint
        for feature in graph_edges
        for endpoint in (
            feature["properties"]["from_node"],
            feature["properties"]["to_node"],
        )
    )
    source_membership: dict[str, set[str]] = defaultdict(set)
    for feature in graph_edges:
        for source_node_id in feature["properties"]["source_node_ids"]:
            source_membership[source_node_id].add(feature["id"])
    crossing_candidates = _segment_intersection_candidates(graph_edges)
    qa = {
        "schema_version": "2.0.0",
        "city_id": CITY_ID,
        "source_id": "openstreetmap_kiyomizu_named_corridor_20260830",
        "source_class": "VGI",
        "geometry_status": "SOURCE_TRACEABLE_REAL",
        "topology_status": "CANDIDATE_REVIEW_REQUIRED",
        "route_continuity": "NOT_ESTABLISHED",
        "route_continuity_reason": "Named OSM subsets are not a verified continuous administrative route",
        "nearest_neighbour_join_applied": False,
        "nearest_neighbour_join_reason": "No reviewed tolerance or authority exists",
        "counts": {
            "source_way_count": len(ways),
            "candidate_node_count": len(graph_nodes),
            "candidate_edge_count": len(graph_edges),
            "duplicate_node_ids": len(graph_nodes) - len({feature["id"] for feature in graph_nodes}),
            "duplicate_edge_ids": len(graph_edges) - len({feature["id"] for feature in graph_edges}),
            "dangling_endpoint_nodes": sum(value == 1 for value in endpoint_counts.values()),
            "self_loops": sum(
                feature["properties"]["from_node"] == feature["properties"]["to_node"]
                for feature in graph_edges
            ),
            "zero_length_edges": sum(
                len({tuple(point) for point in feature["geometry"]["coordinates"]}) < 2
                for feature in graph_edges
            ),
            "connected_components": len(_components(graph_edges)),
            "geometric_cross_no_node_candidates": len(crossing_candidates),
            "geometric_crossings_promoted_to_nodes": 0,
            "operation_unknown_edges": sum(
                feature["properties"]["operation_status"] == "UNKNOWN"
                for feature in graph_edges
            ),
        },
        "connected_components": _components(graph_edges),
        "shared_source_node_ids": sorted(
            node_id for node_id, members in source_membership.items() if len(members) > 1
        ),
        "geometric_cross_no_node_candidates": crossing_candidates,
        "not_computed": {
            "disconnected_destinations": {
                "status": "NOT_COMPUTED",
                "reason": "No verified destination entrance geometry is connected",
            },
            "unsplit_hazard_boundaries": {
                "status": "NOT_COMPUTED",
                "reason": "Official hazard preview is not a validated v2 capability",
            },
        },
    }
    _write(pack / "graph" / "real" / "topology_qa.json", _pretty_bytes(qa))


def _transform_geometry(geometry: dict[str, Any], transformer: Any) -> dict[str, Any]:
    geometry_type = geometry["type"]

    def transform_coordinates(value: Any, depth: int) -> Any:
        if depth == 1:
            x, y = transformer.transform(float(value[0]), float(value[1]))
            return [x, y]
        return [transform_coordinates(item, depth - 1) for item in value]

    depth_by_type = {"Polygon": 3, "MultiPolygon": 4}
    if geometry_type not in depth_by_type:
        raise ValueError(f"official warning zone is not polygonal: {geometry_type}")
    return {
        "type": geometry_type,
        "coordinates": transform_coordinates(geometry["coordinates"], depth_by_type[geometry_type]),
    }


def build_hazard(pack: Path, hazard_root: Path, vendor_root: Path, source_zip_sha256: str) -> None:
    sys.path.insert(0, str(vendor_root))
    import shapefile  # type: ignore
    from pyproj import Transformer  # type: ignore

    transformer = Transformer.from_crs("EPSG:6668", "EPSG:4326", always_xy=True)
    field_names_by_layer: dict[str, list[str]] = {}
    layer_categories = {
        "g_d_yzone": "DEBRIS_FLOW_WARNING_ZONE",
        "g_k_yzone": "STEEP_SLOPE_FAILURE_WARNING_ZONE",
        "g_j_yzone": "LANDSLIDE_WARNING_ZONE",
    }
    features: list[dict[str, Any]] = []
    component_hashes: dict[str, dict[str, str]] = {}
    min_lon, min_lat, max_lon, max_lat = CORRIDOR_BBOX
    for layer, category in layer_categories.items():
        base = hazard_root / layer
        component_hashes[layer] = {
            extension: _sha256_file(base.with_suffix(extension))
            for extension in (".shp", ".shx", ".dbf", ".prj", ".cpg")
        }
        reader = shapefile.Reader(str(base), encoding="utf-8")
        fields = [field[0] for field in reader.fields[1:]]
        field_names_by_layer[layer] = fields
        for shape_record in reader.iterShapeRecords():
            west, south, east, north = shape_record.shape.bbox
            if east < min_lon or west > max_lon or north < min_lat or south > max_lat:
                continue
            attributes = dict(zip(fields, shape_record.record))
            source_key = str(attributes["K_ID"])
            stable_suffix = hashlib.sha256(f"{layer}:{source_key}".encode("utf-8")).hexdigest()[:12]
            stable_id = f"KK-OFFICIAL-LANDSLIDE-{layer.upper()}-{stable_suffix}"
            geometry = _transform_geometry(shape_record.shape.__geo_interface__, transformer)
            features.append(
                {
                    "type": "Feature",
                    "id": stable_id,
                    "geometry": geometry,
                    "properties": {
                        "schema_version": "2.0.0-preview",
                        "city_id": CITY_ID,
                        "source_id": "kyoto_city_hazard_map_landslide_20260830",
                        "source_class": "OFFICIAL",
                        "data_class": "REAL",
                        "source_layer": layer,
                        "source_feature_id": f"{layer}:{source_key}",
                        "stable_feature_id": stable_id,
                        "revision_id": "downloaded-2026-08-30",
                        "lineage": [
                            "Kyoto City Disaster Prevention Information Map GIS download",
                            f"Source layer {layer}; bbox-selected without boundary clipping",
                            "JGD2011 EPSG:6668 transformed to EPSG:4326 with PROJ always_xy",
                        ],
                        "geometry_status": "SOURCE_TRACEABLE_REAL_PREVIEW",
                        "hazard_type": "LANDSLIDE",
                        "hazard_category": category,
                        "hazard_value": None,
                        "hazard_value_unit": None,
                        "hazard_value_reason": "ZONE_CATEGORY_HAS_NO_NUMERIC_VALUE",
                        "designation_id": source_key,
                        "designation_name": attributes.get("K_NAME"),
                        "designation_notice": attributes.get("K_NO1"),
                        "designation_date_text": attributes.get("K_DATE1"),
                        "municipality_name": attributes.get("CITY_NAME"),
                        "operation_status": "UNKNOWN",
                        "edge_state_effect": "NONE",
                        "edge_state_reason": "HAZARD_OVERLAP_DOES_NOT_CREATE_CLOSURE",
                    },
                }
            )
    features.sort(key=lambda feature: feature["id"])
    preview_path = pack / "hazards" / "official" / "landslide_warning_preview.geojson"
    preview_bytes = _pretty_bytes({"type": "FeatureCollection", "features": features})
    _write(preview_path, preview_bytes)
    metadata = _build_hazard_preview_metadata(
        feature_count=len(features),
        source_zip_sha256=source_zip_sha256,
        component_hashes=component_hashes,
        preview_sha256=_sha256_bytes(preview_bytes),
    )
    _write(
        pack / "hazards" / "official" / "landslide_warning_preview.metadata.json",
        _pretty_hazard_metadata_bytes(metadata),
    )


def build_plateau_and_status(pack: Path) -> None:
    tileset_path = pack / "sources" / "retained" / "plateau_26100_bldg_tileset_20260830.json"
    query_path = pack / "sources" / "queries" / "plateau_26100_bldg_tileset_url.txt"
    tileset = json.loads(tileset_path.read_text(encoding="utf-8"))
    children = tileset.get("root", {}).get("children", [])
    child_urls = sorted(
        child.get("content", {}).get("uri")
        for child in children
        if isinstance(child.get("content", {}).get("uri"), str)
    )
    higashiyama = [url for url in child_urls if "26105_higashiyama-ku" in url]
    if len(higashiyama) != 1:
        raise ValueError("PLATEAU retained response must contain one Higashiyama building child")
    metadata = {
        "schema_version": "1.0.0",
        "city_id": CITY_ID,
        "source_id": "plateau_26100_bldg_maxlod2_latest_20260830",
        "source_url": query_path.read_text(encoding="utf-8").strip(),
        "source_class": "OFFICIAL",
        "data_class": "OFFICIAL_METADATA_ONLY",
        "accessed_at": ACCESSED_AT,
        "valid_as_of": None,
        "valid_as_of_reason": "Latest endpoint is dynamic; retained ETag response must be rechecked",
        "license": "Public Data License 1.0 (PDL1.0), CC BY 4.0 compatible",
        "license_terms_url": "https://www.mlit.go.jp/plateau/site-policy/",
        "redistribution_status": "PERMITTED_WITH_OBLIGATIONS_AGENT_REVIEWED_HUMAN_PENDING",
        "retained_response_path": "sources/retained/plateau_26100_bldg_tileset_20260830.json",
        "retained_response_sha256": _sha256_file(tileset_path),
        "query_path": "sources/queries/plateau_26100_bldg_tileset_url.txt",
        "query_sha256": _sha256_file(query_path),
        "building_composite_url": query_path.read_text(encoding="utf-8").strip(),
        "higashiyama_building_lod2_tileset_url": higashiyama[0],
        "road_tileset_status": "EMPTY_COMPOSITE_RESPONSE_AT_ACCESS_TIME",
        "terrain_tileset_status": "EMPTY_COMPOSITE_RESPONSE_AT_ACCESS_TIME",
        "plateau_3d_connected": False,
        "plateau_3d_connection_reason": "Metadata is retained but the city lane does not wire or render Cesium",
        "height_attribute_extracted": False,
        "setback_attribute_extracted": False,
    }
    _write(pack / "sources" / "plateau_26100_metadata.json", _pretty_bytes(metadata))

    readiness = {
        "schema_version": "1.0.0",
        "city_id": CITY_ID,
        "source_geometry_artifact_id": ARTIFACT_ID,
        "building_height_experiment": {
            "status": "NOT_COMPUTED",
            "height_status": "UNKNOWN",
            "setback_status": "UNKNOWN",
            "reason": "PLATEAU metadata/tileset URL is available but no per-building height or road-side setback extraction is validated",
        },
        "edge_input_policy": "M7 only when base clear width and both-side debris inputs are traceable",
        "eligible_edge_count": 0,
        "ineligible_edge_count": 19,
        "damage_state": "UNKNOWN",
        "debris_present": None,
        "m7_connected": False,
        "m7_connection_reason": "No candidate edge has measured clear width plus validated building height/setback and explicit model scenario inputs",
        "m6_connected": False,
        "kpi_connected": False,
    }
    _write(pack / "model" / "m7_input_readiness.json", _pretty_bytes(readiness))
    status = {
        "REAL_GEOMETRY_CONNECTED": True,
        "OFFICIAL_HAZARD_GEOMETRY_CONNECTED": False,
        "PLATEAU_3D_CONNECTED": False,
        "CANDIDATE_GRAPH_CONNECTED": True,
        "M7_CONNECTED": False,
        "M6_CONNECTED": False,
        "KPI_CONNECTED": False,
        "ADMIN_VALIDATED": False,
    }
    _write(pack / "realdata" / "status.json", _pretty_bytes(status))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--hazard-root", type=Path, required=True)
    parser.add_argument("--vendor-root", type=Path, required=True)
    parser.add_argument("--source-zip-sha256", required=True)
    args = parser.parse_args()
    if len(args.source_zip_sha256) != 64:
        raise ValueError("source ZIP sha256 must be a lowercase/uppercase 64-hex digest")
    build_osm(args.pack)
    build_hazard(args.pack, args.hazard_root, args.vendor_root, args.source_zip_sha256)
    build_plateau_and_status(args.pack)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
