import test from "node:test";
import assert from "node:assert/strict";
import { readWorkspaceSelection, serializeWorkspaceSelection, selectSegmentEvidence, DEFAULT_CONDITIONS } from "../../viewer/src/workspaceSelection.mjs";

test("[ui_regression] segment and source conditions survive map/detail/3D URL round trip without computing a route", () => {
  const analysis = { selectable_node_ids: ["a", "b"], path_fixture: { start_node_id: "a", end_node_id: "b" }, path_matrix: { a__b: { edge_ids: ["e"] } } };
  const conditions = { ...DEFAULT_CONDITIONS, scenario: "flood", revision: "2025", terrainProduct: "DEM1A", sortBy: "REASON" };
  const search = serializeWorkspaceSelection("?city=kyoto_kiyomizu&view=3d&map_edge=e", ["a", "b"], conditions);
  assert.deepEqual(readWorkspaceSelection(analysis, search), { nodes: ["a", "b"], conditions });
  const feature = { properties: { edge_id: "e", from_node: "a", to_node: "b" } };
  const evidence = { terrain: { samples: [{ node_id: "a", product: "DEM1A", elevation_m: null, reason: "SOURCE_NODATA" }, { node_id: "a", product: "DEM5A", elevation_m: 4 }] }, hazard: { edge_exposures: [{ edge_id: "e", scenario_id: "flood", source_revision: "2025", relation: "UNKNOWN" }, { edge_id: "e", scenario_id: "other" }] } };
  const selected = selectSegmentEvidence(feature, evidence, conditions);
  assert.equal(selected.terrain.length, 1);
  assert.equal(selected.terrain[0].elevation_m, null);
  assert.equal(selected.terrain[0].reason, "SOURCE_NODATA");
  assert.equal(selected.hazards.length, 1);
  assert.equal(selected.hazards[0].relation, "UNKNOWN");
  assert.deepEqual(analysis.path_matrix.a__b.edge_ids, ["e"]);
});

test("[software_correctness] unregistered endpoints cannot create a route and missing evidence is not fabricated", () => {
  const analysis = { selectable_node_ids: ["a", "b"], path_fixture: { start_node_id: "a", end_node_id: "b" }, path_matrix: { a__b: {} } };
  assert.deepEqual(readWorkspaceSelection(analysis, "?from=arbitrary-address&to=b").nodes, ["a", "b"]);
  assert.deepEqual(selectSegmentEvidence(null, {}, DEFAULT_CONDITIONS), { terrain: [], hazards: [], readiness: null });
});
