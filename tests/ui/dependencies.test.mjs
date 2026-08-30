import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const VIEWER_ROOT = new URL("../../viewer/", import.meta.url);

function readJson(relative) {
  return JSON.parse(readFileSync(new URL(relative, VIEWER_ROOT), "utf8"));
}

function sourceFiles(directory) {
  const files = [];
  for (const entry of readdirSync(directory)) {
    const path = join(directory, entry);
    if (statSync(path).isDirectory()) files.push(...sourceFiles(path));
    else if (/\.(?:js|jsx|mjs|html)$/.test(entry)) files.push(path);
  }
  return files;
}

test("[source_conformance] map runtimes are exact-pinned with reviewed licenses", () => {
  const packageJson = readJson("package.json");
  const lock = readJson("package-lock.json");
  assert.equal(packageJson.dependencies["maplibre-gl"], "6.6.0");
  assert.equal(packageJson.dependencies.cesium, "1.144.0");
  assert.equal(packageJson.scripts["smoke:plateau"], "node scripts/smoke-plateau-url.mjs");
  assert.equal(lock.packages[""].dependencies["maplibre-gl"], "6.6.0");
  assert.equal(lock.packages[""].dependencies.cesium, "1.144.0");
  assert.equal(lock.packages["node_modules/maplibre-gl"].version, "6.6.0");
  assert.equal(lock.packages["node_modules/maplibre-gl"].license, "BSD-3-Clause");
  assert.equal(lock.packages["node_modules/cesium"].version, "1.144.0");
  assert.equal(lock.packages["node_modules/cesium"].license, "Apache-2.0");
  for (const [path, entry] of Object.entries(lock.packages)) {
    if (path !== "" && !entry.link) assert.match(entry.integrity ?? "", /^sha512-/, `${path} must keep npm integrity`);
  }
});

test("[source_conformance] viewer has no CDN runtime imports", () => {
  const files = [
    ...sourceFiles(fileURLToPath(new URL("src/", VIEWER_ROOT))),
    ...sourceFiles(fileURLToPath(new URL("scripts/", VIEWER_ROOT))),
    fileURLToPath(new URL("index.html", VIEWER_ROOT)),
    fileURLToPath(new URL("vite.config.js", VIEWER_ROOT)),
  ];
  const text = files.map((path) => readFileSync(path, "utf8")).join("\n");
  assert.doesNotMatch(text, /(?:cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com)/i);
  assert.doesNotMatch(text, /<script[^>]+https?:\/\//i);
});

test("[source_conformance] dependency notice records exact runtime versions", () => {
  const notice = readFileSync(new URL("DEPENDENCY_LICENSES.md", VIEWER_ROOT), "utf8");
  assert.match(notice, /maplibre-gl` \| 6\.6\.0 \| BSD-3-Clause/);
  assert.match(notice, /cesium` \| 1\.144\.0 \| Apache-2\.0/);
  assert.match(notice, /without a mandatory commercial token/i);
});
