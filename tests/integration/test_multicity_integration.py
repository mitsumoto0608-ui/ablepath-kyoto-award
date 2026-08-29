"""Cross-pack checks that can run only after all overnight lanes are integrated."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from src.citypacks import load_citypack, load_source_manifest
from src.hazards import HazardScenario, load_edge_observation_table


ROOT = Path(__file__).resolve().parents[2]
CITY_ARTIFACTS = {
    "kyoto_kiyomizu": ("hazards/edge_physics.csv", 6),
    "kyoto_arashiyama": ("hazards/edge_physics.csv", 15),
    "fujisawa_enoshima": ("hazards/edge_states.csv", 3),
}


def _viewer_cities() -> dict[str, dict]:
    payload = json.loads(
        (ROOT / "viewer" / "public" / "data" / "cities.json").read_text(encoding="utf-8")
    )
    assert payload["viewer_data_schema_version"] == "1.0.0"
    assert payload["citypack_schema_version"] == "1.0.0"
    return {city["city_id"]: city for city in payload["cities"]}


@pytest.mark.parametrize("city_id", sorted(CITY_ARTIFACTS))
def test_ui_official_sources_and_scenarios_match_city_pack(city_id: str) -> None:
    """[source_conformance] UI metadata cannot drift from the versioned city-pack sources."""
    pack = ROOT / "cities" / city_id
    city_document = load_citypack(pack, trusted_root=ROOT / "cities")
    manifest = {
        record.dataset_id: record
        for record in load_source_manifest(pack / "sources" / "source_manifest.csv")
    }
    viewer = _viewer_cities()[city_id]
    assert viewer["last_verified_at"] == city_document["last_verified_at"]
    assert viewer["profile_status"] == city_document["readiness"]["profile_status"] == "NOT_COMPUTED"
    assert viewer["kpi_status"] == city_document["readiness"]["kpi_status"] == "NOT_COMPUTED"

    ui_sources = {source["source_id"]: source for source in viewer["sources"]}
    assert set(viewer["source_ids"]) == set(ui_sources)
    official_ids = {source_id for source_id in ui_sources if not source_id.startswith("FIXTURE-")}
    assert official_ids
    for source_id in official_ids:
        source = ui_sources[source_id]
        normalized = manifest[source_id]
        assert source["data_class"] == normalized.data_class == "OFFICIAL_METADATA_ONLY"
        assert source["status"] == normalized.freshness_status
        assert source["last_verified_at"] == normalized.raw["accessed_at"]
    for source_id in set(ui_sources) - official_ids:
        assert source_id.startswith("FIXTURE-")
        assert ui_sources[source_id]["data_class"] == "SYNTHETIC_DEMO"

    scenario_document = yaml.safe_load(
        (pack / "hazards" / "scenarios.yaml").read_text(encoding="utf-8")
    )
    runtime_scenarios = {
        item.scenario_id: item
        for item in map(HazardScenario.from_mapping, scenario_document["scenarios"])
    }
    ui_scenarios = {item["scenario_id"]: item for item in viewer["scenarios"]}
    assert set(ui_scenarios) == set(runtime_scenarios)
    for scenario_id, scenario in runtime_scenarios.items():
        assert ui_scenarios[scenario_id]["hazard_type"] == scenario.hazard_type
        assert scenario.source_status == "SYNTHETIC_DEMO"
        assert scenario.default_edge_state == "UNKNOWN"


@pytest.mark.parametrize("city_id", sorted(CITY_ARTIFACTS))
def test_real_city_edge_artifacts_use_shared_unknown_adapter(city_id: str) -> None:
    """[software_correctness] Every shipped edge table crosses the same strict runtime boundary."""
    relative, expected_count = CITY_ARTIFACTS[city_id]
    records = load_edge_observation_table(ROOT / "cities" / city_id / relative)
    assert len(records) == expected_count
    assert all(record.observation.hazard_data_status == "UNKNOWN" for record in records)
    assert all(record.observation.overlap is None for record in records)
    assert all(record.observation.official_closure is None for record in records)
