"""Tests for the bounded Hokonavi 2024 adapter prototype."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest
import yaml

from src.hokonavi.adapter import (
    HokonaviAdapterError,
    canonical_json_bytes,
    export_hokonavi_2024,
    import_hokonavi_2024,
    validate_sidecar,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "hokonavi_2024"
SIDECAR_SCHEMA = ROOT / "schemas" / "hokonavi_2024_sidecar.schema.json"
EXPECTED_INTERNAL = FIXTURE_ROOT / "expected_internal.json"


def source_network() -> dict[str, object]:
    return json.loads(
        (FIXTURE_ROOT / "source_network.geojson").read_text(encoding="utf-8")
    )


def complete_sidecar() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "source_role": "ABLEPATH_DESIGN",
        "edges": {
            "SYNTHETIC-L001": {
                "m7": [{
                    "scenario_id": "SYNTHETIC-EQ-MEAN",
                    "variant": "mean_case",
                    "remaining_clear_width_m": 0.73,
                    "hazard_data_status": "KNOWN",
                    "official_closure": None,
                    "provenance": {
                        "source_role": "ABLEPATH_DESIGN",
                        "source_id": "SYNTHETIC-M7",
                        "crs": "JGD2011",
                        "method": "SYNTHETIC_FIXTURE",
                        "applied_constant_ids": [],
                    },
                }],
                "observation": [{
                    "observation_id": "SYNTHETIC-OBS-001",
                    "attribute": "clear_width_static_m",
                    "raw_value": 4.0,
                    "unit": "m",
                    "method": "SYNTHETIC_FIXTURE",
                    "device": None,
                    "observed_at": "2024-07-01",
                    "observer_role": "SYNTHETIC_TEST",
                    "direction": None,
                    "weather": None,
                    "photo": None,
                    "accuracy": None,
                    "review_status": "SINGLE_REVIEWED",
                }],
                "evidence": [{
                    "source_class": "FIELD",
                    "acquisition_method": "TAPE",
                    "verification_level": "SINGLE_REVIEWED",
                    "validity_status": "CURRENT",
                    "authority_scope": "dimension",
                }],
                "validity": {"valid_from": "2024-07-01", "valid_to": None},
                "profile": [{
                    "profile_id": "SYNTHETIC-WHEELCHAIR",
                    "scenario_id": "SYNTHETIC-EQ-MEAN",
                    "computation_status": "COMPUTED",
                    "profile_state": "UNKNOWN",
                }],
                "scenario": [{
                    "scenario_id": "SYNTHETIC-EQ-MEAN",
                    "computation_status": "COMPUTED",
                    "edge_state": "UNKNOWN",
                }],
                "provenance": {
                    "source_role": "ABLEPATH_DESIGN",
                    "source_id": "SYNTHETIC-SIDECAR",
                    "crs": "JGD2011",
                    "method": "SYNTHETIC_FIXTURE",
                    "applied_constant_ids": [],
                },
                "before_after": [{"intervention_phase": "BEFORE"}],
                "operation_status": [{
                    "scenario_id": "SYNTHETIC-EQ-MEAN",
                    "official_closure": None,
                    "hazard_data_status": "UNKNOWN",
                }],
            }
        },
    }


def edge_by_id(internal: dict[str, object], edge_id: str) -> dict[str, object]:
    return next(edge for edge in internal["edges"] if edge["edge_id"] == edge_id)


def test_import_matches_the_tracked_internal_contract_fixture_exactly() -> None:
    """[source_conformance] The implementation must match the reviewed synthetic internal contract fixture, not a parallel shape."""

    expected = json.loads(EXPECTED_INTERNAL.read_text(encoding="utf-8"))
    assert import_hokonavi_2024(source_network()) == expected


def test_import_preserves_node_link_identity_geometry_crs_and_maint_date() -> None:
    """[source_conformance] Five nodes/five links retain IDs, endpoints, JGD2011 lon/lat, and the literal 2024-07-01 maintenance date."""

    internal = import_hokonavi_2024(source_network())
    assert [node["node_id"] for node in internal["nodes"]] == [
        f"SYNTHETIC-N00{index}" for index in range(1, 6)
    ]
    assert [edge["edge_id"] for edge in internal["edges"]] == [
        f"SYNTHETIC-L00{index}" for index in range(1, 6)
    ]
    assert internal["crs_metadata"] == {
        "name": "JGD2011",
        "axis_order": ["longitude", "latitude"],
    }
    first = edge_by_id(internal, "SYNTHETIC-L001")
    assert (first["from_node"], first["to_node"]) == (
        "SYNTHETIC-N001",
        "SYNTHETIC-N002",
    )
    assert first["geometry"] == {
        "type": "LineString",
        "coordinates": [[135.0, 35.0], [135.0001, 35.0001]],
    }
    assert first["validity"] == {"maint_date": "2024-07-01"}


def test_import_keeps_code_99_semantic_blank_and_missing_distinct() -> None:
    """[source_conformance] The same start_time field yields SOURCE_CODE_99, SEMANTIC_BLANK, and MISSING_ATTRIBUTE without a safe default."""

    internal = import_hokonavi_2024(source_network())
    by_id = {edge["edge_id"]: edge for edge in internal["edges"]}
    assert by_id["SYNTHETIC-L001"]["source_value_provenance"]["start_time"] == {
        "kind": "SOURCE_CODE_99",
        "raw": "99",
        "normalized": "UNKNOWN",
    }
    assert by_id["SYNTHETIC-L002"]["source_value_provenance"]["start_time"] == {
        "kind": "SEMANTIC_BLANK",
        "raw": "",
        "normalized": "NO_TIME_RESTRICTION",
    }
    assert by_id["SYNTHETIC-L003"]["source_value_provenance"]["start_time"] == {
        "kind": "MISSING_ATTRIBUTE",
        "normalized": "UNKNOWN",
    }
    unknown = by_id["SYNTHETIC-L004"]
    assert unknown["travel_direction"] == "UNKNOWN"
    assert unknown["clear_width_static_class"] == "UNKNOWN"
    assert unknown["clear_width_static_m"] is None
    assert unknown["longitudinal_slope_class"] == "UNKNOWN"
    assert unknown["slope_estimate_percent"] is None
    assert unknown["step_class"] == "UNKNOWN"
    assert unknown["step_height_cm"] is None
    assert "profile_state" not in unknown
    assert "edge_state" not in unknown


def test_width_slope_step_and_source_method_are_not_invented_or_flipped() -> None:
    """[source_conformance] w_min=4.0m, vtcl_slope=2 with vSlope_max=3%, levDif_max=0cm, and r_method=121 are preserved exactly."""

    edge = edge_by_id(import_hokonavi_2024(source_network()), "SYNTHETIC-L001")
    assert edge["clear_width_static_class"] == 4
    assert edge["clear_width_static_m"] == 4.0
    assert edge["clear_width_static_measurement"] == {
        "source_field": "w_min",
        "unit": "m",
        "resolution_m": 0.1,
    }
    assert edge["longitudinal_slope_class"] == 2
    assert edge["slope_estimate_percent"] == 3
    assert edge["step_class"] == 1
    assert edge["step_height_cm"] == 0
    assert edge["source_sidecar"]["hokonavi_r_method_raw"] == "121"
    assert edge["source_sidecar"]["source_method"] == {
        "width": "FIELD_SURVEY",
        "longitudinal_slope": "TRACK_LOG",
        "step": "FIELD_SURVEY",
    }
    second = edge_by_id(import_hokonavi_2024(source_network()), "SYNTHETIC-L002")
    assert second["clear_width_static_class"] == 2
    assert second["clear_width_static_m"] == 1.5


def test_floor_direction_and_slope_domains_are_preserved_without_reversal() -> None:
    """[source_conformance] Floors {0,1,-1,1.5}, directions 1/2/3/99, and each directed slope class/value survive without sign invention."""

    internal = import_hokonavi_2024(source_network())
    assert {node["level"] for node in internal["nodes"]} == {0, 1, -1, 1.5}
    assert {
        (edge["travel_direction_code"], edge["travel_direction"])
        for edge in internal["edges"]
    } == {
        (1, "BIDIRECTIONAL"),
        (2, "FORWARD"),
        (3, "REVERSE"),
        (99, "UNKNOWN"),
    }
    assert {
        edge["edge_id"]: (
            edge["longitudinal_slope_class"],
            edge["slope_estimate_percent"],
        )
        for edge in internal["edges"]
    } == {
        "SYNTHETIC-L001": (2, 3),
        "SYNTHETIC-L002": (3, 6),
        "SYNTHETIC-L003": (4, 9),
        "SYNTHETIC-L004": ("UNKNOWN", None),
        "SYNTHETIC-L005": (2, 4),
    }


def test_route_structure_route_type_and_connectors_remain_separate() -> None:
    """[source_conformance] rt_struct=2 and route_type=6 remain different targets, while elevator=1 continues to mean no elevator."""

    internal = import_hokonavi_2024(source_network())
    stairs = edge_by_id(internal, "SYNTHETIC-L002")
    elevator = edge_by_id(internal, "SYNTHETIC-L003")
    assert stairs["route_structure"] == "NOT_PHYSICALLY_SEPARATED"
    assert stairs["route_type"] == "STAIRS"
    assert stairs["connector"] == {
        "stairs": True,
        "stair_count": 12,
        "is_ramp": False,
        "is_elevator": False,
        "elevator_code": 1,
    }
    assert elevator["route_type"] == "ELEVATOR"
    assert elevator["connector"]["is_elevator"] is True
    assert elevator["connector"]["elevator_code"] == 3


def test_sidecar_schema_is_exact_and_covers_all_design_only_concepts() -> None:
    """[software_correctness] The v1 sidecar closes every object and names all eight required AblePath-only concept groups."""

    schema = json.loads(SIDECAR_SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"] == "https://ablepath.example/schemas/hokonavi_2024_sidecar-1.0.0.json"
    assert schema["additionalProperties"] is False
    edge = schema["$defs"]["edgePayload"]
    assert edge["additionalProperties"] is False
    assert edge["required"] == ["provenance"]
    assert all(
        definition.get("additionalProperties") is False
        for definition in schema["$defs"].values()
        if definition.get("type") == "object"
    )
    assert {
        "m7",
        "observation",
        "evidence",
        "validity",
        "profile",
        "scenario",
        "provenance",
        "before_after",
        "operation_status",
    } == set(edge["properties"])
    assert validate_sidecar(
        complete_sidecar(), edge_ids={"SYNTHETIC-L001"}
    ) == complete_sidecar()


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_role",
        "unknown_edge",
        "extra_nested_key",
        "static_width_in_sidecar",
        "profile_open",
        "scenario_pass",
        "unsorted_constants",
    ],
)
def test_sidecar_validation_rejects_role_schema_enum_and_reference_mutants(
    mutation: str,
) -> None:
    """[software_correctness] Exact sidecar validation fails closed for role, key, enum, ID, and deterministic-order mutations."""

    sidecar = complete_sidecar()
    payload = sidecar["edges"]["SYNTHETIC-L001"]
    if mutation == "wrong_role":
        sidecar["source_role"] = "SOURCE_FACT"
    elif mutation == "unknown_edge":
        sidecar["edges"]["MISSING"] = sidecar["edges"].pop("SYNTHETIC-L001")
    elif mutation == "extra_nested_key":
        payload["observation"][0]["confidence"] = 1.0
    elif mutation == "static_width_in_sidecar":
        payload["clear_width_static_m"] = 4.0
    elif mutation == "profile_open":
        payload["profile"][0]["profile_state"] = "OPEN"
    elif mutation == "scenario_pass":
        payload["scenario"][0]["edge_state"] = "PASS"
    else:
        payload["provenance"]["applied_constant_ids"] = ["B", "A"]
    with pytest.raises(HokonaviAdapterError):
        validate_sidecar(sidecar, edge_ids={"SYNTHETIC-L001"})


def test_static_width_and_m7_remaining_width_are_orthogonal() -> None:
    """[software_correctness] The fixture's static 4.00m remains on the edge while the independent scenario example 0.73m remains only in sidecar."""

    internal = import_hokonavi_2024(
        source_network(), ablepath_sidecar=complete_sidecar()
    )
    edge = edge_by_id(internal, "SYNTHETIC-L001")
    assert edge["clear_width_static_m"] == 4.0
    assert "remaining_clear_width_m" not in edge
    assert (
        internal["ablepath_sidecar"]["edges"]["SYNTHETIC-L001"]["m7"][0][
            "remaining_clear_width_m"
        ]
        == 0.73
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "negative_width",
        "nan_width",
        "unknown_width_zero",
        "unknown_closure_false",
        "not_computed_profile_pass",
        "not_computed_scenario_open",
    ],
)
def test_sidecar_cross_field_unknown_contract_fails_closed(mutation: str) -> None:
    """[software_correctness] Unknown/not-computed sidecar records cannot smuggle in zero, false, PASS, or OPEN as known results."""

    sidecar = complete_sidecar()
    payload = sidecar["edges"]["SYNTHETIC-L001"]
    if mutation == "negative_width":
        payload["m7"][0]["remaining_clear_width_m"] = -1
    elif mutation == "nan_width":
        payload["m7"][0]["remaining_clear_width_m"] = float("nan")
    elif mutation == "unknown_width_zero":
        payload["m7"][0]["hazard_data_status"] = "UNKNOWN"
        payload["m7"][0]["remaining_clear_width_m"] = 0
    elif mutation == "unknown_closure_false":
        payload["operation_status"][0]["hazard_data_status"] = "UNKNOWN"
        payload["operation_status"][0]["official_closure"] = False
    elif mutation == "not_computed_profile_pass":
        payload["profile"][0]["computation_status"] = "NOT_COMPUTED"
        payload["profile"][0]["profile_state"] = "PASS"
    else:
        payload["scenario"][0]["computation_status"] = "NOT_COMPUTED"
        payload["scenario"][0]["edge_state"] = "OPEN"
    with pytest.raises(HokonaviAdapterError):
        validate_sidecar(sidecar, edge_ids={"SYNTHETIC-L001"})


def test_import_export_round_trip_is_byte_deterministic_and_non_mutating() -> None:
    """[software_correctness] Two runs and a reversed feature order produce identical canonical bytes without changing the source or sidecar."""

    source = source_network()
    sidecar = complete_sidecar()
    before_source = deepcopy(source)
    before_sidecar = deepcopy(sidecar)
    first = import_hokonavi_2024(source, ablepath_sidecar=sidecar)
    reversed_source = deepcopy(source)
    reversed_source["features"].reverse()
    second = import_hokonavi_2024(reversed_source, ablepath_sidecar=sidecar)
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    before_internal = deepcopy(first)
    exported = export_hokonavi_2024(first, include_sidecar=True)
    exported_again = export_hokonavi_2024(first, include_sidecar=True)
    assert first == before_internal
    assert canonical_json_bytes(exported) == canonical_json_bytes(exported_again)
    restored = import_hokonavi_2024(
        exported["network"], ablepath_sidecar=exported["ablepath_sidecar"]
    )
    assert canonical_json_bytes(restored) == canonical_json_bytes(first)
    assert source == before_source
    assert sidecar == before_sidecar


def test_multiple_scenario_profile_and_m7_records_survive_round_trip() -> None:
    """[software_correctness] Two sorted scenario/profile/M7 records remain distinct; no first-record-only truncation is allowed."""

    sidecar = complete_sidecar()
    payload = sidecar["edges"]["SYNTHETIC-L001"]
    payload["m7"].append(
        {
            "scenario_id": "SYNTHETIC-EQ-SENS",
            "variant": "sensitivity_high_case",
            "remaining_clear_width_m": 0.5,
            "hazard_data_status": "KNOWN",
            "official_closure": None,
            "provenance": {
                "source_role": "ABLEPATH_DESIGN",
                "source_id": "SYNTHETIC-M7-SENS",
                "crs": "JGD2011",
                "method": "SYNTHETIC_FIXTURE",
                "applied_constant_ids": [],
            },
        }
    )
    payload["profile"].append(
        {
            "profile_id": "SYNTHETIC-WHEELCHAIR",
            "scenario_id": "SYNTHETIC-EQ-SENS",
            "computation_status": "COMPUTED",
            "profile_state": "FAIL",
        }
    )
    payload["scenario"].append(
        {
            "scenario_id": "SYNTHETIC-EQ-SENS",
            "computation_status": "COMPUTED",
            "edge_state": "NARROWED",
        }
    )
    payload["operation_status"].append(
        {
            "scenario_id": "SYNTHETIC-EQ-SENS",
            "official_closure": None,
            "hazard_data_status": "KNOWN",
        }
    )
    internal = import_hokonavi_2024(source_network(), ablepath_sidecar=sidecar)
    exported = export_hokonavi_2024(internal, include_sidecar=True)
    restored = import_hokonavi_2024(
        exported["network"], ablepath_sidecar=exported["ablepath_sidecar"]
    )
    restored_payload = restored["ablepath_sidecar"]["edges"]["SYNTHETIC-L001"]
    assert [record["scenario_id"] for record in restored_payload["m7"]] == [
        "SYNTHETIC-EQ-MEAN",
        "SYNTHETIC-EQ-SENS",
    ]
    assert [record["variant"] for record in restored_payload["m7"]] == [
        "mean_case",
        "sensitivity_high_case",
    ]
    assert len(restored_payload["profile"]) == len(restored_payload["scenario"]) == 2


def test_numbered_node_link_columns_preserve_source_column_order() -> None:
    """[source_conformance] Swapping link1/link2 values remains byte-semantic round-trip data, not a lexical ID reorder."""

    source = source_network()
    node = next(
        feature["properties"]
        for feature in source["features"]
        if feature["properties"].get("node_id") == "SYNTHETIC-N001"
    )
    node["link1_id"], node["link2_id"] = node["link2_id"], node["link1_id"]
    internal = import_hokonavi_2024(source)
    assert internal["nodes"][0]["incident_edge_ids"][:2] == [
        "SYNTHETIC-L004",
        "SYNTHETIC-L001",
    ]
    assert export_hokonavi_2024(internal, include_sidecar=True)["network"] == source


def test_sparse_numbered_node_link_columns_are_rejected_before_renumbering() -> None:
    """[software_correctness] A lone link2_id cannot be silently renumbered to link1_id during round trip."""

    source = source_network()
    node = next(
        feature["properties"]
        for feature in source["features"]
        if feature["properties"].get("node_id") == "SYNTHETIC-N005"
    )
    node["link2_id"] = node.pop("link1_id")
    with pytest.raises(HokonaviAdapterError, match="contiguous"):
        import_hokonavi_2024(source)


def test_export_reconstructs_source_facts_including_maint_date_and_blank_kind() -> None:
    """[source_conformance] Round trip reconstructs all synthetic source facts, including maint_date and absent-versus-blank start_time."""

    source = source_network()
    exported = export_hokonavi_2024(
        import_hokonavi_2024(source), include_sidecar=True
    )
    assert exported["network"] == source
    links = {
        feature["properties"]["link_id"]: feature["properties"]
        for feature in exported["network"]["features"]
        if feature["properties"]["entity"] == "link"
    }
    assert links["SYNTHETIC-L001"]["maint_date"] == "2024-07-01"
    assert links["SYNTHETIC-L002"]["start_time"] == ""
    assert "start_time" not in links["SYNTHETIC-L003"]


def test_export_rejects_sidecar_drop_and_unmapped_internal_fields() -> None:
    """[software_correctness] An AblePath sidecar or unknown internal field cannot be silently omitted from export."""

    internal = import_hokonavi_2024(
        source_network(), ablepath_sidecar=complete_sidecar()
    )
    with pytest.raises(HokonaviAdapterError, match="sidecar"):
        export_hokonavi_2024(internal, include_sidecar=False)
    mutated = import_hokonavi_2024(source_network())
    mutated["edges"][0]["unmapped"] = "must-not-drop"
    with pytest.raises(HokonaviAdapterError, match="unsupported schema"):
        export_hokonavi_2024(mutated, include_sidecar=True)


def test_information_loss_report_is_complete_and_exact() -> None:
    """[software_correctness] Every imported entity emits a sorted non-empty loss set and the export reports all ten entity IDs."""

    internal = import_hokonavi_2024(source_network())
    exported = export_hokonavi_2024(internal, include_sidecar=True)
    report = exported["information_loss"]
    assert report["status"] == "PARTIAL_WITH_EXPLICIT_LOSS"
    assert set(report["loss_ids_by_entity"]) == {
        *(f"SYNTHETIC-N00{index}" for index in range(1, 6)),
        *(f"SYNTHETIC-L00{index}" for index in range(1, 6)),
    }
    assert all(
        loss_ids == sorted(set(loss_ids)) and loss_ids
        for loss_ids in report["loss_ids_by_entity"].values()
    )
    common_edge = {
        "LOSS-ABLEPATH-CORE-ABSENT",
        "LOSS-CODEBOOK-MISMATCH",
        "LOSS-RANK-NOT-PROFILE",
        "LOSS-SLOPE-PRECISION",
        "LOSS-SLOPE-QUANTIZATION",
        "LOSS-SOURCE-METHOD-GRANULARITY",
        "LOSS-STEP-PRECISION",
        "LOSS-STEP-QUANTIZATION",
        "LOSS-VALIDITY-SEMANTICS",
        "LOSS-WIDTH-PRECISION",
        "LOSS-WIDTH-QUANTIZATION",
    }
    assert set(report["loss_ids_by_entity"]["SYNTHETIC-L001"]) == common_edge
    assert set(report["loss_ids_by_entity"]["SYNTHETIC-L002"]) == common_edge | {
        "LOSS-CONNECTOR-SEMANTICS"
    }
    assert set(report["loss_ids_by_entity"]["SYNTHETIC-L004"]) == common_edge | {
        "LOSS-UNKNOWN-ENCODING"
    }
    assert set(report["loss_ids_by_entity"]["SYNTHETIC-L003"]) == common_edge | {
        "LOSS-CONNECTOR-SEMANTICS"
    }
    assert set(report["loss_ids_by_entity"]["SYNTHETIC-L005"]) == common_edge | {
        "LOSS-CONNECTOR-SEMANTICS"
    }
    common_node = {
        "LOSS-CODEBOOK-MISMATCH",
        "LOSS-CONNECTIVITY-REPRESENTATION",
        "LOSS-LEVEL-DOMAIN",
    }
    assert set(report["loss_ids_by_entity"]["SYNTHETIC-N001"]) == common_node | {
        "LOSS-ABLEPATH-CORE-ABSENT"
    }
    for node_id in ("SYNTHETIC-N002", "SYNTHETIC-N003", "SYNTHETIC-N004", "SYNTHETIC-N005"):
        assert set(report["loss_ids_by_entity"][node_id]) == common_node


def test_all_mapping_ids_have_one_explicit_runtime_disposition() -> None:
    """[software_correctness] The contract's 40 mapping IDs appear exactly once across output, lossy output, sidecar, and reject dispositions."""

    internal = import_hokonavi_2024(source_network())
    reachability = internal["mapping_reachability"]
    reached = [mapping_id for mapping_ids in reachability.values() for mapping_id in mapping_ids]
    assert len(reached) == len(set(reached)) == 40
    contract = yaml.safe_load(
        (ROOT / "schemas" / "hokonavi_2024_mapping.yaml").read_text(encoding="utf-8")
    )
    assert contract["adapter_implemented"] is False
    assert contract["adapter_prototype_implemented"] is True
    assert contract["adapter_implementation_scope"] == "SYNTHETIC_FIXTURE_ONLY"
    assert contract["sidecar_schema"] == {
        "path": "schemas/hokonavi_2024_sidecar.schema.json",
        "version": "1.0.0",
        "source_role": "ABLEPATH_DESIGN",
    }
    evidence_mapping = next(
        mapping for mapping in contract["mappings"] if mapping["id"] == "EVIDENCE"
    )
    assert evidence_mapping["ablepath_fields"] == ["evidence", "validity"]
    assert set(reached) == {mapping["id"] for mapping in contract["mappings"]}
    by_status = {mapping["id"]: mapping["status"] for mapping in contract["mappings"]}
    assert all(by_status[item] == "FULL" for item in reachability["OUTPUT"])
    assert all(
        by_status[item] == "PARTIAL" for item in reachability["OUTPUT_WITH_LOSS"]
    )
    assert all(by_status[item] == "SIDECAR_REQUIRED" for item in reachability["SIDECAR"])
    assert reachability["REJECT_OR_EXTERNAL_SIDECAR"] == ["PROVENANCE"]
    assert reachability["REJECT_NOT_APPLICABLE"] == ["FACILITY_DATASET"]


def test_every_non_full_mapping_emits_its_declared_loss_id() -> None:
    """[software_correctness] PARTIAL, SIDECAR_REQUIRED, UNMAPPED, and excluded mappings each appear in the mapping-level loss report."""

    contract = yaml.safe_load(
        (ROOT / "schemas" / "hokonavi_2024_mapping.yaml").read_text(encoding="utf-8")
    )
    expected = {
        mapping["id"]: mapping["loss_id"]
        for mapping in contract["mappings"]
        if mapping["status"] != "FULL"
    }
    report = export_hokonavi_2024(
        import_hokonavi_2024(source_network(), ablepath_sidecar=complete_sidecar()),
        include_sidecar=True,
    )["information_loss"]
    assert report["loss_ids_by_mapping"] == dict(sorted(expected.items()))
    assert report["loss_ids_by_mapping"]["PROVENANCE"] == "LOSS-PROVENANCE-UNMAPPED"
    assert "LOSS-ABLEPATH-SCENARIO" in report["loss_ids_by_mapping"].values()
    assert "LOSS-ABLEPATH-EVIDENCE" in report["loss_ids_by_mapping"].values()


@pytest.mark.parametrize("mutation", ["remove", "extra", "duplicate", "unsorted"])
def test_export_rejects_silent_loss_report_mutants(mutation: str) -> None:
    """[software_correctness] Removing, adding, duplicating, or reordering a required loss ID is rejected before export."""

    internal = import_hokonavi_2024(source_network())
    loss_ids = internal["edges"][0]["source_sidecar"]["loss_ids"]
    if mutation == "remove":
        loss_ids.pop()
    elif mutation == "extra":
        loss_ids.append("LOSS-NOT-IN-CONTRACT")
    elif mutation == "duplicate":
        loss_ids.append(loss_ids[0])
    else:
        loss_ids.reverse()
    with pytest.raises(HokonaviAdapterError, match="loss_ids"):
        export_hokonavi_2024(internal, include_sidecar=True)


def test_import_without_sidecar_generates_no_ablepath_analysis_values() -> None:
    """[software_correctness] Import alone preserves rank but creates no M7, profile, scenario, or operation result."""

    internal = import_hokonavi_2024(source_network())
    assert "ablepath_sidecar" not in internal
    for edge in internal["edges"]:
        assert "remaining_clear_width_m" not in edge
        assert "profile_state" not in edge
        assert "edge_state" not in edge
        assert "operation_status" not in edge
        assert edge["hokonavi_rank"]


@pytest.mark.parametrize(
    "mutation",
    ["incident_list", "point_type", "line_type", "reversed_endpoints"],
)
def test_import_rejects_connectivity_and_geometry_mutants(mutation: str) -> None:
    """[software_correctness] Declared incidents, geometry types, and start/end coordinate order cannot be silently repaired."""

    source = source_network()
    node = next(feature for feature in source["features"] if feature["properties"]["entity"] == "node")
    link = next(feature for feature in source["features"] if feature["properties"]["entity"] == "link")
    if mutation == "incident_list":
        node["properties"].pop("link1_id")
    elif mutation == "point_type":
        node["geometry"]["type"] = "LineString"
    elif mutation == "line_type":
        link["geometry"]["type"] = "Point"
    else:
        link["geometry"]["coordinates"].reverse()
    with pytest.raises(HokonaviAdapterError):
        import_hokonavi_2024(source)


@pytest.mark.parametrize(
    "route_type,stair,elevator",
    [
        (1, 1, 1),
        (4, None, 1),
        (1, None, 3),
        (7, 1, 1),
    ],
)
def test_import_rejects_connector_consistency_matrix(
    route_type: int, stair: int | None, elevator: int
) -> None:
    """[software_correctness] Stair, ramp, and elevator source pairs must agree with route_type; contradictions are not auto-fixed."""

    source = source_network()
    link = next(feature for feature in source["features"] if feature["properties"].get("link_id") == "SYNTHETIC-L001")
    link["properties"].update(
        {"route_type": route_type, "stair": stair, "elevator": elevator}
    )
    with pytest.raises(HokonaviAdapterError):
        import_hokonavi_2024(source)


@pytest.mark.parametrize(
    "field,value",
    [("w_min", 4.01), ("vSlope_max", 3.5), ("levDif_max", 0.5), ("elevator", 999)],
)
def test_import_rejects_unreviewed_precision_and_codes(field: str, value: object) -> None:
    """[source_conformance] w_min is 0.1m-resolution, slope/step maxima are integers, and elevator codes use the reviewed subset."""

    source = source_network()
    link = next(feature for feature in source["features"] if feature["properties"].get("link_id") == "SYNTHETIC-L001")
    link["properties"][field] = value
    with pytest.raises(HokonaviAdapterError):
        import_hokonavi_2024(source)


def test_unknown_route_and_elevator_codes_remain_unknown_not_false() -> None:
    """[source_conformance] route_type=99/elevator=99 yields null connector booleans and round-trips both literal source codes."""

    source = source_network()
    link = next(feature for feature in source["features"] if feature["properties"].get("link_id") == "SYNTHETIC-L001")
    link["properties"].update({"route_type": 99, "stair": None, "elevator": 99})
    internal = import_hokonavi_2024(source)
    edge = edge_by_id(internal, "SYNTHETIC-L001")
    assert edge["route_type"] == "UNKNOWN"
    assert edge["connector"] == {
        "stairs": None,
        "stair_count": None,
        "is_ramp": None,
        "is_elevator": None,
        "elevator_code": 99,
    }
    exported = export_hokonavi_2024(internal, include_sidecar=True)["network"]
    restored = next(
        feature["properties"]
        for feature in exported["features"]
        if feature["properties"].get("link_id") == "SYNTHETIC-L001"
    )
    assert restored["route_type"] == 99
    assert restored["elevator"] == 99


@pytest.mark.parametrize(
    "mutation",
    ["duplicate_node", "duplicate_link", "collision", "dangling", "mixed"],
)
def test_import_rejects_identity_reference_and_entity_mutants(mutation: str) -> None:
    """[software_correctness] Duplicate IDs, node/link collision, dangling endpoint, and entity mixing fail closed without auto-fix."""

    source = source_network()
    nodes = [f for f in source["features"] if f["properties"]["entity"] == "node"]
    links = [f for f in source["features"] if f["properties"]["entity"] == "link"]
    if mutation == "duplicate_node":
        source["features"].append(deepcopy(nodes[0]))
    elif mutation == "duplicate_link":
        source["features"].append(deepcopy(links[0]))
    elif mutation == "collision":
        links[0]["properties"]["link_id"] = nodes[0]["properties"]["node_id"]
    elif mutation == "dangling":
        links[0]["properties"]["end_id"] = "MISSING"
    else:
        nodes[0]["properties"]["entity"] = "node_link"
    with pytest.raises(HokonaviAdapterError):
        import_hokonavi_2024(source)


def test_import_rejects_unknown_source_field_and_connector_contradiction() -> None:
    """[software_correctness] A new source field or route_type=6 without a positive stair count is rejected instead of dropped or repaired."""

    extra = source_network()
    extra["features"][0]["properties"]["unmapped_source"] = "must-not-drop"
    with pytest.raises(HokonaviAdapterError, match="unsupported schema"):
        import_hokonavi_2024(extra)

    contradiction = source_network()
    stairs = next(
        feature
        for feature in contradiction["features"]
        if feature["properties"].get("route_type") == 6
    )
    stairs["properties"]["stair"] = None
    with pytest.raises(HokonaviAdapterError, match="stair"):
        import_hokonavi_2024(contradiction)


def test_fixture_boundary_and_claim_language_remain_bounded() -> None:
    """[source_conformance] Only SYNTHETIC input is accepted and implementation/status text avoids certification or production claims."""

    source = source_network()
    source["fixture_status"] = "REAL"
    for feature in source["features"]:
        feature["properties"]["fixture_status"] = "REAL"
    with pytest.raises(HokonaviAdapterError, match="SYNTHETIC"):
        import_hokonavi_2024(source)

    paths = [
        ROOT / "src" / "hokonavi" / "adapter.py",
        ROOT / "reports" / "PHASE3_HOKONAVI_STATUS.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    prohibited = [
        "complete compatibility",
        "official certification",
        "ministry approval",
        "production ready",
    ]
    assert all(phrase not in combined.lower() for phrase in prohibited)
