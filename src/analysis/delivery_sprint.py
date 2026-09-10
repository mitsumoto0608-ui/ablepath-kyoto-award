"""Fail-closed delivery-sprint contracts and source-side spatial analysis."""

from __future__ import annotations

from collections import defaultdict
import math
import re
from typing import Any

from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union


_CITY_CRS = {"kyoto_kiyomizu": "EPSG:6674", "kyoto_arashiyama": "EPSG:6674", "fujisawa_enoshima": "EPSG:6677"}
_FORBIDDEN_HAZARD_FIELDS = {"official_closure", "damage_state", "debris_present", "setback_m", "passability", "safe_route"}
_UNAPPROVED_F1_DETAILS = {"tolerance", "station_interval", "long_edge_split", "unknown_rules"}
_DECISION_ZIP_SHA256 = "d76c60e8285931bf61ffde05a48fda20cc107c845b89a6f83d42c80528911a9f"
_DECISION_HASHES = {
    "F1_F6_DECISION_STATE.json": "101083468c4824de45260c1696a75786ce17e5996db1570eda14d1b50241c817",
    "F1_F6_ONE_PAGE_DECISION_FORM.md": "fa3aac71f5c8da692276f371170e76fc37a5abbdbf1f16f55da828bc9940b46d",
    "F1_SETBACK_CRS_DECISION.md": "bd7e58209e530be572a45ea22d300857ab32a5dd406c860638def31417562089",
    "F2_DAMAGE_MAPPING_DECISION.md": "55666534e2d531da428806ebda339c2ea5de822bee62c4a3f114cfef94ae5061",
    "F3_DEBRIS_REALIZATION_DECISION.md": "ff0ceba3028397356947626d215939ec6d6b7cf64ae6d2aeca4a35003051bae1",
    "F4_HEIGHT_PROVENANCE_DECISION.md": "52483cf23406fc0a8daea155d5902e8d2351b8ffb4b93ee925475955b706eb2b",
    "F5_DEFERRED_FIELD_MEASUREMENT_PLAN.md": "eb1ac0c8ef38504ee989bb7c9fa1d55f244c40ab93da1a69b58d3e146b7c62a3",
    "F6_LICENSE_SCOPE_BINDING.md": "30e4b4c865f2769a4c3a280d89187752817a7f8ae6e40383f644779786cf5c31",
    "POST_DECISION_IMPLEMENTATION_PLAN.md": "0f983ba84cc07101091e240e5df49cb4c69e705ed65800daa2b800122c1193a4",
    "ROLLBACK.md": "6b93637acbf9b06b026e37c54861140c365e74b4715d4c7054280ff3ecd21087",
}
_SHA256 = re.compile(r"[0-9a-f]{64}")
_PUBLIC_GIT_AMENDMENT_SHA256 = "1df66ac07ba476a2a2a412f034775559879206a685d6abb27fbe69e7e915f4f6"


def _finite_coordinates(value: Any) -> bool:
    if isinstance(value, (list, tuple)):
        return bool(value) and all(_finite_coordinates(item) for item in value)
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def select_intersecting_source_features(features: list[dict[str, Any]], coverage_feature: dict[str, Any], *, source_crs: str, coverage_crs: str) -> list[dict[str, Any]]:
    """Select whole source features after an explicit CRS transform of the AOI."""
    coverage = shape(coverage_feature["geometry"])
    if source_crs != coverage_crs:
        convert = Transformer.from_crs(coverage_crs, source_crs, always_xy=True, allow_ballpark=False).transform
        coverage = transform(convert, coverage)
    return [feature for feature in features if shape(feature["geometry"]).intersects(coverage)]


def validate_f1_f6_binding(binding: dict[str, Any]) -> dict[str, Any]:
    """Validate the narrow human-approved policy binding without promoting values."""
    if not isinstance(binding, dict):
        raise ValueError("F1-F6 binding must be an object")
    if binding.get("authority") != "USER_EXPLICIT_APPROVAL_IN_CODEX_SESSION":
        raise ValueError("F1-F6 binding authority is not the approved session receipt")
    if binding.get("source_zip_sha256") != _DECISION_ZIP_SHA256:
        raise ValueError("F1-F6 canonical decision ZIP hash is required")
    if binding.get("source_sha256") != _DECISION_HASHES["F1_F6_DECISION_STATE.json"] or binding.get("source_artifacts") != _DECISION_HASHES:
        raise ValueError("F1-F6 exact decision artifact hashes are required")
    if any(binding.get(key) is not expected for key, expected in {
        "policy_approved": True,
        "policy_bound": True,
        "binding_implemented": True,
        "production_value_implementation": False,
        "value_available": False,
    }.items()):
        raise ValueError("policy approval/binding must remain separate from value availability")
    f1 = binding.get("f1", {})
    if f1.get("target") != "FIELD_CONFIRMED_WALKABLE_SPACE_BOUNDARY_TO_TARGET_BUILDING_FRONTAGE_GEOMETRY_SHORTEST_HORIZONTAL_DISTANCE":
        raise ValueError("unapproved setback target")
    if f1.get("metric_crs") != {"kyoto": "EPSG:6674", "fujisawa": "EPSG:6677"}:
        raise ValueError("unapproved metric CRS binding")
    if set(f1.get("unapproved_details", [])) != _UNAPPROVED_F1_DETAILS:
        raise ValueError("unapproved F1 details were lost or changed")
    if binding.get("f2", {}).get("concrete_taxonomy_mapping_approved") is not False:
        raise ValueError("concrete F2 taxonomy mappings remain unapproved")
    if binding.get("f1", {}).get("rejected_inputs") != ["CANDIDATE_CENTERLINE", "CENTROID_DISTANCE", "ARBITRARY_NEAREST_GEOMETRY"]:
        raise ValueError("F1 rejected inputs changed")
    if binding.get("f2", {}).get("eligible_source_classes") != ["ACCEPTED_OBSERVED_POST_EVENT_STATE", "ACCEPTED_OFFICIAL_ASSET_LEVEL_SCENARIO_STATE"]:
        raise ValueError("F2 eligible source classes changed")
    if binding.get("f3", {}).get("eligible_source_classes") != ["ACCEPTED_OBSERVED_BOOL", "ACCEPTED_OFFICIAL_ASSET_LEVEL_BOOL"]:
        raise ValueError("F3 eligible source classes changed")
    if binding.get("f3", {}).get("probability_realization") != "EXPERIMENTAL_ONLY":
        raise ValueError("F3 probability realization must remain experimental")
    f4 = binding.get("f4", {})
    if f4.get("methods_must_remain_distinct") is not True or f4.get("height_values_accepted") is not False or f4.get("conditional_candidates") != ["KYOTO_POINT_CLOUD_MEDIAN", "FUJISAWA_AERIAL_PHOTOGRAMMETRY_MAXIMUM"] or f4.get("excluded") != ["UNIFORM_3M", "NEGATIVE_9999_SENTINEL"]:
        raise ValueError("F4 conditional candidates are not accepted M7 values")
    f5 = binding.get("f5", {})
    if f5.get("field_measurement_deferred") is not True or f5.get("measurement_value_count") != 0:
        raise ValueError("field measurement remains deferred with zero values")
    f6 = binding.get("f6", {})
    if any(f6.get(key) is not True for key in ("private_internal", "internal_rc", "public_git")):
        raise ValueError("approved internal/public-Git scope is incomplete")
    if any(f6.get(key) is not False for key in ("private_git", "public_rc", "public_demo")):
        raise ValueError("public Git amendment must not authorize private Git, public RC, or public demo")
    amendment = binding.get("scope_amendment", {})
    if amendment != {
        "path": "reports/PUBLIC_GIT_SCOPE_AMENDMENT_20260910.json",
        "sha256": _PUBLIC_GIT_AMENDMENT_SHA256,
        "authority": "USER_EXPLICIT_OWNER_INSTRUCTION_IN_CODEX_SESSION",
    }:
        raise ValueError("current F6 public Git amendment is missing or stale")
    if binding.get("m7_ready_count") != 0 or binding.get("m7_computed_count") != 0:
        raise ValueError("decision binding must not promote M7 readiness or computation")
    if any(binding.get(key) is not False for key in ("safe_route_claim", "accessibility_claim", "passability_claim", "admin_validated", "public_release_ready")):
        raise ValueError("decision binding contains a forbidden claim")
    return binding


def _validate_layer(layer: dict[str, Any]) -> None:
    required = ("source_id", "source_revision", "source_sha256", "source_url", "license_status", "limitations", "scenario_id", "source_crs", "coverage", "coverage_crs", "coverage_evidence", "class_field", "features")
    if any(key not in layer for key in required):
        raise ValueError("hazard layer contract is incomplete")
    if layer["source_crs"] not in {"EPSG:6668", "EPSG:4612"}:
        raise ValueError("hazard source CRS must be explicit EPSG:6668 or EPSG:4612")
    if layer["coverage_crs"] != "EPSG:4326":
        raise ValueError("hazard AOI coverage CRS must remain explicit EPSG:4326")
    if not isinstance(layer["source_sha256"], str) or not _SHA256.fullmatch(layer["source_sha256"]):
        raise ValueError("hazard source SHA-256 is invalid")
    if any(not isinstance(layer[key], str) or not layer[key] or "\0" in layer[key] for key in ("source_id", "source_revision", "scenario_id")):
        raise ValueError("hazard source/scenario identity is invalid")
    if not isinstance(layer["source_url"], str) or not layer["source_url"].startswith("https://") or not layer["license_status"] or not layer["limitations"]:
        raise ValueError("hazard source URL/license/limitations are invalid")
    if (
        ("PUBLIC_" in layer["license_status"] or layer["license_status"] == "CC-BY")
        and (
            not isinstance(layer.get("license_url"), str)
            or not layer["license_url"].startswith("https://")
            or not isinstance(layer.get("attribution"), str)
            or not layer["attribution"]
        )
    ):
        raise ValueError("public hazard derivative lacks license URL or attribution")
    if shape(layer["coverage"]["geometry"]).geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("hazard coverage must be polygonal")
    evidence = layer["coverage_evidence"]
    if evidence.get("status") != "FULL_SOURCE_SCAN_INTERSECTED_WITH_BOUND_AOI" or not isinstance(evidence.get("selection_sha256"), str) or not _SHA256.fullmatch(evidence["selection_sha256"]):
        raise ValueError("hazard AOI coverage requires a hash-bound full-source scan")
    for feature in layer["features"]:
        props = feature.get("properties", {})
        if _FORBIDDEN_HAZARD_FIELDS.intersection(props):
            raise ValueError("hazard evidence contains an unsafe operational inference")
        geometry = shape(feature.get("geometry", {}))
        if geometry.is_empty or not _finite_coordinates(feature.get("geometry", {}).get("coordinates")):
            raise ValueError("hazard feature geometry is empty or non-finite")
        if layer["class_field"] not in props or props[layer["class_field"]] is None or not props.get("source_feature_id"):
            raise ValueError("hazard feature lacks source class or stable feature identity")


def build_edge_hazard_exposure(
    city_id: str,
    edges: list[dict[str, Any]],
    layers: list[dict[str, Any]],
    target_crs: str,
    edge_crs: str = "EPSG:4326",
) -> list[dict[str, Any]]:
    """Intersect candidate edges per official scenario; never derive operational state."""
    if _CITY_CRS.get(city_id) != target_crs:
        raise ValueError("target metric CRS does not match the approved city policy")
    rows: list[dict[str, Any]] = []
    for layer in layers:
        _validate_layer(layer)
        hazard_project = Transformer.from_crs(layer["source_crs"], target_crs, always_xy=True, allow_ballpark=False).transform
        coverage_project = Transformer.from_crs(layer["coverage_crs"], target_crs, always_xy=True, allow_ballpark=False).transform
        edge_project = Transformer.from_crs(edge_crs, target_crs, always_xy=True, allow_ballpark=False).transform
        coverage = transform(coverage_project, shape(layer["coverage"]["geometry"]))
        features = [(transform(hazard_project, shape(feature["geometry"])).intersection(coverage), feature["properties"]) for feature in layer["features"]]
        for edge in edges:
            edge_id = edge.get("properties", {}).get("edge_id")
            line_source = shape(edge.get("geometry", {}))
            if not edge_id or line_source.geom_type != "LineString":
                raise ValueError("candidate edge must have an ID and LineString geometry")
            line = transform(edge_project, line_source)
            if not line.intersects(coverage):
                relation = "OUTSIDE_COVERAGE"
                canonical_relation = "OUTSIDE_COVERAGE"
                coverage_status = "OUTSIDE_KNOWN_COVERAGE"
                overlap_length = None
                reason = "Candidate edge is outside the declared source coverage; overlap is unknown, not zero."
                matched: list[tuple[Any, dict[str, Any]]] = []
            elif not coverage.covers(line):
                relation = "PARTIAL_COVERAGE"
                canonical_relation = "NODATA_OR_UNRESOLVED"
                coverage_status = "PARTIAL_KNOWN_COVERAGE"
                overlap_length = None
                reason = "Candidate edge is only partly inside declared source coverage; no complete-edge overlap value is reported."
                matched = []
            else:
                coverage_status = "WITHIN_KNOWN_COVERAGE"
                matched = [(geometry, props) for geometry, props in features if line.intersects(geometry)]
                positive = [line.intersection(geometry) for geometry, _ in matched if line.intersection(geometry).length > 0]
                intersection = unary_union(positive) if positive else line.intersection(unary_union([geometry for geometry, _ in matched])) if matched else line.intersection(coverage).difference(line.intersection(coverage))
                if positive:
                    relation = "INTERSECTS"
                    canonical_relation = "INTERSECTS"
                    overlap_length = intersection.length
                    reason = "Metric overlap is computed only within complete declared coverage."
                elif matched:
                    relation = "TOUCHES"
                    canonical_relation = "BOUNDARY_ONLY"
                    overlap_length = 0.0
                    reason = "Source geometry touches the candidate edge but has zero metric line overlap."
                else:
                    relation = "ZERO_OVERLAP_WITHIN_KNOWN_COVERAGE"
                    canonical_relation = "NO_INTERSECTION_WITHIN_VERIFIED_COVERAGE"
                    overlap_length = 0.0
                    reason = "No source geometry overlaps an edge wholly inside declared coverage."
            rows.append({
                "city_id": city_id,
                "edge_id": edge_id,
                "scenario_id": layer["scenario_id"],
                "relation": relation,
                "canonical_relation": canonical_relation,
                "coverage_status": coverage_status,
                "overlap_length_m": overlap_length,
                "metric_crs": target_crs,
                "source_id": layer["source_id"],
                "source_revision": layer["source_revision"],
                "source_sha256": layer["source_sha256"],
                "source_feature_ids": sorted({props["source_feature_id"] for _, props in matched}),
                "source_classes": sorted({str(props[layer["class_field"]]) for _, props in matched}),
                "official_closure": None,
                "damage_state": None,
                "debris_present": None,
                "reason": reason,
                "interpretation": "Official hazard overlap evidence only; no closure, passability, safety, damage, or debris state is derived.",
            })
    keys = [(row["edge_id"], row["scenario_id"], row["source_id"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate edge/scenario/source exposure tuple")
    return sorted(rows, key=lambda row: (row["edge_id"], row["scenario_id"], row["source_id"]))


def build_review_checklists(
    city_id: str,
    path_matrix: dict[str, dict[str, Any]],
    exposures: list[dict[str, Any]],
    terrain: dict[str, Any],
    facility: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Build static review checklists; the viewer may only filter and serialize them."""
    by_edge: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in exposures:
        by_edge[row["edge_id"]].append(row)
    result: dict[str, dict[str, Any]] = {}
    terrain_summary = {
        key: value for key, value in terrain.items()
        if key not in {"samples", "edge_samples"}
    }
    for key, path in sorted(path_matrix.items()):
        connected = path.get("status") == "CONNECTED"
        result[key] = {
            "checklist_id": f"{city_id}:{key}:review-v1",
            "city_id": city_id,
            "path_key": key,
            "path_status": path.get("status"),
            "status": "READY_FOR_REVIEW" if connected else "SUPPORTED_UNCOMPUTED",
            "candidate_distance": path.get("geometric_length"),
            "candidate_distance_unit": path.get("unit"),
            "path_reason": path.get("reason"),
            "terrain": terrain_summary,
            "facility": {"status": facility.get("status"), "record_count": facility.get("record_count", 0), "reason": facility.get("reason"), "record_ids": sorted(record["facility_record_id"] for record in facility.get("records", []))},
            "rows": [
                {
                    "edge_id": edge_id,
                    "hazard_refs": [f"{hazard['edge_id']}\0{hazard['scenario_id']}\0{hazard['source_id']}" for hazard in by_edge.get(edge_id, [])],
                    "terrain_status": terrain.get("status"),
                    "terrain_sampled": terrain.get("sampled", terrain.get("elevation_sampled", False)),
                    "terrain_reason": terrain.get("reason"),
                    "terrain_sample_ids": list(terrain.get("edge_samples", {}).get(edge_id, [])),
                    "facility_status": facility.get("status"),
                    "owner_candidate_types": ["HAZARD_DATA_STEWARD", "TERRAIN_DATA_STEWARD", "FACILITY_OPERATOR", "M6_M7_CONTRACT_OWNER"],
                    "unknowns": [
                        "accessibility",
                        "passability",
                        "current_facility_operation",
                        "M6",
                        "M7",
                    ],
                }
                for edge_id in path.get("edge_ids", [])
            ] if connected else [],
            "safe_route_claim": False,
            "accessibility_claim": False,
            "admin_validated": False,
        }
    return result
