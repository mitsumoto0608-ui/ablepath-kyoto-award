import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  assertSupportedMapCatalog,
  selectInitialMapMode,
} from "../../viewer/src/mapDomain.mjs";

const ROOT = new URL("../../", import.meta.url);
const CITY_IDS = ["fujisawa_enoshima", "kyoto_arashiyama", "kyoto_kiyomizu"];

function read(relativePath) {
  return readFileSync(new URL(relativePath, ROOT), "utf8");
}

function readJson(relativePath) {
  return JSON.parse(read(relativePath));
}

test("[source_conformance] Phase 4 gate is the sole three-city machine truth authority", () => {
  const gate = readJson("reports/PHASE4_ANALYSIS_UI_GATE.json");
  const truth = readJson("reports/COMPLETION_LEVELS.json");
  const catalog = assertSupportedMapCatalog(readJson("viewer/public/data/maps/map-layers.json"));

  assert.equal(gate.authority_role, "SOLE_CURRENT_MACHINE_TRUTH_ROOT");
  assert.equal(gate.overall_status, "PARTIAL_COMPLETE");
  assert.equal(gate.default_viewer_layer, "SYNTHETIC_DEMO");
  assert.equal(gate.all_three_data_ingested, true);
  assert.equal(gate.all_three_source_traceable_vgi_candidate_geometry, true);
  assert.equal(gate.all_three_topology_analysis_connected, true);
  assert.equal(gate.all_three_candidate_path_ui_connected, true);
  assert.equal(gate.all_three_explicit_opt_in_candidate_viewer_connected, true);
  assert.deepEqual(Object.keys(gate.cities).sort(), CITY_IDS);
  assert.deepEqual(catalog.cities.map((city) => city.city_id).sort(), CITY_IDS);

  for (const cityId of CITY_IDS) {
    const city = gate.cities[cityId];
    const layer = catalog.cities.find((candidate) => candidate.city_id === cityId);
    assert.equal(city.source_staged, true);
    assert.equal(city.normalized_ingested, true);
    assert.equal(city.topology_analysis, true);
    assert.equal(city.candidate_path_analysis, true);
    assert.equal(city.explicit_opt_in_candidate_viewer_connected, true);
    assert.equal(city.viewer_connection_scope, "VGI_CANDIDATE_ONLY");
    assert.equal(city.route_continuity, "NOT_ESTABLISHED");
    assert.equal(city.hazard_overlap_analysis, false);
    assert.equal(city.m7_ready_edge_count, 0);
    assert.equal(city.m7_computed_edge_count, 0);
    assert.equal(layer.real_2d.source_class, "VGI");
    assert.equal(layer.real_2d.geometry_status, "SOURCE_TRACEABLE_REAL");
    assert.equal(layer.real_2d.topology_status, "CANDIDATE_REVIEW_REQUIRED");
    assert.equal(layer.real_2d.route_continuity, "NOT_ESTABLISHED");
    assert.equal(selectInitialMapMode(catalog, cityId, ""), "synthetic");
    assert.equal(selectInitialMapMode(catalog, cityId, "?layer=real"), "real");
  }

  assert.equal(truth.CURRENT_MACHINE_TRUTH_AUTHORITY, "reports/PHASE4_ANALYSIS_UI_GATE.json");
  assert.equal(truth.ALL_THREE_CITIES_SOURCE_TRACEABLE_VGI_CANDIDATE_GEOMETRY, true);
  assert.equal(truth.ALL_THREE_CITIES_MAPLIBRE_CONNECTED, true);
  assert.equal(
    truth.MAPLIBRE_CONNECTED_SCOPE,
    "ALL_THREE_CITIES_EXPLICIT_OPT_IN_VGI_CANDIDATE_ONLY",
  );
  assert.equal(
    truth.REAL_GEOMETRY_CONNECTED_TO_VIEWER_SCOPE,
    "ALL_THREE_CITIES_EXPLICIT_OPT_IN_VGI_CANDIDATE_ONLY",
  );
  assert.equal(
    truth.TWO_D_IMPLEMENTATION,
    "HYBRID_SYNTHETIC_DEFAULT_WITH_THREE_CITY_REAL_CANDIDATE_OPT_IN",
  );

  assert.equal(gate.official_hazard_analysis_city_count, 0);
  assert.equal(gate.m7_ready_edge_count, 0);
  assert.equal(gate.m7_computed_edge_count, 0);
  assert.equal(gate.m6_status, "NOT_COMPUTED");
  for (const flag of [
    "official_hazard_connected",
    "m7_connected_to_real_edges",
    "m6_connected",
    "model_connected",
    "kpi_connected",
    "hokonavi_production_connected",
    "real_plateau_tileset_connected",
    "official_facilities_connected",
    "route_continuity_established",
    "real_map_complete",
    "safe_route_claim",
    "accessibility_claim",
    "admin_validated",
    "demo_complete",
    "public_release_ready",
  ]) {
    assert.equal(gate[flag], false, `${flag} must remain false`);
  }
  for (const flag of [
    "ALL_THREE_CITIES_REAL_GEOMETRY",
    "REAL_MAP_COMPLETE",
    "MODEL_CONNECTED",
    "M7_CONNECTED_TO_REAL_EDGES",
    "M6_CONNECTED",
    "KPI_CONNECTED",
    "ADMIN_VALIDATED",
    "DEMO_COMPLETE",
    "PUBLIC_RELEASE_READY",
    "CESIUM_CONNECTED",
    "PLATEAU_3D_CONNECTED",
  ]) {
    assert.equal(truth[flag], false, `${flag} must remain false`);
  }
});

test("[ui_regression] runtime catalog preserves explicit candidate mode and disconnected PLATEAU", () => {
  const catalog = assertSupportedMapCatalog(
    readJson("viewer/public/data/maps/map-layers.json"),
  );
  for (const city of catalog.cities) {
    assert.ok(city.real_2d);
    assert.equal(city.real_2d.topology_status, "CANDIDATE_REVIEW_REQUIRED");
    assert.equal(city.real_2d.route_continuity, "NOT_ESTABLISHED");
    assert.equal(selectInitialMapMode(catalog, city.city_id, ""), "synthetic");
    assert.equal(selectInitialMapMode(catalog, city.city_id, "?layer=real"), "real");
  }
  const kiyomizu = catalog.cities.find((city) => city.city_id === "kyoto_kiyomizu");
  assert.equal(kiyomizu.cesium.connected, false);
  assert.equal(kiyomizu.cesium.data_class, "OFFICIAL_METADATA_ONLY");
});

test("[source_conformance] current authority docs preserve scoped three-city truth", () => {
  const authority = read("reports/REPORT_AUTHORITY.md");
  const agents = read("AGENTS.md");
  const readme = read("README.md");
  const gaps = read("reports/KNOWN_GAPS.md");
  const release = read("reports/PUBLIC_RELEASE_GATE.md");
  const current = [agents, readme, gaps, release, authority].join("\n");

  assert.match(authority, /PHASE4_ANALYSIS_UI_GATE\.json.*sole current machine truth root/i);
  assert.match(authority, /PHASE3_MAP_UI_STATUS\.md.*historical/i);
  assert.match(current, /source-traceable VGI.*CANDIDATE/i);
  assert.match(current, /explicit opt-in/i);
  assert.match(current, /SYNTHETIC_DEMO/);
  assert.match(current, /NOT_ESTABLISHED/);
  assert.match(readme, /ALL_THREE_CITIES_SOURCE_TRACEABLE_VGI_CANDIDATE_GEOMETRY=true/);
  assert.match(readme, /ALL_THREE_CITIES_MAPLIBRE_CONNECTED=true/);
  assert.match(readme, /ALL_THREE_CITIES_REAL_GEOMETRY=false/);
  assert.match(readme, /PUBLIC_RELEASE_READY=false/);
  assert.match(readme, /synthetic fixture.*NOT_ESTABLISHED/i);

  for (const staleClaim of [
    "Kiyomizu alone",
    "清水だけは",
    "Arashiyama and Fujisawa remain synthetic fallbacks",
    "嵐山・藤沢はsynthetic fallbackのまま",
  ]) {
    assert.ok(!current.includes(staleClaim), `stale current claim found: ${staleClaim}`);
  }
  for (const unsafeClaim of [
    "安全な避難ルートを提供",
    "実座標edgeは通行可能です",
    "実座標edgeは安全です",
    "行政検証済み",
    "PUBLIC_RELEASE_READY=true",
    "DEMO_COMPLETE=true",
    "RAIN_L4では土砂警戒閉塞で石畳側全滅でも迂回は生きる",
  ]) {
    assert.ok(!current.includes(unsafeClaim), `unsafe claim found: ${unsafeClaim}`);
  }
});

test("[source_conformance] Gate 8 records incomplete official evidence as fail-closed status", () => {
  const gate8 = readJson("reports/G8_PLATEAU_FACILITY_STATUS.json");
  assert.equal(gate8.gate8_plateau_3d.status, "PARTIAL");
  assert.deepEqual(gate8.gate8_plateau_3d.connected_cities, []);
  assert.equal(gate8.gate8_plateau_3d.real_tileset, false);
  assert.equal(gate8.gate8_facilities.status, "BLOCKED");
  assert.deepEqual(gate8.gate8_facilities.connected_sources, []);
  assert.equal(gate8.gate8_facilities.operation_inferred, false);
  for (const source of gate8.gate8_plateau_3d.sources) {
    assert.equal(source.cors_verified, false);
    assert.equal(source.aoi_verified, false);
    assert.equal(source.connection_mode, "NOT_CONNECTED");
    assert.match(source.sha256, /^[a-f0-9]{64}$/);
  }
});
