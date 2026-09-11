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
    canonical_text_bytes,
    canonical_text_sha256,
    canonical_text_sha256_bytes,
    validate_static_candidate_analysis,
)
from src.analysis.delivery_sprint import build_edge_hazard_exposure, build_review_checklists, validate_f1_f6_binding


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


def _coverage(root: Path, city_id: str) -> dict:
    filename = {
        "kyoto_kiyomizu": "aoi_kyoto_kiyomizu_gion_v1.geojson",
        "kyoto_arashiyama": "aoi_kyoto_arashiyama_v1.geojson",
        "fujisawa_enoshima": "aoi_fujisawa_enoshima_v1.geojson",
    }[city_id]
    return _load_json(root / "inputs/staging/PHASE4-MULTICITY-DATA-ACQUISITION/city_aoi" / filename)["features"][0]


def _normalized_hazard_layers(root: Path, city_id: str) -> tuple[list[dict], list[dict]]:
    binding = _load_json(root / "inputs/staging/DELIVERY-SPRINT-V1/source_bindings.json")
    coverage = _coverage(root, city_id)
    layers = []
    display_features = []
    if city_id.startswith("kyoto_"):
        group = "kiyomizu_gion" if city_id == "kyoto_kiyomizu" else "arashiyama"
        flood_path = root / f"inputs/staging/KYOTO-OFFICIAL-PARITY-V1/a31b_{group}_display.geojson"
        flood_features = []
        for feature in _load_json(flood_path)["features"]:
            props = feature["properties"]
            class_key = next(key for key in props if key.startswith("A31b_"))
            normalized = {**feature, "properties": {**props, "source_feature_id": f"{props['_ablepath_layer_id']}:{props['_ablepath_source_feature_index']}", "source_class": f"{class_key}={props[class_key]}", "source_id": "nlni_a31b_2025_kyoto_flood", "scenario_id": f"A31B_FLOOD_2025_{group}"}}
            flood_features.append(normalized)
        for layer_id in ("A31b-10", "A31b-20", "A31b-30", "A31b-41", "A31b-42"):
            selected = [feature for feature in flood_features if feature["properties"]["_ablepath_layer_id"] == layer_id]
            layers.append({"source_id": "nlni_a31b_2025_kyoto_flood", "source_revision": "2025", "source_sha256": "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c", "source_url": "https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip", "license_status": "PERMITTED_WITH_OBLIGATIONS", "limitations": "Hazard overlap is evidence only and does not imply closure, passability, damage, debris, accessibility, or safety.", "scenario_id": f"A31B_FLOOD_2025_{group}_{layer_id}", "source_crs": "EPSG:6668", "coverage": coverage, "coverage_crs": "EPSG:4326", "coverage_evidence": {"status": "FULL_SOURCE_SCAN_INTERSECTED_WITH_BOUND_AOI", "selection_sha256": _hash(flood_path)}, "class_field": "source_class", "features": selected})
        landslide_path = root / f"inputs/staging/DELIVERY-SPRINT-V1/{city_id}/landslide_aoi_selection.geojson"
        landslide_features = _load_json(landslide_path)["features"]
        for layer_id in ("g_d_rzone", "g_d_yzone", "g_j_yzone", "g_k_rzone", "g_k_yzone"):
            selected = []
            for feature in landslide_features:
                if feature["properties"]["source_layer_id"] != layer_id:
                    continue
                props = feature["properties"]
                normalized = {**feature, "properties": {**props, "source_class": f"NATURALC={props['NATURALC']};KINDC={props['KINDC']}", "source_id": "kyoto_city_landslide_gis_20260830", "scenario_id": f"KYOTO_LANDSLIDE_2026_{layer_id}"}}
                selected.append(normalized)
                display_features.append(normalized)
            source = binding["sources"]["kyoto_landslide"]
            layers.append({"source_id": source["source_id"], "source_revision": source["revision"], "source_sha256": source["sha256"], "source_url": "https://www.bousaimap.city.kyoto.lg.jp/GisDownload", "license_status": source["license_scope"], "license_url": source["license_url"], "license_receipt_sha256": source["license_receipt_sha256"], "attribution": source["attribution"], "limitations": "Public reuse requires the recorded Kyoto City attribution. Hazard overlap is evidence only and does not imply closure, passability, damage, debris, accessibility, or safety.", "scenario_id": f"KYOTO_LANDSLIDE_2026_{layer_id}", "source_crs": "EPSG:6668", "coverage": coverage, "coverage_crs": "EPSG:4326", "coverage_evidence": {"status": "FULL_SOURCE_SCAN_INTERSECTED_WITH_BOUND_AOI", "selection_sha256": _hash(landslide_path)}, "class_field": "source_class", "features": selected})
    else:
        path = root / "inputs/staging/DELIVERY-SPRINT-V1/fujisawa_enoshima/tsunami_a40_aoi_selection.geojson"
        selected = []
        for feature in _load_json(path)["features"]:
            props = feature["properties"]
            normalized = {**feature, "properties": {**props, "source_class": f"A40_002={props.get('A40_002')};A40_003={props.get('A40_003')}", "source_id": "nlni_a40_2020_kanagawa_tsunami", "scenario_id": "A40_TSUNAMI_2020"}}
            selected.append(normalized)
            display_features.append(normalized)
        source = binding["sources"]["fujisawa_tsunami"]
        layers.append({"source_id": source["source_id"], "source_revision": source["revision"], "source_sha256": source["sha256"], "source_url": "https://nlftp.mlit.go.jp/ksj/gml/data/A40/A40-20/A40-20_14_GML.zip", "license_status": source["license_scope"], "license_url": source["license_url"], "license_receipt_sha256": source["license_receipt_sha256"], "attribution": source["attribution"], "limitations": "Public redistribution is allowed for Kanagawa under the recorded 2020 A40 terms with attribution. Hazard overlap is evidence only and does not imply closure, passability, damage, debris, accessibility, or safety.", "scenario_id": "A40_TSUNAMI_2020", "source_crs": "EPSG:6668", "coverage": coverage, "coverage_crs": "EPSG:4326", "coverage_evidence": {"status": "FULL_SOURCE_SCAN_INTERSECTED_WITH_BOUND_AOI", "selection_sha256": _hash(path)}, "class_field": "source_class", "features": selected})
        public = _load_json(root / "inputs/staging/PUBLIC-GIT-DEM-FUJISAWA-V1/official_evidence.json")["fujisawa_hazards"]
        if public.get("license_status") != "CC-BY" or public.get("closure_derived") is not False or public.get("damage_or_debris_inferred") is not False:
            raise ValueError("public Fujisawa hazard derivative contract is invalid")
        layers.extend(public["layers"])
        display_features.extend(public["display_features"])
    return layers, display_features


def _official_evidence(root: Path, city_id: str, edges: list[dict]) -> tuple[dict, list[dict]]:
    promotion = _load_json(root / "reports/OFFICIAL_LOCAL_ARTIFACT_PROMOTION_V2.json")
    kyoto = _load_json(root / "reports/KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json") if city_id.startswith("kyoto_") else None
    plateau = _load_json(root / "reports/PLATEAU_BUILDING_EVIDENCE_V2.json")
    m7 = _load_json(root / "reports/M7_REAL_EDGE_STATUS.json")
    m7_all = _load_json(root / "reports/M7_ALL_EDGE_EVIDENCE_READINESS.json")
    public_evidence = _load_json(root / "inputs/staging/PUBLIC-GIT-DEM-FUJISAWA-V1/official_evidence.json")
    dem_city = public_evidence["dem"]["cities"][city_id]
    # Keep the exhaustive, verbose raw-to-cell receipt in staging.  The static
    # viewer artifact carries only the fields needed to validate and display a
    # sample, avoiding thousands of copies of invariant source metadata.
    terrain_sample_fields = {
        "sample_id", "sample_role", "node_id", "edge_id",
        "vertex_index", "product", "query_longitude", "query_latitude",
        "unit", "member_sha256", "status", "elevation_m", "surface_type",
        "reason", "step_inferred", "cross_slope_inferred",
    }
    terrain_samples = [
        {
            key: value
            for key, value in sample.items()
            if key in terrain_sample_fields and (key != "reason" or sample.get("status") != "SAMPLED_NATIVE_CELL")
        }
        for sample in dem_city["samples"]
    ]
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
    for source_product in dem_city["products"]:
        product = dict(source_product)
        product_samples = [sample for sample in terrain_samples if sample["product"] == product["product"]]
        null_samples = [sample for sample in product_samples if sample["elevation_m"] is None]
        product.update({
            "sample_record_count": len(product_samples),
            "unique_coordinate_count": len({(sample["query_longitude"], sample["query_latitude"]) for sample in product_samples}),
            "null_record_count": len(null_samples),
            "null_coordinate_count": len({(sample["query_longitude"], sample["query_latitude"]) for sample in null_samples}),
        })
        terrain_products.append(product)
    null_terrain_samples = [sample for sample in terrain_samples if sample["elevation_m"] is None]
    terrain_summary = {
        "sample_record_count": len(terrain_samples),
        "unique_coordinate_count": len({(sample["query_longitude"], sample["query_latitude"]) for sample in terrain_samples}),
        "numeric_record_count": len(terrain_samples) - len(null_terrain_samples),
        "null_record_count": len(null_terrain_samples),
        "null_coordinate_count": len({(sample["query_longitude"], sample["query_latitude"]) for sample in null_terrain_samples}),
    }
    sample_ids_by_edge = {}
    for sample in terrain_samples:
        if sample.get("sample_role") == "EDGE_VERTEX":
            sample_ids_by_edge.setdefault(sample["edge_id"], []).append(sample["sample_id"])
    terrain_edge_samples = {
        edge["properties"]["edge_id"]: sorted(
            sample_ids_by_edge.get(edge["properties"]["edge_id"], []),
        )
        for edge in edges
    }
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
        connected_by_scenario = {layer["scenario_id"]: layer for layer in public_evidence["fujisawa_hazards"]["layers"]}
        scenarios.extend({
            "dataset_id": layer["scenario_id"], "scenario": layer["scenario_label"], "layer_kind": layer["layer_kind"],
            "official_source": "Kanagawa Prefecture earthquake damage estimation study (March 2025)",
            "official_url": layer["source_url"], "version_date": layer["source_revision"], "license_review": layer["license_status"],
            **({"license_note": layer["license_note"]} if layer.get("license_note") else {}),
            "dataset_publication_date": layer["dataset_publication_date"],
            "definition_resource_id": layer["definition_resource_id"], "definition_sha256": layer["definition_sha256"],
            "crs_sidecar_sha256": layer["crs_sidecar_sha256"],
            "source_member_id": layer["source_member_id"], "source_member_receipt": layer["source_member_receipt"],
            "validation_result": "SOURCE_SHA_CRS_DEFINITION_AND_AOI_SELECTION_BOUND", "crs": layer["source_crs"],
            "bounds_native": "AOI_SELECTION_FROM_FULL_SOURCE_SCAN", "aoi_scope": "enoshima_katase",
            **({"crs_closure": layer["crs_closure"]} if layer.get("crs_closure") else {}),
            "status": "SOURCE_SIDE_EDGE_OVERLAP_CONNECTED", "connected": True,
            "reason": "Official source mesh geometry is connected as source-side overlap evidence only; no operational or safety state is derived.",
        } for layer in connected_by_scenario.values())
    if city_id == "fujisawa_enoshima":
        receipt = _load_json(root / f"cities/{city_id}/facilities/official/facility_source_receipt.json")
        if (
            receipt["row_counts"]["enoshima_katase"] != 57
            or receipt["license_status"] != "LICENSE_REVIEW_REQUIRED"
            or receipt["public_payload_files_present"] is not False
            or receipt["provider_redistribution_permission_bound"] is not False
        ):
            raise ValueError("Fujisawa facility receipt changed without public-scope review")
        # Row-bearing derivatives are retained outside the current public Git
        # tip. Only their non-row metadata receipt is used here.
        records = []
        facility = {
            "status": "NOT_CONNECTED_PUBLIC_GIT_LICENSE_REVIEW_REQUIRED",
            "geometry_status": "ADDRESS_ONLY",
            "marker_policy": "TABLE_ONLY_NO_MARKERS_OR_GEOCODING",
            "record_count": len(records),
            "records": records,
            "source_catalog": {
                "fujisawa_webgis_toilets_accessibility": {
                    "source_url": "https://webgis.alandis.jp/fujisawa14/portal/index.html",
                    "license_status": receipt["license_status"],
                    "published_at": None,
                    "valid_as_of": receipt["valid_as_of"],
                    "acquired_at": receipt["accessed_at"],
                    "temporal_status_reason": "Published, valid-as-of, and acquisition timestamps are unavailable in the bound receipt; currentness is not inferred.",
                    "limitations": receipt["semantic_guard"],
                    "source_sha256": receipt["raw_sha256"],
                    "allowed_attribute_keys": ["ostomate_detail_available"],
                }
            },
            "source_receipt_sha256": _hash(root / f"cities/{city_id}/facilities/official/facility_source_receipt.json"),
            "reason": "The 57-row address-only derivative is excluded from the current public Git tip, viewer, and CI artifacts because provider redistribution permission is not bound. Historical Git reachability is recorded; no records, coordinates, markers, geocoding, or current state are inferred.",
        }
    elif city_truth:
        category_status = _load_json(parity_root / "facility_category_status.json")
        records = [row for row in _load_json(parity_root / "facility_records.json")["records"] if row["aoi_group"] == parity_group]
        source_fields_path = root / "inputs/staging/DELIVERY-SPRINT-V1/kyoto_facility_source_fields.json"
        source_fields_payload = _load_json(source_fields_path)
        if source_fields_payload.get("silent_geocoding") is not False or source_fields_payload.get("current_operation_inferred") is not False:
            raise ValueError("facility source attributes contain an inferred location or operation state")
        source_fields = {row["facility_record_id"]: row for row in source_fields_payload["records"]}
        if any(record["facility_record_id"] not in source_fields for record in records):
            raise ValueError("facility original-source field binding is incomplete")
        records = [{**record, **source_fields[record["facility_record_id"]]} for record in records]
        records = [
            {
                **record,
                "source_attribute_entries": [
                    [key, record["source_attributes"][key]]
                    for key in sorted(record["source_attributes"])
                ],
            }
            for record in records
        ]
        categories = {}
        for category, value in category_status["categories"].items():
            categories[category] = {**value, "record_count": len([row for row in records if row["category"] == category]) if value["map_connected"] else 0, "count_scope": parity_group}
        point_path = parity_root / f"facility_points_{parity_group}.geojson"
        receipt_by_id = {
            row["dataset_id"]: row
            for row in _load_json(parity_root / "source_receipts.json")["sources"]
        }
        allowed_keys = {
            "kyoto_emergency_shelters_r80818": ["administrative_district", "community_disaster_group", "flood_evacuation_target_districts", "landslide_evacuation_target_districts", "official_number"],
            "kyoto_designated_shelters_r80818": ["administrative_district", "community_disaster_group", "listed_maximum_capacity", "official_number"],
            "kyoto_public_toilets_00307": ["administrative_district", "listed_baby_support", "listed_fixture_count_text", "listed_opening_hours", "listed_ostomate_support", "listed_washlet_support", "listed_western_style", "listed_wheelchair_support", "official_map_number", "official_page_url"],
        }
        facility_source_catalog = {}
        for source_id, keys in allowed_keys.items():
            source = receipt_by_id[source_id]
            facility_source_catalog[source_id] = {
                "source_url": source["official_url"],
                "license_status": source.get("license", "LICENSE_REVIEW_REQUIRED"),
                "published_at": None,
                "valid_as_of": source["version"],
                "acquired_at": None,
                "temporal_status_reason": "The bound receipt identifies the listed revision/valid-as-of value; publication and acquisition timestamps are not separately recorded.",
                "limitations": "Official source row only; current opening, entrance, accessibility, safety, and disaster usability are not inferred.",
                "source_sha256": source["sha256"],
                "allowed_attribute_keys": keys,
            }
        facility = {"status": "PARTIAL_3_OF_5_CATEGORIES_SOURCE_COORDINATES_AND_ORIGINAL_ATTRIBUTES", "geometry_status": "SOURCE_PROVIDED_LONGITUDE_LATITUDE", "marker_policy": "SOURCE_COORDINATES_ONLY_NO_GEOCODING", "record_count": len(records), "records": records, "source_catalog": facility_source_catalog, "source_fields_sha256": _hash(source_fields_path), "categories": categories, "display_layer": {"data_path": f"./data/official/facility_points_{parity_group}.geojson", "artifact_sha256": _hash(point_path), "copied_sha256": _hash(point_path), "feature_count": len(_load_json(point_path)["features"])}, "reason": "Three official categories are displayed from source-provided longitude/latitude and exact original-source fields. Listed capacity, hazard applicability, opening hours, and equipment are source attributes, not current operation, entrance, accessibility, safety, or disaster usability; those remain UNKNOWN. Emergency-open-space and temporary-stay rows remain metadata-only."}
    else:
        facility = {"status": "NOT_CONNECTED", "record_count": 0, "reason": "No official facility evidence is connected."}
    plateau_inventory = [row for row in _csv_rows(root / "inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/PLATEAU_BUILDING_AOI_INVENTORY.csv") if row["city_id"] == city_id] if city_truth else []
    kyoto_pilot_edges = [row for row in kyoto_pilot["edges"] if row["aoi_group"] == parity_group] if city_truth else []
    flood_path = parity_root / f"a31b_{parity_group}_display.geojson" if parity_group else None
    flood_data = _load_json(flood_path) if flood_path else None
    source_hashes = {key: _hash(path) for key, path in authoritative_report_paths(root, city_id).items()}
    terrain_reason = "No terrain product has been connected to this city analysis."
    normalized_layers, delivery_display_features = _normalized_hazard_layers(root, city_id)
    target_crs = "EPSG:6677" if city_id == "fujisawa_enoshima" else "EPSG:6674"
    edge_exposures = build_edge_hazard_exposure(city_id, edges, normalized_layers, target_crs, edge_crs="EPSG:4326")
    source_catalog = {
        layer["source_id"]: {
            "source_revision": layer["source_revision"],
            "source_sha256": layer["source_sha256"],
            "source_url": layer["source_url"],
            "license_status": layer["license_status"],
            "limitations": layer["limitations"],
            "license_url": layer.get("license_url"),
            "license_receipt_sha256": layer.get("license_receipt_sha256"),
            "attribution": layer.get("attribution"),
            "source_crs": layer["source_crs"],
            "dataset_publication_date": layer.get("dataset_publication_date"),
            "scenario_label": layer.get("scenario_label"),
            "layer_kind": layer.get("layer_kind"),
            "definition_resource_id": layer.get("definition_resource_id"),
            "definition_sha256": layer.get("definition_sha256"),
            "definition_resource_response_sha256": layer.get("definition_resource_response_sha256"),
            "crs_sidecar_sha256": layer.get("crs_sidecar_sha256"),
            "coverage_selection_sha256": layer["coverage_evidence"]["selection_sha256"],
            **({"source_member_id": layer["source_member_id"], "source_member_receipt": layer["source_member_receipt"]} if layer.get("source_member_id") else {}),
        }
        for layer in normalized_layers
    }
    connected_scenarios = sorted({row["scenario_id"] for row in edge_exposures})
    if city_truth:
        hazard_layers = [
            {**row, "status": "SOURCE_SIDE_EDGE_OVERLAP_CONNECTED", "connected": True, "artifact_status": "SOURCE_HASH_AND_EDGE_JOIN_BOUND", "reason": "Scenario-separated source-side edge overlap is connected; no operational or safety state is derived."}
            if row["layer"] in {"flood", "landslide"} else row
            for row in hazard_layers
        ]
    display_path = f"./data/official/{city_id}.delivery_hazards.geojson"
    delivery_layer = {"data_path": display_path, "artifact_sha256": None, "copied_sha256": None, "feature_count": len(delivery_display_features), "display_only": True}
    display_layers = [delivery_layer]
    if city_truth:
        display_layers.insert(0, {"data_path": f"./data/official/a31b_{parity_group}_display.geojson", "artifact_sha256": _hash(flood_path), "copied_sha256": _hash(flood_path), "feature_count": len(flood_data["features"]), "display_only": True})
    hazard_reason = "Official source geometry is connected to candidate edges as scenario-separated overlap evidence only; no CLOSED, FAIL, damage, debris, passability, or safety state is derived."
    official = {
        "source_status": promotion["status"],
        "source_hashes": source_hashes,
        "subareas": subareas,
        "terrain": {"status": "NATIVE_CELL_SAMPLES_CONNECTED", "reason": "GSI DEM1A and DEM5A are shown as separate exact native-cell samples; record counts and independent query locations are reported separately, with no interpolation, product precedence, step, or cross-slope inference.", "connected": True, "evidence_ui_connected": True, "elevation_sampled": True, "step_inferred": False, "cross_slope_inferred": False, "aoi_validation": parity_aoi["terrain"] if city_truth else None, "receipt_sha256": _hash(root / "inputs/staging/PUBLIC-GIT-DEM-FUJISAWA-V1/official_evidence.json"), **terrain_summary, "products": terrain_products, "samples": terrain_samples, "edge_samples": terrain_edge_samples},
        "hazard": {"status": "SOURCE_SIDE_EDGE_OVERLAP_CONNECTED", "reason": hazard_reason, "connected": True, "operational_state_connected": False, "display_connected": True, "display_feature_count": sum(layer["feature_count"] for layer in display_layers), "display_layers": display_layers, "connected_scenarios": connected_scenarios, "source_catalog": source_catalog, "edge_exposures": edge_exposures, "display_features": delivery_display_features, "numeric_serialization": "FULL_PYTHON_FLOAT_NO_DECISION_TOLERANCE", "decision_threshold_applied": False, "closure_derived": False, "damage_or_debris_inferred": False, "layers": hazard_layers, "scenarios": scenarios},
        "facility": facility,
        "plateau": {"status": "NOT_CONNECTED", "aoi_count": len(subareas), "aoi_scope": subareas, "inventory": plateau_inventory, "inventory_connected": bool(city_truth), "fallback": plateau["fallback"], "m7_evidence_ready_count": plateau["m7_evidence_ready_count"], "m7_computed_count": plateau["m7_computed_count"], "reason": "PLATEAU 2025 package SHA, EPSG:6697 axis semantics, stable IDs, roof-edge footprints, height provenance codes, and pilot-buffer mesh coverage are inventoried. Real 3D and M7 remain NOT_CONNECTED: setback is not frozen, field confirmation is deferred, and candidate building/height evidence is not promoted. Existing source-traceable candidate 2D is the deterministic fallback."},
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
    node_bytes = canonical_text_bytes(node_path.read_bytes())
    edge_bytes = canonical_text_bytes(edge_path.read_bytes())
    nodes = json.loads(node_bytes)["features"]
    edges = json.loads(edge_bytes)["features"]
    revisions = sorted({feature.get("properties", {}).get("revision_id") for feature in [*nodes, *edges] if feature.get("properties", {}).get("revision_id")})
    official, readiness = _official_evidence(root, city["id"], edges)
    context = {"city_id": city["id"], "source_artifact_ids": [city["nodes"], city["edges"]], "source_revision_ids": revisions, "input_sha256": sha256(node_bytes + b"\0" + edge_bytes).hexdigest(), "input_hashes": {"node_sha256": sha256(node_bytes).hexdigest(), "edge_sha256": sha256(edge_bytes).hexdigest()}, "snapshot_at": city["snapshot"], "source_id": city["source"]}
    artifact = build_static_candidate_analysis(context, nodes, edges, official, readiness)
    artifact["hazard_overlap"] = artifact["result"]["hazard_overlap"] = {
        "status": "CONNECTED_PRECOMPUTED_PER_EDGE",
        "value": None,
        "reason": "See scenario-separated edge_exposures and review_checklists; no operational state is derived.",
    }
    display_features = artifact["official_evidence"]["hazard"].pop("display_features")
    display_payload = _serialize({"type": "FeatureCollection", "features": display_features})
    display_sha = sha256(display_payload).hexdigest()
    artifact["official_evidence"]["hazard"]["display_layers"][-1].update({"artifact_sha256": display_sha, "copied_sha256": display_sha})
    artifact["review_checklists"] = build_review_checklists(city["id"], artifact["path_matrix"], official["hazard"]["edge_exposures"], {**official["terrain"], "sampled": official["terrain"]["elevation_sampled"]}, official["facility"])
    artifact["decision_binding"] = validate_f1_f6_binding(_load_json(root / "reports/F1_F6_DECISION_BINDING.json"))
    artifact["_delivery_hazard_payload"] = display_payload
    return artifact


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
    # These are machine-consumed static artifacts. Canonical compact JSON keeps
    # the largest city below the repository public-artifact size gate without
    # dropping any evidence rows or changing their values.
    return (json.dumps(compatible, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


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
        display_payload = artifact.pop("_delivery_hazard_payload")
        display_destination = output.parent / "official" / f"{city['id']}.delivery_hazards.geojson"
        if check:
            if not display_destination.exists() or display_destination.read_bytes().replace(b"\r\n", b"\n") != display_payload:
                raise ValueError(f"stale committed delivery hazard display: {city['id']}")
        else:
            display_destination.parent.mkdir(parents=True, exist_ok=True)
            display_destination.write_bytes(display_payload)
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
