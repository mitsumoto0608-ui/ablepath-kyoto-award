"""Static candidate-analysis authority and deterministic generation tests."""

from __future__ import annotations

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from scripts.build_candidate_analysis import generate_static_candidate_analyses
from src.analysis.static_candidate_analysis import (
    build_static_candidate_analysis,
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
    for city_id in CITY_IDS:
        committed = ROOT / "viewer" / "public" / "data" / "analysis" / f"{city_id}.json"
        first_bytes = (first / f"{city_id}.json").read_bytes()
        second_bytes = (second / f"{city_id}.json").read_bytes()
        assert first_bytes == committed.read_bytes()
        assert second_bytes == committed.read_bytes()
        assert sha256(first_bytes).hexdigest() == sha256(second_bytes).hexdigest()


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


def test_source_analysis_handles_components_ties_invalid_values_and_input_immutability():
    """[software_correctness] Canonical analysis is deterministic, lexical, non-mutating, and rejects bool/NaN coordinates."""
    nodes = [_node(value) for value in ("a", "b", "c", "d", "y", "z")]
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

    assert result["topology"]["connected_components"] == 2
    assert result["selectable_node_ids"] == ["a", "d", "y"]
    assert result["path_fixture"]["edge_ids"] == ["e1", "e3"]
    assert result["path_matrix"]["a__y"]["status"] == "DISCONNECTED"
    assert nodes == original_nodes
    assert edges == original_edges

    for invalid in (True, float("nan"), float("inf")):
        bad_edges = deepcopy(edges)
        bad_edges[0]["geometry"]["coordinates"][0][0] = invalid
        with pytest.raises(ValueError, match="finite"):
            build_static_candidate_analysis(context, nodes, bad_edges, official, [])
