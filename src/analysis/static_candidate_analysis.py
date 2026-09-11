"""Canonical source-side construction and validation of static candidate analysis."""

from __future__ import annotations

import json
import math
from hashlib import sha256
from pathlib import Path

from src.analysis.candidate_network import (
    build_candidate_graph,
    build_path_matrix,
    candidate_components,
    choose_selectable_node_ids,
)
from src.analysis.delivery_sprint import validate_f1_f6_binding


def canonical_text_bytes(payload: bytes) -> bytes:
    """Return canonical Git text bytes independent of Windows checkout newlines."""
    return payload.replace(b"\r\n", b"\n")


def canonical_text_sha256_bytes(payload: bytes) -> str:
    """Hash canonical Git text bytes independent of Windows checkout newlines."""
    return sha256(canonical_text_bytes(payload)).hexdigest()


def canonical_text_sha256(path: Path) -> str:
    return canonical_text_sha256_bytes(Path(path).read_bytes())


CONNECTED_REASON = "Candidate connectivity only; accessibility, safety, and operation are unconfirmed."
DISCONNECTED_REASON = "No candidate-network connection exists between the selected nodes; accessibility, safety, and operation are unconfirmed."
CITY_INPUTS = (
    {"id": "kyoto_kiyomizu", "nodes": "cities/kyoto_kiyomizu/graph/real/candidate_nodes.geojson", "edges": "cities/kyoto_kiyomizu/graph/real/candidate_edges.geojson", "source": "openstreetmap_kiyomizu_named_corridor_20260830", "snapshot": "2026-08-30T00:00:00Z"},
    {"id": "kyoto_arashiyama", "nodes": "cities/kyoto_arashiyama/graph/walk_nodes.real.geojson", "edges": "cities/kyoto_arashiyama/graph/walk_edges.real.geojson", "source": "openstreetmap-overpass-arashiyama-20260829", "snapshot": "2026-08-29T00:00:00Z"},
    {"id": "fujisawa_enoshima", "nodes": "cities/fujisawa_enoshima/graph/candidate_walk_nodes.real.geojson", "edges": "cities/fujisawa_enoshima/graph/candidate_walk_edges.real.geojson", "source": "OSM_CANDIDATE_SOURCE", "snapshot": "2026-08-30T00:00:00Z"},
)
EXPECTED_HAZARD_SOURCES = {
    "kyoto_kiyomizu": {
        "nlni_a31b_2025_kyoto_flood": ("https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip", "PERMITTED_WITH_OBLIGATIONS", "d10455a376ee3d89b9618b77be85c51da5ebcc6687d17e92c492573f056e699e", "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c", "2025"),
        "kyoto_city_landslide_gis_20260830": ("https://www.bousaimap.city.kyoto.lg.jp/GisDownload", "PUBLIC_REUSE_ALLOWED_WITH_ATTRIBUTION", "a3a8976c8708b95f1ccc5d5b8aaefdb4c0d7aaa0e8eb879a64d28e812818fdd6", "ac40e0b7116d81516dc10e279f5ca67ba48bbece68dc1164ec8f1d3e0c095828", "2026-01-22"),
    },
    "kyoto_arashiyama": {
        "nlni_a31b_2025_kyoto_flood": ("https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip", "PERMITTED_WITH_OBLIGATIONS", "2f02464358d7671c82bf69c346914f9c765e6558a20dca9af233aa54a5bfdbd7", "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c", "2025"),
        "kyoto_city_landslide_gis_20260830": ("https://www.bousaimap.city.kyoto.lg.jp/GisDownload", "PUBLIC_REUSE_ALLOWED_WITH_ATTRIBUTION", "9935a4b22f656f3ef66d120bbc94c0d97e42e71a7956db181b6e8f0002700b4f", "ac40e0b7116d81516dc10e279f5ca67ba48bbece68dc1164ec8f1d3e0c095828", "2026-01-22"),
    },
    "fujisawa_enoshima": {
        "nlni_a40_2020_kanagawa_tsunami": ("https://nlftp.mlit.go.jp/ksj/gml/data/A40/A40-20/A40-20_14_GML.zip", "PUBLIC_REDISTRIBUTION_ALLOWED_WITH_ATTRIBUTION", "5dc5a3351b57f1b13b2a1d3571d82e789d8e7f859a1acf9c131749726260cb8c", "6b3192e4ed4f8f28d057e4738ecc0d2e7bef232d6adc3022f2d6aec8375f7479", "2020"),
    },
}
EXPECTED_HAZARD_SOURCES["fujisawa_enoshima"].update({
    **{f"kanagawa_r7_intensity_distribution_{index:02d}": ("https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/704a2ee0-0040-4a96-b92a-c8e36b559d3d", "LICENSE_REVIEW_REQUIRED", selection_sha, "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442", "R7_MARCH_2025_SCENARIO_SET") for index, selection_sha in enumerate((
        "1748165a3d296fac37f4c8298a3bc013e28d3869c24d8fc9b6af7d10db660595", "28636eefca222b65c5c29ec6e2f66dc63939864a3a1b185aa46b0c210811ca4d", "621401abd0c56324be78d97b34a63e1833e173cd178c66b101ec7ac65d128b1a", "f13dc5d92d7e7bd743da1c1567bee9f0cd03a12b2e9748f37a8a59586ebb7d3b", "acdef6ce4c816a8332966f9a35b119f4b60c4074af03eb75a0c4e649c8ac41d3", "fda1ba2847dfd9d9bfe1a69f3ea930f312db654d5f0d326f59d6c8a3ca2db195", "eb3ca595ee5976f36b340acdcd07f913134cdb422aeb7acdd58079cb1ef20b36", "c8be7d19522b39d81f058f5a5196f49408b6c60cd4db8afd6933b0729771df66",
    ), 1)},
    **{f"kanagawa_r7_liquefaction_distribution_{index:02d}": ("https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/1f94e194-1764-46db-baf9-e8b017ae458d", "CC-BY", selection_sha, "91f721e0f37114379d7535f5a9c09eac03ffa9c4d3dc1a2088d6d8ee5f47d023", "R7_MARCH_2025_SCENARIO_SET") for index, selection_sha in enumerate((
        "5d37e622abc6c4bf28b93362016f7d7bbe64c5c1103220cbe467ba94c577690d", "1cf28d1ce1b89873302deac16eee5ad429926307aa5889308fde765d68f5d029", "d0fa5f079eb18c1ac7971c6c75320239c83ada6767e53458d7696357bf10e983", "86a375a1981712ff30ae1f2e547d120ef32bd931d54bc21a7c05707223bc0949", "b37720d8c2dffcda8f292799e1486850cb45a52562a5fa1432d0a55d62fe6341", "c4f788db34ddccbc011167480ccecb64f0508db347a0591733565f3e1cab4fbf", "d0750f3a40e14c6d88fa4c8339d14a10a5207ddc2bd1a98fdb2b03876dd5aee9", "835c9e16cfd046f0c05cb20bf9d28d70babea0b610b3eb0ca736da4882315b67",
    ), 1)},
    "kanagawa_r7_shaking_susceptibility": ("https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/0511f2b8-db28-4eae-a5a9-83ac58d31fbc", "CC-BY", "10298a53d8e5ab3084ee68d84fe727a5cb63f28812fd0578e55626b392e47de1", "281f43260b2a0d18f8b4afb4fdbfdba79464692ed175d1d0be3c8f88df6dcaa3", "R6_UPDATE_2025-02-05"),
    "kanagawa_r7_liquefaction_hazard": ("https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/cd7619e9-b6f8-48ad-a251-f8fa9cc84462", "CC-BY", "54af719e9815befcc950f9bacf40512eab57fe878014f191c5622ae9e870ae22", "fb18d09991f63eae642483334c2eb1657b139cc746aa4c4af083260a070146de", "R6_UPDATE_2025-02-15_V01"),
})
EXPECTED_FUJISAWA_SCENARIO_IDS = sorted([
    *(f"fujisawa_earthquake_intensity_scenario_{index:02d}" for index in range(1, 9)),
    "fujisawa_shaking_susceptibility_r6_01",
    *(f"fujisawa_liquefaction_distribution_scenario_{index:02d}" for index in range(1, 9)),
    "fujisawa_liquefaction_hazard_r6_01",
])
KYOTO_FACILITY_SOURCES = {
    "kyoto_emergency_shelters_r80818": ("https://data.city.kyoto.lg.jp/resource/?id=7855", "LICENSE_REVIEW_REQUIRED", "R8.8.18", "e1c03e4e0f830d10430b6a0fb1e1669886c3708cdc61164e5471cea7f9a4d639", ["administrative_district", "community_disaster_group", "flood_evacuation_target_districts", "landslide_evacuation_target_districts", "official_number"]),
    "kyoto_designated_shelters_r80818": ("https://data.city.kyoto.lg.jp/resource/?id=7854", "LICENSE_REVIEW_REQUIRED", "R8.8.18", "a30cf1556380359a1fa8fc69e4641fbfb7c3c099595818ac24c01417c9e28246", ["administrative_district", "community_disaster_group", "listed_maximum_capacity", "official_number"]),
    "kyoto_public_toilets_00307": ("https://data.city.kyoto.lg.jp/resource/?id=20314", "CC BY 4.0", "2026-03-06", "a46448d7bb6fe814631b1230e69ce6d825d36ccf0ddb35dc339bc49ed60fc764", ["administrative_district", "listed_baby_support", "listed_fixture_count_text", "listed_opening_hours", "listed_ostomate_support", "listed_washlet_support", "listed_western_style", "listed_wheelchair_support", "official_map_number", "official_page_url"]),
}
EXPECTED_FACILITY_SOURCES = {
    "kyoto_kiyomizu": KYOTO_FACILITY_SOURCES,
    "kyoto_arashiyama": KYOTO_FACILITY_SOURCES,
    "fujisawa_enoshima": {
        "fujisawa_webgis_toilets_accessibility": ("https://webgis.alandis.jp/fujisawa14/portal/index.html", "LICENSE_REVIEW_REQUIRED", None, "71bd70b0703086017e26d71cf4d73b76bcb0d14aaa0143c351e4763442b4530d", ["ostomate_detail_available"]),
    },
}
EXPECTED_CONTENT_SHA256 = {
    "kyoto_kiyomizu": {"hazard_catalog": "f4ad20c463de90e7e52b81afd55c78a938fc7c4ea592fcdcaf6a1158fa33ccbc", "facility_catalog": "6a09b762af8ecc69a2637a2177755dfce5a01420611b250779f20300b48e610e", "facility_records": "d8d74884e7e7194439cabf7da0f9675b9a6c91dec5926160ae838f92e7af0102"},
    "kyoto_arashiyama": {"hazard_catalog": "0319376da1a250956930e1ee6980af4fe43150f25d4dcf50161adb81fbcbcc96", "facility_catalog": "6a09b762af8ecc69a2637a2177755dfce5a01420611b250779f20300b48e610e", "facility_records": "7a7cafb3bb85b38aaf6de39a950d4e26c6ccf08af76627199739e1c65243246d"},
    "fujisawa_enoshima": {"hazard_catalog": "f84c26d92534ede0bbc5295e4763156fa3dbb10692f603b36620d89921e25fc6", "facility_catalog": "f5104b2d859dc0a776c2d9f7899e130dced7162a123d5e2561d267ee81743006", "facility_records": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "scenarios": "5efd762875dd827d4a9894abe24af8e1fe54c58c44f0fba9770362d40843c267"},
}


def _is_sha256(value) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _canonical_object_sha256(value) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(payload).hexdigest()


def authoritative_report_paths(root: Path, city_id: str) -> dict[str, Path]:
    """Return every source file whose bytes directly shape official analysis evidence."""
    paths = {
        "promotion_sha256": root / "reports/OFFICIAL_LOCAL_ARTIFACT_PROMOTION_V2.json",
        "plateau_sha256": root / "reports/PLATEAU_BUILDING_EVIDENCE_V2.json",
        "m7_sha256": root / "reports/M7_REAL_EDGE_STATUS.json",
        "f1_f6_binding_sha256": root / "reports/F1_F6_DECISION_BINDING.json",
        "public_git_scope_amendment_sha256": root / "reports/PUBLIC_GIT_SCOPE_AMENDMENT_20260910.json",
        "public_official_evidence_sha256": root / "inputs/staging/PUBLIC-GIT-DEM-FUJISAWA-V1/official_evidence.json",
        "public_official_source_receipt_sha256": root / "inputs/staging/PUBLIC-GIT-DEM-FUJISAWA-V1/official_source_receipt.json",
        "delivery_source_binding_sha256": root / "inputs/staging/DELIVERY-SPRINT-V1/source_bindings.json",
    }
    if city_id.startswith("kyoto_"):
        group = "kiyomizu_gion" if city_id == "kyoto_kiyomizu" else "arashiyama"
        paths.update({
            "kyoto_status_sha256": root / "reports/KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json",
            "terrain_inventory_sha256": root / f"cities/{city_id}/terrain/official/dem_product_inventory.csv",
            "kyoto_parity_sha256": root / "reports/KYOTO_PARITY_STATUS.json",
            "kyoto_m7_pilot_sha256": root / "reports/KYOTO_M7_DEEP_PILOT_STATUS.json",
            "kyoto_facility_sha256": root / "inputs/staging/KYOTO-OFFICIAL-PARITY-V1/facility_records.json",
            "kyoto_facility_category_status_sha256": root / "inputs/staging/KYOTO-OFFICIAL-PARITY-V1/facility_category_status.json",
            "kyoto_flood_display_sha256": root / f"inputs/staging/KYOTO-OFFICIAL-PARITY-V1/a31b_{group}_display.geojson",
            "plateau_inventory_sha256": root / "inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/PLATEAU_BUILDING_AOI_INVENTORY.csv",
            "delivery_landslide_sha256": root / f"inputs/staging/DELIVERY-SPRINT-V1/{city_id}/landslide_aoi_selection.geojson",
        })
    if city_id == "fujisawa_enoshima":
        paths.update({
            "terrain_inventory_sha256": root / f"cities/{city_id}/terrain/official/dem_product_inventory.csv",
            "facility_receipt_sha256": root / f"cities/{city_id}/facilities/official/facility_source_receipt.json",
            "earthquake_inventory_sha256": root / f"cities/{city_id}/hazards/official/earthquake_scenario_inventory.csv",
            "liquefaction_inventory_sha256": root / f"cities/{city_id}/hazards/official/liquefaction_scenario_inventory.csv",
            "delivery_tsunami_sha256": root / "inputs/staging/DELIVERY-SPRINT-V1/fujisawa_enoshima/tsunami_a40_aoi_selection.geojson",
        })
    return paths


def summarize_m7_readiness(official_evidence: dict, readiness: list[dict]) -> dict:
    """Copy the authoritative reasoned-null M7 counts and rows without running M7."""
    m7 = official_evidence.get("m7") if isinstance(official_evidence, dict) else None
    if not isinstance(m7, dict):
        raise ValueError("official M7 summary is required")
    ready = m7.get("evidence_ready_count")
    computed = m7.get("computed_count")
    if isinstance(ready, bool) or not isinstance(ready, int) or ready < 0:
        raise ValueError("official M7 evidence-ready count is invalid")
    if isinstance(computed, bool) or not isinstance(computed, int) or computed < 0:
        raise ValueError("official M7 computed count is invalid")
    if not isinstance(readiness, list):
        raise ValueError("M7 readiness rows must be a list")
    if any(
        not isinstance(row, dict)
        or row.get("m7_evidence_ready") is not False
        or row.get("m7_computed") is not False
        or row.get("m7_result") is not None
        for row in readiness
    ):
        raise ValueError("M7 readiness rows contain an unsupported promotion")
    if ready != sum(row["m7_evidence_ready"] is True for row in readiness):
        raise ValueError("official M7 summary does not match readiness rows")
    if computed != sum(row["m7_computed"] is True for row in readiness):
        raise ValueError("official M7 summary does not match computed rows")
    return {
        "status": m7.get("status"),
        "ready_edge_count": ready,
        "computed_edge_count": computed,
    }


def build_static_candidate_analysis(
    context: dict,
    nodes: list[dict],
    edges: list[dict],
    official_evidence: dict,
    m7_readiness: list[dict],
) -> dict:
    """Build the complete deterministic analysis artifact consumed by the viewer."""
    if not isinstance(nodes, list):
        raise ValueError("candidate nodes must be a list")
    if any(
        not isinstance(edge, dict)
        or edge.get("geometry", {}).get("type") != "LineString"
        for edge in edges
    ):
        raise ValueError("static candidate edge must be a LineString")
    adjacency, _ = build_candidate_graph(edges)
    node_ids = []
    for node in nodes:
        node_id = node.get("properties", {}).get("node_id") if isinstance(node, dict) else None
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("candidate node_id must be a non-empty string")
        node_ids.append(node_id)
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("candidate node_id values must be unique")
    if not set(adjacency).issubset(node_ids):
        raise ValueError("candidate edge endpoint is not present in the node artifact")
    components = candidate_components(adjacency, node_ids)
    selectable = choose_selectable_node_ids(edges, node_ids)
    path_matrix = build_path_matrix(edges, selectable)
    start = selectable[0] if selectable else None
    end = selectable[1] if len(selectable) > 1 else None
    path_fixture = path_matrix.get(f"{start}__{end}")
    if path_fixture is None:
        path_fixture = {
            "start_node_id": start,
            "end_node_id": end,
            "status": "CONNECTED",
            "unit": "coordinate_degree",
            "edge_ids": [],
            "geometric_length": 0,
            "reason": CONNECTED_REASON,
        }
    m7_summary = summarize_m7_readiness(official_evidence, m7_readiness)
    result = {
        "topology": {
            "node_count": len(node_ids),
            "edge_count": len(edges),
            "connected_components": len(components),
            "topology_status": "CANDIDATE_REVIEW_REQUIRED",
        },
        "selectable_node_ids": selectable,
        "path_matrix": path_matrix,
        "path_fixture": path_fixture,
        "hazard_overlap": {
            "status": "NOT_CONNECTED",
            "value": None,
            "reason": "No trusted official hazard geometry is connected; no closure is derived.",
        },
        "m7": m7_summary,
        "m6": {"status": "NOT_COMPUTED", "reason": "M6/profile evaluation is not connected."},
    }
    artifact = {
        "analysis_id": f"{context['city_id']}:candidate-topology-v2",
        "analysis_type": "CANDIDATE_TOPOLOGY_STATIC_FIXTURE",
        "city_id": context["city_id"],
        "source_artifact_ids": context["source_artifact_ids"],
        "source_revision_ids": context["source_revision_ids"],
        "input_sha256": context["input_sha256"],
        "algorithm": "deterministic-undirected-dijkstra-coordinate-degree",
        "algorithm_version": "2.0.0",
        "parameters": {
            "coordinate_unit": "coordinate_degree",
            "input_binding": "sha256(LF-canonical node_geojson_bytes + 0x00 + LF-canonical edge_geojson_bytes); input order=node,edge",
            "tie_break": "lexical ordered edge-ID tuple",
        },
        "generated_at": context["snapshot_at"],
        "deterministic": True,
        "result": result,
        "official_evidence": official_evidence,
        "limitations": [
            "Candidate connectivity only",
            "coordinate_degree is not a geographic or meter distance",
            "Hazard, M7, M6, accessibility, safety, operation, and administrative validation are unconnected or not computed",
        ],
        "provenance": {
            "source_class": "VGI",
            "source_id": context["source_id"],
            "input_binding": "LF-canonical node bytes then NUL then LF-canonical edge bytes",
            "input_artifacts": context["source_artifact_ids"],
            "input_hashes": context["input_hashes"],
        },
        "safety_claim": False,
        "accessibility_claim": False,
        "admin_validated": False,
    }
    artifact.update(result)
    artifact["m7"] = {**result["m7"], "readiness": m7_readiness}
    artifact["interpretation"] = "Candidate network connectivity only; accessibility, safety, and operation are unconfirmed."
    return artifact


def validate_static_candidate_analysis(repo_root: Path, artifact: dict) -> dict:
    """Fail closed if canonical source bytes, report bindings, or safety truth are stale."""
    root = Path(repo_root).resolve()
    decision_binding = artifact.get("decision_binding") if isinstance(artifact, dict) else None
    expected_binding = json.loads((root / "reports/F1_F6_DECISION_BINDING.json").read_text(encoding="utf-8"))
    if decision_binding != expected_binding:
        raise ValueError("static analysis decision binding is stale or not exact")
    validate_f1_f6_binding(decision_binding)
    city_id = artifact.get("city_id") if isinstance(artifact, dict) else None
    try:
        city = next(item for item in CITY_INPUTS if item["id"] == city_id)
    except StopIteration as exc:
        raise ValueError("unsupported static analysis city") from exc
    node_bytes = canonical_text_bytes((root / city["nodes"]).read_bytes())
    edge_bytes = canonical_text_bytes((root / city["edges"]).read_bytes())
    expected_input = sha256(node_bytes + b"\0" + edge_bytes).hexdigest()
    if artifact.get("input_sha256") != expected_input:
        raise ValueError(f"{city_id} static analysis input SHA-256 is stale")
    if artifact.get("provenance", {}).get("input_hashes") != {
        "node_sha256": sha256(node_bytes).hexdigest(),
        "edge_sha256": sha256(edge_bytes).hexdigest(),
    }:
        raise ValueError(f"{city_id} static analysis input hash provenance is stale")
    nodes = json.loads(node_bytes)["features"]
    edges = json.loads(edge_bytes)["features"]
    revisions = sorted(
        {
            feature.get("properties", {}).get("revision_id")
            for feature in [*nodes, *edges]
            if feature.get("properties", {}).get("revision_id")
        }
    )
    if artifact.get("source_artifact_ids") != [city["nodes"], city["edges"]]:
        raise ValueError(f"{city_id} static analysis source artifacts are stale")
    if artifact.get("source_revision_ids") != revisions:
        raise ValueError(f"{city_id} static analysis source revisions are stale")
    official = artifact.get("official_evidence", {})
    if any(
        value is not False
        for value in (
            artifact.get("safety_claim"),
            artifact.get("accessibility_claim"),
            artifact.get("admin_validated"),
            official.get("safe_route_claim"),
            official.get("accessibility_claim"),
            official.get("admin_validated"),
        )
    ):
        raise ValueError("static analysis contains a forbidden safety or validation promotion")
    for key, path in authoritative_report_paths(root, city_id).items():
        expected = canonical_text_sha256(path)
        if official.get("source_hashes", {}).get(key) != expected:
            raise ValueError(f"{city_id} static analysis report SHA-256 is stale: {key}")
    if official.get("m7", {}).get("edge_receipts_source_sha256") != canonical_text_sha256(
        root / "reports/M7_ALL_EDGE_EVIDENCE_READINESS.json"
    ):
        raise ValueError(f"{city_id} static analysis M7 readiness source is stale")
    if city_id.startswith("kyoto_"):
        group = "kiyomizu_gion" if city_id == "kyoto_kiyomizu" else "arashiyama"
        point_path = root / f"inputs/staging/KYOTO-OFFICIAL-PARITY-V1/facility_points_{group}.geojson"
        point_hash = canonical_text_sha256(point_path)
        display = official.get("facility", {}).get("display_layer", {})
        if display.get("artifact_sha256") != point_hash or display.get("copied_sha256") != point_hash:
            raise ValueError(f"{city_id} static facility display binding is stale")
    terrain = official.get("terrain", {})
    if (
        terrain.get("status") != "NATIVE_CELL_SAMPLES_CONNECTED"
        or terrain.get("connected") is not True
        or terrain.get("elevation_sampled") is not True
        or terrain.get("step_inferred") is not False
        or terrain.get("cross_slope_inferred") is not False
        or len(terrain.get("products", [])) != 2
        or any(
            product.get("terrain_connected") is not True
            or product.get("status") != "NATIVE_CELL_SAMPLES_CONNECTED"
            or product.get("vertical_datum") != "JGD2024_VERTICAL_JAPAN_DATUM_2024"
            or product.get("implicit_precedence") is not False
            or product.get("mosaic_applied") is not False
            for product in terrain.get("products", [])
        )
        or any(
            sample.get("product") not in {"DEM1A", "DEM5A"}
            or sample.get("unit") != "m"
            or sample.get("status") not in {"SAMPLED_NATIVE_CELL", "NODATA", "SURFACE_VALUE_UNRESOLVED", "OMITTED_SEQUENCE_VALUE", "AMBIGUOUS_CELL_BOUNDARY", "AMBIGUOUS_OR_MISSING_MEMBER"}
            or (
                sample.get("status") != "SAMPLED_NATIVE_CELL"
                and (not isinstance(sample.get("reason"), str) or not sample["reason"].strip())
            )
            or (
                sample.get("status") == "SAMPLED_NATIVE_CELL"
                and (
                    isinstance(sample.get("elevation_m"), bool)
                    or not isinstance(sample.get("elevation_m"), (int, float))
                    or not math.isfinite(sample["elevation_m"])
                )
            )
            or (sample.get("status") != "SAMPLED_NATIVE_CELL" and sample.get("elevation_m") is not None)
            for sample in terrain.get("samples", [])
        )
    ):
        raise ValueError(f"{city_id} terrain native-cell evidence is stale or unsafe")
    samples = terrain.get("samples", [])
    coordinates = {(sample["query_longitude"], sample["query_latitude"]) for sample in samples}
    null_samples = [sample for sample in samples if sample["elevation_m"] is None]
    if (
        terrain.get("sample_record_count") != len(samples)
        or terrain.get("unique_coordinate_count") != len(coordinates)
        or terrain.get("numeric_record_count") != len(samples) - len(null_samples)
        or terrain.get("null_record_count") != len(null_samples)
        or terrain.get("null_coordinate_count")
        != len({(sample["query_longitude"], sample["query_latitude"]) for sample in null_samples})
    ):
        raise ValueError(f"{city_id} terrain record/location summary is stale")
    for product in terrain["products"]:
        product_samples = [sample for sample in samples if sample["product"] == product["product"]]
        product_nulls = [sample for sample in product_samples if sample["elevation_m"] is None]
        if (
            product.get("sample_count") != len(product_samples)
            or product.get("sample_record_count") != len(product_samples)
            or product.get("unique_coordinate_count")
            != len({(sample["query_longitude"], sample["query_latitude"]) for sample in product_samples})
            or product.get("numeric_sample_count") != len(product_samples) - len(product_nulls)
            or product.get("null_sample_count") != len(product_nulls)
            or product.get("null_record_count") != len(product_nulls)
            or product.get("null_coordinate_count")
            != len({(sample["query_longitude"], sample["query_latitude"]) for sample in product_nulls})
        ):
            raise ValueError(f"{city_id} terrain product record/location summary is stale")
    city_input = next(city for city in CITY_INPUTS if city["id"] == city_id)
    source_nodes = json.loads((root / city_input["nodes"]).read_text(encoding="utf-8"))["features"]
    source_edges = json.loads((root / city_input["edges"]).read_text(encoding="utf-8"))["features"]
    expected_sample_coordinates = {}
    for node in source_nodes:
        node_id = node["properties"]["node_id"]
        for product in ("DEM1A", "DEM5A"):
            expected_sample_coordinates[f"{city_id}:node:{node_id}:{product}"] = ("GRAPH_NODE", node["geometry"]["coordinates"])
    expected_edge_sample_ids = {}
    for edge in source_edges:
        edge_id = edge["properties"]["edge_id"]
        edge_ids = []
        for vertex_index, coordinate in enumerate(edge["geometry"]["coordinates"]):
            for product in ("DEM1A", "DEM5A"):
                sample_id = f"{city_id}:edge:{edge_id}:{vertex_index}:{product}"
                expected_sample_coordinates[sample_id] = ("EDGE_VERTEX", coordinate)
                edge_ids.append(sample_id)
        expected_edge_sample_ids[edge_id] = sorted(edge_ids)
    sample_ids = [sample.get("sample_id") for sample in samples]
    if (
        len(sample_ids) != len(set(sample_ids))
        or set(sample_ids) != set(expected_sample_coordinates)
        or set(terrain.get("edge_samples", {})) != set(expected_edge_sample_ids)
        or any(sorted(terrain["edge_samples"][edge_id]) != expected for edge_id, expected in expected_edge_sample_ids.items())
    ):
        raise ValueError(f"{city_id} terrain sample identity/reference set is stale")
    for sample in samples:
        expected_role, expected_coordinate = expected_sample_coordinates[sample["sample_id"]]
        if (
            sample.get("sample_role") != expected_role
            or sample.get("query_longitude") != expected_coordinate[0]
            or sample.get("query_latitude") != expected_coordinate[1]
            or not _is_sha256(sample.get("member_sha256"))
            or (expected_role == "GRAPH_NODE" and not sample.get("node_id"))
            or (expected_role == "EDGE_VERTEX" and (not sample.get("edge_id") or isinstance(sample.get("vertex_index"), bool) or not isinstance(sample.get("vertex_index"), int)))
        ):
            raise ValueError(f"{city_id} terrain sample provenance is stale")
    member_hashes = {
        member.get("member_sha256")
        for product in terrain.get("products", [])
        for member in product.get("members", [])
        if _is_sha256(member.get("member_sha256")) and _is_sha256(member.get("nested_zip_sha256"))
    }
    if len(member_hashes) == 0 or any(sample.get("member_sha256") not in member_hashes for sample in samples):
        raise ValueError(f"{city_id} terrain member provenance is stale")
    facility = official.get("facility", {})
    facility_catalog = facility.get("source_catalog", {})
    facility_records = facility.get("records", [])
    temporal_keys = ("published_at", "valid_as_of", "acquired_at")
    if (
        not facility_catalog
        or facility.get("record_count") != len(facility_records)
        or any(
            not isinstance(source.get("source_url"), str) or not source["source_url"].startswith("https://")
            or not isinstance(source.get("license_status"), str) or not source["license_status"]
            or not isinstance(source.get("limitations"), str) or not source["limitations"]
            or not isinstance(source.get("temporal_status_reason"), str) or not source["temporal_status_reason"]
            or not _is_sha256(source.get("source_sha256"))
            or not isinstance(source.get("allowed_attribute_keys"), list)
            or any(source.get(key) is not None and not isinstance(source.get(key), str) for key in temporal_keys)
            for source in facility_catalog.values()
        )
        or any(
            record.get("source_id") not in facility_catalog
            or record.get("source_sha256") != facility_catalog.get(record.get("source_id"), {}).get("source_sha256")
            or record.get("source_version_or_valid_as_of") != facility_catalog.get(record.get("source_id"), {}).get("valid_as_of")
            or sorted(record.get("source_attributes", {})) != sorted(facility_catalog.get(record.get("source_id"), {}).get("allowed_attribute_keys", []))
            or record.get("source_attribute_entries") != [[key, record["source_attributes"][key]] for key in sorted(record.get("source_attributes", {}))]
            or not isinstance(record.get("limitations"), str) or not record["limitations"]
            or any(record.get(key) != "UNKNOWN" for key in ("current_operation_status", "entrance_status", "unlock_status", "accessibility_status", "step_free_status", "disaster_availability_status"))
            for record in facility_records
        )
    ):
        raise ValueError(f"{city_id} facility source binding or current state is invalid")
    expected_facility_sources = EXPECTED_FACILITY_SOURCES[city_id]
    if set(facility_catalog) != set(expected_facility_sources) or any(
        facility_catalog[source_id].get("source_url") != expected[0]
        or facility_catalog[source_id].get("license_status") != expected[1]
        or facility_catalog[source_id].get("valid_as_of") != expected[2]
        or facility_catalog[source_id].get("source_sha256") != expected[3]
        or sorted(facility_catalog[source_id].get("allowed_attribute_keys", [])) != sorted(expected[4])
        for source_id, expected in expected_facility_sources.items()
    ):
        raise ValueError(f"{city_id} facility source provenance is not exact")
    expected_content = EXPECTED_CONTENT_SHA256[city_id]
    if (
        _canonical_object_sha256(facility_catalog) != expected_content["facility_catalog"]
        or _canonical_object_sha256(facility_records) != expected_content["facility_records"]
    ):
        raise ValueError(f"{city_id} facility canonical content is stale")
    m7_report = json.loads((root / "reports/M7_REAL_EDGE_STATUS.json").read_text(encoding="utf-8"))
    m7 = artifact.get("m7", {})
    if (
        m7.get("ready_edge_count") != m7_report.get("evidence_ready_count")
        or m7.get("computed_edge_count") != m7_report.get("computed_count")
        or artifact.get("result", {}).get("m7") != {
            key: m7.get(key) for key in ("status", "ready_edge_count", "computed_edge_count")
        }
        or len(m7.get("readiness", [])) != official.get("m7", {}).get("city_edge_count")
        or any(
            row.get("m7_evidence_ready") is not False
            or row.get("m7_computed") is not False
            or row.get("m7_result") is not None
            for row in m7.get("readiness", [])
        )
    ):
        raise ValueError(f"{city_id} static analysis M7 summary is stale or promoted")
    hazard = official.get("hazard", {})
    if (
        hazard.get("status") != "SOURCE_SIDE_EDGE_OVERLAP_CONNECTED"
        or hazard.get("numeric_serialization") != "FULL_PYTHON_FLOAT_NO_DECISION_TOLERANCE"
        or hazard.get("decision_threshold_applied") is not False
        or hazard.get("operational_state_connected") is not False
        or hazard.get("closure_derived") is not False
        or hazard.get("damage_or_debris_inferred") is not False
    ):
        raise ValueError(f"{city_id} delivery hazard contract is stale or unsafe")
    expected_crs = "EPSG:6677" if city_id == "fujisawa_enoshima" else "EPSG:6674"
    source_catalog = hazard.get("source_catalog", {})
    if not source_catalog or any(
        not isinstance(source.get("source_url"), str) or not source["source_url"].startswith("https://")
        or not isinstance(source.get("license_status"), str) or not source["license_status"]
        or not isinstance(source.get("limitations"), str) or not source["limitations"]
        or not _is_sha256(source.get("coverage_selection_sha256"))
        or not _is_sha256(source.get("source_sha256"))
        or not isinstance(source.get("source_revision"), str) or not source["source_revision"] or "\0" in source["source_revision"]
        for source in source_catalog.values()
    ):
        raise ValueError(f"{city_id} delivery hazard source catalog is invalid")
    expected_hazard_sources = dict(EXPECTED_HAZARD_SOURCES[city_id])
    if city_id == "fujisawa_enoshima":
        public = json.loads((root / "inputs/staging/PUBLIC-GIT-DEM-FUJISAWA-V1/official_evidence.json").read_text(encoding="utf-8"))["fujisawa_hazards"]
        for layer in public["layers"]:
            expected_hazard_sources[layer["source_id"]] = (
                layer["source_url"], layer["license_status"], layer["coverage_evidence"]["selection_sha256"],
                layer["source_sha256"], layer["source_revision"],
            )
        public_by_source = {layer["source_id"]: layer for layer in public["layers"]}
        if any(
            source_catalog[source_id].get("source_member_id") != layer.get("source_member_id")
            or source_catalog[source_id].get("source_member_receipt") != layer.get("source_member_receipt")
            or not all(_is_sha256(layer.get("source_member_receipt", {}).get(key)) for key in ("member_path_sha256", "shp_sha256", "shx_sha256", "dbf_sha256", "txt_sha256"))
            for source_id, layer in public_by_source.items()
        ):
            raise ValueError("Fujisawa hazard member identity is stale")
    if set(source_catalog) != set(expected_hazard_sources) or any(
        source_catalog[source_id].get("source_url") != expected[0]
        or source_catalog[source_id].get("license_status") != expected[1]
        or source_catalog[source_id].get("coverage_selection_sha256") != expected[2]
        or source_catalog[source_id].get("source_sha256") != expected[3]
        or source_catalog[source_id].get("source_revision") != expected[4]
        for source_id, expected in expected_hazard_sources.items()
    ):
        raise ValueError(f"{city_id} delivery hazard source provenance is not exact")
    if _canonical_object_sha256(source_catalog) != expected_content["hazard_catalog"]:
        raise ValueError(f"{city_id} delivery hazard source catalog content is stale")
    if city_id == "fujisawa_enoshima" and (
        _canonical_object_sha256(hazard.get("scenarios", [])) != expected_content["scenarios"]
        or sorted(row.get("dataset_id") for row in hazard.get("scenarios", [])) != EXPECTED_FUJISAWA_SCENARIO_IDS
        or sum(row.get("connected") is True for row in hazard.get("scenarios", [])) != 18
        or sum(row.get("connected") is False for row in hazard.get("scenarios", [])) != 0
        or any(
        row.get("aoi_scope") != "enoshima_katase"
        or not isinstance(row.get("reason"), str) or not row["reason"]
        or row.get("connected") is not True
        or row.get("status") != "SOURCE_SIDE_EDGE_OVERLAP_CONNECTED"
        or row.get("validation_result") != "SOURCE_SHA_CRS_DEFINITION_AND_AOI_SELECTION_BOUND"
        or row.get("crs") not in {"EPSG:4612", "EPSG:6668"}
        # CRS closure and license receipt are separate gates: the mesh-code display
        # layers connect while their license receipt is still under review.
        or row.get("license_review") != ("LICENSE_REVIEW_REQUIRED" if row.get("crs") == "EPSG:6668" else "CC-BY")
        or (row.get("crs") == "EPSG:6668" and "CC-BY-4.0" not in str(row.get("license_note", "")))
        # The intensity scenarios display mesh-code geometry, so their CRS closure
        # receipt travels with the row and is never a derived state.
        or (row.get("crs") == "EPSG:6668" and (
            row.get("crs_closure", {}).get("decision") != "EPSG:6677_JGD2011_ZONE_IX_PROVIDER_DECLARED"
            or row["crs_closure"].get("display_geometry_source") != "JIS_X_0410_MESH_CODE_EPSG_6668"
            or row["crs_closure"].get("tolerance_scope") != "VERIFICATION_ONLY_NOT_REGISTRY_NOT_EVALUATION"
            or not isinstance(row["crs_closure"].get("max_vertex_error_m"), (int, float))
            or row["crs_closure"]["max_vertex_error_m"] > row["crs_closure"].get("tolerance_m", 0)
            or row["crs_closure"].get("erroneous_sidecar", {}).get("status") != "ERRONEOUS_SIDECAR_RECORDED_NOT_USED"
        ))
        for row in hazard.get("scenarios", []))
    ):
        raise ValueError("Fujisawa earthquake/liquefaction scenario inventory contract is stale")
    exposures = hazard.get("edge_exposures", [])
    if not exposures or any(
        row.get("metric_crs") != expected_crs
        or row.get("source_id") not in source_catalog
        or row.get("source_sha256") != source_catalog.get(row.get("source_id"), {}).get("source_sha256")
        or row.get("source_revision") != source_catalog.get(row.get("source_id"), {}).get("source_revision")
        or not all(isinstance(row.get(key), str) and row[key] and "\0" not in row[key] for key in ("edge_id", "scenario_id", "source_id", "source_revision"))
        or row.get("official_closure") is not None
        or row.get("damage_state") is not None
        or row.get("debris_present") is not None
        or row.get("relation") not in {"INTERSECTS", "TOUCHES", "ZERO_OVERLAP_WITHIN_KNOWN_COVERAGE", "OUTSIDE_COVERAGE", "PARTIAL_COVERAGE", "NO_DATA"}
        or row.get("coverage_status") not in {"WITHIN_KNOWN_COVERAGE", "OUTSIDE_KNOWN_COVERAGE", "PARTIAL_KNOWN_COVERAGE"}
        or (row.get("relation") in {"OUTSIDE_COVERAGE", "PARTIAL_COVERAGE", "NO_DATA"} and row.get("overlap_length_m") is not None)
        for row in exposures
    ):
        raise ValueError(f"{city_id} delivery hazard exposure rows are invalid")
    for row in exposures:
        relation = row["relation"]
        coverage_status = row["coverage_status"]
        length = row["overlap_length_m"]
        if not (
            (relation == "INTERSECTS" and coverage_status == "WITHIN_KNOWN_COVERAGE" and isinstance(length, (int, float)) and not isinstance(length, bool) and length > 0)
            or (relation in {"TOUCHES", "ZERO_OVERLAP_WITHIN_KNOWN_COVERAGE"} and coverage_status == "WITHIN_KNOWN_COVERAGE" and length == 0)
            or (relation == "OUTSIDE_COVERAGE" and coverage_status == "OUTSIDE_KNOWN_COVERAGE" and length is None)
            or (relation == "PARTIAL_COVERAGE" and coverage_status == "PARTIAL_KNOWN_COVERAGE" and length is None)
            or (relation == "NO_DATA" and length is None)
        ):
            raise ValueError(f"{city_id} delivery hazard relation/coverage/length combination is invalid")
    checklists = artifact.get("review_checklists", {})
    facility_ids = sorted(record["facility_record_id"] for record in official.get("facility", {}).get("records", []))
    exposure_by_key = {(row["edge_id"], row["scenario_id"], row["source_id"]): row for row in exposures}
    exposure_refs_by_edge = {
        edge_id: sorted("\0".join(key) for key in exposure_by_key if key[0] == edge_id)
        for edge_id in {key[0] for key in exposure_by_key}
    }
    path_matrix = artifact.get("path_matrix", {})
    checklist_unknowns = {"accessibility", "passability", "current_facility_operation", "M6", "M7"}
    if set(checklists) != set(path_matrix) or any(
        item.get("path_key") != key
        or item.get("city_id") != city_id
        or item.get("path_status") != path_matrix[key].get("status")
        or [row.get("edge_id") for row in item.get("rows", [])] != (path_matrix[key].get("edge_ids", []) if path_matrix[key].get("status") == "CONNECTED" else [])
        or item.get("safe_route_claim") is not False
        or item.get("accessibility_claim") is not False
        or item.get("admin_validated") is not False
        or sorted(item.get("facility", {}).get("record_ids", [])) != facility_ids
        or item.get("facility", {}).get("record_count") != len(facility_ids)
        or any(not row.get("owner_candidate_types") for row in item.get("rows", []))
        or any(not isinstance(row.get("unknowns"), list) or len(row["unknowns"]) != len(checklist_unknowns) or set(row["unknowns"]) != checklist_unknowns for row in item.get("rows", []))
        or any(not isinstance(row.get("hazard_refs"), list) or sorted(row["hazard_refs"]) != exposure_refs_by_edge.get(row.get("edge_id"), []) for row in item.get("rows", []))
        or any(not isinstance(row.get("terrain_sample_ids"), list) or sorted(row["terrain_sample_ids"]) != expected_edge_sample_ids.get(row.get("edge_id"), []) for row in item.get("rows", []))
        for key, item in checklists.items()
    ):
        raise ValueError(f"{city_id} review checklist contract is stale or unsafe")
    for key, item in checklists.items():
        path = path_matrix[key]
        if path.get("status") == "CONNECTED":
            if (
                item.get("status") != "READY_FOR_REVIEW"
                or item.get("candidate_distance") != path.get("geometric_length")
                or item.get("candidate_distance_unit") != path.get("unit")
                or item.get("path_reason") != path.get("reason")
                or not item.get("rows")
            ):
                raise ValueError(f"{city_id} connected review checklist is stale")
        elif (
            path.get("status") != "DISCONNECTED"
            or item.get("status") != "SUPPORTED_UNCOMPUTED"
            or item.get("candidate_distance") is not None
            or item.get("candidate_distance_unit") != path.get("unit")
            or item.get("path_reason") != path.get("reason")
            or not isinstance(item.get("path_reason"), str)
            or not item.get("path_reason")
            or item.get("rows") != []
        ):
            raise ValueError(f"{city_id} disconnected review checklist is stale")
    displays = hazard.get("display_layers", [])
    if not displays:
        raise ValueError(f"{city_id} delivery hazard display binding is missing")
    for display in displays:
        relative = display.get("data_path", "")
        if not isinstance(relative, str) or not relative.startswith("./data/official/") or "/" in relative.removeprefix("./data/official/") or not relative.endswith(".geojson"):
            raise ValueError(f"{city_id} delivery hazard display path is not confined")
        official_root = (root / "viewer/public/data/official").resolve()
        display_path = (root / "viewer/public" / relative.removeprefix("./")).resolve()
        if display_path.parent != official_root or not display_path.exists():
            raise ValueError(f"{city_id} delivery hazard display path is missing or escaped")
        if display.get("artifact_sha256") != display.get("copied_sha256") or (
            canonical_text_sha256(display_path) != display.get("copied_sha256")
        ):
            raise ValueError(f"{city_id} delivery hazard display binding is stale")
    return artifact
