"""Static candidate-analysis authority and deterministic generation tests."""

from __future__ import annotations

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

import scripts.build_candidate_analysis as generator
from scripts.build_candidate_analysis import generate_static_candidate_analyses
from src.analysis.static_candidate_analysis import (
    build_static_candidate_analysis,
    canonical_text_sha256_bytes,
    validate_static_candidate_analysis,
)


ROOT = Path(__file__).parents[2]
CITY_IDS = ("kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima")
def _node(node_id: str) -> dict:
    return {"properties": {"node_id": node_id}}


def _edge(edge_id: str, start: str, end: str, coordinates: list[list[float]]) -> dict:
    return {
        "properties": {"edge_id": edge_id, "from_node": start, "to_node": end},
        "geometry": {"type": "LineString", "coordinates": coordinates},
    }


def test_generator_reproduces_committed_three_city_bytes_twice(tmp_path: Path):
    """[source_conformance] Two source-side builds must exactly reproduce all committed static analysis bytes."""
    first = tmp_path / "first"
    second = tmp_path / "second"

    first_receipt = generate_static_candidate_analyses(ROOT, first)
    second_receipt = generate_static_candidate_analyses(ROOT, second)

    assert first_receipt == second_receipt
    manifest = json.loads((ROOT / "viewer/public/data/analysis/manifest.json").read_text(encoding="utf-8"))
    for city_id in CITY_IDS:
        committed = ROOT / "viewer" / "public" / "data" / "analysis" / f"{city_id}.json"
        first_bytes = (first / f"{city_id}.json").read_bytes()
        second_bytes = (second / f"{city_id}.json").read_bytes()
        committed_bytes = committed.read_bytes().replace(b"\r\n", b"\n")
        assert first_bytes == committed_bytes
        assert second_bytes == committed_bytes
        assert sha256(first_bytes).hexdigest() == sha256(second_bytes).hexdigest()
        assert sha256(first_bytes).hexdigest() == manifest["artifacts"][f"{city_id}.json"]
    assert (first / "manifest.json").read_bytes() == (second / "manifest.json").read_bytes()
    assert (first / "manifest.json").read_bytes() == (ROOT / "viewer/public/data/analysis/manifest.json").read_bytes().replace(b"\r\n", b"\n")


def test_canonical_text_hash_is_checkout_newline_independent():
    """[software_correctness] LF and CRLF checkouts bind the same canonical tracked-text content."""
    assert canonical_text_sha256_bytes(b"alpha\nbeta\n") == canonical_text_sha256_bytes(b"alpha\r\nbeta\r\n")


def test_delivery_sprint_hazard_expansion_is_scenario_complete_and_fail_closed(tmp_path: Path):
    """[source_conformance] Approved delivery outputs replace the predecessor-only hash invariant with ten Kyoto layers and one Fuji layer, while null safety fields remain unchanged."""
    generated = tmp_path / "analysis"
    generate_static_candidate_analyses(ROOT, generated)

    for city_id, aoi in (("kyoto_kiyomizu", "kiyomizu_gion"), ("kyoto_arashiyama", "arashiyama")):
        artifact = json.loads((generated / f"{city_id}.json").read_text(encoding="utf-8"))
        hazard = artifact["official_evidence"]["hazard"]
        expected = {
            *(f"A31B_FLOOD_2025_{aoi}_A31b-{code}" for code in ("10", "20", "30", "41", "42")),
            *(f"KYOTO_LANDSLIDE_2026_{layer}" for layer in ("g_d_rzone", "g_d_yzone", "g_j_yzone", "g_k_rzone", "g_k_yzone")),
        }
        assert set(hazard["connected_scenarios"]) == expected
        assert len(hazard["connected_scenarios"]) == 10

    fuji = json.loads((generated / "fujisawa_enoshima.json").read_text(encoding="utf-8"))
    assert fuji["official_evidence"]["hazard"]["connected_scenarios"] == ["A40_TSUNAMI_2020"]

    for city_id in CITY_IDS:
        artifact = json.loads((generated / f"{city_id}.json").read_text(encoding="utf-8"))
        exposures = artifact["official_evidence"]["hazard"]["edge_exposures"]
        keys = {(row["edge_id"], row["scenario_id"]) for row in exposures}
        assert len(keys) == len(exposures)
        for row in exposures:
            assert row["official_closure"] is None
            assert row["damage_state"] is None
            assert row["debris_present"] is None
            assert row["reason"]
            if row["relation"] == "ZERO_OVERLAP_WITHIN_KNOWN_COVERAGE":
                assert row["coverage_status"] == "WITHIN_KNOWN_COVERAGE"
                assert row["overlap_length_m"] == 0
            elif row["coverage_status"] in {"OUTSIDE_KNOWN_COVERAGE", "PARTIAL_KNOWN_COVERAGE"}:
                assert row["overlap_length_m"] is None


def test_static_analysis_detects_stale_source_and_summary_mutations(tmp_path: Path):
    """[source_conformance] Source binding or M7-summary drift must fail closed instead of serving stale analysis."""
    generated = tmp_path / "analysis"
    generate_static_candidate_analyses(ROOT, generated)
    path = generated / "kyoto_kiyomizu.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))

    stale_hash = deepcopy(artifact)
    stale_hash["input_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="input SHA-256"):
        validate_static_candidate_analysis(ROOT, stale_hash)

    promoted_m7 = deepcopy(artifact)
    promoted_m7["m7"]["ready_edge_count"] = 1
    with pytest.raises(ValueError, match="M7 summary"):
        validate_static_candidate_analysis(ROOT, promoted_m7)

    stale_report = deepcopy(artifact)
    stale_report["official_evidence"]["source_hashes"]["promotion_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="report SHA-256"):
        validate_static_candidate_analysis(ROOT, stale_report)

    stale_hazard_source = deepcopy(artifact)
    hazard_source = stale_hazard_source["official_evidence"]["hazard"]["source_catalog"]["nlni_a31b_2025_kyoto_flood"]
    hazard_source["source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="hazard source provenance"):
        validate_static_candidate_analysis(ROOT, stale_hazard_source)

    stale_hazard_revision = deepcopy(artifact)
    hazard_source = stale_hazard_revision["official_evidence"]["hazard"]["source_catalog"]["nlni_a31b_2025_kyoto_flood"]
    hazard_source["source_revision"] = "invented"
    with pytest.raises(ValueError, match="hazard source provenance"):
        validate_static_candidate_analysis(ROOT, stale_hazard_revision)

    promoted_terrain = deepcopy(artifact)
    promoted_terrain["official_evidence"]["terrain"]["products"][0]["terrain_connected"] = True
    with pytest.raises(ValueError, match="terrain evidence"):
        validate_static_candidate_analysis(ROOT, promoted_terrain)

    invented_facility_source = deepcopy(artifact)
    invented_facility_source["official_evidence"]["facility"]["records"][0]["source_id"] = "invented"
    with pytest.raises(ValueError, match="facility source binding"):
        validate_static_candidate_analysis(ROOT, invented_facility_source)

    wrong_path = deepcopy(artifact)
    connected_key = next(key for key, path_row in wrong_path["path_matrix"].items() if path_row["status"] == "CONNECTED")
    wrong_path["review_checklists"][connected_key]["rows"].reverse()
    with pytest.raises(ValueError, match="review checklist contract"):
        validate_static_candidate_analysis(ROOT, wrong_path)

    fujisawa = json.loads((generated / "fujisawa_enoshima.json").read_text(encoding="utf-8"))
    invented_time = deepcopy(fujisawa)
    invented_time["official_evidence"]["facility"]["source_catalog"]["fujisawa_webgis_toilets_accessibility"]["acquired_at"] = "2030-01-01"
    with pytest.raises(ValueError, match="facility canonical content"):
        validate_static_candidate_analysis(ROOT, invented_time)

    rewritten_attribute = deepcopy(fujisawa)
    record = rewritten_attribute["official_evidence"]["facility"]["records"][0]
    replacement = not record["source_attributes"]["ostomate_detail_available"]
    record["source_attributes"]["ostomate_detail_available"] = replacement
    record["source_attribute_entries"][0][1] = replacement
    with pytest.raises(ValueError, match="facility canonical content"):
        validate_static_candidate_analysis(ROOT, rewritten_attribute)

    rewritten_scenario = deepcopy(fujisawa)
    rewritten_scenario["official_evidence"]["hazard"]["scenarios"][0]["layer_kind"] = "invented"
    with pytest.raises(ValueError, match="scenario inventory"):
        validate_static_candidate_analysis(ROOT, rewritten_scenario)


def test_generator_cannot_bypass_source_analysis_authority(tmp_path: Path, monkeypatch):
    """[software_correctness] Removing the source analysis call kills generation instead of falling back to viewer logic."""
    def rejected(*_args, **_kwargs):
        raise RuntimeError("source analysis authority invoked")

    monkeypatch.setattr(generator, "build_static_candidate_analysis", rejected)
    with pytest.raises(RuntimeError, match="source analysis authority invoked"):
        generate_static_candidate_analyses(ROOT, tmp_path)


def test_source_analysis_handles_components_ties_invalid_values_and_input_immutability():
    """[software_correctness] Canonical analysis is deterministic, lexical, non-mutating, and rejects bool/NaN coordinates."""
    nodes = [_node(value) for value in ("a", "b", "c", "d", "x", "y", "z")]
    edges = [
        _edge("e2", "a", "b", [[0.0, 0.0], [1.0, 0.0]]),
        _edge("e1", "a", "c", [[0.0, 0.0], [0.0, 1.0]]),
        _edge("e4", "b", "d", [[1.0, 0.0], [1.0, 1.0]]),
        _edge("e3", "c", "d", [[0.0, 1.0], [1.0, 1.0]]),
        _edge("e5", "y", "z", [[3.0, 0.0], [4.0, 0.0]]),
    ]
    original_nodes = deepcopy(nodes)
    original_edges = deepcopy(edges)
    official = {"m7": {"status": "NOT_COMPUTED", "evidence_ready_count": 0, "computed_count": 0}}
    context = {
        "city_id": "fixture",
        "source_artifact_ids": ["nodes", "edges"],
        "source_revision_ids": [],
        "input_sha256": "a" * 64,
        "input_hashes": {"node_sha256": "b" * 64, "edge_sha256": "c" * 64},
        "snapshot_at": "2026-09-08T00:00:00Z",
        "source_id": "fixture",
    }

    result = build_static_candidate_analysis(context, nodes, edges, official, [])

    assert result["topology"]["node_count"] == 7
    assert result["topology"]["connected_components"] == 3
    assert result["selectable_node_ids"] == ["a", "d", "x"]
    assert result["path_fixture"]["edge_ids"] == ["e1", "e3"]
    assert result["path_matrix"]["a__x"]["status"] == "DISCONNECTED"
    assert nodes == original_nodes
    assert edges == original_edges

    for invalid in (True, float("nan"), float("inf")):
        bad_edges = deepcopy(edges)
        bad_edges[0]["geometry"]["coordinates"][0][0] = invalid
        with pytest.raises(ValueError, match="finite"):
            build_static_candidate_analysis(context, nodes, bad_edges, official, [])

    wrong_geometry = deepcopy(edges)
    wrong_geometry[0]["geometry"]["type"] = "Polygon"
    with pytest.raises(ValueError, match="LineString"):
        build_static_candidate_analysis(context, nodes, wrong_geometry, official, [])
