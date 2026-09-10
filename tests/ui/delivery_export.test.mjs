import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";

import {
  checklistToCsv,
  checklistToJson,
  checklistToPrintableHtml,
  loadDeliveryAnalysis,
  selectChecklistRows,
  selectUnresolvedTerrainRecords,
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
  assert.match(csv, /^row_kind,city_id,path_key,path_status,checklist_status,candidate_distance,candidate_distance_unit,path_reason,filters,sort_by,safe_route_claim,accessibility_claim,admin_validated,/);
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

function exportChecklist(analysis, pathKey, terrainProduct = "ALL") {
  const checklist = structuredClone(analysis.review_checklists[pathKey]);
  const exposure = new Map(analysis.official_evidence.hazard.edge_exposures.map((row) => [`${row.edge_id}\0${row.scenario_id}\0${row.source_id}`, row]));
  const terrain = new Map(analysis.official_evidence.terrain.samples.map((row) => [row.sample_id, row]));
  checklist.rows = checklist.rows.map((row) => ({ ...row, terrain_samples: row.terrain_sample_ids.map((key) => terrain.get(key)).filter((sample) => terrainProduct === "ALL" || sample.product === terrainProduct), hazards: row.hazard_refs.map((key) => exposure.get(key)) }));
  checklist.facility.records = analysis.official_evidence.facility.records;
  const unresolved = selectUnresolvedTerrainRecords(analysis.official_evidence.terrain.samples, terrainProduct);
  checklist.terrain_unresolved_records = unresolved.records;
  checklist.terrain_unresolved_summary = unresolved.summary;
  checklist.filters = { scenario: "ALL", relation: "ALL", owner: "ALL", unknown_only: false, terrain_product: terrainProduct };
  checklist.sort_by = "EDGE";
  return checklist;
}

test("[ui_regression] three-region connected and disconnected exports preserve selection, DEM filter, sort, and row sets", () => {
  const examples = [
    ["kyoto_kiyomizu", "KK-OSM-N1697644482__KK-OSM-N5315789346", "KK-OSM-N1697644482__KK-OSM-N3752885643"],
    ["kyoto_arashiyama", "kyoto-arashiyama:osm-node-000243776546__kyoto-arashiyama:osm-node-014102818768", "kyoto-arashiyama:osm-node-000243776546__kyoto-arashiyama:osm-node-001212123705"],
    ["fujisawa_enoshima", "FJ-OSM-N-1922FF848B18A1BF__FJ-OSM-N-2174B5DE701CA180", null],
  ];
  for (const [cityId, configuredConnected, configuredDisconnected] of examples) {
    const analysis = JSON.parse(readFileSync(new URL(`../../viewer/public/data/analysis/${cityId}.json`, import.meta.url), "utf8"));
    const connectedKey = configuredConnected ?? Object.keys(analysis.path_matrix).find((key) => analysis.path_matrix[key].status === "CONNECTED");
    const disconnectedKey = configuredDisconnected === null ? null : configuredDisconnected;
    const pathCases = [[connectedKey, "CONNECTED"]];
    if (disconnectedKey !== null) pathCases.push([disconnectedKey, "DISCONNECTED"]);
    for (const [pathKey, expectedStatus] of pathCases) {
      const selected = exportChecklist(analysis, pathKey);
      const csv = checklistToCsv(selected);
      const json = JSON.parse(checklistToJson(selected));
      const html = checklistToPrintableHtml(selected);
      assert.equal(json.path_key, pathKey);
      assert.equal(json.path_status, expectedStatus);
      assert.match(csv, new RegExp(pathKey.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
      assert.match(html, new RegExp(pathKey.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
      assert.match(csv, /"\{""owner"":""ALL""/u);
      assert.match(html, /filters:/);
      const exportedCandidateEdges = csv.split("\n").slice(1).filter((line) => line.startsWith('"candidate_edge"')).map((line) => selected.rows.find((row) => line.includes(row.edge_id))?.edge_id).filter(Boolean);
      assert.deepEqual([...new Set(exportedCandidateEdges)], selected.rows.map((row) => row.edge_id));
      for (const row of selected.rows) assert.match(html, new RegExp(row.edge_id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
      if (expectedStatus === "DISCONNECTED") {
        assert.equal(selected.rows.length, 0);
        assert.equal(json.candidate_distance, null);
        assert.match(csv, /"path_summary"/);
        assert.match(csv, new RegExp(selected.path_reason.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
        assert.match(html, new RegExp(selected.path_reason.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
        assert.match(csv, /accessibility \| passability \| current_facility_operation \| M6 \| M7/);
      } else {
        assert.ok(selected.rows.length > 0);
        assert.equal(json.candidate_distance, analysis.path_matrix[pathKey].geometric_length);
        assert.ok(json.rows.every((row) => row.terrain_samples.length > 0));
        assert.match(csv, /DEM1A/);
        assert.match(csv, /DEM5A/);
        assert.match(html, /SAMPLED_NATIVE_CELL/);
        for (const product of ["DEM1A", "DEM5A"]) {
          const filtered = exportChecklist(analysis, pathKey, product);
          const filteredCsv = checklistToCsv(filtered);
          const filteredJson = JSON.parse(checklistToJson(filtered));
          const filteredHtml = checklistToPrintableHtml(filtered);
          assert.equal(filteredJson.city_id, cityId);
          assert.equal(filteredJson.path_key, pathKey);
          assert.equal(filteredJson.filters.terrain_product, product);
          assert.equal(filteredJson.sort_by, "EDGE");
          assert.ok(filteredJson.rows.every((row) => row.terrain_samples.every((sample) => sample.product === product)));
          assert.match(filteredCsv, /terrain_product/);
          assert.match(filteredHtml, new RegExp(product));
          const expectedEdges = filteredJson.rows.map((row) => row.edge_id);
          const csvEdges = filteredCsv.split("\n").slice(1).filter((line) => line.startsWith('"candidate_edge"')).map((line) => expectedEdges.find((edgeId) => line.includes(edgeId))).filter(Boolean);
          assert.deepEqual([...new Set(csvEdges)], expectedEdges);
          for (const edgeId of expectedEdges) assert.match(filteredHtml, new RegExp(edgeId.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
        }
      }
      assert.equal(json.safe_route_claim, false);
      assert.equal(json.accessibility_claim, false);
      assert.equal(json.admin_validated, false);
      assert.match(csv, /,"false","false","false",/);
      assert.match(html, /safe_route_claim=false \/ accessibility_claim=false \/ admin_validated=false/);
      assert.match(html, /official_closure=null \/ damage_state=null \/ debris_present=null/);
      assert.match(csv, /current_operation_status,entrance_status,unlock_status,accessibility_status,step_free_status,disaster_availability_status/);
      if (expectedStatus === "CONNECTED") {
        for (const line of csv.split("\n").filter((value) => value.startsWith('"candidate_edge"'))) assert.match(line, /,"null","null","null",/);
      }
    }
    const filteredToZero = exportChecklist(analysis, connectedKey);
    filteredToZero.rows = [];
    const filteredCsv = checklistToCsv(filteredToZero);
    assert.match(filteredCsv, /"path_summary"/);
    assert.match(filteredCsv, /accessibility \| passability \| current_facility_operation \| M6 \| M7/);
    assert.doesNotMatch(filteredCsv, /"candidate_edge"/);
  }
});

test("[ui_regression] Fujisawa unresolved native-cell records remain null and reasoned in every export format", () => {
  const analysis = JSON.parse(readFileSync(new URL("../../viewer/public/data/analysis/fujisawa_enoshima.json", import.meta.url), "utf8"));
  const connectedKey = Object.keys(analysis.path_matrix).find((key) => analysis.path_matrix[key].status === "CONNECTED");
  for (const [product, expectedRecords] of [["ALL", 6], ["DEM1A", 3], ["DEM5A", 3]]) {
    const selected = exportChecklist(analysis, connectedKey, product);
    const csv = checklistToCsv(selected);
    const json = JSON.parse(checklistToJson(selected));
    const html = checklistToPrintableHtml(selected);
    assert.equal(json.terrain_unresolved_records.length, expectedRecords);
    assert.equal(json.terrain_unresolved_summary.record_count, expectedRecords);
    assert.equal(json.terrain_unresolved_summary.unique_coordinate_count, 1);
    assert.equal(csv.split("\n").filter((line) => line.startsWith('"terrain_unresolved"')).length, expectedRecords);
    for (const sample of json.terrain_unresolved_records) {
      assert.equal(sample.elevation_m, null);
      assert.equal(sample.status, "SURFACE_VALUE_UNRESOLVED");
      assert.ok(sample.reason);
      assert.match(csv, new RegExp(sample.sample_id));
      assert.match(csv, /,"null",/);
      assert.match(html, new RegExp(sample.sample_id));
      assert.match(html, new RegExp(sample.reason.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
    }
  }
  const twoLocations = selectUnresolvedTerrainRecords([
    { elevation_m: null, product: "DEM1A", query_longitude: 135.0, query_latitude: 35.0 },
    { elevation_m: null, product: "DEM1A", query_longitude: 135.1, query_latitude: 35.1 },
  ]);
  assert.deepEqual(twoLocations.summary, { record_count: 2, unique_coordinate_count: 2 });
});

test("[ui_regression] every review filter and sort preserves screen-equivalent row order across CSV JSON and HTML", () => {
  for (const cityId of ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"]) {
    const analysis = JSON.parse(readFileSync(new URL(`../../viewer/public/data/analysis/${cityId}.json`, import.meta.url), "utf8"));
    const pathKey = Object.keys(analysis.path_matrix).find((key) => analysis.path_matrix[key].status === "CONNECTED");
    const base = exportChecklist(analysis, pathKey);
    const sourceCatalog = base.source_catalog ?? {};
    const exposures = new Map(analysis.official_evidence.hazard.edge_exposures.map((hazardRow) => [`${hazardRow.edge_id}\0${hazardRow.scenario_id}\0${hazardRow.source_id}`, { ...hazardRow, ...sourceCatalog[hazardRow.source_id] }]));
    const hydratedRows = base.rows.map((row) => ({ ...row, hazards: row.hazard_refs.map((ref) => exposures.get(ref)).filter(Boolean) }));
    const hazards = hydratedRows.flatMap((row) => row.hazards);
    const representativeFilters = [
      { scenario: hazards[0]?.scenario_id },
      { revision: hazards[0]?.source_revision },
      { coverage: hazards[0]?.coverage_status },
      { unknown: hydratedRows[0]?.unknowns[0] },
      { owner: hydratedRows[0]?.owner_candidate_types[0] },
      { reason: hazards[0]?.source_id.slice(0, 10) },
    ].filter((entry) => Object.values(entry)[0]);
    for (const filters of [{}, ...representativeFilters]) {
      for (const sortBy of ["EDGE", "REVISION", "COVERAGE", "REASON", "OWNER"]) {
        const rows = selectChecklistRows(hydratedRows, filters, sortBy);
        const selected = { ...base, rows, filters: { scenario: "ALL", revision: "ALL", coverage: "ALL", unknown: "ALL", owner: "ALL", reason: "", ...filters }, sort_by: sortBy };
        const json = JSON.parse(checklistToJson(selected));
        const csv = checklistToCsv(selected);
        const html = checklistToPrintableHtml(selected);
        const expectedOrder = rows.map((row) => row.edge_id);
        assert.deepEqual(json.rows.map((row) => row.edge_id), expectedOrder);
        let previousPosition = -1;
        for (const edgeId of expectedOrder) {
          assert.match(csv, new RegExp(edgeId.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
          const position = html.indexOf(edgeId);
          assert.ok(position > previousPosition);
          previousPosition = position;
        }
        const csvOrder = [...new Set(csv.split("\n").filter((line) => line.startsWith('"candidate_edge"')).map((line) => base.rows.map((row) => row.edge_id).find((edgeId) => line.includes(`"${edgeId}"`))).filter(Boolean))];
        assert.deepEqual(csvOrder, expectedOrder);
        const htmlOrder = base.rows.map((row) => [row.edge_id, html.indexOf(row.edge_id)]).filter(([, position]) => position >= 0).sort((left, right) => left[1] - right[1]).map(([edgeId]) => edgeId);
        assert.deepEqual(htmlOrder, expectedOrder);
        assert.match(csv, new RegExp(`"${sortBy}"`));
        assert.match(html, new RegExp(`sort: ${sortBy}`));
      }
    }
  }
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
    (value) => { value.official_evidence.terrain.products[0].terrain_connected = false; },
    (value) => { value.official_evidence.terrain.samples[0].elevation_m = true; },
    (value) => { value.official_evidence.terrain.sample_record_count += 1; },
    (value) => { value.review_checklists[Object.keys(value.review_checklists).find((key) => value.path_matrix[key].status === "CONNECTED")].rows[0].terrain_sample_ids[0] = "stale-sample-id"; },
    (value) => { value.official_evidence.facility.records[0].source_id = "invented"; },
    (value) => { value.official_evidence.facility.records[0].source_attributes = { wheelchair: true }; },
    (value) => { value.official_evidence.hazard.edge_exposures[0].source_sha256 = "0".repeat(64); },
    (value) => { value.official_evidence.hazard.edge_exposures[0].source_revision = "forged-revision"; },
    (value) => {
      const [key] = Object.keys(value.review_checklists).filter((candidate) => value.path_matrix[candidate].status === "CONNECTED");
      value.review_checklists[key].rows[0].edge_id = "other-edge";
    },
    (value) => {
      const [key] = Object.keys(value.review_checklists).filter((candidate) => value.path_matrix[candidate].status === "CONNECTED");
      value.review_checklists[key].rows[0].unknowns = value.review_checklists[key].rows[0].unknowns.filter((entry) => entry !== "M7");
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

  const matchingTamperedManifest = JSON.parse(manifestText);
  matchingTamperedManifest.artifacts["kyoto_kiyomizu.json"] = createHash("sha256").update(tamperedText).digest("hex");
  const matchingTamperedManifestText = `${JSON.stringify(matchingTamperedManifest, null, 2)}\n`;
  const jointlyTamperedFetch = async (url) => response(url.endsWith("manifest.json") ? matchingTamperedManifestText : tamperedText);
  await assert.rejects(() => loadDeliveryAnalysis(jointlyTamperedFetch, "./data/analysis/kyoto_kiyomizu.json", "kyoto_kiyomizu"), /canonical delivery artifact/);

  const arashiyamaText = readFileSync(new URL("../../viewer/public/data/analysis/kyoto_arashiyama.json", import.meta.url), "utf8");
  assert.ok(new TextEncoder().encode(arashiyamaText).byteLength < 8_000_000);
  const arashiyamaFetch = async (url) => response(url.endsWith("manifest.json") ? manifestText : arashiyamaText);
  await assert.doesNotReject(() => loadDeliveryAnalysis(arashiyamaFetch, "./data/analysis/kyoto_arashiyama.json", "kyoto_arashiyama"));

  const oversizedFetch = async (url) => response(url.endsWith("manifest.json") ? manifestText : " ".repeat(8_000_001));
  await assert.rejects(() => loadDeliveryAnalysis(oversizedFetch, "./data/analysis/kyoto_arashiyama.json", "kyoto_arashiyama"), /exceeds static viewer byte limit/);
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
    (value) => { value.official_evidence.hazard.source_catalog.kanagawa_r7_liquefaction_distribution_01.source_member_receipt.dbf_sha256 = "0".repeat(64); },
    (value) => { value.official_evidence.hazard.source_catalog.nlni_a40_2020_kanagawa_tsunami.limitations = "unrestricted"; },
    (value) => { value.official_evidence.facility.source_catalog.fujisawa_webgis_toilets_accessibility.license_status = "APPROVED"; },
    (value) => { value.official_evidence.facility.source_catalog.fujisawa_webgis_toilets_accessibility.acquired_at = "2030-01-01"; },
    (value) => { value.official_evidence.facility.source_catalog.fujisawa_webgis_toilets_accessibility.temporal_status_reason = "current"; },
    (value) => { value.official_evidence.facility.records.push({ facility_record_id: "republished-without-license" }); value.official_evidence.facility.record_count = 1; },
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
