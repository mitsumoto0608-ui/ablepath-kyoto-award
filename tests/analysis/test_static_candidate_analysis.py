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
PRE_TK02_SHA256 = {
    "kyoto_kiyomizu": "e47d38b18d2f5f17954492d0704c6a406fac4d32cc03aadaa774c0b850846050",
    "kyoto_arashiyama": "2e739a5645182fb3b6d2bc071f0e3c6d06b09109d4e77eaeaf4ed3d0310673b5",
    "fujisawa_enoshima": "a801bf4b2378be151a04444c55255eca176559816d594218bc5f637bff94a098",
}
SOURCE_BOUND_SUCCESSOR_SHA256 = {
    "kyoto_kiyomizu": "9abc8824003b6270cf6eb0faaee21e3976845b2c9d103743691f706abd4ca921",
    "kyoto_arashiyama": "1ba2c82e7ee2acfce94182a8a285cedea41cd73a6630cbcce51050d818abb22b",
    "fujisawa_enoshima": "b382ba453cf2166e9242fa32433682c36a2f38b5b87062cdbc7ba4c92fc4ad37",
}
PRE_TK02_SOURCE_HASHES = {
    "kyoto_kiyomizu": {
        "kyoto_status_sha256": "991ca56c11a0c50c29f360ddbb42cf4d6fee98c6a382bb4815186e9088171731",
        "terrain_inventory_sha256": "b7eddd300d3930d93b137fdc5500429a4c4eb05f161b240232af400fac37e81f",
    },
    "kyoto_arashiyama": {
        "kyoto_status_sha256": "991ca56c11a0c50c29f360ddbb42cf4d6fee98c6a382bb4815186e9088171731",
        "terrain_inventory_sha256": "f624053384847964a0b6473687b24cad00a8f81513da047ddb8e3d82d9e83f3b",
    },
    "fujisawa_enoshima": {
        "terrain_inventory_sha256": "f1a785e878ae0e3ca6a2b33c80eaf12bbcce7c1583d06c0f6c8d753b322aa5cb",
        "facility_receipt_sha256": "90b0a7b1c95b429d3b1d2e878f0856a36c9f84d131d3f281645db4e8f703d52a",
    },
}


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
        committed_bytes = committed.read_bytes().replace(b"\r\n", b"\n")
        assert first_bytes == committed_bytes
        assert second_bytes == committed_bytes
        assert sha256(first_bytes).hexdigest() == sha256(second_bytes).hexdigest()
        assert sha256(first_bytes).hexdigest() == SOURCE_BOUND_SUCCESSOR_SHA256[city_id]
        assert SOURCE_BOUND_SUCCESSOR_SHA256[city_id] != PRE_TK02_SHA256[city_id]
    assert (first / "manifest.json").read_bytes() == (second / "manifest.json").read_bytes()
    assert (first / "manifest.json").read_bytes() == (ROOT / "viewer/public/data/analysis/manifest.json").read_bytes().replace(b"\r\n", b"\n")


def test_canonical_text_hash_is_checkout_newline_independent():
    """[software_correctness] LF and CRLF checkouts bind the same canonical tracked-text content."""
    assert canonical_text_sha256_bytes(b"alpha\nbeta\n") == canonical_text_sha256_bytes(b"alpha\r\nbeta\r\n")


def test_successor_diff_is_limited_to_corrected_source_bindings(tmp_path: Path):
    """[source_conformance] Reversing only reviewed LF/source-binding updates reconstructs each pre-TK02 byte hash."""
    generated = tmp_path / "analysis"
    generate_static_candidate_analyses(ROOT, generated)
    for city_id in CITY_IDS:
        artifact = json.loads((generated / f"{city_id}.json").read_text(encoding="utf-8"))
        source_hashes = artifact["official_evidence"]["source_hashes"]
        for key, old_hash in PRE_TK02_SOURCE_HASHES[city_id].items():
            source_hashes[key] = old_hash
        artifact["official_evidence"]["terrain"]["receipt_sha256"] = PRE_TK02_SOURCE_HASHES[city_id]["terrain_inventory_sha256"]
        source_hashes.pop("kyoto_facility_category_status_sha256", None)
        source_hashes.pop("plateau_inventory_sha256", None)
        predecessor = (json.dumps(artifact, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        assert sha256(predecessor).hexdigest() == PRE_TK02_SHA256[city_id]


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
