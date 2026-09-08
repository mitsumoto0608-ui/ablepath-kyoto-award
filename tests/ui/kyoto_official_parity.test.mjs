import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";

const readJson = (path) => JSON.parse(readFileSync(new URL(`../../${path}`, import.meta.url), "utf8"));
const sha256 = (path) => createHash("sha256").update(readFileSync(new URL(`../../${path}`, import.meta.url))).digest("hex");

test("[source_conformance] Kyoto parity status separates display evidence from scientific and safety claims", () => {
  const status = readJson("reports/KYOTO_PARITY_STATUS.json");
  assert.deepEqual(Object.keys(status.aois).sort(), ["arashiyama", "gion", "kiyomizu", "kiyomizu_gion_connector"]);
  for (const aoi of Object.values(status.aois)) {
    assert.equal(aoi.terrain.evidence_ui_connected, true);
    assert.equal(aoi.terrain.elevation_sampled, false);
    assert.equal(aoi.terrain.step_inferred, false);
    assert.equal(aoi.terrain.cross_slope_inferred, false);
    assert.equal(aoi.flood.display_connected, true);
    assert.equal(aoi.flood.closure_derived, false);
    assert.equal(aoi.landslide.status, "NOT_CONNECTED");
    assert.ok(aoi.landslide.reason.length > 40);
    assert.equal(aoi.plateau.setback_derived, false);
  }
  assert.equal(status.safe_route_claim, false);
  assert.equal(status.accessibility_claim, false);
  assert.equal(status.admin_validated, false);
  assert.equal(status.MODEL_ROUTE_VERIFIED, false);
});

test("[source_conformance] Kyoto facilities use only source-provided coordinates and keep five categories distinct", () => {
  const root = "inputs/staging/KYOTO-OFFICIAL-PARITY-V1";
  const categories = readJson(`${root}/facility_category_status.json`);
  const records = readJson(`${root}/facility_records.json`);
  const points = readJson(`${root}/facility_points.geojson`);
  assert.deepEqual(Object.keys(categories.categories).sort(), [
    "designated_emergency_evacuation_place",
    "designated_shelter",
    "emergency_open_space",
    "public_tourist_toilet",
    "temporary_stay_facility",
  ]);
  assert.ok(records.records.length > 0);
  assert.equal(points.features.length, records.records.length);
  for (const record of records.records) {
    assert.equal(record.coordinate_method, "SOURCE_PROVIDED_LONGITUDE_LATITUDE");
    assert.equal(record.silent_geocoding, false);
    assert.equal(record.entrance_status, "UNKNOWN");
    assert.equal(record.operation_status, "UNKNOWN");
    assert.equal(record.accessibility_status, "UNKNOWN");
    assert.ok(Number.isFinite(record.longitude) && Number.isFinite(record.latitude));
  }
  assert.equal(categories.categories.emergency_open_space.status, "METADATA_ONLY_NOT_CONNECTED");
  assert.equal(categories.categories.temporary_stay_facility.status, "METADATA_ONLY_NOT_CONNECTED");
});

test("[software_correctness] Kyoto handoff receipt is non-recursive and binds every generated peer artifact", () => {
  const root = "inputs/staging/KYOTO-OFFICIAL-PARITY-V1";
  const handoff = readJson(`${root}/handoff.json`);
  assert.equal(Object.hasOwn(handoff.generated_artifacts, "handoff.json"), false);
  for (const name of [
    "a31b_kiyomizu_gion_display.geojson",
    "a31b_arashiyama_display.geojson",
    "dem_aoi_validation.json",
    "facility_category_status.json",
    "facility_points.geojson",
    "facility_points_kiyomizu_gion.geojson",
    "facility_points_arashiyama.geojson",
    "facility_records.json",
    "source_receipts.json",
  ]) assert.equal(handoff.generated_artifacts[name], sha256(`${root}/${name}`), name);
});

test("[software_correctness] Kyoto hazard display artifacts cannot create operational or M7 state", () => {
  for (const name of ["a31b_kiyomizu_gion_display.geojson", "a31b_arashiyama_display.geojson"]) {
    const artifact = readJson(`inputs/staging/KYOTO-OFFICIAL-PARITY-V1/${name}`);
    assert.ok(artifact.features.length > 0);
    for (const feature of artifact.features) {
      for (const forbidden of ["official_closure", "damage_state", "debris_present", "setback_m"]) {
        assert.equal(Object.hasOwn(feature.properties, forbidden), false);
      }
      assert.equal(feature.properties._ablepath_display_only, true);
      assert.ok(feature.properties._ablepath_source_member);
      assert.ok(Number.isInteger(feature.properties._ablepath_source_feature_index));
    }
  }
});

test("[source_conformance] Kyoto ten-edge M7 pilot is reasoned null with per-field acquisition guidance", () => {
  const pilot = readJson("reports/KYOTO_M7_DEEP_PILOT_STATUS.json");
  assert.equal(pilot.selected_edge_count, 10);
  assert.equal(pilot.computed_count, 0);
  assert.equal(pilot.evidence_ready_count, 0);
  assert.equal(pilot.groups.kiyomizu_gion.selected_edge_count, 5);
  assert.equal(pilot.groups.arashiyama.selected_edge_count, 5);
  for (const edge of pilot.edges) {
    assert.equal(edge.m7_result, null);
    assert.equal(edge.status, "NOT_COMPUTED");
    assert.ok(edge.reason);
    assert.ok(edge.missing_fields.length > 0);
    for (const field of edge.missing_fields) {
      assert.ok(edge.field_resolution[field].evidence_candidates.length > 0, `${edge.edge_id}:${field}`);
      assert.ok(edge.field_resolution[field].next_acquisition_method.length > 20, `${edge.edge_id}:${field}`);
    }
  }
});

test("[ui_regression] delivered Kyoto analyses bind flood, facilities, PLATEAU fallback, and reasoned-null pilot", () => {
  for (const cityId of ["kyoto_kiyomizu", "kyoto_arashiyama"]) {
    const analysis = readJson(`viewer/public/data/analysis/${cityId}.json`);
    const evidence = analysis.official_evidence;
    assert.equal(evidence.terrain.evidence_ui_connected, true);
    assert.equal(evidence.hazard.display_connected, true);
    assert.ok(evidence.hazard.display_feature_count > 0);
    assert.equal(evidence.hazard.closure_derived, false);
    assert.ok(evidence.facility.records.length > 0);
    assert.ok(evidence.facility.records.every((row) => row.silent_geocoding === false));
    assert.equal(Object.values(evidence.facility.categories).reduce((sum, row) => sum + row.record_count, 0), evidence.facility.record_count);
    assert.ok(evidence.plateau.inventory.length > 0);
    assert.equal(evidence.plateau.fallback, "EXISTING_DETERMINISTIC_2D");
    assert.equal(evidence.m7.kyoto_deep_pilot_edges.length, 5);
    assert.ok(evidence.m7.kyoto_deep_pilot_edges.every((row) => row.m7_result === null && row.field_resolution));
  }
});

test("[source_conformance] global reports preserve scoped Kyoto connection truth", () => {
  const promotion = readJson("reports/KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json");
  const status = readJson("reports/OFFICIAL_DATA_ANALYSIS_UI_STATUS.json");
  const gate = readJson("reports/OFFICIAL_DATA_ANALYSIS_UI_GATE.json");
  const final = readJson("reports/OFFICIAL_DATA_TO_M7_FINAL_STATUS.json");
  const authority = readJson("reports/PHASE4_ANALYSIS_UI_GATE.json");
  for (const cityId of ["kyoto_kiyomizu", "kyoto_arashiyama"]) {
    const city = promotion.cities[cityId];
    assert.equal(city.dem_validated, false);
    assert.equal(city.dem_inventory_validated, true);
    assert.equal(city.terrain_evidence_ui_connected, true);
    assert.equal(city.terrain_elevation_analysis_connected, false);
    assert.equal(city.flood_connected, true);
    assert.match(city.flood_connected_scope, /DISPLAY_ONLY_NOT_EDGE_OVERLAP_OR_OPERATIONAL_STATE/);
    assert.equal(city.official_facility_map_connected, true);
    assert.match(city.official_facility_connection_scope, /SOURCE_PROVIDED_COORDINATES_ONLY/);
    assert.equal(status.cities[cityId].hazard_edge_analysis, "NOT_CONNECTED");
    assert.equal(status.cities[cityId].plateau_real_3d, "NOT_CONNECTED");
  }
  assert.equal(gate.pass_conditions.kyoto_a31b_two_aoi_display_connected, true);
  assert.equal(gate.pass_conditions.kyoto_silent_geocoding, false);
  assert.equal(final.data.kyoto_a31b_internal_display_aoi_count, 2);
  assert.equal(final.data.kyoto_facility_source_coordinate_record_count, 77);
  assert.equal(final.data.official_hazard_edge_analysis_connected_city_count, 0);
  assert.equal(promotion.cities.kyoto_kiyomizu.official_facility_record_count, 58);
  assert.equal(promotion.cities.kyoto_arashiyama.official_facility_record_count, 19);
  assert.equal(authority.kyoto_a31b_internal_display_connected, true);
  assert.equal(authority.official_hazard_connected, false);
  assert.equal(authority.kyoto_terrain_evidence_ui_connected, true);
  assert.equal(authority.kyoto_terrain_elevation_analysis_connected, false);
  assert.equal(authority.kyoto_official_facility_source_coordinate_display_connected, true);
  assert.equal(authority.official_facilities_connected, false);
});
