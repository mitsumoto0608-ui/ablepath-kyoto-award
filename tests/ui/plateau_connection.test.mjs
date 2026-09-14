import test from "node:test";
import assert from "node:assert/strict";
import { PLATEAU_SOURCE_BINDINGS, PLATEAU_RECEIPT_SHA256, assertVerifiedPlateauSource, plateauConfigFromReceipt } from "../../viewer/src/plateauConnection.mjs";

test("[source_conformance] reviewed root and non-empty live evidence enable source capability, not unconditional session success", () => {
  const city = "kyoto_kiyomizu";
  const receipt = { city_id: city, ...PLATEAU_SOURCE_BINDINGS[city], cors_observed: true, root_hash_verified: true, child_content_decoded: true, target_aoi_live_rendered: true, post_interaction_rendered: true, visible_tile_count: 5, visible_triangle_count: 7556, candidate_path_visible: true };
  const config = plateauConfigFromReceipt(receipt, PLATEAU_RECEIPT_SHA256);
  assert.equal(assertVerifiedPlateauSource(config, city), config);
  assert.equal(config.source_status, "VERIFIED_SOURCE");
  assert.equal(config.session_status, "IDLE");
  assert.equal(config.connected, true);
  assert.equal(config.requires_commercial_token, false);
});

test("[source_conformance] boolean promotion, changed root, missing CORS and empty content cannot enable real PLATEAU", () => {
  const receipt = { city_id: "kyoto_kiyomizu", ...PLATEAU_SOURCE_BINDINGS.kyoto_kiyomizu, cors_observed: true, root_hash_verified: true, child_content_decoded: true, target_aoi_live_rendered: true, post_interaction_rendered: true, visible_tile_count: 5, visible_triangle_count: 7556, candidate_path_visible: true };
  for (const mutation of [
    { cors_observed: false }, { visible_triangle_count: 0 }, { visible_tile_count: true },
    { child_content_decoded: false }, { root_sha256: "0".repeat(64) }, { target_aoi_live_rendered: false },
  ]) assert.throws(() => plateauConfigFromReceipt({ ...receipt, ...mutation }, PLATEAU_RECEIPT_SHA256));
  assert.throws(() => plateauConfigFromReceipt(receipt, "a".repeat(64)), /receipt SHA-256/);
  assert.throws(() => assertVerifiedPlateauSource({ connected: true, data_class: "OFFICIAL_REMOTE_TILESET", connection_receipt_sha256: "a".repeat(64) }, "kyoto_kiyomizu"));
});
