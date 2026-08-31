"""Candidate network tests."""
from src.analysis.candidate_network import summarize

def test_candidate_summary_is_connected_and_reasoned_null():
    """[software_correctness] Candidate path has coordinate-degree units and no M7 promotion."""
    nodes=[{"properties":{"node_id":"a"}},{"properties":{"node_id":"b"}}]
    edges=[{"properties":{"edge_id":"e","from_node":"a","to_node":"b"},"geometry":{"coordinates":[[0,0],[1,0]]}}]
    result=summarize(nodes,edges,"a","b")
    assert result["path"]["status"] == "CONNECTED" and result["path"]["unit"] == "coordinate_degree"
    assert result["m7"]["readiness"][0]["m7_result"] is None

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
