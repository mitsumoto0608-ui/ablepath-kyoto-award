import assert from "node:assert/strict";
import { copyFileSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { buildMapArtifacts } from "../../viewer/scripts/build-map-artifacts.mjs";

const REPO_ROOT = new URL("../../", import.meta.url);
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));
const CITY_IDS = ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"];

function analysisFixture() {
  const root = mkdtempSync(join(tmpdir(), "ablepath-analysis-fixture-"));
  copyFileSync(
    new URL("../../viewer/public/data/analysis/manifest.json", import.meta.url),
    join(root, "manifest.json"),
  );
  for (const city of CITY_IDS) copyFileSync(
    new URL(`../../viewer/public/data/analysis/${city}.json`, import.meta.url),
    join(root, `${city}.json`),
  );
  return root;
}

function refreshFixtureHash(root, city) {
  const manifestPath = join(root, "manifest.json");
  const manifest = readJson(manifestPath);
  const canonical = readFileSync(join(root, `${city}.json`), "utf8").replaceAll("\r\n", "\n");
  manifest.artifacts[`${city}.json`] = createHash("sha256").update(canonical).digest("hex");
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
}

test("[source_conformance] official analysis separates display connections from scientific and operational states", () => {
  const output = mkdtempSync(join(tmpdir(), "ablepath-official-analysis-"));
  try {
    buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output });
    const kiyomizu = readJson(new URL("../../viewer/public/data/analysis/kyoto_kiyomizu.json", import.meta.url));
    const fujisawa = readJson(new URL("../../viewer/public/data/analysis/fujisawa_enoshima.json", import.meta.url));
    const p3 = readJson(new URL("../../reports/M7_ALL_EDGE_EVIDENCE_READINESS.json", import.meta.url));
    assert.equal(kiyomizu.official_evidence.terrain.status, "NATIVE_CELL_SAMPLES_CONNECTED");
    assert.equal(kiyomizu.official_evidence.terrain.connected, true);
    assert.equal(kiyomizu.official_evidence.terrain.evidence_ui_connected, true);
    assert.equal(kiyomizu.official_evidence.terrain.elevation_sampled, true);
    assert.equal(kiyomizu.official_evidence.terrain.products.length, 2);
    assert.equal(kiyomizu.official_evidence.terrain.samples.length, 360);
    assert.ok(kiyomizu.official_evidence.terrain.samples.every((row) => row.step_inferred === false && row.cross_slope_inferred === false));
    assert.equal(kiyomizu.official_evidence.hazard.layers.length, 15);
    assert.equal(kiyomizu.official_evidence.hazard.layers.filter((row) => ["flood", "landslide"].includes(row.layer) && row.connected).length, 6);
    assert.ok(kiyomizu.official_evidence.hazard.layers.filter((row) => !["flood", "landslide"].includes(row.layer)).every((row) => row.connected === false && row.status === "NOT_CONNECTED" && row.reason));
    assert.equal(kiyomizu.official_evidence.hazard.status, "SOURCE_SIDE_EDGE_OVERLAP_CONNECTED");
    assert.ok(kiyomizu.official_evidence.hazard.edge_exposures.some((row) => row.relation === "INTERSECTS"));
    assert.ok(kiyomizu.official_evidence.hazard.edge_exposures.every((row) => row.official_closure === null && row.damage_state === null && row.debris_present === null));
    assert.equal(kiyomizu.official_evidence.hazard.closure_derived, false);
    assert.equal(kiyomizu.official_evidence.hazard.damage_or_debris_inferred, false);
    assert.equal(kiyomizu.official_evidence.facility.marker_policy, "SOURCE_COORDINATES_ONLY_NO_GEOCODING");
    assert.ok(kiyomizu.official_evidence.facility.records.length > 0);
    assert.ok(kiyomizu.official_evidence.facility.records.every((record) => record.coordinate_method === "SOURCE_PROVIDED_LONGITUDE_LATITUDE" && record.silent_geocoding === false));
    assert.equal(kiyomizu.official_evidence.plateau.fallback, "EXISTING_DETERMINISTIC_2D");
    assert.equal(fujisawa.official_evidence.facility.status, "NOT_CONNECTED_PUBLIC_GIT_LICENSE_REVIEW_REQUIRED");
    assert.equal(fujisawa.official_evidence.terrain.products.length, 2);
    assert.equal(fujisawa.official_evidence.terrain.samples.length, 92);
    assert.equal(fujisawa.official_evidence.hazard.scenarios.length, 18);
    assert.equal(fujisawa.official_evidence.hazard.scenarios.filter((row) => row.connected).length, 10);
    assert.equal(fujisawa.official_evidence.hazard.scenarios.filter((row) => !row.connected).length, 8);
    assert.equal(fujisawa.official_evidence.hazard.connected_scenarios.length, 11);
    assert.equal(fujisawa.official_evidence.facility.records.length, 0);
    assert.ok(fujisawa.official_evidence.facility.records.every((record) => record.geometry_status === "ADDRESS_ONLY" && record.latitude === null && record.longitude === null));
    assert.equal(kiyomizu.official_evidence.m7.all_edge_count, 612);
    assert.equal(kiyomizu.official_evidence.m7.computed_count, 0);
    assert.equal(kiyomizu.official_evidence.m7.kyoto_deep_pilot_edges.length, 5);
    assert.ok(kiyomizu.official_evidence.m7.kyoto_deep_pilot_edges.every((edge) => edge.m7_result === null && edge.field_resolution));
    assert.deepEqual(kiyomizu.m7.readiness, p3.edges.filter((edge) => edge.city_id === "kyoto_kiyomizu"));
    assert.equal("edge_receipts" in kiyomizu.official_evidence.m7, false);
    assert.equal("readiness" in kiyomizu.result.m7, false);
    assert.equal(kiyomizu.official_evidence.safe_route_claim, false);
  } finally {
    rmSync(output, { recursive: true, force: true });
  }
});

test("[source_conformance] report-byte source hashes are exact LF Git-blob hashes", () => {
  const expected = {
    "reports/OFFICIAL_LOCAL_ARTIFACT_PROMOTION_V2.json": "1e0bcd2a0687c863421576f60a256ce52072d2ed7e7d4abe19b83a8befc26505",
    "reports/PLATEAU_BUILDING_EVIDENCE_V1.json": "1648afedc3dcd486cafdc74105e514707c99c621df263bc10c2c1d1c4e3a0551",
    "reports/M7_REAL_EDGE_STATUS.json": "8d57dd0e2c0c355ea4615ff8c7702f9d11f48cbe533bd37027aadd31a994dfc8",
  };
  for (const [relative, digest] of Object.entries(expected)) {
    const bytes = readFileSync(new URL(`../../${relative}`, import.meta.url));
    assert.equal(createHash("sha256").update(bytes).digest("hex"), digest, relative);
    assert.equal(bytes.includes(Buffer.from("\r\n")), false, `${relative} must be LF`);
  }
});

test("[software_correctness] altered P3 aggregate count or result fails before analysis delivery", () => {
  const output = mkdtempSync(join(tmpdir(), "ablepath-official-analysis-p3-mutated-"));
  const analysisRoot = analysisFixture();
  try {
    const path = join(analysisRoot, "kyoto_kiyomizu.json");
    const mutated = readJson(path);
    mutated.result.m7.ready_edge_count = 1;
    writeFileSync(path, `${JSON.stringify(mutated, null, 2)}\n`);
    refreshFixtureHash(analysisRoot, "kyoto_kiyomizu");
    assert.throws(() => buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output, analysisRoot }), /M7 summary/);
  } finally {
    rmSync(output, { recursive: true, force: true });
    rmSync(analysisRoot, { recursive: true, force: true });
  }
});

test("[software_correctness] unsafe official evidence promotion is rejected before analysis delivery", () => {
  const output = mkdtempSync(join(tmpdir(), "ablepath-official-analysis-unsafe-"));
  const analysisRoot = analysisFixture();
  try {
    const path = join(analysisRoot, "kyoto_kiyomizu.json");
    const mutated = readJson(path);
    mutated.official_evidence.safe_route_claim = true;
    writeFileSync(path, `${JSON.stringify(mutated, null, 2)}\n`);
    refreshFixtureHash(analysisRoot, "kyoto_kiyomizu");
    assert.throws(
      () => buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output, analysisRoot }),
      /forbidden safety or validation promotion/,
    );
  } finally {
    rmSync(output, { recursive: true, force: true });
    rmSync(analysisRoot, { recursive: true, force: true });
  }
});
