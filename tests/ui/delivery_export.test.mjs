import test from "node:test";
import assert from "node:assert/strict";

import {
  checklistToCsv,
  checklistToJson,
  checklistToPrintableHtml,
  loadDeliveryAnalysis,
  validateDeliveryAnalysis,
} from "../../viewer/src/analysisDomain.mjs";
import { readFileSync } from "node:fs";

const hazard = { edge_id: " =formula", scenario_id: "flood", relation: "INTERSECTS", coverage_status: "WITHIN_KNOWN_COVERAGE", overlap_length_m: 12, metric_crs: "EPSG:6674", source_id: "nlni_a31b_2025_kyoto_flood", source_revision: "v1", source_sha256: "a".repeat(64), source_url: "https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip", license_status: "PERMITTED_WITH_OBLIGATIONS", coverage_selection_sha256: "d10455a376ee3d89b9618b77be85c51da5ebcc6687d17e92c492573f056e699e", source_feature_ids: ["feature-1"], source_classes: ["<script>alert(1)</script>"], reason: "metric overlap", limitations: "fixture only", interpretation: "evidence only", official_closure: null, damage_state: null, debris_present: null };

const checklist = {
  checklist_id: "kyoto_kiyomizu:a__b:review-v1",
  city_id: "kyoto_kiyomizu",
  path_key: "a__b",
  path_status: "CONNECTED",
  status: "READY_FOR_REVIEW",
  candidate_distance: 1,
  candidate_distance_unit: "coordinate_degree",
  path_reason: "candidate only",
  terrain: { status: "BLOCKED", sampled: false, reason: "datum unresolved" },
  facility: { status: "TABLE_ONLY", record_count: 1, reason: "operation UNKNOWN", record_ids: ["f1"] },
  rows: [{ edge_id: " =formula", hazard_refs: [" =formula\0flood\0nlni_a31b_2025_kyoto_flood"], terrain_status: "BLOCKED", terrain_sampled: false, terrain_reason: "datum unresolved", facility_status: "TABLE_ONLY", owner_candidate_types: ["HAZARD_DATA_STEWARD"], unknowns: ["M6", "M7"] }],
  safe_route_claim: false,
  accessibility_claim: false,
  admin_validated: false,
};

test("[ui_regression] review exports retain provenance and neutralize CSV/HTML injection", () => {
  const exportChecklist = { ...checklist, facility: { ...checklist.facility, records: [{ facility_record_id: "f1", name: " <script>alert(2)</script>", address: "address", source_id: "official-facility", source_version_or_valid_as_of: "v1", source_sha256: "b".repeat(64), source_url: "https://example.invalid/facility", license_status: "FIXTURE_ONLY", source_published_at: null, source_valid_as_of: "v1", source_acquired_at: null, source_temporal_status_reason: "timestamps unavailable", limitations: "fixture facility only", source_attributes: { listed: " =cmd" }, current_operation_status: "UNKNOWN", entrance_status: "UNKNOWN", unlock_status: "UNKNOWN", accessibility_status: "UNKNOWN", step_free_status: "UNKNOWN", disaster_availability_status: "UNKNOWN" }] }, rows: checklist.rows.map((row) => ({ ...row, hazards: [hazard] })) };
  const csv = checklistToCsv(exportChecklist);
  assert.match(csv, /^row_kind,edge_id,scenario_id,relation,coverage_status,/);
  assert.match(csv, /' =formula/);
  assert.match(csv, /official-facility/);
  assert.match(csv, /a{64}/);
  assert.match(csv, /metric overlap/);
  assert.match(csv, /https:\/\/nlftp\.mlit\.go\.jp\/ksj\/gml\/data\/A31b/);
  assert.match(csv, /https:\/\/example\.invalid\/facility/);
  assert.match(csv, /fixture facility only/);
  assert.match(csv, /timestamps unavailable/);
  const json = JSON.parse(checklistToJson(exportChecklist));
  assert.equal(json.rows[0].hazards[0].source_id, "nlni_a31b_2025_kyoto_flood");
  const html = checklistToPrintableHtml(exportChecklist);
  assert.ok(html.startsWith("<!doctype html>"));
  assert.doesNotMatch(html, /<script>alert/);
  assert.match(html, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.match(html, /印刷用確認リスト/);
  assert.match(html, /Content-Security-Policy/);
  assert.match(html, /公式施設原本属性/);
  assert.match(html, /WITHIN_KNOWN_COVERAGE/);
  assert.match(html, /metric overlap/);
  assert.match(html, /fixture facility only/);
  assert.match(html, /valid-as-of v1/);
});

test("[ui_regression] delivery analysis rejects promoted claims and missing checklist contract", () => {
  const analysis = JSON.parse(readFileSync(new URL("../../viewer/public/data/analysis/kyoto_kiyomizu.json", import.meta.url), "utf8"));
  assert.equal(validateDeliveryAnalysis(analysis, "kyoto_kiyomizu"), analysis);
  assert.throws(() => validateDeliveryAnalysis({ ...analysis, safety_claim: true }, "kyoto_kiyomizu"), /claim/i);
  assert.throws(() => validateDeliveryAnalysis({ ...analysis, review_checklists: {} }, "kyoto_kiyomizu"), /checklist/i);
  const badRelation = structuredClone(analysis);
  badRelation.official_evidence.hazard.edge_exposures.find((row) => row.relation === "INTERSECTS").overlap_length_m = 0;
  assert.throws(() => validateDeliveryAnalysis(badRelation, "kyoto_kiyomizu"), /hazard/i);
  for (const field of ["unlock_status", "step_free_status", "disaster_availability_status"]) {
    const promoted = structuredClone(analysis);
    promoted.official_evidence.facility.records[0][field] = "PROMOTED";
    assert.throws(() => validateDeliveryAnalysis(promoted, "kyoto_kiyomizu"), /facility/i);
  }
  for (const mutate of [
    (value) => { value.official_evidence.terrain.status = "ELEVATION_SAMPLED"; },
    (value) => { value.official_evidence.terrain.products[0].terrain_connected = true; },
    (value) => { value.official_evidence.facility.records[0].source_id = "invented"; },
    (value) => { value.official_evidence.facility.records[0].source_attributes = { wheelchair: true }; },
    (value) => { value.official_evidence.hazard.edge_exposures[0].source_sha256 = "0".repeat(64); },
    (value) => { value.official_evidence.hazard.edge_exposures[0].source_revision = "forged-revision"; },
    (value) => {
      const [key] = Object.keys(value.review_checklists).filter((candidate) => value.path_matrix[candidate].status === "CONNECTED");
      value.review_checklists[key].rows[0].edge_id = "other-edge";
    },
    (value) => {
      const [key] = Object.keys(value.review_checklists);
      value.review_checklists[key].path_key = "other-path";
    },
  ]) {
    const promoted = structuredClone(analysis);
    mutate(promoted);
    assert.throws(() => validateDeliveryAnalysis(promoted, "kyoto_kiyomizu"));
  }
});

test("[source_conformance] runtime analysis bytes must match the committed manifest", async () => {
  const analysisText = readFileSync(new URL("../../viewer/public/data/analysis/kyoto_kiyomizu.json", import.meta.url), "utf8");
  const manifestText = readFileSync(new URL("../../viewer/public/data/analysis/manifest.json", import.meta.url), "utf8");
  const response = (text) => ({ ok: true, status: 200, text: async () => text });
  const validFetch = async (url) => response(url.endsWith("manifest.json") ? manifestText : analysisText);
  await assert.doesNotReject(() => loadDeliveryAnalysis(validFetch, "./data/analysis/kyoto_kiyomizu.json", "kyoto_kiyomizu"));

  const changed = JSON.parse(analysisText);
  const overlap = changed.official_evidence.hazard.edge_exposures.find((row) => row.relation === "INTERSECTS");
  overlap.overlap_length_m += 123;
  const tamperedText = `${JSON.stringify(changed, null, 2)}\n`;
  const tamperedFetch = async (url) => response(url.endsWith("manifest.json") ? manifestText : tamperedText);
  await assert.rejects(() => loadDeliveryAnalysis(tamperedFetch, "./data/analysis/kyoto_kiyomizu.json", "kyoto_kiyomizu"), /committed manifest/);
});

test("[source_conformance] canonical Fujisawa evidence mutations fail closed", () => {
  const original = JSON.parse(readFileSync(new URL("../../viewer/public/data/analysis/fujisawa_enoshima.json", import.meta.url), "utf8"));
  for (const mutate of [
    (value) => { value.official_evidence.terrain.products[0].status = "CONNECTED"; },
    (value) => { value.official_evidence.hazard.scenarios[0].license_review = "APPROVED"; },
    (value) => { value.official_evidence.hazard.scenarios[0].validation_result = "VALIDATED"; },
    (value) => { value.official_evidence.hazard.scenarios[0].crs = "EPSG:4326"; },
    (value) => { value.official_evidence.hazard.scenarios.splice(1); },
    (value) => { value.official_evidence.hazard.scenarios[0].dataset_id = "invented"; },
    (value) => { value.official_evidence.hazard.scenarios[0].bounds_native = "[0, 0, 1, 1]"; },
    (value) => { value.official_evidence.hazard.scenarios[0].layer_kind = "invented"; },
    (value) => { value.official_evidence.hazard.source_catalog.nlni_a40_2020_kanagawa_tsunami.license_status = "PUBLIC_UNRESTRICTED"; },
    (value) => { value.official_evidence.hazard.source_catalog.nlni_a40_2020_kanagawa_tsunami.source_url = "https://example.invalid"; },
    (value) => { value.official_evidence.hazard.source_catalog.nlni_a40_2020_kanagawa_tsunami.coverage_selection_sha256 = "0".repeat(64); },
    (value) => { value.official_evidence.hazard.source_catalog.nlni_a40_2020_kanagawa_tsunami.source_sha256 = "0".repeat(64); },
    (value) => { value.official_evidence.hazard.source_catalog.nlni_a40_2020_kanagawa_tsunami.source_revision = "invented"; },
    (value) => { value.official_evidence.hazard.source_catalog.nlni_a40_2020_kanagawa_tsunami.limitations = "unrestricted"; },
    (value) => { value.official_evidence.facility.source_catalog.fujisawa_webgis_toilets_accessibility.license_status = "APPROVED"; },
    (value) => { value.official_evidence.facility.source_catalog.fujisawa_webgis_toilets_accessibility.acquired_at = "2030-01-01"; },
    (value) => { value.official_evidence.facility.source_catalog.fujisawa_webgis_toilets_accessibility.temporal_status_reason = "current"; },
    (value) => { value.official_evidence.facility.records[0].source_attributes.ostomate_detail_available = !value.official_evidence.facility.records[0].source_attributes.ostomate_detail_available; },
    (value) => {
      const replacement = !value.official_evidence.facility.records[0].source_attributes.ostomate_detail_available;
      value.official_evidence.facility.records[0].source_attributes.ostomate_detail_available = replacement;
      value.official_evidence.facility.records[0].source_attribute_entries[0][1] = replacement;
    },
    (value) => { value.official_evidence.facility.records[0].source_id = "invented"; },
    (value) => { value.official_evidence.facility.records[0].source_attributes = { wheelchair: true }; },
    (value) => {
      const [key] = Object.keys(value.review_checklists).filter((candidate) => value.path_matrix[candidate].status === "CONNECTED");
      value.review_checklists[key].rows.reverse();
    },
  ]) {
    const mutated = structuredClone(original);
    mutate(mutated);
    assert.throws(() => validateDeliveryAnalysis(mutated, "fujisawa_enoshima"));
  }
});
