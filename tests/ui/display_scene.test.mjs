import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { DISPLAY_TERRAIN, heightMethod, registeredPoints, selectDisplayEdges, cameraCoordinates } from "../../viewer/src/displayScene.mjs";

test("[ui_regression] display-only terrain, registered coordinates and path selection preserve evidence", () => {
  const feature = { properties: { edge_id: "e1", from_node: "A", to_node: "B", bridge: "UNKNOWN", tunnel: "UNKNOWN", width_m: null }, geometry: { coordinates: [[135, 35], [135.01, 35.01]] } };
  const geometry = { features: [feature] };
  const before = JSON.stringify(geometry);
  assert.equal(DISPLAY_TERRAIN.url, "https://tile.plateauview.mlit.go.jp/terrain");
  assert.equal(DISPLAY_TERRAIN.evidence_input, false);
  assert.equal(heightMethod(feature), "TERRAIN_PROJECTION_NOT_ROAD_HEIGHT");
  assert.deepEqual(registeredPoints(geometry, ["A", "B"]), [{ id: "A", label: "地点A", coordinates: [135, 35] }, { id: "B", label: "地点B", coordinates: [135.01, 35.01] }]);
  assert.deepEqual(registeredPoints(geometry, ["B", "A"], ["A", "B"]).map((p) => p.label), ["地点B", "地点A"]);
  assert.deepEqual(selectDisplayEdges(geometry, ["e1"], null, false), [feature]);
  assert.deepEqual(selectDisplayEdges(geometry, [], null, false), []);
  assert.equal(JSON.stringify(geometry), before);
});

test("[source_conformance] scene projects onto terrain only and roof-clamping mutation is rejected", () => {
  const source = readFileSync(new URL("../../viewer/src/CesiumScene.jsx", import.meta.url), "utf8");
  const boundary = (text) => {
    // Two ground geometries: source hazard polygons and existing candidate lines.
    assert.equal((text.match(/classificationType: ClassificationType\.TERRAIN/g) ?? []).length, 2);
    assert.match(text, /clampToGround: true/);
    assert.match(text, /heightReference: HeightReference\.CLAMP_TO_TERRAIN/);
    assert.doesNotMatch(text, /ClassificationType\.(BOTH|CESIUM_3D_TILE)|CLAMP_TO_GROUND|depthFailMaterial|modelMatrix\s*=/);
  };
  boundary(source);
  assert.throws(() => boundary(source.replaceAll("ClassificationType.TERRAIN", "ClassificationType.BOTH")));
});

test("[source_conformance] bridge/tunnel/layer evidence cannot become a surveyed surface or invented endpoint", () => {
  for (const properties of [{ bridge: true }, { bridge: "yes" }, { tunnel: true }, { source_tags: { tunnel: "culvert" } }, { layer: -1 }, { level: "1" }]) {
    assert.equal(heightMethod({ properties }), "SCHEMATIC_HEIGHT_UNKNOWN_USE_2D");
  }
  const g = { features: [{ properties: { edge_id: "e", from_node: "A", to_node: "B" }, geometry: { coordinates: [[135, 35], [136, 36]] } }] };
  assert.deepEqual(registeredPoints(g, ["MISSING", "B"]), [{ id: "B", label: "地点B", coordinates: [136, 36] }]);
  assert.equal(registeredPoints(g, ["B", "B"]).length, 1);
  assert.deepEqual(cameraCoordinates(g, "path", [], null, ["A", "B"]), [[135, 35], [136, 36]]);
  assert.deepEqual(selectDisplayEdges(g, [], null, false), []);
  assert.equal(heightMethod({ properties: { bridge: "UNKNOWN", layer: null, tunnel: "UNKNOWN" } }), "TERRAIN_PROJECTION_NOT_ROAD_HEIGHT");
});
