import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  assertSupportedCatalog,
  formatKpi,
  loadCatalog,
  selectInitialState,
  serializeState,
} from "../../viewer/src/domain.mjs";

function validCatalog() {
  return JSON.parse(readFileSync(new URL("../../viewer/public/data/cities.json", import.meta.url), "utf8"));
}

test("[software_correctness] accepts supported, reasoned viewer data", () => {
  assert.equal(assertSupportedCatalog(validCatalog()).cities[0].city_id, "kyoto_kiyomizu");
});

test("[software_correctness] rejects unsupported major schema versions", () => {
  const catalog = validCatalog();
  catalog.viewer_data_schema_version = "2.0.0";
  assert.throws(() => assertSupportedCatalog(catalog), /unsupported viewer_data_schema_version/);
});

test("[software_correctness] rejects malformed semantic versions", () => {
  for (const version of ["1", "1.0", "1evil", "v1.0.0", "01.0.0", "1.00.0", 1]) {
    const catalog = validCatalog();
    catalog.viewer_data_schema_version = version;
    assert.throws(() => assertSupportedCatalog(catalog), /invalid viewer_data_schema_version/);
  }
});

test("[software_correctness] rejects a missing or partial city pack", () => {
  const emptyCatalog = validCatalog();
  emptyCatalog.cities = [];
  assert.throws(() => assertSupportedCatalog(emptyCatalog), /contain 1-20 cities/);
  const catalog = validCatalog();
  delete catalog.cities[0].map;
  assert.throws(() => assertSupportedCatalog(catalog), /missing=map/);
});

test("[source_conformance] rejects a null KPI without an explicit reason", () => {
  const catalog = validCatalog();
  catalog.cities[0].kpis.accommodated.reason = "";
  assert.throws(() => assertSupportedCatalog(catalog), /reason must be a non-empty bounded string/);
});

test("[source_conformance] rejects a fabricated computed profile state", () => {
  const catalog = validCatalog();
  catalog.cities[0].profile_status = "PASS";
  assert.throws(() => assertSupportedCatalog(catalog), /unsupported computed profile state/);
});

test("[source_conformance] rejects an unclassified source or false facility readiness", () => {
  const sourceMutation = validCatalog();
  sourceMutation.cities[0].sources[0].data_class = "UNTRUSTED";
  assert.throws(() => assertSupportedCatalog(sourceMutation), /data_class has unsupported value/);
  const facilityMutation = validCatalog();
  facilityMutation.cities[0].facility_status = "READY";
  assert.throws(() => assertSupportedCatalog(facilityMutation), /facility_status must remain UNKNOWN/);
});

test("[source_conformance] rejects impossible dates and unsupported metadata labels", () => {
  const dateMutation = validCatalog();
  dateMutation.cities[0].sources[0].last_verified_at = "2026-02-31";
  assert.throws(() => assertSupportedCatalog(dateMutation), /ISO calendar date/);

  const metadataMutation = validCatalog();
  metadataMutation.cities[0].official_metadata_status = "VERIFIED_SAFE";
  assert.throws(() => assertSupportedCatalog(metadataMutation), /official_metadata_status has unsupported value/);
});

test("[source_conformance] rejects unverified REAL and MODEL_DERIVED self-assertions", () => {
  for (const dataClass of ["REAL", "MODEL_DERIVED"]) {
    const catalog = validCatalog();
    const city = catalog.cities[0];
    const fixture = city.sources.find((source) => source.data_class === "SYNTHETIC_DEMO");
    fixture.data_class = dataClass;
    fixture.status = "UNKNOWN";
    city.data_status = dataClass === "REAL" ? "REAL" : "MIXED";
    city.map.geometry_status = dataClass;
    city.map.edges.forEach((edge) => { edge.evidence_status = dataClass; });
    assert.throws(() => assertSupportedCatalog(catalog), /data_class has unsupported value/);
  }
});

test("[source_conformance] accepts VGI metadata without promoting it to real geometry", () => {
  const catalog = validCatalog();
  const source = catalog.cities[0].sources.find((item) => item.data_class === "OFFICIAL_METADATA_ONLY");
  source.data_class = "VGI_METADATA_ONLY";
  source.status = "UNKNOWN";
  catalog.cities[0].official_metadata_status = "UNKNOWN";
  assert.equal(assertSupportedCatalog(catalog).cities[0].sources.find((item) => item.source_id === source.source_id).data_class, "VGI_METADATA_ONLY");
});

test("[source_conformance] official metadata status requires official source provenance", () => {
  const catalog = validCatalog();
  const source = catalog.cities[0].sources.find((item) => item.data_class === "OFFICIAL_METADATA_ONLY");
  source.data_class = "UNKNOWN";
  source.status = "UNKNOWN";
  assert.throws(() => assertSupportedCatalog(catalog), /lacks official source provenance/);
});

test("[source_conformance] rejects fabricated city, edge, and KPI states", () => {
  const realWithoutProvenance = validCatalog();
  realWithoutProvenance.cities[0].data_status = "REAL";
  assert.throws(() => assertSupportedCatalog(realWithoutProvenance), /REAL status lacks REAL provenance/);

  const openEdge = validCatalog();
  openEdge.cities[0].map.edges[0].display_state = "OPEN";
  assert.throws(() => assertSupportedCatalog(openEdge), /display_state has unsupported value OPEN/);

  for (const value of ["SAFE FOR ALL", -1, Number.POSITIVE_INFINITY]) {
    const invalidKpi = validCatalog();
    invalidKpi.cities[0].kpis.physically_reachable = { value, reason: "invalid fixture" };
    assert.throws(() => assertSupportedCatalog(invalidKpi), /value must be null or a finite non-negative number/);
  }
  const fabricatedNumericKpi = validCatalog();
  fabricatedNumericKpi.cities[0].kpis.physically_reachable = { value: 100, reason: "invented" };
  assert.throws(() => assertSupportedCatalog(fabricatedNumericKpi), /must remain null while kpi_status is NOT_COMPUTED/);
});

test("[source_conformance] UNKNOWN and metadata-only evidence cannot become PASS", () => {
  const catalog = validCatalog();
  const city = catalog.cities[0];
  city.sources.forEach((source) => {
    source.data_class = "UNKNOWN";
    source.status = "UNKNOWN";
  });
  city.official_metadata_status = "UNKNOWN";
  city.data_status = "MIXED";
  city.map.edges.forEach((edge) => { edge.evidence_status = "UNKNOWN"; });
  city.map.edges[0].display_state = "PASS";
  assert.throws(() => assertSupportedCatalog(catalog), /cannot promote unknown or metadata-only evidence to PASS/);
});

test("[software_correctness] top-level, city, map, and edge schemas reject extra state fields", () => {
  for (const mutate of [
    (catalog) => { catalog.route_state = "PASS"; },
    (catalog) => { catalog.cities[0].profile_state = "PASS"; },
    (catalog) => { catalog.cities[0].map.route_state = "PASS"; },
    (catalog) => { catalog.cities[0].map.edges[0].accessibility_state = "PASS"; },
  ]) {
    const catalog = validCatalog();
    mutate(catalog);
    assert.throws(() => assertSupportedCatalog(catalog), /keys must be exact/);
  }
});

test("[source_conformance] map REAL and MODEL_DERIVED self-assertions are unavailable in v1", () => {
  for (const [cityStatus, geometryStatus] of [["UNKNOWN", "REAL"], ["MIXED", "MODEL_DERIVED"]]) {
    const catalog = validCatalog();
    catalog.cities[0].data_status = cityStatus;
    catalog.cities[0].map.geometry_status = geometryStatus;
    assert.throws(() => assertSupportedCatalog(catalog), /requires unavailable build-verified provenance/);
  }
});

test("[source_conformance] official closure cannot coexist with PASS", () => {
  const catalog = validCatalog();
  const edge = catalog.cities[0].map.edges[0];
  edge.hazard_data_status = "KNOWN";
  edge.official_closure = true;
  edge.display_state = "PASS";
  assert.throws(() => assertSupportedCatalog(catalog), /official closure contradicts PASS/);
});

test("[software_correctness] rejects duplicate IDs and broken source references", () => {
  const duplicateCity = validCatalog();
  duplicateCity.cities[1].city_id = duplicateCity.cities[0].city_id;
  assert.throws(() => assertSupportedCatalog(duplicateCity), /duplicate city_id/);

  const duplicateEdge = validCatalog();
  duplicateEdge.cities[0].map.edges[1].edge_id = duplicateEdge.cities[0].map.edges[0].edge_id;
  assert.throws(() => assertSupportedCatalog(duplicateEdge), /duplicate edge_id/);

  const danglingSource = validCatalog();
  danglingSource.cities[0].map.edges[0].source_ids = ["DOES-NOT-EXIST"];
  assert.throws(() => assertSupportedCatalog(danglingSource), /references unknown source/);

  const missingSourceIds = validCatalog();
  missingSourceIds.cities[0].map.edges[0].source_ids = [];
  assert.throws(() => assertSupportedCatalog(missingSourceIds), /source_ids must be non-empty/);
});

test("[software_correctness] rejects malformed, non-finite, and out-of-bounds SVG coordinates", () => {
  for (const points of [["not-a-point", [1, 2]], [[0, 0], [Number.NaN, 1]], [[0, 0], [1001, 1]], [[1, 1], [1, 1]]]) {
    const catalog = validCatalog();
    catalog.cities[0].map.edges[0].points = points;
    assert.throws(() => assertSupportedCatalog(catalog), /coordinate|SVG bounds|zero-length geometry/);
  }
});

test("[source_conformance] requires every edge evidence class to match a referenced source", () => {
  const catalog = validCatalog();
  catalog.cities[0].map.edges[0].evidence_status = "MODEL_DERIVED";
  assert.throws(() => assertSupportedCatalog(catalog), /unsupported value MODEL_DERIVED/);
});

test("[source_conformance] requires the exact five reasoned KPI cards", () => {
  const catalog = validCatalog();
  delete catalog.cities[0].kpis.unknown_affected_upper_bound;
  assert.throws(() => assertSupportedCatalog(catalog), /exact five V4 KPI/);
});

test("[software_correctness] reports invalid JSON without substituting data", async () => {
  const fetchImpl = async () => ({ ok: true, text: async () => "{invalid" });
  await assert.rejects(loadCatalog(fetchImpl, "/data.json"), /invalid JSON/);
});

test("[software_correctness] reports HTTP and CORS-like fetch failures", async () => {
  await assert.rejects(loadCatalog(async () => ({ ok: false, status: 404 }), "/missing.json"), /HTTP 404/);
  await assert.rejects(loadCatalog(async () => { throw new TypeError("Failed to fetch"); }, "/cors.json"), /Failed to fetch/);
});

test("[software_correctness] enforces the fetch timeout", async () => {
  const fetchImpl = (_url, { signal }) => new Promise((_resolve, reject) => {
    signal.addEventListener("abort", () => {
      const error = new Error("aborted");
      error.name = "AbortError";
      reject(error);
    });
  });
  await assert.rejects(loadCatalog(fetchImpl, "/slow.json", 5), /timed out after 5 ms/);
});

test("[software_correctness] rejects oversized payloads before parsing", async () => {
  const fetchImpl = async () => ({ ok: true, text: async () => `{"padding":"${"x".repeat(2_000_001)}"}` });
  await assert.rejects(loadCatalog(fetchImpl, "/large.json"), /exceeds 2000000 byte limit/);
});

test("[ui_regression] URL persists only controls backed by an available output", () => {
  const catalog = validCatalog();
  const city = catalog.cities[1];
  const edge = city.map.edges[1];
  const state = selectInitialState(catalog, `?city=${city.city_id}&scenario=unsafe&evidence=optimistic&phase=after&view=3d&edge=${edge.edge_id}`);
  assert.equal(state.scenario.scenario_id, city.scenarios[0].scenario_id);
  assert.equal(state.evidenceMode, "strict");
  assert.equal(state.phase, "before");
  assert.equal(state.selectedEdge.edge_id, edge.edge_id);
  assert.equal(serializeState(state), `?city=${city.city_id}&view=3d&edge=${edge.edge_id}`);
});

test("[ui_regression] unknown query values fail closed to documented defaults", () => {
  const state = selectInitialState(validCatalog(), "?city=missing&scenario=missing&evidence=unsafe&phase=future&view=vr&edge=missing");
  assert.equal(state.city.city_id, "kyoto_kiyomizu");
  assert.equal(state.scenario.scenario_id, "EQ_LOW");
  assert.equal(state.evidenceMode, "strict");
  assert.equal(state.phase, "before");
  assert.equal(state.view, "2d");
  assert.equal(state.selectedEdge.edge_id, "KYS-DEMO-E001");
});

test("[ui_regression] null KPI is rendered as an em dash with its reason", () => {
  assert.deepEqual(formatKpi({ value: null, reason: "demand unavailable" }), {
    value: "—",
    reason: "demand unavailable",
    status: "NOT_COMPUTED",
  });
});
