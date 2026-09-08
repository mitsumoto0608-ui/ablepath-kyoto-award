import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import {
  assertSupportedMapCatalog,
  computeGeoJsonBounds,
  isVerifiedCesiumConnection,
  selectInitialMapMode,
} from "../../viewer/src/mapDomain.mjs";
import { assertDeliveredMapArtifacts, buildMapArtifacts } from "../../viewer/scripts/build-map-artifacts.mjs";
import { installCesiumFailureListeners, withTimeout } from "../../viewer/src/mapAsync.mjs";
import { selectInitialState, serializeState } from "../../viewer/src/domain.mjs";

const REPO_ROOT = new URL("../../", import.meta.url);
const SOURCE_EDGE_SHA = "73e4f2d6965be2c8bb7a13229b4352fdef6886510219ebf9855d9581bbc3da7b";
const CORRIDOR_SHA = "48b08553a9c2d7f8388bd893e83133287e01ad2efa9326116f5e8d3a31836dc7";
const SOURCE_EDGE_PATHS = {
  kyoto_kiyomizu: "cities/kyoto_kiyomizu/graph/real/candidate_edges.geojson",
  kyoto_arashiyama: "cities/kyoto_arashiyama/graph/walk_edges.real.geojson",
  fujisawa_enoshima: "cities/fujisawa_enoshima/graph/candidate_walk_edges.real.geojson",
};

const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

test("[source_conformance] build copies all allowlisted city candidate graphs with hash-bound lineage", () => {
  const output = mkdtempSync(join(tmpdir(), "ablepath-map-artifacts-"));
  try {
    const result = buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output });
    const catalog = assertSupportedMapCatalog(readJson(join(output, "map-layers.json")));
    const kiyomizu = catalog.cities.find((city) => city.city_id === "kyoto_kiyomizu");
    assert.equal(kiyomizu.real_2d.artifact_sha256, SOURCE_EDGE_SHA);
    assert.equal(kiyomizu.real_2d.corridor_sha256, CORRIDOR_SHA);
    assert.equal(kiyomizu.real_2d.copied_sha256, SOURCE_EDGE_SHA);
    assert.equal(kiyomizu.real_2d.feature_count, 19);
    assert.equal(kiyomizu.real_2d.topology_status, "CANDIDATE_REVIEW_REQUIRED");
    assert.equal(kiyomizu.real_2d.route_continuity, "NOT_ESTABLISHED");
    assert.equal(result.files.length, 8);
    for (const filename of ["a31b_kiyomizu_gion_display.geojson", "a31b_arashiyama_display.geojson", "facility_points_kiyomizu_gion.geojson", "facility_points_arashiyama.geojson"]) {
      assert.deepEqual(
        readFileSync(join(output, "..", "official", filename)),
        readFileSync(new URL(`../../inputs/staging/KYOTO-OFFICIAL-PARITY-V1/${filename}`, import.meta.url)),
        `${filename} must remain an exact-byte-copy delivery`,
      );
    }

    for (const city of catalog.cities) {
      const deliveredPath = join(output, city.real_2d.data_path.replace("./data/maps/", ""));
      assert.equal(
        city.real_2d.artifact_sha256,
        sha256(readFileSync(new URL(`../../${SOURCE_EDGE_PATHS[city.city_id]}`, import.meta.url))),
        `${city.city_id} artifact_sha256 must bind the source bytes`,
      );
      assert.equal(
        city.real_2d.copied_sha256,
        sha256(readFileSync(deliveredPath)),
        `${city.city_id} copied_sha256 must bind the delivered bytes`,
      );
      assert.deepEqual(
        readFileSync(deliveredPath),
        readFileSync(new URL(`../../${SOURCE_EDGE_PATHS[city.city_id]}`, import.meta.url)),
        `${city.city_id} uses the versioned exact-byte-copy transform`,
      );
      assert.ok(city.real_2d.lineage.includes("transform:EXACT_BYTE_COPY@1.0.0"));
    }

    const copied = readJson(join(output, kiyomizu.real_2d.data_path.replace("./data/maps/", "")));
    assert.equal(copied.features.length, 19);
    for (const feature of copied.features) {
      assert.equal(feature.properties.data_class, "REAL");
      assert.equal(feature.properties.geometry_status, "SOURCE_TRACEABLE_REAL");
      assert.equal(feature.properties.topology_status, "CANDIDATE");
      assert.equal(feature.properties.accessibility_state, "UNKNOWN");
      assert.equal(feature.properties.operation_status, "UNKNOWN");
    }
  } finally {
    rmSync(output, { recursive: true, force: true });
  }
});

test("[software_correctness] artifact generation is byte deterministic", () => {
  const first = mkdtempSync(join(tmpdir(), "ablepath-map-first-"));
  const second = mkdtempSync(join(tmpdir(), "ablepath-map-second-"));
  try {
    const firstResult = buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: first });
    const secondResult = buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: second });
    for (let index = 0; index < firstResult.files.length; index += 1) {
      assert.deepEqual(readFileSync(firstResult.files[index]), readFileSync(secondResult.files[index]));
      assert.equal(sha256(readFileSync(firstResult.files[index])), sha256(readFileSync(secondResult.files[index])));
    }
  } finally {
    rmSync(first, { recursive: true, force: true });
    rmSync(second, { recursive: true, force: true });
  }
});

test("[source_conformance] delivered-byte validation rejects one-byte mutation", () => {
  const output = mkdtempSync(join(tmpdir(), "ablepath-map-mutated-"));
  try {
    buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output });
    const catalog = readJson(join(output, "map-layers.json"));
    const deliveredPath = join(output, catalog.cities[0].real_2d.data_path.replace("./data/maps/", ""));
    writeFileSync(deliveredPath, Buffer.concat([readFileSync(deliveredPath), Buffer.from(" ")]));
    assert.throws(
      () => assertDeliveredMapArtifacts(catalog, output),
      /delivered byte SHA-256 mismatch/,
    );
  } finally {
    rmSync(output, { recursive: true, force: true });
  }
});

test("[source_conformance] tracked three-city catalog binds current destination bytes", () => {
  const output = new URL("../../viewer/public/data/maps/", import.meta.url);
  assertDeliveredMapArtifacts(readJson(new URL("map-layers.json", output)), output);
});

test("[source_conformance] GeoJSON bounds preserve longitude-latitude axis order", () => {
  const geojson = readJson(new URL("../../cities/kyoto_kiyomizu/graph/real/candidate_edges.geojson", import.meta.url));
  const bounds = computeGeoJsonBounds(geojson);
  assert.ok(bounds[0][0] > 135 && bounds[1][0] < 136, "longitude must be the first axis");
  assert.ok(bounds[0][1] > 34 && bounds[1][1] < 36, "latitude must be the second axis");
  assert.ok(bounds[0][0] < bounds[1][0]);
  assert.ok(bounds[0][1] < bounds[1][1]);
});

test("[ui_regression] real mode is explicit for every allowlisted city", () => {
  const catalog = readJson(new URL("../../viewer/public/data/maps/map-layers.json", import.meta.url));
  const validated = assertSupportedMapCatalog(catalog);
  assert.equal(selectInitialMapMode(validated, "kyoto_kiyomizu", "?layer=real"), "real");
  assert.equal(selectInitialMapMode(validated, "kyoto_kiyomizu", "?layer=synthetic"), "synthetic");
  assert.equal(selectInitialMapMode(validated, "kyoto_arashiyama", "?layer=real"), "real");
  assert.equal(selectInitialMapMode(validated, "fujisawa_enoshima", "?layer=real"), "real");
});

test("[source_conformance] every city allowlist fails closed on an artifact hash mismatch", () => {
  const source = readJson(new URL("../../viewer/public/data/maps/map-layers.json", import.meta.url));
  for (const city of source.cities) {
    const mutated = structuredClone(source);
    mutated.cities.find((entry) => entry.city_id === city.city_id).real_2d.artifact_sha256 = "0".repeat(64);
    assert.throws(() => assertSupportedMapCatalog(mutated), /copied bytes do not match|exact allowlisted artifact value/);
    assert.equal(selectInitialMapMode({ cities: [] }, city.city_id, "?layer=real"), "synthetic");
  }
});

test("[source_conformance] PLATEAU remains official metadata only and disconnected", () => {
  const catalog = assertSupportedMapCatalog(
    readJson(new URL("../../viewer/public/data/maps/map-layers.json", import.meta.url)),
  );
  const layer = catalog.cities.find((city) => city.city_id === "kyoto_kiyomizu");
  assert.equal(layer.cesium.data_class, "OFFICIAL_METADATA_ONLY");
  assert.equal(layer.cesium.lod, "LOD2");
  assert.equal(layer.cesium.connected, false);
  assert.equal(layer.cesium.requires_commercial_token, false);
  assert.match(layer.cesium.tileset_url, /^https:\/\/assets\.cms\.plateau\.reearth\.io\//);
  // The retained root metadata has no reviewed CORS, AOI, or child-tile receipt.
  // A mock response must therefore not turn this into a real PLATEAU connection.
  assert.equal(isVerifiedCesiumConnection(layer.cesium), false);
  assert.equal(isVerifiedCesiumConnection({ ...layer.cesium, connected: true }), false);
});

test("[source_conformance] catalog validation rejects truth-status promotion and lineage drift", () => {
  const source = readJson(new URL("../../viewer/public/data/maps/map-layers.json", import.meta.url));
  const mutations = [
    ["candidate topology promoted to verified", (city) => { city.real_2d.topology_status = "VERIFIED"; }],
    ["route continuity promoted to established", (city) => { city.real_2d.route_continuity = "ESTABLISHED"; }],
    ["static PLATEAU connection promoted", (city) => { city.cesium.connected = true; }],
    ["copied artifact lineage changed", (city) => { city.real_2d.copied_sha256 = "0".repeat(64); }],
    ["topology artifact lineage changed", (city) => { city.real_2d.topology_sha256 = "0".repeat(64); }],
    ["PLATEAU metadata lineage changed", (city) => { city.cesium.metadata_sha256 = "0".repeat(64); }],
    ["OSM copyright destination changed", (city) => { city.real_2d.copyright_url = "https://example.invalid/"; }],
    ["PLATEAU license destination changed", (city) => { city.cesium.license_url = "https://example.invalid/"; }],
  ];

  for (const [label, mutate] of mutations) {
    const catalog = structuredClone(source);
    const kiyomizu = catalog.cities.find((city) => city.city_id === "kyoto_kiyomizu");
    mutate(kiyomizu);
    assert.throws(() => assertSupportedMapCatalog(catalog), undefined, label);
  }
});

test("[software_correctness] delayed Cesium tile/render failures trigger one fallback and clean up listeners", () => {
  function eventFixture() {
    const listeners = new Set();
    return {
      addEventListener: (listener) => listeners.add(listener),
      removeEventListener: (listener) => listeners.delete(listener),
      raise: (...args) => [...listeners].forEach((listener) => listener(...args)),
      size: () => listeners.size,
    };
  }
  const tileFailed = eventFixture();
  const renderError = eventFixture();
  const failures = [];
  const registration = installCesiumFailureListeners({
    tileset: { tileFailed },
    scene: { renderError },
    onFailure: (message) => failures.push(message),
  });
  tileFailed.raise({ url: "child.b3dm" });
  renderError.raise(null, new Error("later render failure"));
  assert.deepEqual(failures, ["PLATEAU tile/renderの読込に失敗しました: child.b3dm"]);
  assert.equal(registration.hasFailed(), true);
  registration.remove();
  assert.equal(tileFailed.size(), 0);
  assert.equal(renderError.size(), 0);
});

test("[software_correctness] a pending 3D request times out instead of hanging", async () => {
  await assert.rejects(
    withTimeout(new Promise(() => {}), 5, "3D timeout fixture"),
    /3D timeout fixture/,
  );
});

test("[ui_regression] real layer and selected candidate edge round-trip through URL state", () => {
  const cityCatalog = readJson(new URL("../../viewer/public/data/cities.json", import.meta.url));
  const initial = selectInitialState(cityCatalog, "?city=kyoto_kiyomizu&view=2d&layer=real&map_edge=KK-OSM-W1251544286-S01");
  const state = { ...initial, mapMode: "real" };
  assert.equal(state.selectedRealEdgeId, "KK-OSM-W1251544286-S01");
  assert.equal(
    serializeState(state),
    "?city=kyoto_kiyomizu&view=2d&layer=real&map_edge=KK-OSM-W1251544286-S01",
  );
});
