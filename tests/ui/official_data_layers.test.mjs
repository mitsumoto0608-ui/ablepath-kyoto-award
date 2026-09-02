import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { createHash } from "node:crypto";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { buildMapArtifacts } from "../../viewer/scripts/build-map-artifacts.mjs";

const REPO_ROOT = new URL("../../", import.meta.url);
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));

test("[source_conformance] official analysis separates display connections from scientific and operational states", () => {
  const output = mkdtempSync(join(tmpdir(), "ablepath-official-analysis-"));
  try {
    buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output });
    const kiyomizu = readJson(join(output, "..", "analysis", "kyoto_kiyomizu.json"));
    const fujisawa = readJson(join(output, "..", "analysis", "fujisawa_enoshima.json"));
    const p3 = readJson(new URL("../../reports/M7_ALL_EDGE_EVIDENCE_READINESS.json", import.meta.url));
    assert.equal(kiyomizu.official_evidence.terrain.status, "AOI_COVERAGE_VALIDATED_ELEVATION_NOT_SAMPLED");
    assert.equal(kiyomizu.official_evidence.terrain.connected, false);
    assert.equal(kiyomizu.official_evidence.terrain.evidence_ui_connected, true);
    assert.equal(kiyomizu.official_evidence.terrain.elevation_sampled, false);
    assert.equal(kiyomizu.official_evidence.terrain.products.length, 6);
    assert.equal(kiyomizu.official_evidence.hazard.layers.length, 15);
    assert.equal(kiyomizu.official_evidence.hazard.layers.filter((row) => row.layer === "flood" && row.connected).length, 3);
    assert.ok(kiyomizu.official_evidence.hazard.layers.filter((row) => row.layer !== "flood").every((row) => row.connected === false && row.status === "NOT_CONNECTED" && row.reason));
    assert.equal(kiyomizu.official_evidence.hazard.closure_derived, false);
    assert.equal(kiyomizu.official_evidence.hazard.damage_or_debris_inferred, false);
    assert.equal(kiyomizu.official_evidence.facility.marker_policy, "SOURCE_COORDINATES_ONLY_NO_GEOCODING");
    assert.ok(kiyomizu.official_evidence.facility.records.length > 0);
    assert.ok(kiyomizu.official_evidence.facility.records.every((record) => record.coordinate_method === "SOURCE_PROVIDED_LONGITUDE_LATITUDE" && record.silent_geocoding === false));
    assert.equal(kiyomizu.official_evidence.plateau.fallback, "EXISTING_DETERMINISTIC_2D");
    assert.equal(fujisawa.official_evidence.facility.status, "READY_FOR_TABLE_ONLY");
    assert.equal(fujisawa.official_evidence.terrain.products.length, 3);
    assert.equal(fujisawa.official_evidence.hazard.scenarios.length, 18);
    assert.ok(fujisawa.official_evidence.hazard.scenarios.every((row) => row.connected === false && row.status === "NOT_CONNECTED" && row.aoi_scope === "enoshima_katase"));
    assert.equal(fujisawa.official_evidence.facility.records.length, 57);
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
  try {
    assert.throws(() => buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output, m7EvidenceOverride: { all_edge_count: 611 } }), /P3 M7 receipt binding/);
    assert.throws(() => buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output, m7EvidenceOverride: { edges: [{ city_id: "kyoto_kiyomizu", status: "NOT_COMPUTED", m7_result: 1, m7_computed: false, m7_evidence_ready: false }] } }), /P3 M7 receipt binding/);
  } finally {
    rmSync(output, { recursive: true, force: true });
  }
});

test("[software_correctness] unsafe official evidence promotion is rejected before analysis delivery", () => {
  const output = mkdtempSync(join(tmpdir(), "ablepath-official-analysis-unsafe-"));
  try {
    assert.throws(
      () => buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output, officialEvidenceOverride: { safe_route_claim: true } }),
      /unsafe official evidence promotion/,
    );
  } finally {
    rmSync(output, { recursive: true, force: true });
  }
});
