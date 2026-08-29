# -*- coding: utf-8 -*-
"""Hokonavi 2024 reference mapping contract tests; no production adapter exists yet."""
from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path
from copy import deepcopy

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "hokonavi_2024_mapping.yaml"
MAPPING_DOC = ROOT / "docs" / "data" / "HOKONAVI_2024_MAPPING.md"
LOSS_DOC = ROOT / "docs" / "data" / "HOKONAVI_2024_INFORMATION_LOSS.md"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "hokonavi_2024"
BRIEF = ROOT / "AI_TASKS" / "05_HOKONAVI_2024_ADAPTER_IMPLEMENTATION.md"
STATUSES = {"FULL", "PARTIAL", "SIDECAR_REQUIRED", "UNMAPPED", "NOT_APPLICABLE"}


def load_contract() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_required_contract_metadata_is_fixed():
    """[source_conformance] 仕様版・公式URL・確認日・新版確認を必須metadataとして固定する。"""
    contract = load_contract()
    required = {
        "contract_id", "contract_version", "title", "contract_status",
        "adapter_implemented", "source_specification", "reference_scope",
        "mapping_status_enum", "mapping_summary", "crs", "unknown_policy",
        "direction_codebook", "in_out_codebook", "validation_contract", "width_separation", "information_loss_report", "fixture_root", "mappings",
    }
    assert required <= contract.keys()
    source = contract["source_specification"]
    assert source["version"] == "2024年7月"
    assert source["publisher"] == "国土交通省 政策統括官付"
    assert source["official_url"].startswith("https://www.mlit.go.jp/")
    assert type(source["newer_revision_found"]) is bool
    assert contract["adapter_implemented"] is False


def test_mapping_status_is_complete_and_summary_matches():
    """[software_correctness] 全40 mappingが許可enumを持ち、summaryを実数と一致させる。"""
    contract = load_contract()
    mappings = contract["mappings"]
    assert len(mappings) == contract["mapping_summary"]["field_count"] == 40
    assert set(contract["mapping_status_enum"]) == STATUSES
    assert all(mapping["status"] in STATUSES for mapping in mappings)
    assert Counter(m["status"] for m in mappings) == contract["mapping_summary"]["by_status"]
    assert Counter(m["entity"] for m in mappings) == contract["mapping_summary"]["by_entity"]
    ids = [mapping["id"] for mapping in mappings]
    assert len(ids) == len(set(ids)), "mapping id must be unique"
    required = {"id", "entity", "concept", "direction", "hokonavi_fields",
                "ablepath_fields", "status", "source_role", "source", "adapter_action"}
    assert all(required <= mapping.keys() for mapping in mappings)


def test_node_and_link_are_separate_and_cover_required_concepts():
    """[source_conformance] node/linkを分離し、端点・方向・geometry・connector等を明示する。"""
    mappings = load_contract()["mappings"]
    node = {m["concept"] for m in mappings if m["entity"] == "node"}
    link = {m["concept"] for m in mappings if m["entity"] == "link"}
    assert {"stable_id", "latitude", "longitude", "geometry", "level", "connector"} <= node
    assert {
        "stable_id", "from_node", "to_node", "geometry", "direction",
        "route_path_structure", "route_type", "width", "longitudinal_slope",
        "step", "stairs", "ramp", "elevator", "source_measurement_method",
    } <= link
    assert all(m["entity"] in {"node", "link", "metadata", "sidecar"} for m in mappings)


def test_stable_ids_and_endpoint_references_are_not_reassigned():
    """[software_correctness] stable IDとfrom/toをpreserve契約にし、node IDとlink IDを混ぜない。"""
    by_id = {m["id"]: m for m in load_contract()["mappings"]}
    assert by_id["NODE_ID"]["adapter_action"] == "preserve"
    assert by_id["LINK_ID"]["adapter_action"] == "preserve"
    assert by_id["LINK_FROM"]["ablepath_fields"] == ["from_node"]
    assert by_id["LINK_TO"]["ablepath_fields"] == ["to_node"]
    assert by_id["LINK_FROM"]["hokonavi_fields"] == ["start_id"]
    assert by_id["LINK_TO"]["hokonavi_fields"] == ["end_id"]


def test_crs_metadata_cites_jgd2011_and_axis_order():
    """[source_conformance] §2.2のJGD2011とGeoJSONのlon/lat axis orderを固定する。"""
    crs = load_contract()["crs"]
    assert crs == {
        "source_name": "JGD2011",
        "coordinate_representation": "decimal_degrees",
        "axis_order_in_ablepath_geojson": ["longitude", "latitude"],
        "source_section": "2.2",
        "source_document_pages": [4],
        "source_pdf_file_pages": [6],
    }


def test_source_fact_and_ablepath_design_provenance_are_separate():
    """[source_conformance] 原典頁とAblePath正本を別roleで記録し、印刷頁/PDF頁を混ぜない。"""
    for mapping in load_contract()["mappings"]:
        source = mapping["source"]
        if mapping["source_role"] == "SOURCE_FACT":
            assert source["section"].strip(), mapping["id"]
            assert source["document_pages"], mapping["id"]
            assert source["pdf_file_pages"], mapping["id"]
            assert len(source["document_pages"]) == len(source["pdf_file_pages"]), mapping["id"]
            assert all(pdf == document + 2 for document, pdf in
                       zip(source["document_pages"], source["pdf_file_pages"])), mapping["id"]
        else:
            assert mapping["source_role"] == "ABLEPATH_DESIGN"
            assert source["document"].startswith("docs/"), mapping["id"]
            assert mapping["scope_exclusion"]["source_role"] == "SOURCE_FACT"
            exclusion = mapping["scope_exclusion"]
            assert len(exclusion["document_pages"]) == len(exclusion["pdf_file_pages"]), mapping["id"]


def test_corrected_page_anchors_are_fixed():
    """[source_conformance] 表3.2/3.3/3.8、取得方法、§3.4の印刷頁とPDFファイル頁を固定する。"""
    by_id = {m["id"]: m for m in load_contract()["mappings"]}
    assert by_id["LINK_ID"]["source"]["document_pages"] == [13, 16]
    assert by_id["LINK_ID"]["source"]["pdf_file_pages"] == [15, 18]
    assert by_id["RANK"]["source"]["document_pages"] == [13, 21]
    assert by_id["RANK"]["source"]["pdf_file_pages"] == [15, 23]
    assert by_id["NODE_ID"]["source"]["document_pages"] == [33, 34]
    assert by_id["NODE_ID"]["source"]["pdf_file_pages"] == [35, 36]
    assert by_id["LINK_GEOMETRY"]["source"]["document_pages"] == [37]
    assert by_id["LINK_GEOMETRY"]["source"]["pdf_file_pages"] == [39]
    assert by_id["LINK_FROM"]["source"]["document_pages"] == [5, 13]
    assert by_id["LINK_FROM"]["source"]["pdf_file_pages"] == [7, 15]
    method = by_id["SOURCE_METHOD"]
    assert method["source"]["document_pages"] == [13, 16, 22]
    assert method["source"]["pdf_file_pages"] == [15, 18, 24]
    unknown = by_id["UNKNOWN_SEMANTICS"]["source"]
    assert unknown["document_pages"] == [13, 14, 15]
    assert unknown["pdf_file_pages"] == [15, 16, 17]


def test_static_width_and_m7_remaining_width_are_disjoint():
    """[software_correctness] static=4.00mとscenario=0.73mを別fieldに保ち上書きを禁止する。"""
    separation = load_contract()["width_separation"]
    assert separation["static_field"] == "clear_width_static_m"
    assert separation["scenario_field"] == "remaining_clear_width_m"
    assert separation["static_field"] != separation["scenario_field"]
    assert separation["overwrite_forbidden"] is True
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    edge = expected["edges"][0]
    assert edge["clear_width_static_m"] == 4.0
    assert "remaining_clear_width_m" not in edge
    assert "scenario_sidecar" not in edge


def test_unknown_is_preserved_without_safe_default():
    """[software_correctness] UNKNOWNを0/false/OPEN/PASS/safeへ落とさない。"""
    policy = load_contract()["unknown_policy"]
    assert policy["preserve_literal"] == "UNKNOWN"
    assert policy["source_unknown_code"] == 99
    assert policy["unclassified_missing"] == "UNKNOWN"
    assert policy["semantic_blank_rules_required"] is True
    forbidden = {str(value).lower() for value in policy["forbidden_coercions"]}
    assert {"0", "false", "open", "pass", "safe"} <= forbidden
    source = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    source_link = next(f["properties"] for f in source["features"] if f["properties"].get("link_id") == "SYNTHETIC-L004")
    edge = next(e for e in expected["edges"] if e["edge_id"] == "SYNTHETIC-L004")
    assert source_link["lev_diff"] == 99
    assert edge["step_class"] == "UNKNOWN"
    assert edge["source_unknown"]["lev_diff"] == 99
    assert "scenario_sidecar" not in edge


def test_direction_codebook_is_exact_and_fixture_covers_all_codes():
    """[source_conformance] direction 1/2/3/99をexact enumとして固定し99だけUNKNOWNにする。"""
    contract = load_contract()
    assert contract["direction_codebook"] == {
        1: "BIDIRECTIONAL", 2: "FORWARD", 3: "REVERSE", 99: "UNKNOWN"
    }
    source = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    source_codes = {p["link_id"]: p["direction"] for p in
                    (f["properties"] for f in source["features"] if f["properties"]["entity"] == "link")}
    outputs = {edge["edge_id"]: edge["travel_direction"] for edge in expected["edges"]}
    assert {source_codes[key]: outputs[key] for key in source_codes} == {
        1: "BIDIRECTIONAL", 2: "FORWARD", 3: "REVERSE", 99: "UNKNOWN"
    }


def test_in_out_codebook_is_exact_and_raw_code_is_preserved():
    """[source_conformance] in_out 1/2/3をOUTDOOR/BOUNDARY/INDOORへexact対応しraw codeを保持する。"""
    assert load_contract()["in_out_codebook"] == {1: "OUTDOOR", 2: "BOUNDARY", 3: "INDOOR"}
    source = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    source_nodes = {f["properties"]["node_id"]: f["properties"] for f in source["features"]
                    if f["properties"]["entity"] == "node"}
    expected_nodes = {node["node_id"]: node for node in expected["nodes"]}
    assert {node["in_out"] for node in source_nodes.values()} == {1, 2, 3}
    for node_id, node in expected_nodes.items():
        raw = source_nodes[node_id]["in_out"]
        assert node["in_out_code"] == raw
        assert node["node_type"] == load_contract()["in_out_codebook"][raw]
    assert expected_nodes["SYNTHETIC-N003"]["node_type"] == "BOUNDARY"
    assert expected_nodes["SYNTHETIC-N004"]["node_type"] == "BOUNDARY"


def test_route_and_structure_codebooks_are_not_swapped():
    """[source_conformance] route_type 4/5/6/7とrt_struct 1..4の原典意味をfixtureで固定する。"""
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    route_types = {edge["route_type_code"]: edge["route_type"] for edge in expected["edges"]}
    assert route_types == {
        1: "NO_ASSOCIATED_ATTRIBUTE", 4: "ELEVATOR", 5: "ESCALATOR", 6: "STAIRS", 7: "RAMP"
    }
    structures = {edge["route_structure_code"]: edge["route_structure"] for edge in expected["edges"]}
    assert structures == {
        1: "PHYSICALLY_SEPARATED", 2: "NOT_PHYSICALLY_SEPARATED",
        3: "CROSSWALK", 4: "UNMARKED_ROAD_CROSSING",
    }
    elevator = next(edge for edge in expected["edges"] if edge["route_type_code"] == 4)
    assert elevator["connector_sidecar"]["elevator_code"] == 3
    assert all(edge["connector_sidecar"]["elevator_code"] == 1
               for edge in expected["edges"] if edge["route_type_code"] != 4)


def test_route_structure_and_route_type_have_disjoint_targets():
    """[software_correctness] rt_structとroute_typeを同じedge_typeへ畳み込まない。"""
    by_id = {m["id"]: m for m in load_contract()["mappings"]}
    structure = set(by_id["ROUTE_STRUCTURE"]["ablepath_fields"])
    route_type = set(by_id["ROUTE_TYPE"]["ablepath_fields"])
    assert "route_structure" in structure
    assert "route_type" in route_type
    assert "edge_type" not in structure | route_type
    assert structure.isdisjoint(route_type)


def test_fixture_covers_domains_and_preserves_loss_traceability():
    """[software_correctness] floor/direction/connector/障壁属性とloss IDをfixtureで直接固定する。"""
    source = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    node_props = [f["properties"] for f in source["features"] if f["properties"]["entity"] == "node"]
    link_props = [f["properties"] for f in source["features"] if f["properties"]["entity"] == "link"]
    assert {n["floor"] for n in node_props} == {0, 1, -1, 1.5}
    assert {l["direction"] for l in link_props} == {1, 2, 3, 99}
    assert {l["route_type"] for l in link_props} >= {4, 5, 6, 7}
    assert any(l["stair"] == 12 for l in link_props)
    assert any(l["elevator"] == 1 for l in link_props)
    assert all(edge["source_sidecar"]["loss_ids"] for edge in expected["edges"])
    required = {"hokonavi_rank", "travel_direction", "route_structure_code", "route_type_code",
                "longitudinal_slope_class", "step_class", "connector_sidecar"}
    assert all(required <= edge.keys() for edge in expected["edges"])


def test_full_outputs_and_mapping_reachability_are_explicit():
    """[software_correctness] FULL出力と全mappingのoutput/sidecar/reject到達をfixtureで固定する。"""
    contract = load_contract()
    source = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    assert expected["crs_metadata"] == {"name": "JGD2011", "axis_order": ["longitude", "latitude"]}
    node_required = {"node_id", "latitude", "longitude", "geometry", "level", "node_type",
                     "in_out_code", "incident_edge_ids"}
    edge_required = {"edge_id", "from_node", "to_node", "geometry", "length_m"}
    assert all(node_required <= node.keys() for node in expected["nodes"])
    assert all(edge_required <= edge.keys() for edge in expected["edges"])
    source_nodes = {f["properties"]["node_id"]: f for f in source["features"]
                    if f["properties"]["entity"] == "node"}
    source_links = {f["properties"]["link_id"]: f for f in source["features"]
                    if f["properties"]["entity"] == "link"}
    for node in expected["nodes"]:
        feature = source_nodes[node["node_id"]]
        props = feature["properties"]
        assert node["node_id"] == props["node_id"]
        assert node["latitude"] == props["lat"]
        assert node["longitude"] == props["lon"]
        assert node["geometry"] == feature["geometry"]
        assert node["geometry"] is not None
    for edge in expected["edges"]:
        feature = source_links[edge["edge_id"]]
        props = feature["properties"]
        assert edge["edge_id"] == props["link_id"]
        assert edge["from_node"] == props["start_id"]
        assert edge["to_node"] == props["end_id"]
        assert edge["geometry"] == feature["geometry"]
        assert type(edge["length_m"]) is float and math.isfinite(edge["length_m"])
        assert edge["length_m"] > 0 and edge["length_m"] == props["distance"]
    reachability = expected["mapping_reachability"]
    reached = [mapping_id for values in reachability.values() for mapping_id in values]
    assert len(reached) == len(set(reached)) == 40
    assert set(reached) == {mapping["id"] for mapping in contract["mappings"]}
    by_status = {mapping["id"]: mapping["status"] for mapping in contract["mappings"]}
    assert all(by_status[mid] == "FULL" for mid in reachability["OUTPUT"])
    assert all(by_status[mid] == "PARTIAL" for mid in reachability["OUTPUT_WITH_LOSS"])
    assert all(by_status[mid] == "SIDECAR_REQUIRED" for mid in reachability["SIDECAR"])
    assert reachability["REJECT_OR_EXTERNAL_SIDECAR"] == ["PROVENANCE"]
    assert reachability["REJECT_NOT_APPLICABLE"] == ["FACILITY_DATASET"]


def test_every_declared_source_field_has_fixture_reachability():
    """[software_correctness] mappingが宣言する各source fieldをfixture入力または明示metadataで到達可能にする。"""
    contract = load_contract()
    source = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    property_names = {key for feature in source["features"] for key in feature["properties"]}
    special = {"geometry", "JGD2011", "link{1..99}_id"}
    declared = {field for mapping in contract["mappings"] for field in mapping["hokonavi_fields"]}
    assert declared - special <= property_names
    assert all("geometry" in feature for feature in source["features"])
    assert source["crs_metadata"]["name"] == "JGD2011"
    assert any(key.startswith("link2_id") for key in property_names)


def test_each_edge_has_exact_applicable_loss_ids():
    """[software_correctness] source fieldごとのlossをexact集合で追跡しmaint_date/directionを落とさない。"""
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    common = {
        "LOSS-ABLEPATH-CORE-ABSENT", "LOSS-CODEBOOK-MISMATCH", "LOSS-RANK-NOT-PROFILE",
        "LOSS-SLOPE-PRECISION", "LOSS-SLOPE-QUANTIZATION", "LOSS-SOURCE-METHOD-GRANULARITY",
        "LOSS-STEP-PRECISION", "LOSS-STEP-QUANTIZATION", "LOSS-VALIDITY-SEMANTICS",
        "LOSS-WIDTH-PRECISION", "LOSS-WIDTH-QUANTIZATION",
    }
    expected_by_edge = {
        "SYNTHETIC-L001": common,
        "SYNTHETIC-L002": common | {"LOSS-CONNECTOR-SEMANTICS"},
        "SYNTHETIC-L003": common | {"LOSS-CONNECTOR-SEMANTICS"},
        "SYNTHETIC-L004": common | {"LOSS-UNKNOWN-ENCODING"},
        "SYNTHETIC-L005": common | {"LOSS-CONNECTOR-SEMANTICS"},
    }
    assert {edge["edge_id"]: set(edge["source_sidecar"]["loss_ids"])
            for edge in expected["edges"]} == expected_by_edge


def test_each_node_has_exact_applicable_loss_ids():
    """[software_correctness] level/type/connected-links/elevationのPARTIAL・sidecar lossをnode別exact集合で固定する。"""
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    common_connected = {"LOSS-CODEBOOK-MISMATCH", "LOSS-CONNECTIVITY-REPRESENTATION", "LOSS-LEVEL-DOMAIN"}
    expected_by_node = {
        "SYNTHETIC-N001": common_connected | {"LOSS-ABLEPATH-CORE-ABSENT"},
        "SYNTHETIC-N002": common_connected,
        "SYNTHETIC-N003": common_connected,
        "SYNTHETIC-N004": common_connected,
        "SYNTHETIC-N005": common_connected,
    }
    assert {node["node_id"]: set(node["source_sidecar"]["loss_ids"])
            for node in expected["nodes"]} == expected_by_node


def test_code_99_semantic_blank_and_missing_are_distinct_for_same_field():
    """[source_conformance] start_timeの99/意味ある空欄/欠落を異なるkindとnormalized値で保持する。"""
    source = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    source_by_id = {f["properties"]["link_id"]: f["properties"] for f in source["features"]
                    if f["properties"]["entity"] == "link"}
    assert source_by_id["SYNTHETIC-L001"]["start_time"] == "99"
    assert source_by_id["SYNTHETIC-L002"]["start_time"] == ""
    assert "start_time" not in source_by_id["SYNTHETIC-L003"]
    provenance = {edge["edge_id"]: edge["source_value_provenance"]["start_time"]
                  for edge in expected["edges"] if "source_value_provenance" in edge}
    assert provenance["SYNTHETIC-L001"] == {
        "kind": "SOURCE_CODE_99", "raw": "99", "normalized": "UNKNOWN"
    }
    assert provenance["SYNTHETIC-L002"] == {
        "kind": "SEMANTIC_BLANK", "raw": "", "normalized": "NO_TIME_RESTRICTION"
    }
    assert provenance["SYNTHETIC-L003"] == {"kind": "MISSING_ATTRIBUTE", "normalized": "UNKNOWN"}
    policy = load_contract()["unknown_policy"]
    assert policy["policy_only_examples"]["start_time"].endswith(
        "not counted as a field mapping in this 40-mapping contract"
    )
    assert not any("start_time" in mapping["hokonavi_fields"] for mapping in load_contract()["mappings"])


def test_negative_graph_contract_rejects_duplicate_dangling_and_mixed_entity():
    """[software_correctness] duplicate ID、dangling endpoint、node/link entity混在を拒否する契約。"""
    fixture = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    validation = load_contract()["validation_contract"]
    assert validation == {
        "reject": ["duplicate_node_id", "duplicate_link_id", "node_link_id_collision",
                   "dangling_endpoint", "mixed_or_unknown_entity"],
        "auto_fix_forbidden": True,
    }

    def validate_graph_contract(document):
        props = [feature["properties"] for feature in document["features"]]
        nodes = [item for item in props if item.get("entity") == "node"]
        links = [item for item in props if item.get("entity") == "link"]
        if len(nodes) + len(links) != len(props):
            raise ValueError("mixed or unknown entity")
        node_ids = [node["node_id"] for node in nodes]
        link_ids = [link["link_id"] for link in links]
        if len(node_ids) != len(set(node_ids)) or len(link_ids) != len(set(link_ids)):
            raise ValueError("duplicate id")
        if set(node_ids) & set(link_ids):
            raise ValueError("node/link id collision")
        if any(link[endpoint] not in set(node_ids) for link in links for endpoint in ("start_id", "end_id")):
            raise ValueError("dangling endpoint")

    validate_graph_contract(fixture)
    duplicate_node = deepcopy(fixture)
    duplicate_node["features"].append(deepcopy(duplicate_node["features"][0]))
    duplicate_link = deepcopy(fixture)
    first_link = next(f for f in duplicate_link["features"] if f["properties"]["entity"] == "link")
    duplicate_link["features"].append(deepcopy(first_link))
    collision = deepcopy(fixture)
    next(f for f in collision["features"] if f["properties"]["entity"] == "link")["properties"]["link_id"] = "SYNTHETIC-N001"
    dangling = deepcopy(fixture)
    next(f for f in dangling["features"] if f["properties"]["entity"] == "link")["properties"]["end_id"] = "MISSING"
    mixed = deepcopy(fixture)
    mixed["features"][0]["properties"]["entity"] = "node_link"
    import pytest
    for invalid in (duplicate_node, duplicate_link, collision, dangling, mixed):
        with pytest.raises(ValueError):
            validate_graph_contract(invalid)


def test_r_method_is_split_by_attribute_and_raw_value_is_preserved():
    """[source_conformance] mixed r_method=121を幅/勾配/段差へ分解しrawもsidecar保持する。"""
    by_id = {m["id"]: m for m in load_contract()["mappings"]}
    method = by_id["SOURCE_METHOD"]
    assert method["adapter_action"] == "split_three_positions_and_preserve_raw"
    assert method["ablepath_fields"] == [
        "source_method.width", "source_method.longitudinal_slope", "source_method.step",
        "source_sidecar.hokonavi_r_method_raw",
    ]
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    for edge in expected["edges"]:
        sidecar = edge["source_sidecar"]
        assert sidecar["hokonavi_r_method_raw"] == "121"
        assert sidecar["source_method"] == {
            "width": "FIELD_SURVEY", "longitudinal_slope": "TRACK_LOG", "step": "FIELD_SURVEY"
        }


def test_node_connected_link_pattern_covers_link1_through_link99():
    """[source_conformance] node接続linkはlink1_idだけでなくlink1_id..link99_idを列として扱う。"""
    by_id = {m["id"]: m for m in load_contract()["mappings"]}
    assert by_id["NODE_CONNECTED_LINKS"]["hokonavi_fields"] == ["link{1..99}_id"]
    assert by_id["NODE_CONNECTED_LINKS"]["adapter_action"] == "collect_pattern_derive_and_validate"
    source = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURE_ROOT / "expected_internal.json").read_text(encoding="utf-8"))
    first_node = next(f["properties"] for f in source["features"] if f["properties"].get("node_id") == "SYNTHETIC-N001")
    assert first_node["link1_id"] == "SYNTHETIC-L001"
    assert first_node["link2_id"] == "SYNTHETIC-L004"
    assert expected["nodes"][0]["incident_edge_ids"] == [
        "SYNTHETIC-L001", "SYNTHETIC-L004", "SYNTHETIC-L005"
    ]
    source_n005 = next(f["properties"] for f in source["features"]
                       if f["properties"].get("node_id") == "SYNTHETIC-N005")
    source_l005 = next(f["properties"] for f in source["features"]
                       if f["properties"].get("link_id") == "SYNTHETIC-L005")
    expected_n005 = next(node for node in expected["nodes"] if node["node_id"] == "SYNTHETIC-N005")
    assert source_n005["link1_id"] == source_l005["link_id"]
    assert source_l005["end_id"] == source_n005["node_id"]
    assert expected_n005["incident_edge_ids"] == ["SYNTHETIC-L005"]


def test_information_loss_register_matches_non_full_mappings():
    """[software_correctness] 非FULL mappingをloss registerへ全件接続し、孤立lossも許さない。"""
    contract = load_contract()
    mappings = contract["mappings"]
    referenced = {m["loss_id"] for m in mappings if m["status"] != "FULL"}
    assert all("loss_id" in m for m in mappings if m["status"] != "FULL")
    text = LOSS_DOC.read_text(encoding="utf-8")
    declared = {
        line.removeprefix("<!-- LOSS:").removesuffix(" -->")
        for line in text.splitlines() if line.startswith("<!-- LOSS:")
    }
    assert referenced == declared


def test_unmapped_and_sidecar_fields_are_never_silently_dropped():
    """[software_correctness] UNMAPPEDは拒否/外部sidecar、SIDECAR_REQUIREDはsidecar保持を要求する。"""
    mappings = load_contract()["mappings"]
    for mapping in mappings:
        if mapping["status"] == "UNMAPPED":
            assert mapping["adapter_action"] == "reject_or_preserve_external_sidecar"
        if mapping["status"] == "SIDECAR_REQUIRED":
            assert "sidecar" in mapping["adapter_action"]
    sidecar_concepts = {m["concept"] for m in mappings if m["entity"] == "sidecar"}
    assert {"scenario_width", "observation", "evidence", "profile", "scenario",
            "provenance", "before_after", "operation_status"} <= sidecar_concepts


def test_fixtures_are_explicitly_synthetic():
    """[software_correctness] fixture全ファイルがSYNTHETICと明示され、実在データに見えない。"""
    files = sorted(path for path in FIXTURE_ROOT.rglob("*") if path.is_file())
    assert {path.name for path in files} == {"README.md", "source_network.geojson", "expected_internal.json"}
    assert all("SYNTHETIC" in path.read_text(encoding="utf-8") for path in files)
    source = json.loads((FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8"))
    assert source["fixture_status"] == "SYNTHETIC"
    assert all(feature["properties"]["fixture_status"] == "SYNTHETIC" for feature in source["features"])


def test_contract_artifacts_do_not_use_prohibited_claims():
    """[source_conformance] 参照契約を認証・承認・無損失の主張へ誇張しない。"""
    prohibited = ["完全" + "互換", "国交省" + "認証", "国交省" + "承認", "正式" + "対応"]
    paths = [SCHEMA_PATH, MAPPING_DOC, LOSS_DOC, BRIEF]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for phrase in prohibited:
        assert phrase not in combined
