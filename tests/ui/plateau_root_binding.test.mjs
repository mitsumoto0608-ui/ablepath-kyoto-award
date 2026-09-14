import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { Resource } from "../../viewer/node_modules/cesium/Source/Cesium.js";
import { loadTilesetForSession } from "../../viewer/src/plateauResource.mjs";

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
