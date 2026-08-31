import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  assertSupportedMapCatalog,
  selectInitialMapMode,
} from "../../viewer/src/mapDomain.mjs";

const ROOT = new URL("../../", import.meta.url);

function read(relativePath) {
  return readFileSync(new URL(relativePath, ROOT), "utf8");
}

function readJson(relativePath) {
  return JSON.parse(read(relativePath));
}

test("[source_conformance] global truth matches the scoped Phase 3 map capability", () => {
  const truth = readJson("reports/COMPLETION_LEVELS.json");
  assert.equal(truth.MAPLIBRE_RUNTIME_IMPLEMENTED, true);
  assert.equal(truth.MAPLIBRE_CONNECTED, true);
  assert.equal(truth.MAPLIBRE_CONNECTED_SCOPE, "KIYOMIZU_EXPLICIT_OPT_IN_CANDIDATE_ONLY");
  assert.equal(truth.KIYOMIZU_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER, true);
  assert.equal(truth.REAL_GEOMETRY_CONNECTED_TO_VIEWER, true);
  assert.equal(truth.REAL_GEOMETRY_CONNECTED_TO_VIEWER_SCOPE, "KIYOMIZU_CANDIDATE_ONLY");
  assert.equal(truth.ALL_THREE_CITIES_MAPLIBRE_CONNECTED, false);
  assert.equal(truth.ALL_THREE_CITIES_REAL_GEOMETRY, false);
  assert.equal(truth.REAL_MAP_COMPLETE, false);
  assert.equal(
    truth.TWO_D_IMPLEMENTATION,
    "HYBRID_SYNTHETIC_DEFAULT_WITH_KIYOMIZU_REAL_CANDIDATE_OPT_IN",
  );
  assert.equal(truth.CESIUM_RUNTIME_IMPLEMENTED, true);
  assert.equal(truth.CESIUM_CONNECTED, false);
  assert.equal(truth.PLATEAU_3D_CONNECTED, false);
  assert.equal(
    truth.THREE_D_IMPLEMENTATION,
    "RUNTIME_IMPLEMENTED_MOCKED_GATE_REAL_TILESET_NOT_VALIDATED",
  );
  for (const flag of [
    "MODEL_CONNECTED",
    "M7_CONNECTED_TO_REAL_EDGES",
    "M6_CONNECTED",
    "KPI_CONNECTED",
    "ADMIN_VALIDATED",
    "DEMO_COMPLETE",
    "PUBLIC_RELEASE_READY",
  ]) {
    assert.equal(truth[flag], false, `${flag} must remain false`);
  }
});

test("[ui_regression] runtime catalog preserves explicit Kiyomizu-only real mode and disconnected PLATEAU", () => {
  const catalog = assertSupportedMapCatalog(
    readJson("viewer/public/data/maps/map-layers.json"),
  );
  const kiyomizu = catalog.cities.find((city) => city.city_id === "kyoto_kiyomizu");
  const arashiyama = catalog.cities.find((city) => city.city_id === "kyoto_arashiyama");
  const fujisawa = catalog.cities.find((city) => city.city_id === "fujisawa_enoshima");

  assert.ok(kiyomizu.real_2d);
  assert.equal(kiyomizu.real_2d.topology_status, "CANDIDATE_REVIEW_REQUIRED");
  assert.equal(kiyomizu.real_2d.route_continuity, "NOT_ESTABLISHED");
  assert.equal(selectInitialMapMode(catalog, "kyoto_kiyomizu", ""), "synthetic");
  assert.equal(selectInitialMapMode(catalog, "kyoto_kiyomizu", "?layer=real"), "real");
  assert.equal(arashiyama.real_2d, null);
  assert.equal(fujisawa.real_2d, null);
  assert.equal(kiyomizu.cesium.connected, false);
  assert.equal(kiyomizu.cesium.data_class, "OFFICIAL_METADATA_ONLY");
});

test("[source_conformance] authoritative docs state the same scoped map truth without unsafe claims", () => {
  const docs = [
    "AGENTS.md",
    "README.md",
    "reports/KNOWN_GAPS.md",
    "reports/PUBLIC_RELEASE_GATE.md",
    "reports/REPORT_AUTHORITY.md",
    "reports/PHASE3_MAP_UI_STATUS.md",
  ].map((path) => [path, read(path)]);
  const joined = docs.map(([path, content]) => `${path}\n${content}`).join("\n");

  for (const expected of [
    "MAPLIBRE_RUNTIME_IMPLEMENTED=true",
    "MAPLIBRE_CONNECTED_SCOPE=KIYOMIZU_EXPLICIT_OPT_IN_CANDIDATE_ONLY",
    "KIYOMIZU_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER=true",
    "REAL_GEOMETRY_CONNECTED_TO_VIEWER_SCOPE=KIYOMIZU_CANDIDATE_ONLY",
    "ALL_THREE_CITIES_MAPLIBRE_CONNECTED=false",
    "CESIUM_RUNTIME_IMPLEMENTED=true",
    "PLATEAU_3D_CONNECTED=false",
    "PUBLIC_RELEASE_READY=false",
  ]) {
    assert.ok(joined.includes(expected), `missing authoritative truth: ${expected}`);
  }

  const expectedAssignments = new Map([
    ["TWO_D_IMPLEMENTATION", "HYBRID_SYNTHETIC_DEFAULT_WITH_KIYOMIZU_REAL_CANDIDATE_OPT_IN"],
    ["MAPLIBRE_RUNTIME_IMPLEMENTED", "true"],
    ["MAPLIBRE_CONNECTED", "true"],
    ["MAPLIBRE_CONNECTED_SCOPE", "KIYOMIZU_EXPLICIT_OPT_IN_CANDIDATE_ONLY"],
    ["KIYOMIZU_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER", "true"],
    ["REAL_GEOMETRY_ARTIFACTS_AVAILABLE", "PARTIAL"],
    ["REAL_GEOMETRY_CONNECTED", "true"],
    ["REAL_GEOMETRY_CONNECTED_SCOPE", "KIYOMIZU_CANDIDATE_VIEWER_ONLY_NOT_MODEL_PIPELINE"],
    ["REAL_GEOMETRY_CONNECTED_TO_VIEWER", "true"],
    ["REAL_GEOMETRY_CONNECTED_TO_VIEWER_SCOPE", "KIYOMIZU_CANDIDATE_ONLY"],
    ["ALL_THREE_CITIES_MAPLIBRE_CONNECTED", "false"],
    ["ALL_THREE_CITIES_REAL_GEOMETRY", "false"],
    ["REAL_MAP_COMPLETE", "false"],
    ["CESIUM_RUNTIME_IMPLEMENTED", "true"],
    ["CESIUM_CONNECTED", "false"],
    ["PLATEAU_3D_CONNECTED", "false"],
    ["THREE_D_IMPLEMENTATION", "RUNTIME_IMPLEMENTED_MOCKED_GATE_REAL_TILESET_NOT_VALIDATED"],
    ["MODEL_CONNECTED", "false"],
    ["M7_CONNECTED_TO_REAL_EDGES", "false"],
    ["M6_CONNECTED", "false"],
    ["KPI_CONNECTED", "false"],
    ["ADMIN_VALIDATED", "false"],
    ["DEMO_COMPLETE", "false"],
    ["PUBLIC_RELEASE_READY", "false"],
  ]);
  for (const [key, expected] of expectedAssignments) {
    const pattern = new RegExp(`\\b${key}=([A-Z0-9_]+|true|false)\\b`, "g");
    const observed = [...joined.matchAll(pattern)].map((match) => match[1]);
    assert.ok(observed.length > 0, `missing assignment for ${key}`);
    assert.deepEqual([...new Set(observed)], [expected], `conflicting assignment for ${key}`);
  }

  assert.doesNotMatch(joined, /MapLibre is not connected/);
  assert.doesNotMatch(joined, /3D\/Cesium\/PLATEAU is `NOT_IMPLEMENTED`/);
  for (const unsafeClaim of [
    "安全な避難ルートを提供",
    "実座標edgeは通行可能です",
    "実座標edgeは安全です",
    "行政検証済み",
    "PUBLIC_RELEASE_READY=true",
    "DEMO_COMPLETE=true",
  ]) {
    assert.ok(!joined.includes(unsafeClaim), `unsafe claim found: ${unsafeClaim}`);
  }
});
