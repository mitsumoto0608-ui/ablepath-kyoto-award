"""Deterministic Gate 6 pilot; computes M7 only for evidence-ready real edges."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from src.analysis.candidate_network import M7_API_FIELDS, assess_m7_readiness
from src.residual_width import calculate_residual_width


CITY_ARTIFACTS = {
    "kyoto_kiyomizu": "cities/kyoto_kiyomizu/graph/real/candidate_edges.geojson",
    "kyoto_arashiyama": "cities/kyoto_arashiyama/graph/walk_edges.real.geojson",
    "fujisawa_enoshima": "cities/fujisawa_enoshima/graph/candidate_walk_edges.real.geojson",
}
SELECTION_RULE = (
    "First five candidate edges by lexical stable edge_id. This bounded rule is "
    "deterministic and reviewable; it does not imply accessibility, safety, priority, "
    "or operational suitability."
)


def _edge_id(feature: dict) -> str:
    props = feature.get("properties", {}) if isinstance(feature, dict) else {}
    edge_id = props.get("edge_id")
    if not isinstance(edge_id, str) or not edge_id:
        raise ValueError("pilot feature must have a non-empty properties.edge_id")
    return edge_id


def _geometry_receipt(props: dict) -> dict:
    source_sha256 = props.get("source_sha256")
    return {
        "source_id": props.get("source_id"),
        "revision_id": props.get("revision_id"),
        "source_feature_id": props.get("source_feature_id"),
        "source_sha256": source_sha256 if isinstance(source_sha256, str) else None,
        "geometry_status": props.get("geometry_status"),
        "note": (
            "Geometry provenance is reported separately from M7 per-field evidence; "
            "it cannot make an edge M7-evidence-ready."
        ),
    }


def _require_source_traceable_real_geometry(props: dict, edge_id: str) -> None:
    if props.get("geometry_status") != "SOURCE_TRACEABLE_REAL":
        raise ValueError(f"pilot edge {edge_id} is not source-traceable real geometry")
    for field in ("revision_id", "source_feature_id"):
        value = props.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"pilot edge {edge_id} lacks geometry provenance field {field}")


def evaluate_city_pilot(city_id: str, features: list[dict], *, pilot_size: int = 5) -> dict:
    """Select a stable 5–20 edge pilot and run frozen M7 only after both readiness gates."""
    if not isinstance(city_id, str) or not city_id:
        raise ValueError("city_id must be a non-empty string")
    if isinstance(pilot_size, bool) or not isinstance(pilot_size, int) or not 5 <= pilot_size <= 20:
        raise ValueError("pilot_size must be an integer from 5 through 20")
    if not isinstance(features, list) or len(features) < pilot_size:
        raise ValueError("candidate feature list is shorter than pilot_size")

    ordered = sorted(features, key=_edge_id)
    edge_ids = [_edge_id(feature) for feature in ordered]
    if len(edge_ids) != len(set(edge_ids)):
        raise ValueError("candidate edge_id values must be unique")

    rows = []
    for feature in ordered[:pilot_size]:
        props = feature["properties"]
        edge_id = _edge_id(feature)
        _require_source_traceable_real_geometry(props, edge_id)
        row = assess_m7_readiness(edge_id, props)
        row["geometry_provenance"] = _geometry_receipt(props)
        if row["m7_api_structurally_callable"] and row["m7_evidence_ready"]:
            inputs = {field: props[field] for field in M7_API_FIELDS}
            canonical_inputs = json.dumps(
                inputs, ensure_ascii=False, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")
            row.update(
                {
                    "status": "COMPUTED",
                    "m7_computed": True,
                    "m7_result": calculate_residual_width(**inputs),
                    "reason": (
                        "M7 ran only because every frozen-API input has source-traceable evidence."
                    ),
                    "m7_execution_receipt": {
                        "input_sha256": hashlib.sha256(canonical_inputs).hexdigest(),
                        "per_field_provenance": props["m7_provenance"],
                        "model": "src.residual_width.calculate_residual_width",
                    },
                }
            )
        rows.append(row)

    evidence_ready_count = sum(row["m7_evidence_ready"] for row in rows)
    computed_count = sum(row["m7_computed"] for row in rows)
    return {
        "city_id": city_id,
        "selection_rule": SELECTION_RULE,
        "selected_edge_count": len(rows),
        "m7_api_structurally_callable_edge_count": sum(
            row["m7_api_structurally_callable"] for row in rows
        ),
        "m7_evidence_ready_edge_count": evidence_ready_count,
        "m7_computed_edge_count": computed_count,
        "safe_route_claim": False,
        "accessibility_claim": False,
        "m6_status": "NOT_COMPUTED",
        "edges": rows,
    }


def build_repository_report(root: Path, *, pilot_size: int = 5) -> dict:
    """Build the three-city Gate 6 receipt from tracked candidate artifacts."""
    cities = []
    for city_id, relative_path in CITY_ARTIFACTS.items():
        artifact_bytes = (root / relative_path).read_bytes()
        artifact = json.loads(artifact_bytes.decode("utf-8"))
        city = evaluate_city_pilot(city_id, artifact["features"], pilot_size=pilot_size)
        city["candidate_artifact"] = relative_path
        city["candidate_artifact_sha256"] = hashlib.sha256(artifact_bytes).hexdigest()
        city["candidate_artifact_binding"] = (
            "Tracked commit path and exact bytes are bound here for pilot reproducibility; "
            "this is not a substitute for per-field M7 evidence."
        )
        cities.append(city)
    selected = sum(city["selected_edge_count"] for city in cities)
    ready = sum(city["m7_evidence_ready_edge_count"] for city in cities)
    computed = sum(city["m7_computed_edge_count"] for city in cities)
    return {
        "schema_version": "1.0.0",
        "gate": "G6_M7_REAL_EDGE_PILOT",
        "status": "PASS" if computed else "PARTIAL",
        "selected_edge_count": selected,
        "evidence_ready_count": ready,
        "computed_count": computed,
        "model_route": {
            "requested": "Sol/high parent implementation and independent review",
            "actual": "UNVERIFIED",
            "MODEL_ROUTE_VERIFIED": False,
        },
        "constraints": {
            "synthetic_fixture_presented_as_real": False,
            "width_inferred_from_highway_class": False,
            "centroid_distance_used_as_setback": False,
            "hazard_overlap_used_for_damage_or_debris": False,
            "missing_value_defaulted_to_zero": False,
            "safe_route_claim": False,
            "accessibility_claim": False,
        },
        "cities": cities,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pilot-size", type=int, default=5)
    args = parser.parse_args()
    report = build_repository_report(args.root.resolve(), pilot_size=args.pilot_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
