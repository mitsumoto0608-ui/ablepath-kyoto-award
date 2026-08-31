"""Candidate network tests."""
import json
from copy import deepcopy
from pathlib import Path

from src.analysis.candidate_network import summarize


def _edge_with_complete_m7_input():
    fields = (
        "clear_width_m",
        "left_buildings",
        "right_buildings",
        "variant",
        "official_closure",
        "hazard_data_status",
    )
    provenance = {
        field: {
            "source_id": f"survey:{field}",
            "revision_id": "survey-2026-08-31-v1",
            "source_sha256": "a" * 64,
            "evidence_status": "SOURCE_TRACEABLE",
        }
        for field in fields
    }
    provenance["left_buildings"]["observed_count"] = 1
    provenance["right_buildings"]["observed_count"] = 0
    provenance["left_buildings"]["coverage_status"] = "COMPLETE"
    provenance["right_buildings"]["coverage_status"] = "COMPLETE"
    return {
        "properties": {
            "edge_id": "e",
            "from_node": "a",
            "to_node": "b",
            "clear_width_m": 4.0,
            "left_buildings": [
                {
                    "height_m": 7.0,
                    "setback_m": 2.0,
                    "damage_state": "COLLAPSED",
                    "debris_present": True,
                }
            ],
            "right_buildings": [],
            "variant": "mean_case",
            "official_closure": None,
            "hazard_data_status": "UNKNOWN",
            "m7_provenance": provenance,
        },
        "geometry": {"coordinates": [[0, 0], [1, 0]]},
    }

def test_candidate_summary_is_connected_and_reasoned_null():
    """[software_correctness] Candidate path has coordinate-degree units and no M7 promotion."""
    nodes=[{"properties":{"node_id":"a"}},{"properties":{"node_id":"b"}}]
    edges=[{"properties":{"edge_id":"e","from_node":"a","to_node":"b"},"geometry":{"coordinates":[[0,0],[1,0]]}}]
    result=summarize(nodes,edges,"a","b")
    assert result["path"]["status"] == "CONNECTED" and result["path"]["unit"] == "coordinate_degree"
    assert result["m7"]["readiness"][0]["m7_result"] is None


def test_complete_nested_m7_input_is_callable_and_evidence_ready_without_computation():
    """[source_conformance] Exact nested API values and receipts make M7 callable/ready, but the helper never computes it."""
    nodes = [{"properties": {"node_id": "a"}}, {"properties": {"node_id": "b"}}]

    result = summarize(nodes, [_edge_with_complete_m7_input()], "a", "b")
    readiness = result["m7"]["readiness"][0]

    assert readiness == {
        "edge_id": "e",
        "status": "NOT_COMPUTED",
        "m7_api_structurally_callable": True,
        "m7_evidence_ready": True,
        "m7_computed": False,
        "m7_result": None,
        "missing_fields": [],
        "reason": "M7 inputs are structurally callable and evidence-ready; M7 was not run.",
    }
    assert result["m7"]["ready_edge_count"] == 1
    assert result["m7"]["computed_edge_count"] == 0


def test_incomplete_or_invalid_m7_input_fails_closed_with_reasoned_null():
    """[software_correctness] Missing evidence and invalid exact-API values cannot silently become M7-ready or computed."""
    nodes = [{"properties": {"node_id": "a"}}, {"properties": {"node_id": "b"}}]
    cases = []

    missing_side_evidence = _edge_with_complete_m7_input()
    del missing_side_evidence["properties"]["m7_provenance"]["right_buildings"]
    cases.append((missing_side_evidence, True))

    missing_width = _edge_with_complete_m7_input()
    del missing_width["properties"]["clear_width_m"]
    cases.append((missing_width, False))

    invalid_source_hash = _edge_with_complete_m7_input()
    invalid_source_hash["properties"]["m7_provenance"]["clear_width_m"]["source_sha256"] = "unbound"
    cases.append((invalid_source_hash, True))

    incomplete_side_coverage = _edge_with_complete_m7_input()
    incomplete_side_coverage["properties"]["m7_provenance"]["right_buildings"]["coverage_status"] = "PARTIAL"
    cases.append((incomplete_side_coverage, True))

    invalid_values = (
        ("clear_width_m", True),
        ("clear_width_m", float("nan")),
        ("clear_width_m", float("inf")),
        ("variant", "pessimistic"),
        ("official_closure", 0),
        ("hazard_data_status", "OPEN"),
    )
    for field, value in invalid_values:
        invalid = _edge_with_complete_m7_input()
        invalid["properties"][field] = value
        cases.append((invalid, False))

    invalid_building = _edge_with_complete_m7_input()
    del invalid_building["properties"]["left_buildings"][0]["setback_m"]
    cases.append((invalid_building, False))

    invalid_nested_number = _edge_with_complete_m7_input()
    invalid_nested_number["properties"]["left_buildings"][0]["height_m"] = float("inf")
    cases.append((invalid_nested_number, False))

    silent_empty_default = _edge_with_complete_m7_input()
    silent_empty_default["properties"]["left_buildings"] = []
    cases.append((silent_empty_default, True))

    for edge, structurally_callable in cases:
        result = summarize(nodes, [deepcopy(edge)], "a", "b")
        readiness = result["m7"]["readiness"][0]
        assert readiness["m7_api_structurally_callable"] is structurally_callable
        assert readiness["m7_evidence_ready"] is False
        assert readiness["m7_computed"] is False
        assert readiness["m7_result"] is None
        assert readiness["missing_fields"]
        assert readiness["reason"]
        assert result["m7"]["ready_edge_count"] == 0
        assert result["m7"]["computed_edge_count"] == 0

def test_candidate_summary_rejects_orphan_endpoint():
    """[software_correctness] An orphan edge cannot become connected analysis."""
    try: summarize([{"properties":{"node_id":"a"}}],[{"properties":{"edge_id":"e","from_node":"a","to_node":"b"},"geometry":{"coordinates":[[0,0],[1,0]]}}],"a","b")
    except ValueError: return
    raise AssertionError("orphan endpoint must fail")

def test_candidate_summary_has_stable_ties_and_reasoned_disconnection():
    """[software_correctness] Equal coordinate-degree paths select edge IDs lexically; a separate node is reasoned-null."""
    nodes=[{"properties":{"node_id":x}} for x in ["a", "b", "c", "d", "z"]]
    edges=[
        {"properties":{"edge_id":"e2","from_node":"a","to_node":"b"},"geometry":{"coordinates":[[0,0],[1,0]]}},
        {"properties":{"edge_id":"e1","from_node":"a","to_node":"c"},"geometry":{"coordinates":[[0,0],[0,1]]}},
        {"properties":{"edge_id":"e4","from_node":"b","to_node":"d"},"geometry":{"coordinates":[[1,0],[1,1]]}},
        {"properties":{"edge_id":"e3","from_node":"c","to_node":"d"},"geometry":{"coordinates":[[0,1],[1,1]]}},
    ]
    connected=summarize(nodes,edges,"a","d")
    assert connected["path"]["edge_ids"] == ["e1", "e3"]
    assert connected["path"]["unit"] == "coordinate_degree"
    assert connected["m7"]["ready_edge_count"] == 0
    assert {row["status"] for row in connected["m7"]["readiness"]} == {"NOT_COMPUTED"}
    disconnected=summarize(nodes,edges,"a","z")
    assert disconnected["path"] == {
        "status":"DISCONNECTED", "edge_ids":[], "geometric_length":None, "unit":"coordinate_degree",
        "reason":"No candidate-network connection exists between the selected nodes; accessibility, safety, and operation are unconfirmed.",
    }


    root = Path(__file__).parents[2]
    total_edges = total_ready = total_computed = 0
    for city_id in ("kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"):
        artifact = json.loads(
            (root / "viewer" / "public" / "data" / "maps" / f"{city_id}.candidate_edges.geojson").read_text(encoding="utf-8")
        )
        actual_edges = artifact["features"]
        actual_node_ids = sorted(
            {
                endpoint
                for edge in actual_edges
                for endpoint in (edge["properties"]["from_node"], edge["properties"]["to_node"])
            }
        )
        actual_nodes = [{"properties": {"node_id": node_id}} for node_id in actual_node_ids]
        actual = summarize(actual_nodes, actual_edges, actual_node_ids[0], actual_node_ids[-1])
        total_edges += len(actual_edges)
        total_ready += actual["m7"]["ready_edge_count"]
        total_computed += actual["m7"]["computed_edge_count"]
        assert all(row["m7_result"] is None for row in actual["m7"]["readiness"])
        assert all(row["missing_fields"] and row["reason"] for row in actual["m7"]["readiness"])

    assert total_edges == 612
    assert total_ready == 0
    assert total_computed == 0
