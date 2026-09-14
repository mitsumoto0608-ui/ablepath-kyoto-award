import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { filterHazardDisplayFeatures, isHazardDisplayFeature } from "../../viewer/src/workspaceSelection.mjs";

test("[source_conformance] both Kyoto A31b AOIs retain exact source polygons under scenario and revision selection", () => {
  for (const [city, aoi] of [["kyoto_kiyomizu", "kiyomizu_gion"], ["kyoto_arashiyama", "arashiyama"]]) {
    const original = JSON.parse(readFileSync(new URL(`../../viewer/public/data/official/a31b_${aoi}_display.geojson`, import.meta.url)));
    const before = JSON.stringify(original);
    const analysis = JSON.parse(readFileSync(new URL(`../../viewer/public/data/analysis/${city}.json`, import.meta.url)));
    // Kiyomizu's retained AOI has zero A31b-10 polygons; A31b-20 has 329.
    // Use a genuinely non-empty layer, not an invented A31b-10 expectation.
    const layer = aoi === "kiyomizu_gion" ? "A31b-20" : "A31b-10";
    const selected = filterHazardDisplayFeatures(original.features, { scenario: `A31B_FLOOD_2025_${aoi}_${layer}`, revision: "2025" }, analysis.official_evidence.hazard.source_catalog);
    assert.ok(selected.length > 0, `${city} must not silently hide its selected flood polygons`);
    assert.deepEqual(selected, original.features.filter((f) => f.properties._ablepath_layer_id === layer));
    assert.equal(filterHazardDisplayFeatures(original.features, { scenario: "ALL", revision: "2025" }, analysis.official_evidence.hazard.source_catalog).length, original.features.length);
    assert.equal(JSON.stringify(original), before);
  }
});

test("[source_conformance] unrelated and unknown display identities cannot inherit a source scenario", () => {
  const features = [{ properties: { _ablepath_layer_id: "A31b-10", _ablepath_aoi_id: "not-a-reviewed-aoi" } }];
  assert.deepEqual(filterHazardDisplayFeatures(features, { scenario: "A31B_FLOOD_2025_arashiyama_A31b-10", revision: "2025" }, {}), []);
  assert.deepEqual(filterHazardDisplayFeatures([{ properties: { source_id: "s", scenario_id: "scenario" } }], { scenario: "scenario", revision: "wrong" }, { s: { source_revision: "2025" } }), []);
});

test("[source_conformance] all retained city hazard features use their hash-bound display manifest without rewriting source properties", () => {
  for (const city of ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"]) {
    const analysis = JSON.parse(readFileSync(new URL(`../../viewer/public/data/analysis/${city}.json`, import.meta.url)));
    for (const config of analysis.official_evidence.hazard.display_layers) {
      const original = JSON.parse(readFileSync(new URL(`../../viewer/public/${config.data_path}`, import.meta.url)));
      const before = JSON.stringify(original);
      assert.equal(original.features.length, config.feature_count);
      assert.ok(original.features.every((feature) => isHazardDisplayFeature(feature, config)));
      assert.equal(JSON.stringify(original), before);
    }
  }
});

test("[source_conformance] absent display authority, contradictory flags and inferred hazard states fail closed", () => {
  const feature = { geometry: { type: "Polygon" }, properties: { source_id: "fixture", scenario_id: "fixture-scenario", source_feature_id: "fixture:1" } };
  assert.equal(isHazardDisplayFeature(feature, { display_only: true }), true);
  assert.equal(isHazardDisplayFeature(feature, {}), false);
  for (const properties of [{ ...feature.properties, _ablepath_display_only: false }, {}, ...["official_closure", "damage_state", "debris_present", "setback_m"].map((field) => ({ ...feature.properties, [field]: null }))]) {
    assert.equal(isHazardDisplayFeature({ ...feature, properties }, { display_only: true }), false);
  }
  assert.equal(isHazardDisplayFeature({ ...feature, geometry: { type: "Point" } }, { display_only: true }), false);
});
