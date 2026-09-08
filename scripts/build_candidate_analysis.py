"""Generate the canonical three-city static candidate-analysis artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from hashlib import sha256
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis.static_candidate_analysis import (
    CITY_INPUTS,
    authoritative_report_paths,
    build_static_candidate_analysis,
    canonical_text_sha256,
    canonical_text_sha256_bytes,
    validate_static_candidate_analysis,
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _hash(path: Path) -> str:
    return canonical_text_sha256(path)


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or any(not field for field in reader.fieldnames):
            raise ValueError(f"strict CSV parse failed: {path}")
        return list(reader)


def _official_evidence(root: Path, city_id: str) -> tuple[dict, list[dict]]:
    promotion = _load_json(root / "reports/OFFICIAL_LOCAL_ARTIFACT_PROMOTION_V2.json")
    kyoto = _load_json(root / "reports/KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json") if city_id.startswith("kyoto_") else None
    plateau = _load_json(root / "reports/PLATEAU_BUILDING_EVIDENCE_V1.json")
    m7 = _load_json(root / "reports/M7_REAL_EDGE_STATUS.json")
    m7_all = _load_json(root / "reports/M7_ALL_EDGE_EVIDENCE_READINESS.json")
    if promotion.get("closure_derived") or promotion.get("damage_derived") or promotion.get("debris_derived"):
        raise ValueError("unsafe official evidence promotion is forbidden")
    if (
        len(m7_all["edges"]) != m7_all["all_edge_count"]
        or m7_all["all_edge_count"] != m7["all_edge_count"]
        or m7_all["deep_pilot_count"] != m7["deep_pilot_count"]
        or m7_all["evidence_ready_count"] != m7["evidence_ready_count"]
        or m7_all["computed_count"] != m7["computed_count"]
        or any(row["status"] != "NOT_COMPUTED" or row["m7_result"] is not None or row["m7_computed"] or row["m7_evidence_ready"] for row in m7_all["edges"])
    ):
        raise ValueError("P3 M7 receipt binding is incomplete or promoted")
    edge_receipts = [row for row in m7_all["edges"] if row["city_id"] == city_id]
    city_truth = kyoto.get("cities", {}).get(city_id) if kyoto else None
    parity_root = root / "inputs/staging/KYOTO-OFFICIAL-PARITY-V1"
    parity_group = "kiyomizu_gion" if city_id == "kyoto_kiyomizu" else "arashiyama" if city_id == "kyoto_arashiyama" else None
    kyoto_parity = _load_json(root / "reports/KYOTO_PARITY_STATUS.json") if city_truth else None
    kyoto_pilot = _load_json(root / "reports/KYOTO_M7_DEEP_PILOT_STATUS.json") if city_truth else None
    parity_aoi = (kyoto_parity["aois"]["kiyomizu"] if city_id == "kyoto_kiyomizu" else kyoto_parity["aois"]["arashiyama"]) if city_truth else None
    subareas = city_truth["subareas"] if city_truth else (["enoshima_katase"] if city_id == "fujisawa_enoshima" else [])
    terrain_path = root / f"cities/{city_id}/terrain/official/dem_product_inventory.csv"
    terrain_rows = _csv_rows(terrain_path) if terrain_path.exists() else []
    terrain_products = []
    for row in terrain_rows:
        selected = {key: row[key] for key in ("dataset_id", "mesh_id", "dem_class", "horizontal_crs", "vertical_datum")}
        if city_truth:
            selected.update({"aoi": parity_group, "aoi_status": "AOI_INTERSECTS_REVIEWED_BOUNDS", "validation_result": "HORIZONTAL_CRS_AXIS_AOI_VALIDATED_VERTICAL_DATUM_NOT_EXPLICIT", "license_status": row["license_status"], "terrain_connected": False, "status": "EVIDENCE_UI_ONLY_NOT_ELEVATION_ANALYSIS", "legacy_inventory_status": {"aoi": row["aoi"], "aoi_status": row["aoi_status"], "validation_result": row["validation_result"], "terrain_connected": row["terrain_connected"] == "true"}})
        else:
            selected.update({"aoi": row["aoi"], "aoi_status": row["aoi_status"], "validation_result": row["validation_result"], "license_status": row["license_status"], "terrain_connected": row["terrain_connected"] == "true", "status": "NOT_CONNECTED"})
        terrain_products.append(selected)
    fixed_absent = "No accepted source-traceable AOI artifact in P1; no closure, damage, debris, or FAIL state is derived."
    hazard_layers = []
    if city_truth:
        for subarea in subareas:
            for layer, artifact_status, reason in (
                ("flood", city_truth["flood_artifact_status"], city_truth["flood_reason"]),
                ("landslide", city_truth["landslide_artifact_status"], city_truth["landslide_reason"]),
                ("earthquake", None, None), ("liquefaction", None, None), ("inner_flood", None, None),
            ):
                if layer == "flood" and parity_aoi:
                    hazard_layers.append({"subarea": subarea, "layer": layer, "status": "CONNECTED_FOR_INTERNAL_DISPLAY_ONLY", "connected": True, "artifact_status": "AOI_INTERSECTION_SELECTION_HASH_BOUND", "reason": parity_aoi["flood"]["reason"]})
                else:
                    hazard_layers.append({"subarea": subarea, "layer": layer, "status": "NOT_CONNECTED", "connected": False, "artifact_status": artifact_status or "NOT_ACCEPTED", "reason": reason or fixed_absent})
    scenarios = []
    if city_id == "fujisawa_enoshima":
        for filename in ("earthquake_scenario_inventory.csv", "liquefaction_scenario_inventory.csv"):
            for row in _csv_rows(root / f"cities/{city_id}/hazards/official/{filename}"):
                scenarios.append({key: row[key] for key in ("dataset_id", "scenario", "layer_kind", "official_source", "official_url", "version_date", "license_review", "validation_result", "crs", "bounds_native")} | {"aoi_scope": "enoshima_katase", "status": "NOT_CONNECTED", "connected": False, "reason": "Scenario inventory only; no AOI geometry connection or closure derivation."})
    if city_id == "fujisawa_enoshima":
        table = _load_json(root / f"cities/{city_id}/facilities/official/FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json")
        facility = {"status": promotion["fujisawa_accessibility_facilities"]["status"], "geometry_status": "ADDRESS_ONLY", "marker_policy": "TABLE_ONLY_NO_MARKERS_OR_GEOCODING", "record_count": len(table["records"]), "records": table["records"], "reason": "57 address-only records are displayed as a table; coordinates, map markers, geocoding, accessibility, opening, and disaster availability are not inferred."}
    elif city_truth:
        category_status = _load_json(parity_root / "facility_category_status.json")
        records = [row for row in _load_json(parity_root / "facility_records.json")["records"] if row["aoi_group"] == parity_group]
        categories = {}
        for category, value in category_status["categories"].items():
            categories[category] = {**value, "record_count": len([row for row in records if row["category"] == category]) if value["map_connected"] else 0, "count_scope": parity_group}
        point_path = parity_root / f"facility_points_{parity_group}.geojson"
        facility = {"status": "PARTIAL_3_OF_5_CATEGORIES_SOURCE_COORDINATES", "geometry_status": "SOURCE_PROVIDED_LONGITUDE_LATITUDE", "marker_policy": "SOURCE_COORDINATES_ONLY_NO_GEOCODING", "record_count": len(records), "records": records, "categories": categories, "display_layer": {"data_path": f"./data/official/facility_points_{parity_group}.geojson", "artifact_sha256": _hash(point_path), "copied_sha256": _hash(point_path), "feature_count": len(_load_json(point_path)["features"])}, "reason": "Three official categories are displayed from source-provided longitude/latitude only. Emergency-open-space and temporary-stay rows remain metadata-only; opening, entrance, accessibility, safety, and disaster usability are UNKNOWN."}
    else:
        facility = {"status": "NOT_CONNECTED", "record_count": 0, "reason": "No official facility evidence is connected."}
    plateau_inventory = [row for row in _csv_rows(root / "inputs/staging/PLATEAU-BUILDING-EVIDENCE-V1/PLATEAU_BUILDING_AOI_INVENTORY.csv") if row["city_id"] == city_id] if city_truth else []
    kyoto_pilot_edges = [row for row in kyoto_pilot["edges"] if row["aoi_group"] == parity_group] if city_truth else []
    flood_path = parity_root / f"a31b_{parity_group}_display.geojson" if parity_group else None
    flood_data = _load_json(flood_path) if flood_path else None
    source_hashes = {key: _hash(path) for key, path in authoritative_report_paths(root, city_id).items()}
    terrain_reason = "No terrain product has been connected to this city analysis."
    hazard_reason = "No official hazard geometry is connected; earthquake and liquefaction inventories remain scenario metadata and do not derive CLOSED or FAIL."
    official = {
        "source_status": promotion["status"],
        "source_hashes": source_hashes,
        "subareas": subareas,
        "terrain": {"status": "AOI_COVERAGE_VALIDATED_ELEVATION_NOT_SAMPLED" if city_truth else "NOT_CONNECTED", "reason": parity_aoi["terrain"]["reason"] if city_truth else terrain_reason, "connected": False, "evidence_ui_connected": bool(city_truth), "elevation_sampled": False, "step_inferred": False, "cross_slope_inferred": False, "aoi_validation": parity_aoi["terrain"] if city_truth else None, "receipt_sha256": _hash(terrain_path) if terrain_path.exists() else None, "products": terrain_products},
        "hazard": {"status": "A31B_DISPLAY_CONNECTED_LANDSLIDE_NOT_CONNECTED" if city_truth else "NOT_CONNECTED", "reason": f"A31b is connected for internal display only. Landslide remains NOT_CONNECTED: {parity_aoi['landslide']['reason']}" if city_truth else hazard_reason, "connected": False, "display_connected": bool(city_truth), "display_feature_count": len(flood_data["features"]) if flood_data else 0, "display_layer": {"data_path": f"./data/official/a31b_{parity_group}_display.geojson", "artifact_sha256": _hash(flood_path), "copied_sha256": _hash(flood_path), "feature_count": len(flood_data["features"]), "display_only": True} if city_truth else None, "closure_derived": False, "damage_or_debris_inferred": False, "layers": hazard_layers, "scenarios": scenarios},
        "facility": facility,
        "plateau": {"status": "NOT_CONNECTED", "aoi_count": len(subareas), "aoi_scope": subareas, "inventory": plateau_inventory, "inventory_connected": bool(city_truth), "fallback": plateau["fallback"], "m7_evidence_ready_count": plateau["m7_evidence_ready_count"], "m7_computed_count": plateau["m7_computed_count"], "reason": "The PLATEAU 2025 evidence inventory is connected, but verified package bytes, building IDs, footprints, direct height, side coverage, and real 3D remain unavailable. Existing source-traceable candidate 2D is the deterministic fallback, not a PLATEAU-derived footprint layer."},
        "m7": {"status": "NOT_COMPUTED", "all_edge_count": m7["all_edge_count"], "deep_pilot_count": m7["deep_pilot_count"], "evidence_ready_count": m7["evidence_ready_count"], "computed_count": m7["computed_count"], "city_edge_count": len(edge_receipts), "edge_receipts_source_sha256": _hash(root / "reports/M7_ALL_EDGE_EVIDENCE_READINESS.json"), "kyoto_deep_pilot_edges": kyoto_pilot_edges, "city_limitations": m7["subarea_limitations"].get(city_id, "No reviewed source-traceable per-edge M7 inputs are connected."), "reason": "M7 is not connected to real candidate edges; every Kyoto pilot exposes field-level evidence candidates and next acquisition without inferring setback, damage, or debris."},
        "m6": {"status": "NOT_COMPUTED", "reason": "M6/profile evaluation is not connected."},
        "safe_route_claim": False,
        "accessibility_claim": False,
        "admin_validated": False,
    }
    return official, edge_receipts


def _artifact_for(root: Path, city: dict) -> dict:
    node_path = root / city["nodes"]
    edge_path = root / city["edges"]
    node_bytes = node_path.read_bytes()
    edge_bytes = edge_path.read_bytes()
    nodes = json.loads(node_bytes)["features"]
    edges = json.loads(edge_bytes)["features"]
    revisions = sorted({feature.get("properties", {}).get("revision_id") for feature in [*nodes, *edges] if feature.get("properties", {}).get("revision_id")})
    official, readiness = _official_evidence(root, city["id"])
    context = {"city_id": city["id"], "source_artifact_ids": [city["nodes"], city["edges"]], "source_revision_ids": revisions, "input_sha256": sha256(node_bytes + b"\0" + edge_bytes).hexdigest(), "input_hashes": {"node_sha256": sha256(node_bytes).hexdigest(), "edge_sha256": sha256(edge_bytes).hexdigest()}, "snapshot_at": city["snapshot"], "source_id": city["source"]}
    return build_static_candidate_analysis(context, nodes, edges, official, readiness)


def _javascript_json_values(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {key: _javascript_json_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_javascript_json_values(item) for item in value]
    return value


def _serialize(artifact: dict) -> bytes:
    compatible = _javascript_json_values(artifact)
    return (json.dumps(compatible, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def generate_static_candidate_analyses(repo_root: Path, output_root: Path, *, check: bool = False) -> dict:
    """Generate or check all canonical analysis files and return deterministic hashes."""
    root = Path(repo_root).resolve()
    output = Path(output_root).resolve()
    receipt = {"source_analysis_authority": "src/analysis", "viewer_analysis_mode": "STATIC_READ_ONLY", "cities": {}}
    if not check:
        output.mkdir(parents=True, exist_ok=True)
    generated = {}
    for city in CITY_INPUTS:
        artifact = _artifact_for(root, city)
        validate_static_candidate_analysis(root, artifact)
        payload = _serialize(artifact)
        destination = output / f"{city['id']}.json"
        if check:
            if not destination.exists() or destination.read_bytes().replace(b"\r\n", b"\n") != payload:
                raise ValueError(f"stale committed static analysis: {city['id']}")
        else:
            destination.write_bytes(payload)
        receipt["cities"][city["id"]] = {"bytes": len(payload), "sha256": sha256(payload).hexdigest()}
        generated[city["id"]] = payload
    manifest_payload = _serialize({
        "schema_version": "1.0.0",
        "source_analysis_authority": "src/analysis",
        "generator": "scripts/build_candidate_analysis.py",
        "artifacts": {
            f"{city_id}.json": canonical_text_sha256_bytes(payload)
            for city_id, payload in sorted(generated.items())
        },
    })
    manifest_path = output / "manifest.json"
    if check:
        if not manifest_path.exists() or manifest_path.read_bytes().replace(b"\r\n", b"\n") != manifest_payload:
            raise ValueError("stale committed static analysis manifest")
    else:
        manifest_path.write_bytes(manifest_payload)
    receipt["manifest"] = {"bytes": len(manifest_payload), "sha256": sha256(manifest_payload).hexdigest()}
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output_root or args.repo_root / "viewer/public/data/analysis"
    receipt = generate_static_candidate_analyses(args.repo_root, output, check=args.check)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
