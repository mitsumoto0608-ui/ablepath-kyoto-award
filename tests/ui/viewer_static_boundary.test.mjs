import assert from "node:assert/strict";
import { copyFileSync, existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import {
  assertStaticAnalysisArtifacts,
  buildMapArtifacts,
} from "../../viewer/scripts/build-map-artifacts.mjs";

const REPO_ROOT = new URL("../../", import.meta.url);
const CITY_IDS = ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"];

test("[ui_regression] viewer artifact code contains no graph, path, component, or M7 aggregation implementation", () => {
  const source = readFileSync(new URL("../../viewer/scripts/build-map-artifacts.mjs", import.meta.url), "utf8");
  for (const forbidden of [
    "shortestCandidateFixture",
    "function analysisFor",
    "Math.hypot",
    "pathMatrix",
    "pathFixture",
    "const components",
    "const pending = [node]",
    "ready_edge_count:",
    "computed_edge_count:",
  ]) {
    assert.equal(source.includes(forbidden), false, `${forbidden} must remain source-side only`);
  }
  assert.match(source, /assertStaticAnalysisArtifacts/);
});

test("[source_conformance] viewer build validates static analysis without changing its bytes", () => {
  const root = mkdtempSync(join(tmpdir(), "ablepath-static-viewer-"));
  const output = join(root, "maps");
  mkdirSync(output);
  const before = new Map(CITY_IDS.map((city) => [city, readFileSync(new URL(`../../viewer/public/data/analysis/${city}.json`, import.meta.url))]));
  try {
    buildMapArtifacts({ repoRoot: REPO_ROOT, outputRoot: output });
    for (const city of CITY_IDS) {
      assert.deepEqual(
        readFileSync(new URL(`../../viewer/public/data/analysis/${city}.json`, import.meta.url)),
        before.get(city),
      );
    }
    assert.equal(existsSync(join(root, "analysis")), false, "viewer build must not create analysis output");
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("[source_conformance] missing or stale static analysis fails closed", () => {
  const analysisRoot = mkdtempSync(join(tmpdir(), "ablepath-static-analysis-"));
  try {
    for (const city of CITY_IDS) {
      copyFileSync(
        new URL(`../../viewer/public/data/analysis/${city}.json`, import.meta.url),
        join(analysisRoot, `${city}.json`),
      );
    }
    assertStaticAnalysisArtifacts({ repoRoot: REPO_ROOT, analysisRoot });

    const path = join(analysisRoot, "kyoto_kiyomizu.json");
    const stale = JSON.parse(readFileSync(path, "utf8"));
    stale.input_sha256 = "0".repeat(64);
    writeFileSync(path, `${JSON.stringify(stale, null, 2)}\n`);
    assert.throws(
      () => assertStaticAnalysisArtifacts({ repoRoot: REPO_ROOT, analysisRoot }),
      /input SHA-256/,
    );

    copyFileSync(
      new URL("../../viewer/public/data/analysis/kyoto_kiyomizu.json", import.meta.url),
      path,
    );
    rmSync(join(analysisRoot, "fujisawa_enoshima.json"));
    assert.throws(
      () => assertStaticAnalysisArtifacts({ repoRoot: REPO_ROOT, analysisRoot }),
      /missing static analysis/,
    );
  } finally {
    rmSync(analysisRoot, { recursive: true, force: true });
  }
});

test("[ui_regression] source generator remains the only static-analysis generation entry point", () => {
  const generator = readFileSync(new URL("../../scripts/build_candidate_analysis.py", import.meta.url), "utf8");
  assert.match(generator, /src\.analysis\.static_candidate_analysis/);
  assert.match(generator, /generate_static_candidate_analyses/);
  assert.doesNotMatch(generator, /viewer\/scripts\/build-map-artifacts/);
});
