import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import { assertDeliveredOfficialArtifacts, buildMapArtifacts } from "../../viewer/scripts/build-map-artifacts.mjs";

// TK-01 / TK-05 (CLAUDE_TAKEOVER_AUDIT): committed maps/official bytes must equal a fresh deterministic
// viewer rebuild. Static analysis parity is enforced by the source generator and viewer boundary tests.
// TK-04: official display_layer.copied_sha256 must be the SHA-256 of the DELIVERED file bytes.

const REPO_ROOT = fileURLToPath(new URL("../../", import.meta.url));
const DELIVERED_ROOT = join(REPO_ROOT, "viewer", "public", "data");
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));

function listFiles(root, prefix = "") {
  return readdirSync(join(root, prefix)).flatMap((name) => {
    const relative = prefix ? `${prefix}/${name}` : name;
    return statSync(join(root, relative)).isDirectory() ? listFiles(root, relative) : [relative];
  }).sort();
}

test("[source_conformance] committed viewer maps/official bytes equal a fresh deterministic rebuild", () => {
  const scratch = mkdtempSync(join(tmpdir(), "ablepath-delivered-rebuild-"));
  try {
    const rebuiltRoot = join(scratch, "data");
    buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: join(rebuiltRoot, "maps") });
    for (const directory of ["maps", "official"]) {
      const rebuilt = listFiles(join(rebuiltRoot, directory));
      const committed = listFiles(join(DELIVERED_ROOT, directory));
      assert.deepEqual(committed, rebuilt, `${directory}: committed file set must equal the rebuilt file set (no orphan or missing generated files)`);
      for (const relative of rebuilt) {
        assert.ok(committed.includes(relative), `${directory}/${relative} is rebuilt but not committed`);
        const rebuiltBytes = readFileSync(join(rebuiltRoot, directory, relative));
        const committedBytes = readFileSync(join(DELIVERED_ROOT, directory, relative));
        assert.equal(sha256(committedBytes), sha256(rebuiltBytes), `${directory}/${relative}: committed bytes are stale; run \`npm run build:data\` in viewer/`);
        assert.equal(rebuiltBytes.includes(Buffer.from("\r\n")), false, `${directory}/${relative} must be LF`);
      }
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("[source_conformance] analysis source_hashes bind to the current repository report bytes", () => {
  const bindings = {
    promotion_sha256: "reports/OFFICIAL_LOCAL_ARTIFACT_PROMOTION_V2.json",
    plateau_sha256: "reports/PLATEAU_BUILDING_EVIDENCE_V2.json",
    m7_sha256: "reports/M7_REAL_EDGE_STATUS.json",
    kyoto_status_sha256: "reports/KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json",
    kyoto_parity_sha256: "reports/KYOTO_PARITY_STATUS.json",
    kyoto_m7_pilot_sha256: "reports/KYOTO_M7_DEEP_PILOT_STATUS.json",
  };
  const perCity = {
    kyoto_kiyomizu: { terrain_inventory_sha256: "cities/kyoto_kiyomizu/terrain/official/dem_product_inventory.csv" },
    kyoto_arashiyama: { terrain_inventory_sha256: "cities/kyoto_arashiyama/terrain/official/dem_product_inventory.csv" },
    fujisawa_enoshima: {
      terrain_inventory_sha256: "cities/fujisawa_enoshima/terrain/official/dem_product_inventory.csv",
      facility_receipt_sha256: "cities/fujisawa_enoshima/facilities/official/facility_source_receipt.json",
      facility_table_sha256: "cities/fujisawa_enoshima/facilities/official/FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json",
      earthquake_inventory_sha256: "cities/fujisawa_enoshima/hazards/official/earthquake_scenario_inventory.csv",
      liquefaction_inventory_sha256: "cities/fujisawa_enoshima/hazards/official/liquefaction_scenario_inventory.csv",
    },
  };
  for (const [cityId, extra] of Object.entries(perCity)) {
    const analysis = readJson(join(DELIVERED_ROOT, "analysis", `${cityId}.json`));
    const hashes = analysis.official_evidence.source_hashes;
    for (const [key, relative] of Object.entries({ ...bindings, ...extra })) {
      if (!(key in hashes)) continue;
      assert.equal(hashes[key], sha256(Buffer.from(readFileSync(join(REPO_ROOT, relative), "utf8").replaceAll("\r\n", "\n"), "utf8")), `${cityId}.${key} must equal canonical text sha256(${relative})`);
    }
    assert.equal(analysis.official_evidence.terrain.receipt_sha256, hashes.terrain_inventory_sha256, `${cityId} terrain receipt hash`);
  }
});

test("[source_conformance] official display_layer copied_sha256 equals delivered bytes and source bytes", () => {
  for (const cityId of ["kyoto_kiyomizu", "kyoto_arashiyama"]) {
    const analysis = readJson(join(DELIVERED_ROOT, "analysis", `${cityId}.json`));
    for (const layer of [analysis.official_evidence.facility.display_layer, ...analysis.official_evidence.hazard.display_layers]) {
      assert.ok(layer, `${cityId} display_layer present`);
      const delivered = readFileSync(join(DELIVERED_ROOT, "official", layer.data_path.replace("./data/official/", "")));
      assert.equal(layer.copied_sha256, sha256(delivered), `${cityId} ${layer.data_path} copied_sha256 must be delivered-byte hash`);
      assert.equal(layer.artifact_sha256, layer.copied_sha256, `${cityId} ${layer.data_path} exact byte copy`);
    }
  }
  const fujisawa = readJson(join(DELIVERED_ROOT, "analysis", "fujisawa_enoshima.json"));
  assert.equal(fujisawa.official_evidence.facility.display_layer ?? null, null, "Fujisawa ADDRESS_ONLY table must not ship a display layer");
});

test("[software_correctness] official delivered-byte mismatch fails closed before analysis delivery", () => {
  const scratch = mkdtempSync(join(tmpdir(), "ablepath-official-delivered-mutated-"));
  try {
    const officialDirectory = join(scratch, "official");
    buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: join(scratch, "maps") });
    const analysis = readJson(join(DELIVERED_ROOT, "analysis", "kyoto_arashiyama.json"));
    const built = [{ city_id: "kyoto_arashiyama", official_evidence: analysis.official_evidence }];
    assert.doesNotThrow(() => assertDeliveredOfficialArtifacts(built, officialDirectory));
    const target = join(officialDirectory, "a31b_arashiyama_display.geojson");
    const lfBytes = readFileSync(target, "utf8");
    writeFileSync(target, lfBytes.replaceAll("\n", "\r\n"));
    assert.throws(() => assertDeliveredOfficialArtifacts(built, officialDirectory), /official delivered byte SHA-256 mismatch/);
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("[software_correctness] official display paths cannot escape their static directory", () => {
  const analysis = readJson(join(DELIVERED_ROOT, "analysis", "kyoto_arashiyama.json"));
  const mutated = structuredClone(analysis.official_evidence);
  mutated.hazard.display_layers[0].data_path = "./data/official/../analysis/kyoto_arashiyama.json";
  assert.throws(() => assertDeliveredOfficialArtifacts([{ city_id: "kyoto_arashiyama", official_evidence: mutated }], join(DELIVERED_ROOT, "official")), /not confined/);
});
