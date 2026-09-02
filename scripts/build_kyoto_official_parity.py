"""Build fail-closed Kyoto official-data display artifacts from bounded trusted inputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL_NS = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}
EXPECTED_SHA = {
    "a31b": "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c",
    "emergency": "e1c03e4e0f830d10430b6a0fb1e1669886c3708cdc61164e5471cea7f9a4d639",
    "shelter": "a30cf1556380359a1fa8fc69e4641fbfb7c3c099595818ac24c01417c9e28246",
    "toilet": "a46448d7bb6fe814631b1230e69ce6d825d36ccf0ddb35dc339bc49ed60fc764",
}
FIELD_RESOLUTION = {
    "clear_width_m": {
        "evidence_candidates": ["reviewed H23 walking-space evidence", "explicit source-tagged width", "verified field measurement"],
        "next_acquisition_method": "Acquire a reviewed source-tagged walking clear-width measurement for the exact edge; do not infer it from highway class, raster appearance, or DEM.",
    },
    "left_buildings": {
        "evidence_candidates": ["official PLATEAU stable building IDs", "complete left-side coverage receipt"],
        "next_acquisition_method": "Verify PLATEAU package bytes, CRS, stable IDs, footprints, and complete left-side coverage; an empty list requires evidence that no influencing building exists.",
    },
    "right_buildings": {
        "evidence_candidates": ["official PLATEAU stable building IDs", "complete right-side coverage receipt"],
        "next_acquisition_method": "Verify PLATEAU package bytes, CRS, stable IDs, footprints, and complete right-side coverage; an empty list requires evidence that no influencing building exists.",
    },
    "variant": {
        "evidence_candidates": ["human-reviewed M7 pilot decision receipt"],
        "next_acquisition_method": "Record a reviewed mean_case or sensitivity_high_case decision for this pilot edge; do not apply a silent default.",
    },
    "official_closure": {
        "evidence_candidates": ["official operational closure record", "bounded official query receipt preserving tri-state None"],
        "next_acquisition_method": "Acquire a bounded official road-closure query or record for the edge and preserve None when no answer is evidenced; hazard overlap cannot create closure.",
    },
    "hazard_data_status": {
        "evidence_candidates": ["verified connected hazard context", "bounded UNKNOWN decision receipt"],
        "next_acquisition_method": "Bind the edge to a reviewed hazard-context receipt or explicitly record UNKNOWN with provenance; missing evidence cannot become a silent enum value.",
    },
}


def resolution_for_missing_field(field: str) -> dict:
    if field in FIELD_RESOLUTION:
        return FIELD_RESOLUTION[field]
    prefix = "m7_provenance."
    if field.startswith(prefix) and field[len(prefix):] in FIELD_RESOLUTION:
        base = field[len(prefix):]
        return {
            "evidence_candidates": [f"source/revision/field locator receipt for {base}", "reviewed transformation lineage with no silent default"],
            "next_acquisition_method": f"Bind {base} to an exact source ID, revision, field locator, and reviewed transformation receipt; a value without this provenance remains not evidence-ready.",
        }
    raise ValueError(f"no acquisition guidance for missing M7 field: {field}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def bounds_from_aoi(path: Path) -> tuple[float, float, float, float]:
    coordinates = load_json(path)["features"][0]["geometry"]["coordinates"][0]
    return min(point[0] for point in coordinates), min(point[1] for point in coordinates), max(point[0] for point in coordinates), max(point[1] for point in coordinates)


def bbox_intersects(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> bool:
    return not (left[2] < right[0] or right[2] < left[0] or left[3] < right[1] or right[3] < left[1])


def coordinate_points(value):
    if isinstance(value, list) and len(value) >= 2 and all(isinstance(item, (int, float)) for item in value[:2]):
        yield float(value[0]), float(value[1])
    elif isinstance(value, list):
        for item in value:
            yield from coordinate_points(item)


def point_in_rect(point: tuple[float, float], rect: tuple[float, float, float, float]) -> bool:
    return rect[0] <= point[0] <= rect[2] and rect[1] <= point[1] <= rect[3]


def orientation(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def segments_intersect(a, b, c, d) -> bool:
    values = (orientation(a, b, c), orientation(a, b, d), orientation(c, d, a), orientation(c, d, b))
    if values[0] == values[1] == values[2] == values[3] == 0:
        return bbox_intersects((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), (min(c[0], d[0]), min(c[1], d[1]), max(c[0], d[0]), max(c[1], d[1])))
    return values[0] * values[1] <= 0 and values[2] * values[3] <= 0


def point_in_ring(point, ring) -> bool:
    inside = False
    x, y = point
    for first, second in zip(ring, ring[1:] + ring[:1]):
        if ((first[1] > y) != (second[1] > y)) and x < (second[0] - first[0]) * (y - first[1]) / (second[1] - first[1]) + first[0]:
            inside = not inside
    return inside


def polygon_intersects_rect(rings, rect) -> bool:
    if any(point_in_rect(tuple(point[:2]), rect) for ring in rings for point in ring):
        return True
    corners = [(rect[0], rect[1]), (rect[2], rect[1]), (rect[2], rect[3]), (rect[0], rect[3])]
    if rings and any(point_in_ring(corner, rings[0]) and not any(point_in_ring(corner, hole) for hole in rings[1:]) for corner in corners):
        return True
    edges = list(zip(corners, corners[1:] + corners[:1]))
    return any(segments_intersect(tuple(first[:2]), tuple(second[:2]), edge[0], edge[1]) for ring in rings for first, second in zip(ring, ring[1:]) for edge in edges)


def geometry_intersects_rect(geometry: dict, rect) -> bool:
    coords = geometry.get("coordinates", [])
    geometry_type = geometry.get("type")
    polygons = [coords] if geometry_type == "Polygon" else coords if geometry_type == "MultiPolygon" else []
    points = list(coordinate_points(coords))
    if not points or not bbox_intersects((min(x for x, _ in points), min(y for _, y in points), max(x for x, _ in points), max(y for _, y in points)), rect):
        return False
    return any(polygon_intersects_rect(polygon, rect) for polygon in polygons)


def xlsx_rows(path: Path, sheet_name: str) -> list[list[object]]:
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {node.attrib["Id"]: node.attrib["Target"] for node in relations.findall("p:Relationship", REL_NS)}
        sheet = next((node for node in workbook.findall("m:sheets/m:sheet", NS) if node.attrib["name"] == sheet_name), None)
        if sheet is None:
            raise ValueError(f"worksheet not found: {sheet_name}")
        target = targets[sheet.attrib[f"{{{NS['r']}}}id"]].lstrip("/")
        if not target.startswith("xl/"):
            target = f"xl/{target}"
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(part.text or "" for part in node.findall(".//m:t", NS)) for node in strings.findall("m:si", NS)]
        root = ET.fromstring(archive.read(target))
        rows = []
        for row_node in root.findall("m:sheetData/m:row", NS):
            values = {}
            for cell in row_node.findall("m:c", NS):
                letters = re.match(r"[A-Z]+", cell.attrib["r"]).group(0)
                index = 0
                for letter in letters:
                    index = index * 26 + ord(letter) - 64
                index -= 1
                cell_type = cell.attrib.get("t")
                value_node = cell.find("m:v", NS)
                if cell_type == "inlineStr":
                    value = "".join(part.text or "" for part in cell.findall(".//m:t", NS))
                elif value_node is None:
                    value = None
                elif cell_type == "s":
                    value = shared[int(value_node.text)]
                elif cell_type in {"str", "e"}:
                    value = value_node.text
                else:
                    text = value_node.text or ""
                    try:
                        value = float(text)
                        if value.is_integer():
                            value = int(value)
                    except ValueError:
                        value = text
                values[index] = value
            width = max(values, default=-1) + 1
            rows.append([values.get(index) for index in range(width)])
        return rows


def as_float(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number == number and abs(number) != float("inf") else None


def aoi_for_point(longitude: float, latitude: float, aoi_bounds: dict) -> str | None:
    for aoi_id, rect in aoi_bounds.items():
        if point_in_rect((longitude, latitude), rect):
            return aoi_id
    return None


def normalize_facilities(paths: dict, aoi_bounds: dict) -> tuple[list[dict], dict]:
    records = []

    def add_rows(rows, category, source_id, version, indices):
        for row in rows[1:]:
            required_indices = [index for index in indices.values() if index is not None]
            if len(row) <= max(required_indices):
                continue
            latitude = as_float(row[indices["latitude"]])
            longitude = as_float(row[indices["longitude"]])
            if latitude is None or longitude is None:
                continue
            aoi_id = aoi_for_point(longitude, latitude, aoi_bounds)
            if aoi_id is None:
                continue
            source_row_id = str(row[indices["id"]] if row[indices["id"]] not in (None, "") else len(records) + 1)
            records.append({
                "facility_record_id": f"{source_id}:{source_row_id}",
                "category": category,
                "name": str(row[indices["name"]] or "").strip(),
                "address": str(row[indices["address"]] or "").strip(),
                "phone": str(row[indices["phone"]]).strip() if indices.get("phone") is not None and len(row) > indices["phone"] and row[indices["phone"]] not in (None, "") else None,
                "longitude": longitude,
                "latitude": latitude,
                "coordinate_method": "SOURCE_PROVIDED_LONGITUDE_LATITUDE",
                "silent_geocoding": False,
                "aoi_group": aoi_id,
                "source_id": source_id,
                "source_version_or_valid_as_of": version,
                "entrance_status": "UNKNOWN",
                "operation_status": "UNKNOWN",
                "accessibility_status": "UNKNOWN",
                "safety_status": "UNKNOWN",
                "limitations": "Official source row and source-provided coordinates only; current opening, entrance, accessibility, safety, and disaster usability are not inferred.",
            })

    add_rows(xlsx_rows(paths["emergency"], "指定避難場所データベース"), "designated_emergency_evacuation_place", "kyoto_emergency_shelters_r80818", "R8.8.18", {"id": 0, "name": 3, "phone": 6, "address": 7, "latitude": 8, "longitude": 9})
    add_rows(xlsx_rows(paths["shelter"], "指定避難所データベース"), "designated_shelter", "kyoto_designated_shelters_r80818", "R8.8.18", {"id": 0, "name": 3, "phone": 5, "address": 6, "latitude": 7, "longitude": 8})
    toilet_rows = xlsx_rows(paths["toilet"], "公衆・観光トイレ")
    add_rows(toilet_rows[1:], "public_tourist_toilet", "kyoto_public_toilets_00307", "2026-03-06", {"id": 3, "name": 1, "phone": None, "address": 5, "latitude": 7, "longitude": 6})
    records.sort(key=lambda row: (row["aoi_group"], row["category"], row["facility_record_id"]))
    categories = {
        "designated_shelter": {"status": "CONNECTED_SOURCE_COORDINATES_INTERNAL_UI", "record_count": sum(row["category"] == "designated_shelter" for row in records), "map_connected": True},
        "designated_emergency_evacuation_place": {"status": "CONNECTED_SOURCE_COORDINATES_INTERNAL_UI", "record_count": sum(row["category"] == "designated_emergency_evacuation_place" for row in records), "map_connected": True},
        "public_tourist_toilet": {"status": "CONNECTED_SOURCE_COORDINATES_INTERNAL_UI", "record_count": sum(row["category"] == "public_tourist_toilet" for row in records), "map_connected": True},
        "emergency_open_space": {"status": "METADATA_ONLY_NOT_CONNECTED", "record_count": 0, "map_connected": False, "reason": "The official landing page is source-bound, but no reviewed current row-level original with source-provided coordinates is present in the bounded trust scope.", "next_acquisition_method": "Acquire the current official emergency-open-space row list and preserve stable IDs, direct coordinates, version, licence, and row lineage."},
        "temporary_stay_facility": {"status": "METADATA_ONLY_NOT_CONNECTED", "record_count": 0, "map_connected": False, "reason": "The official landing page is source-bound, but no reviewed current row-level original with source-provided coordinates is present in the bounded trust scope.", "next_acquisition_method": "Acquire the current official temporary-stay facility row list and preserve stable IDs, direct coordinates, version, licence, and row lineage."},
    }
    return records, categories


def build_a31b(path: Path, aoi_bounds: dict) -> tuple[dict, dict]:
    outputs = {aoi_id: [] for aoi_id in aoi_bounds}
    layer_counts = {aoi_id: {} for aoi_id in aoi_bounds}
    with zipfile.ZipFile(path) as archive:
        for member in sorted(name for name in archive.namelist() if name.lower().endswith(".geojson")):
            source = json.loads(archive.read(member).decode("utf-8-sig"))
            layer_match = re.search(r"A31b-(\d+)-", Path(member).name)
            layer_id = f"A31b-{layer_match.group(1)}" if layer_match else Path(member).stem
            for index, feature in enumerate(source.get("features", [])):
                for aoi_id, rect in aoi_bounds.items():
                    if not geometry_intersects_rect(feature.get("geometry", {}), rect):
                        continue
                    properties = dict(feature.get("properties", {}))
                    properties.update({
                        "_ablepath_aoi_id": aoi_id,
                        "_ablepath_display_only": True,
                        "_ablepath_layer_id": layer_id,
                        "_ablepath_source_member": member,
                        "_ablepath_source_feature_index": index,
                        "_ablepath_geometry_transform": "NONE_WHOLE_SOURCE_FEATURE_INTERSECTION_SELECTION",
                    })
                    outputs[aoi_id].append({"type": "Feature", "properties": properties, "geometry": feature["geometry"]})
                    layer_counts[aoi_id][layer_id] = layer_counts[aoi_id].get(layer_id, 0) + 1
    artifacts = {aoi_id: {"type": "FeatureCollection", "name": f"A31b 2025 {aoi_id} display-only intersection selection", "features": features} for aoi_id, features in outputs.items()}
    return artifacts, layer_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--raw-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    raw = args.raw_root.resolve()
    paths = {
        "a31b": raw / "kyoto_arashiyama" / "A31b-25_10_5235_GEOJSON.zip",
        "emergency": raw / "human-actions" / "auto-download-kyoto-emergency-shelters-20260901T1912JST" / "20260825185105_02指定緊急避難場所水害・土砂災害R80818現在.xlsx",
        "shelter": raw / "human-actions" / "auto-download-kyoto-shelters-20260901T1910JST" / "20260825185151_01指定避難所R80818現在.xlsx",
        "toilet": raw / "phase4-multicity-data-acquisition" / "raw" / "shared" / "kyoto_public_toilets_00307" / "20260306112900_オープンデータ（公衆トイレ、観光トイレ）.xlsx",
    }
    for key, path in paths.items():
        actual = sha256(path)
        if actual != EXPECTED_SHA[key]:
            raise ValueError(f"raw SHA mismatch for {key}: expected {EXPECTED_SHA[key]}, got {actual}")

    aoi_paths = {
        "kiyomizu_gion": root / "inputs/staging/PHASE4-MULTICITY-DATA-ACQUISITION/city_aoi/aoi_kyoto_kiyomizu_gion_v1.geojson",
        "arashiyama": root / "inputs/staging/PHASE4-MULTICITY-DATA-ACQUISITION/city_aoi/aoi_kyoto_arashiyama_v1.geojson",
    }
    aoi_bounds = {key: bounds_from_aoi(path) for key, path in aoi_paths.items()}
    output = root / "inputs/staging/KYOTO-OFFICIAL-PARITY-V1"

    dem_rows = list(csv.DictReader((root / "inputs/staging/OFFICIAL-LOCAL-ARTIFACT-PROMOTION-V2/dem_product_inventory.csv").open(encoding="utf-8-sig", newline="")))
    dem_validation = {"schema_version": "1.0.0", "status": "AOI_COVERAGE_VALIDATED_ELEVATION_NOT_SAMPLED", "aois": {}}
    for aoi_id, rect in aoi_bounds.items():
        products = []
        for row in dem_rows:
            product_bounds = tuple(json.loads(row["bounds_wgs84"]))
            if bbox_intersects(rect, product_bounds):
                products.append({key: row[key] for key in ("dataset_id", "source_sha256", "mesh_id", "dem_class", "package_date", "horizontal_crs", "axis_semantics", "vertical_datum", "bounds_wgs84", "source_url", "issuer", "license_url", "license_status")})
        dem_validation["aois"][aoi_id] = {
            "aoi_bounds_longitude_latitude": rect,
            "intersecting_product_count": len(products),
            "products": products,
            "evidence_ui_connected": True,
            "elevation_sampled": False,
            "terrain_surface_computed": False,
            "step_inferred": False,
            "cross_slope_inferred": False,
            "reason": "Package bounds, declared horizontal CRS, formal GML axis semantics, and AOI intersection are validated for inventory display. Vertical datum is not explicit and elevation was not sampled; no step, curb, longitudinal slope, cross-slope, M6, or accessibility value is derived.",
        }
    write_json(output / "dem_aoi_validation.json", dem_validation)

    flood_artifacts, flood_layer_counts = build_a31b(paths["a31b"], aoi_bounds)
    flood_files = {"kiyomizu_gion": "a31b_kiyomizu_gion_display.geojson", "arashiyama": "a31b_arashiyama_display.geojson"}
    for aoi_id, artifact in flood_artifacts.items():
        write_json(output / flood_files[aoi_id], artifact)

    records, categories = normalize_facilities(paths, aoi_bounds)
    write_json(output / "facility_records.json", {"schema_version": "1.0.0", "records": records, "silent_geocoding": False})
    write_json(output / "facility_category_status.json", {"schema_version": "1.0.0", "status": "PARTIAL_SOURCE_COORDINATE_CONNECTION", "categories": categories, "silent_geocoding": False})
    facility_geojson = {"type": "FeatureCollection", "name": "Kyoto official facility source-coordinate points", "features": [{"type": "Feature", "properties": {key: value for key, value in record.items() if key not in {"longitude", "latitude"}}, "geometry": {"type": "Point", "coordinates": [record["longitude"], record["latitude"]]}} for record in records]}
    write_json(output / "facility_points.geojson", facility_geojson)
    for aoi_id in aoi_bounds:
        write_json(
            output / f"facility_points_{aoi_id}.geojson",
            {
                "type": "FeatureCollection",
                "name": f"Kyoto official facility source-coordinate points — {aoi_id}",
                "features": [feature for feature in facility_geojson["features"] if feature["properties"]["aoi_group"] == aoi_id],
            },
        )

    receipts = {
        "schema_version": "1.0.0",
        "raw_tracked": False,
        "sources": [
            {"dataset_id": "nlni_a31b_2025_kyoto_flood", "sha256": EXPECTED_SHA["a31b"], "raw_locator": "raw-root:kyoto_arashiyama/A31b-25_10_5235_GEOJSON.zip", "official_url": "https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip", "version": "2025", "license": "CC BY 4.0"},
            {"dataset_id": "kyoto_emergency_shelters_r80818", "sha256": EXPECTED_SHA["emergency"], "raw_locator": "raw-root:human-actions/auto-download-kyoto-emergency-shelters-20260901T1912JST/current-r80818.xlsx", "official_url": "https://data.city.kyoto.lg.jp/resource/?id=7855", "version": "R8.8.18", "integrity": "ZIP_SIGNATURE_PASS"},
            {"dataset_id": "kyoto_designated_shelters_r80818", "sha256": EXPECTED_SHA["shelter"], "raw_locator": "raw-root:human-actions/auto-download-kyoto-shelters-20260901T1910JST/current-r80818.xlsx", "official_url": "https://data.city.kyoto.lg.jp/resource/?id=7854", "version": "R8.8.18", "integrity": "ZIP_SIGNATURE_PASS"},
            {"dataset_id": "kyoto_public_toilets_00307", "sha256": EXPECTED_SHA["toilet"], "raw_locator": "raw-root:phase4-multicity-data-acquisition/raw/shared/kyoto_public_toilets_00307/current.xlsx", "official_url": "https://data.city.kyoto.lg.jp/resource/?id=20314", "version": "2026-03-06", "license": "CC BY 4.0"},
        ],
        "dem_inventory_binding": {"path": "inputs/staging/OFFICIAL-LOCAL-ARTIFACT-PROMOTION-V2/dem_product_inventory.csv", "sha256": sha256(root / "inputs/staging/OFFICIAL-LOCAL-ARTIFACT-PROMOTION-V2/dem_product_inventory.csv"), "scope": "PACKAGE_BOUNDS_DECLARED_HORIZONTAL_CRS_FORMAL_GML_AXIS_AOI_INTERSECTION_ONLY", "elevation_sampled": False},
        "transform": {"script": "scripts/build_kyoto_official_parity.py", "aoi_inputs": {key: {"path": path.relative_to(root).as_posix(), "sha256": sha256(path)} for key, path in aoi_paths.items()}, "address_geocoding_used": False, "hazard_to_closure_damage_debris": False, "dem_to_step_or_cross_slope": False, "plateau_to_setback": False},
    }
    write_json(output / "source_receipts.json", receipts)

    m7_all = load_json(root / "reports/M7_ALL_EDGE_EVIDENCE_READINESS.json")
    pilot_rows = []
    group_counts = {"kiyomizu_gion": 0, "arashiyama": 0}
    for row in m7_all["edges"]:
        if not row.get("deep_pilot") or row["city_id"] not in {"kyoto_kiyomizu", "kyoto_arashiyama"}:
            continue
        group = "kiyomizu_gion" if row["city_id"] == "kyoto_kiyomizu" else "arashiyama"
        copy = dict(row)
        copy["aoi_group"] = group
        copy["field_resolution"] = {field: resolution_for_missing_field(field) for field in row["missing_fields"]}
        copy["subarea_partition_status"] = "COMBINED_PACK_UNPARTITIONED" if group == "kiyomizu_gion" else "ARASHIYAMA_PACK"
        pilot_rows.append(copy)
        group_counts[group] += 1
    pilot_status = {
        "schema_version": "1.0.0",
        "status": "COMPLETE_REASONED_NULL_EVIDENCE_ACQUISITION_PACKET",
        "selected_edge_count": len(pilot_rows),
        "evidence_ready_count": sum(row["m7_evidence_ready"] for row in pilot_rows),
        "computed_count": sum(row["m7_computed"] for row in pilot_rows),
        "groups": {key: {"selected_edge_count": count, "partition_status": "COMBINED_KIYOMIZU_GION_CONNECTOR_NOT_REVIEWED" if key == "kiyomizu_gion" else "ARASHIYAMA"} for key, count in group_counts.items()},
        "edges": pilot_rows,
        "damage_or_debris_derived_from_hazard": False,
        "plateau_setback_derived": False,
        "m6_status": "NOT_COMPUTED",
        "MODEL_ROUTE_VERIFIED": False,
    }
    write_json(root / "reports/KYOTO_M7_DEEP_PILOT_STATUS.json", pilot_status)

    plateau_rows = list(csv.DictReader((root / "inputs/staging/PLATEAU-BUILDING-EVIDENCE-V1/PLATEAU_BUILDING_AOI_INVENTORY.csv").open(encoding="utf-8-sig", newline="")))
    plateau_by_aoi = {row["subarea_id"]: row for row in plateau_rows if row["subarea_id"] in {"kiyomizu", "gion", "kiyomizu_gion_connector", "arashiyama"}}
    flood_hashes = {aoi_id: sha256(output / filename) for aoi_id, filename in flood_files.items()}
    facility_hash = sha256(output / "facility_records.json")
    parity_aois = {}
    for subarea in ("kiyomizu", "gion", "kiyomizu_gion_connector", "arashiyama"):
        group = "arashiyama" if subarea == "arashiyama" else "kiyomizu_gion"
        parity_aois[subarea] = {
            "aoi_group": group,
            "subarea_partition_status": "ARASHIYAMA_AOI" if group == "arashiyama" else "COMBINED_KIYOMIZU_GION_CONNECTOR_AOI_NOT_PARTITIONED",
            "terrain": {**dem_validation["aois"][group], "evidence_ui_connected": True},
            "flood": {"status": "CONNECTED_FOR_INTERNAL_DISPLAY_ONLY", "display_connected": True, "aoi_group": group, "feature_count": len(flood_artifacts[group]["features"]), "layer_counts": flood_layer_counts[group], "artifact_sha256": flood_hashes[group], "closure_derived": False, "damage_or_debris_derived": False, "reason": "Exact source features intersecting the reviewed AOI rectangle are displayed without geometry rewriting or operational interpretation."},
            "landslide": {"status": "NOT_CONNECTED", "reason": "Exact g_dosha_00all.zip SHA is known, but prior-consent terms, redistribution review, and source-feature-to-AOI lineage are unresolved; no layer is displayed and no CLOSED, damage, or debris state is derived."},
            "facilities": {"evidence_ui_connected": True, "record_count": sum(row["aoi_group"] == group for row in records), "category_status_source": "inputs/staging/KYOTO-OFFICIAL-PARITY-V1/facility_category_status.json", "silent_geocoding": False},
            "plateau": {"status": plateau_by_aoi[subarea]["connection_mode"], "inventory_connected": True, "fallback": plateau_by_aoi[subarea]["fallback"], "setback_derived": False, "reason": plateau_by_aoi[subarea]["reason"]},
        }
    parity_status = {
        "schema_version": "1.0.0",
        "status": "PARTIAL_FAIL_CLOSED_EVIDENCE_UI_CONNECTED",
        "task_id": "KYOTO-OFFICIAL-PARITY-V1",
        "aois": parity_aois,
        "facility_categories": categories,
        "plateau_inventory": list(plateau_by_aoi.values()),
        "m7": {"selected_edge_count": len(pilot_rows), "evidence_ready_count": 0, "computed_count": 0, "reasoned_null_ui_connected": True, "source": "reports/KYOTO_M7_DEEP_PILOT_STATUS.json"},
        "screenshots": {"required": ["kyoto-kiyomizu-gion-parity.png", "kyoto-arashiyama-parity.png", "kyoto-m7-reasoned-null.png"], "binary_git_tracked": False, "ci_artifact_directory": "viewer/test-results"},
        "safe_route_claim": False,
        "accessibility_claim": False,
        "admin_validated": False,
        "m6_status": "NOT_COMPUTED",
        "MODEL_ROUTE_VERIFIED": False,
    }
    write_json(root / "reports/KYOTO_PARITY_STATUS.json", parity_status)
    write_json(output / "handoff.json", {"schema_version": "1.0.0", "status": parity_status["status"], "generated_artifacts": {path.name: sha256(path) for path in sorted(output.iterdir()) if path.is_file() and path.name != "handoff.json"}, "raw_redownloaded": False, "raw_tracked": False, "absolute_paths_tracked": False})


if __name__ == "__main__":
    main()
