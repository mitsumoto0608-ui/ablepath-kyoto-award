"""Phase 4 P0 checks for the bounded Arashiyama VGI candidate artifact."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "cities" / "kyoto_arashiyama"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _records_bind_receipt(records: list[dict], expected_source_sha256: str) -> bool:
    return bool(records) and all(record.get("source_sha256") == expected_source_sha256 for record in records)


def test_receipt_binds_normalized_candidate_artifacts_to_fixed_osm_source() -> None:
    """[source_conformance] receipt, query, manifest, and normalized candidate hashes preserve VGI lineage."""
    receipt = json.loads((PACK / "sources" / "retention_receipt.json").read_text(encoding="utf-8"))
    manifest = json.loads((PACK / "sources" / "realdata_manifest.json").read_text(encoding="utf-8"))
    graph = json.loads((PACK / "graph" / "graph_provenance.real.json").read_text(encoding="utf-8"))
    source = receipt["external_sources"]["osm_arashiyama_20260829.raw.json"]
    assert source["repository_copy"] is None
    assert source["retention_verified_this_run"] is True
    assert source["raw_byte_size"] == 106_464
    assert source["sha256"] == "1cde93d68bebf633989e825cbd5ac1e772cee81508043f44beb311250a1e8013"
    assert _sha(PACK / "sources" / "osm_arashiyama_20260829.overpassql") == graph["retrieval_query_sha256"]
    assert len(manifest["artifacts"]) == 1
    assert manifest["artifacts"][0]["artifact_path"] == "geography/corridor.real.geojson"
    assert _records_bind_receipt(manifest["artifacts"], source["sha256"])
    for output in graph["outputs"]:
        assert _sha(PACK / output["path"]) == output["sha256"]


def test_mismatched_receipt_hash_cannot_establish_source_traceability() -> None:
    """[source_conformance] fatal fixture: a changed raw SHA is not accepted as the manifest's VGI source."""
    receipt = json.loads((PACK / "sources" / "retention_receipt.json").read_text(encoding="utf-8"))
    manifest = json.loads((PACK / "sources" / "realdata_manifest.json").read_text(encoding="utf-8"))
    expected = receipt["external_sources"]["osm_arashiyama_20260829.raw.json"]["sha256"]
    mutated_records = [dict(record) for record in manifest["artifacts"]]
    mutated_records[0]["source_sha256"] = "0" * 64
    assert not _records_bind_receipt(mutated_records, expected)


def test_status_issues_only_artifact_capability_not_connection_claims() -> None:
    """[source_conformance] P0 ingestion cannot promote viewer, model, analysis, M7, or real-geometry connection."""
    status = json.loads((PACK / "realdata_status.json").read_text(encoding="utf-8"))
    assert status["SOURCE_STAGED"] is True
    assert status["NORMALIZED_INGESTED"] is True
    assert status["SOURCE_TRACEABLE_CANDIDATE_ARTIFACT_AVAILABLE"] is True
    assert "REAL_GEOMETRY_CONNECTED" not in status
    assert status["VIEWER_CONNECTED"] is True
    assert status["ANALYSIS_CONNECTED"] is True
    assert status["VIEWER_CONNECTED_SCOPE"] == "SOURCE_TRACEABLE_VGI_CANDIDATE_EXPLICIT_OPT_IN_ONLY"
    assert status["ANALYSIS_CONNECTED_SCOPE"] == "SOURCE_TRACEABLE_VGI_CANDIDATE_EXPLICIT_OPT_IN_ONLY"
    assert all(status[key] is False for key in ("MODEL_CONNECTED", "M7_CONNECTED"))
