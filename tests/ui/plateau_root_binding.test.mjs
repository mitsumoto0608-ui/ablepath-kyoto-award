import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { Resource } from "../../viewer/node_modules/cesium/Source/Cesium.js";
import { loadTilesetForSession, loadTerrainForSession } from "../../viewer/src/plateauResource.mjs";

// Exact reviewed service metadata, not a road-height fixture or raw DEM.
const TERRAIN_ROOT = { attribution: '<a href="https://www.mlit.go.jp/plateau/" target="_blank">PLATEAU</a> | <a href="https://mapterhorn.com/" target="_blank">Mapterhorn</a> | <a href="https://www.gsi.go.jp/" target="_blank">国土地理院</a>', bounds: [-180, -90, 180, 90], description: "", extensions: ["metadata", "octvertexnormals"], format: "quantized-mesh-1.0", maxzoom: 18, metadataAvailability: 10, minzoom: 0, name: "", projection: "EPSG:4326", scheme: "tms", tiles: ["{z}/{x}/{y}.terrain"], version: "1.11265.0" };

test("[source_conformance] terrain metadata is pinned through clones and never accepts a changed root or dead session", async () => {
  const bytes = new TextEncoder().encode(JSON.stringify(TERRAIN_ROOT));
  const fetchImpl = async () => ({ ok: true, url: "https://tile.plateauview.mlit.go.jp/terrain/layer.json", arrayBuffer: async () => bytes.buffer });
  let calls = 0;
  const createTerrain = async (resource) => {
    calls += 1;
    const layer = Resource.createIfNeeded(resource).getDerivedResource({ url: "layer.json" });
    assert.deepEqual(await Resource.createIfNeeded(layer).fetchJson(), TERRAIN_ROOT);
    return { fixture: true };
  };
  assert.deepEqual(await loadTerrainForSession({ isActive: () => true, fetchImpl, createTerrain }), { fixture: true });
  await assert.rejects(loadTerrainForSession({ isActive: () => false, fetchImpl, createTerrain }), /session/);
  await assert.rejects(loadTerrainForSession({ isActive: () => true, fetchImpl: async () => ({ ...(await fetchImpl()), arrayBuffer: async () => new TextEncoder().encode("{}").buffer }), createTerrain }), /metadata/);
  assert.equal(calls, 1);
  let active = true;
  let started;
  let finish;
  const creationStarted = new Promise((resolve) => { started = resolve; });
  const pending = loadTerrainForSession({ isActive: () => active, fetchImpl, createTerrain: () => { started(); return new Promise((resolve) => { finish = resolve; }); } });
  await creationStarted;
  active = false;
  finish({ fixture: true });
  await assert.rejects(pending, /session/);
});

// Additional provenance/lifecycle tests close the independent review's root
// re-fetch and late-disposal findings; these are not scientific calculations.
test("[source_conformance] exact hashed root survives Cesium's repeated clones and relative children use normal requests", async (t) => {
  const url = "https://example.invalid/official/tileset.json";
  const root = { asset: { version: "1.0" }, root: { content: { uri: "data/nested.json" } } };
  const bytes = new TextEncoder().encode(JSON.stringify(root));
  let rootRequests = 0;
  const childRequests = [];
  t.mock.method(Resource.prototype, "fetchJson", function () { childRequests.push(this.url); return Promise.resolve({ child: true }); });
  const result = await loadTilesetForSession({ tileset_url: url, root_bytes: bytes.length, root_sha256: createHash("sha256").update(bytes).digest("hex") }, {
    isActive: () => true,
    fetchImpl: async () => { rootRequests += 1; return { ok: true, url, arrayBuffer: async () => bytes.buffer }; },
    createTileset: async (resource) => {
      const clone = Resource.createIfNeeded(Resource.createIfNeeded(resource));
      assert.deepEqual(await clone.fetchJson(), root);
      const child = clone.getDerivedResource({ url: root.root.content.uri });
      assert.deepEqual(await Resource.createIfNeeded(child).fetchJson(), { child: true });
      return { fixture: true };
    },
  });
  assert.equal(result.fixture, true);
  assert.equal(rootRequests, 1);
  assert.deepEqual(childRequests, ["https://example.invalid/official/data/nested.json"]);
});

test("[software_correctness] changed root never starts Cesium and a late tileset is destroyed after session exit", async () => {
  let creations = 0;
  await assert.rejects(loadTilesetForSession({ tileset_url: "https://example.invalid/root.json", root_sha256: "0".repeat(64), root_bytes: 2 }, {
    isActive: () => true,
    fetchImpl: async () => ({ ok: true, url: "https://example.invalid/root.json", arrayBuffer: async () => new TextEncoder().encode("{}").buffer }),
    createTileset: async () => { creations += 1; },
  }), /changed since reviewed receipt/);
  assert.equal(creations, 0);
  let active = true;
  let destroyed = 0;
  let resolveCreation;
  const late = loadTilesetForSession({ tileset_url: "./synthetic-root.json" }, {
    isActive: () => active,
    createTileset: () => new Promise((resolve) => { resolveCreation = resolve; }),
  });
  active = false;
  resolveCreation({ isDestroyed: () => false, destroy: () => { destroyed += 1; } });
  await assert.rejects(late, /no longer active/);
  assert.equal(destroyed, 1);
});
