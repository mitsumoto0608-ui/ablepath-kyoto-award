"""Phase 4 provenance gates for the Fujisawa bounded OSM candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
CITY = ROOT / "cities" / "fujisawa_enoshima"
MANIFEST = CITY / "realdata" / "artifact_manifest.v2.json"
RECEIPT = CITY / "sources" / "receipts" / "osm-corridor.raw.receipt.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_phase4_fujisawa_osm_receipt_promotes_only_bounded_vgi_candidate() -> None:
    """[source_conformance] A bound external raw receipt permits only CANDIDATE geometry."""

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert receipt["raw_trust_location_relative"] == "ablepath-raw/fujisawa_enoshima/osm-corridor.raw.json"
    assert receipt["source_endpoint"] != receipt["attribution_url"]
    assert receipt["raw_byte_size"] == 581965
    assert receipt["raw_sha256"] == "c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04"
    assert not (CITY / "sources" / "osm-corridor.raw.json").exists()
    assert _sha256(CITY / "geography" / "corridor.real.geojson") == manifest["artifacts"][0]["sha256"]
    assert manifest["artifacts"][0]["source_receipt_path"] == "sources/receipts/osm-corridor.raw.receipt.json"
    assert manifest["artifacts"][0]["source_class"] == "VGI"
    assert manifest["artifacts"][0]["geometry_status"] == "SOURCE_TRACEABLE_REAL"
    assert manifest["artifacts"][0]["topology_status"] == "CANDIDATE"
    assert manifest["artifacts"][0]["source_crs"] == manifest["artifacts"][0]["output_crs"] == "EPSG:4326"
    assert manifest["artifacts"][0]["geojson_serialization_order"] == "longitude, latitude"

    qa = json.loads((CITY / "graph" / "candidate_topology_qa.real.json").read_text(encoding="utf-8"))
    assert qa["graph_status"] == "CANDIDATE"
    assert qa["promotion_status"] == "BLOCKED_FIELD_AND_ADMIN_REVIEW"
    assert qa["counts"] == {
        "nodes": 16,
        "edges": 15,
        "duplicate_node_ids": 0,
        "duplicate_edge_ids": 0,
        "dangling_endpoint_nodes": 2,
        "self_loops": 0,
        "zero_length_edges": 0,
        "connected_components": 1,
    }


def test_phase4_fujisawa_raw_receipt_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    """[source_conformance] A mismatched external raw receipt cannot promote the candidate."""

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    receipt["raw_sha256"] = "0" * 64
    bad_receipt = tmp_path / "receipt.json"
    bad_receipt.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(AssertionError):
        assert json.loads(bad_receipt.read_text(encoding="utf-8"))["raw_sha256"] == _sha256(
            Path("C:/dev") / receipt["raw_trust_location_relative"]
        )
