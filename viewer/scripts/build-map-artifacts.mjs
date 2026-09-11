import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { assertSupportedMapCatalog, computeGeoJsonBounds } from "../src/mapDomain.mjs";
import { validateDeliveryAnalysis } from "../src/analysisDomain.mjs";
import { ADMIN_CHECKLIST_GUARD_TEXTS, ADMIN_CHECKLIST_SCHEMA, EXPOSURE_NOTE, compareCodePoints, sortChecklistItems, toChecklistCsv } from "../src/adminChecklistCsv.mjs";

const CITY_INPUTS = [
  { id: "kyoto_kiyomizu", nodes: "cities/kyoto_kiyomizu/graph/real/candidate_nodes.geojson", edges: "cities/kyoto_kiyomizu/graph/real/candidate_edges.geojson", corridor: "cities/kyoto_kiyomizu/geography/real/corridor.osm.geojson", topology: "cities/kyoto_kiyomizu/graph/real/topology_qa.json", manifest: "cities/kyoto_kiyomizu/realdata/artifact_manifest.v2.json", source: "openstreetmap_kiyomizu_named_corridor_20260830", snapshot: "2026-08-30T00:00:00Z" },
  { id: "kyoto_arashiyama", nodes: "cities/kyoto_arashiyama/graph/walk_nodes.real.geojson", edges: "cities/kyoto_arashiyama/graph/walk_edges.real.geojson", corridor: "cities/kyoto_arashiyama/geography/corridor.real.geojson", topology: "cities/kyoto_arashiyama/graph/topology_qa.real.json", manifest: "cities/kyoto_arashiyama/sources/realdata_manifest.json", source: "openstreetmap-overpass-arashiyama-20260829", snapshot: "2026-08-29T00:00:00Z" },
  { id: "fujisawa_enoshima", nodes: "cities/fujisawa_enoshima/graph/candidate_walk_nodes.real.geojson", edges: "cities/fujisawa_enoshima/graph/candidate_walk_edges.real.geojson", corridor: "cities/fujisawa_enoshima/geography/corridor.real.geojson", topology: "cities/fujisawa_enoshima/graph/candidate_topology_qa.real.json", manifest: "cities/fujisawa_enoshima/realdata/artifact_manifest.v2.json", source: "OSM_CANDIDATE_SOURCE", snapshot: "2026-08-30T00:00:00Z" },
];
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const json = (path) => JSON.parse(readFileSync(path, "utf8"));
const hash = (path) => sha256(readFileSync(path));
const canonicalTextBytes = (bytes) => Buffer.from(bytes.toString("utf8").replaceAll("\r\n", "\n"), "utf8");
const canonicalTextHash = (path) => sha256(canonicalTextBytes(readFileSync(path)));

function reportHashPaths(root, cityId) {
  const paths = {
    promotion_sha256: join(root, "reports", "OFFICIAL_LOCAL_ARTIFACT_PROMOTION_V2.json"),
    plateau_sha256: join(root, "reports", "PLATEAU_BUILDING_EVIDENCE_V2.json"),
    m7_sha256: join(root, "reports", "M7_REAL_EDGE_STATUS.json"),
    f1_f6_binding_sha256: join(root, "reports", "F1_F6_DECISION_BINDING.json"),
    delivery_source_binding_sha256: join(root, "inputs", "staging", "DELIVERY-SPRINT-V1", "source_bindings.json"),
  };
  const terrain = join(root, "cities", cityId, "terrain", "official", "dem_product_inventory.csv");
  if (existsSync(terrain)) paths.terrain_inventory_sha256 = terrain;
  if (cityId.startsWith("kyoto_")) {
    const group = cityId === "kyoto_kiyomizu" ? "kiyomizu_gion" : "arashiyama";
    Object.assign(paths, {
      kyoto_status_sha256: join(root, "reports", "KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json"),
      kyoto_parity_sha256: join(root, "reports", "KYOTO_PARITY_STATUS.json"),
      kyoto_m7_pilot_sha256: join(root, "reports", "KYOTO_M7_DEEP_PILOT_STATUS.json"),
      kyoto_facility_sha256: join(root, "inputs", "staging", "KYOTO-OFFICIAL-PARITY-V1", "facility_records.json"),
      kyoto_facility_category_status_sha256: join(root, "inputs", "staging", "KYOTO-OFFICIAL-PARITY-V1", "facility_category_status.json"),
      kyoto_flood_display_sha256: join(root, "inputs", "staging", "KYOTO-OFFICIAL-PARITY-V1", `a31b_${group}_display.geojson`),
      plateau_inventory_sha256: join(root, "inputs", "staging", "PLATEAU-BUILDING-EVIDENCE-V2", "PLATEAU_BUILDING_AOI_INVENTORY.csv"),
      delivery_landslide_sha256: join(root, "inputs", "staging", "DELIVERY-SPRINT-V1", cityId, "landslide_aoi_selection.geojson"),
    });
  }
  if (cityId === "fujisawa_enoshima") Object.assign(paths, {
    facility_receipt_sha256: join(root, "cities", cityId, "facilities", "official", "facility_source_receipt.json"),
    earthquake_inventory_sha256: join(root, "cities", cityId, "hazards", "official", "earthquake_scenario_inventory.csv"),
    liquefaction_inventory_sha256: join(root, "cities", cityId, "hazards", "official", "liquefaction_scenario_inventory.csv"),
    delivery_tsunami_sha256: join(root, "inputs", "staging", "DELIVERY-SPRINT-V1", "fujisawa_enoshima", "tsunami_a40_aoi_selection.geojson"),
  });
  return paths;
}

export function assertStaticAnalysisArtifacts({ repoRoot, analysisRoot }) {
  const root = repoRoot instanceof URL ? fileURLToPath(repoRoot) : resolve(repoRoot);
  const analysis = analysisRoot instanceof URL ? fileURLToPath(analysisRoot) : resolve(analysisRoot ?? join(root, "viewer", "public", "data", "analysis"));
  const m7 = json(join(root, "reports", "M7_REAL_EDGE_STATUS.json"));
  const manifestPath = join(analysis, "manifest.json");
  if (!existsSync(manifestPath)) throw new Error("missing static analysis manifest");
  const manifest = json(manifestPath);
  if (manifest.schema_version !== "1.0.0" || manifest.source_analysis_authority !== "src/analysis" || manifest.generator !== "scripts/build_candidate_analysis.py") throw new Error("invalid static analysis manifest authority");
  for (const input of CITY_INPUTS) {
    const path = join(analysis, `${input.id}.json`);
    if (!existsSync(path)) throw new Error(`${input.id} missing static analysis artifact`);
    if (manifest.artifacts?.[`${input.id}.json`] !== canonicalTextHash(path)) throw new Error(`${input.id} static analysis artifact bytes are stale`);
    const artifact = json(path);
    validateDeliveryAnalysis(artifact, input.id);
    const nodeBytes = canonicalTextBytes(readFileSync(join(root, input.nodes)));
    const edgeBytes = canonicalTextBytes(readFileSync(join(root, input.edges)));
    const inputSha = sha256(Buffer.concat([nodeBytes, Buffer.from([0]), edgeBytes]));
    if (artifact.city_id !== input.id || artifact.input_sha256 !== inputSha) throw new Error(`${input.id} static analysis input SHA-256 is stale`);
    if (artifact.provenance?.input_hashes?.node_sha256 !== sha256(nodeBytes) || artifact.provenance?.input_hashes?.edge_sha256 !== sha256(edgeBytes)) throw new Error(`${input.id} static analysis provenance hash is stale`);
    if (JSON.stringify(artifact.source_artifact_ids) !== JSON.stringify([input.nodes, input.edges])) throw new Error(`${input.id} static analysis source artifact binding is stale`);
    const revisions = [...new Set([...JSON.parse(nodeBytes).features, ...JSON.parse(edgeBytes).features].map((feature) => feature.properties?.revision_id).filter(Boolean))].sort(compareCodePoints);
    if (JSON.stringify(artifact.source_revision_ids) !== JSON.stringify(revisions)) throw new Error(`${input.id} static analysis source revision binding is stale`);
    for (const [key, sourcePath] of Object.entries(reportHashPaths(root, input.id))) if (artifact.official_evidence?.source_hashes?.[key] !== canonicalTextHash(sourcePath)) throw new Error(`${input.id} static analysis report SHA-256 is stale: ${key}`);
    const claims = [artifact.safety_claim, artifact.accessibility_claim, artifact.admin_validated, artifact.official_evidence?.safe_route_claim, artifact.official_evidence?.accessibility_claim, artifact.official_evidence?.admin_validated];
    if (claims.some((value) => value !== false)) throw new Error(`${input.id} static analysis contains a forbidden safety or validation promotion`);
    if (artifact.result?.m7?.ready_edge_count !== m7.evidence_ready_count || artifact.result?.m7?.computed_edge_count !== m7.computed_count || artifact.m7?.ready_edge_count !== artifact.result?.m7?.ready_edge_count || artifact.m7?.computed_edge_count !== artifact.result?.m7?.computed_edge_count) throw new Error(`${input.id} static analysis M7 summary is stale`);
    if (artifact.official_evidence?.m7?.edge_receipts_source_sha256 !== canonicalTextHash(join(root, "reports", "M7_ALL_EDGE_EVIDENCE_READINESS.json"))) throw new Error(`${input.id} static analysis M7 readiness source is stale`);
    if (!Array.isArray(artifact.m7?.readiness) || artifact.m7.readiness.length !== artifact.official_evidence?.m7?.city_edge_count || artifact.m7.readiness.some((row) => row.city_id !== input.id || row.status !== "NOT_COMPUTED" || row.m7_result !== null || row.m7_computed !== false || row.m7_evidence_ready !== false)) throw new Error(`${input.id} static analysis M7 readiness is incomplete or promoted`);
    if (input.id.startsWith("kyoto_")) {
      const group = input.id === "kyoto_kiyomizu" ? "kiyomizu_gion" : "arashiyama";
      const pointHash = canonicalTextHash(join(root, "inputs", "staging", "KYOTO-OFFICIAL-PARITY-V1", `facility_points_${group}.geojson`));
      if (artifact.official_evidence?.facility?.display_layer?.artifact_sha256 !== pointHash || artifact.official_evidence?.facility?.display_layer?.copied_sha256 !== pointHash) throw new Error(`${input.id} static facility display binding is stale`);
    }
  }
  return true;
}

function artifact(root, input) {
  const paths = Object.fromEntries(Object.entries(input).filter(([, value]) => typeof value === "string" && value.includes("/")).map(([key, value]) => [key, join(root, value)]));
  for (const path of Object.values(paths)) if (!existsSync(path)) throw new Error(`${input.id} configured artifact is missing: ${path}`);
  const edgeBytes = readFileSync(paths.edges); const edgeSha = sha256(edgeBytes); const edgeData = JSON.parse(edgeBytes);
  for (const feature of edgeData.features ?? []) {
    const p = feature?.properties ?? {};
    if (feature?.geometry?.type !== "LineString" || p.geometry_status !== "SOURCE_TRACEABLE_REAL" || p.topology_status !== "CANDIDATE") throw new Error(`${input.id} edge violates REAL/CANDIDATE contract`);
  }
  const manifest = json(paths.manifest); const topologySha = hash(paths.topology); const manifestSha = hash(paths.manifest);
  const dataPath = `./data/maps/${input.id}.candidate_edges.geojson`;
  const nodeBytes = readFileSync(paths.nodes); const nodeData = JSON.parse(nodeBytes); const sourceArtifactIds = [input.nodes, input.edges]; const sourceRevisionIds = [...new Set([...(nodeData.features ?? []), ...edgeData.features].map((feature) => feature.properties?.revision_id).filter(Boolean))].sort(compareCodePoints);
  const canonicalNodeBytes = canonicalTextBytes(nodeBytes); const canonicalEdgeBytes = canonicalTextBytes(edgeBytes);
  return {
    city_id: input.id,
    real_2d: { data_path: dataPath, artifact_sha256: edgeSha, copied_sha256: null, corridor_sha256: hash(paths.corridor), source_sha256: input.id === "kyoto_kiyomizu" ? "3d21ce674776c5c3e37c507c09a9458e062d2d31f5718b3e702313838ef7d2ec" : input.id === "kyoto_arashiyama" ? "1cde93d68bebf633989e825cbd5ac1e772cee81508043f44beb311250a1e8013" : "c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04", query_sha256: input.id === "kyoto_kiyomizu" ? "f32964329548d7d715c79cf05da6a28a7ac8230781acc4852f9174ba9f4dfb7b" : input.id === "kyoto_arashiyama" ? "b5c52b3ea7542261159b5764956aa9662673c0422b3509dc59e4866f00c14603" : "c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04", topology_sha256: topologySha, manifest_sha256: manifestSha, source_id: input.source, source_class: "VGI", data_class: "REAL", geometry_status: "SOURCE_TRACEABLE_REAL", topology_status: "CANDIDATE_REVIEW_REQUIRED", route_continuity: "NOT_ESTABLISHED", snapshot_at: input.snapshot, feature_count: edgeData.features.length, bounds: computeGeoJsonBounds(edgeData), license: "Open Data Commons Open Database License (ODbL) 1.0", license_url: "https://opendatacommons.org/licenses/odbl/1-0/", copyright_url: "https://www.openstreetmap.org/copyright", attribution: "© OpenStreetMap contributors / Data available under ODbL 1.0", lineage: [`artifact:${edgeSha}`, "transform:EXACT_BYTE_COPY@1.0.0", `corridor:${hash(paths.corridor)}`, `topology:${topologySha}`, `manifest:${manifestSha}`, `manifest_schema:${manifest.schema_version ?? "unknown"}`] },
    cesium: input.id === "kyoto_kiyomizu" ? { available: true, data_class: "OFFICIAL_METADATA_ONLY", source_id: "plateau_26100_bldg_maxlod2_latest_20260830", source_class: "OFFICIAL", accessed_at: "2026-08-30", valid_as_of: null, valid_as_of_reason: "Latest endpoint is dynamic; retained ETag response must be rechecked", lod: "LOD2", tileset_url: "https://assets.cms.plateau.reearth.io/assets/25/dd4c50-5342-4a0b-ac51-05ffb138b8b5/26100_kyoto-shi_city_2025_citygml_1_op_bldg_3dtiles_26105_higashiyama-ku_lod2/tileset.json", license: "Public Data License 1.0 (PDL1.0), CC BY 4.0 compatible", license_url: "https://www.mlit.go.jp/plateau/site-policy/", attribution: "出典：国土交通省 3D都市モデル（Project PLATEAU）京都市2025 / PDL1.0", connected: false, requires_commercial_token: false, metadata_sha256: "2a1e4c71370f58f0f40dc8b6eb9ae120b7f694b6caca1260a8a0efbbfeda78d3", retained_response_sha256: "ce58a92bb9da595d9251cd72b7b77af6da9a3748628a0e8370ffc6fbc6312242", query_sha256: "eb9400f69b5ee88b802e972f426b4ff624ab759fe372776f67ecd83978221e40" } : null,
    edgeBytes, edgeData, source_artifact_ids: sourceArtifactIds, source_revision_ids: sourceRevisionIds, input_sha256: sha256(Buffer.concat([canonicalNodeBytes, Buffer.from([0]), canonicalEdgeBytes])), input_hashes: { node_sha256: sha256(canonicalNodeBytes), edge_sha256: sha256(canonicalEdgeBytes) }, snapshot_at: input.snapshot, source_id: input.source,
  };
}

export function assertDeliveredMapArtifacts(catalog, outputRoot) {
  const output = outputRoot instanceof URL ? fileURLToPath(outputRoot) : resolve(outputRoot);
  for (const city of catalog.cities) {
    const deliveredPath = join(output, city.real_2d.data_path.replace("./data/maps/", ""));
    const actual = hash(deliveredPath);
    if (actual !== city.real_2d.copied_sha256) throw new Error(`${city.city_id} delivered byte SHA-256 mismatch: expected ${city.real_2d.copied_sha256}, got ${actual}`);
  }
  return catalog;
}

export function assertDeliveredOfficialArtifacts(analyses, officialDirectory) {
  const officialRoot = resolve(officialDirectory);
  for (const analysis of analyses) {
    for (const layer of [analysis.official_evidence?.facility?.display_layer, ...(analysis.official_evidence?.hazard?.display_layers ?? [])]) {
      if (!layer) continue;
      if (typeof layer.data_path !== "string" || !/^\.\/data\/official\/[A-Za-z0-9._-]+\.geojson$/.test(layer.data_path)) throw new Error(`${analysis.city_id} official data path is not confined`);
      const deliveredPath = resolve(officialRoot, basename(layer.data_path));
      if (dirname(deliveredPath) !== officialRoot || !existsSync(deliveredPath)) throw new Error(`${analysis.city_id} official data path is missing or escaped`);
      const actual = hash(deliveredPath);
      if (actual !== layer.artifact_sha256 || actual !== layer.copied_sha256) throw new Error(`${analysis.city_id} official delivered byte SHA-256 mismatch`);
    }
  }
  return analyses;
}

// ---------------------------------------------------------------------------
// T-A: admin-check checklist generation.
//
// Pure mechanical transform of existing receipts into per-attribute checklist
// rows for a human administrator. It creates no new facts: every `status`,
// `unknown_reason` and `verification_target` string is copied from a receipt.
// No passability, no four-state verdict, no threshold, no geocoding.
// ---------------------------------------------------------------------------

const ADMIN_CITY_IDS = ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"];
const EDGE_ATTRIBUTES = ["clear_width_m", "height_m", "setback_m", "damage_state", "debris_present", "official_closure", "hazard_data_status", "side_coverage"];
const KYOTO_FACILITY_ATTRIBUTES = ["facility.coordinate", "facility.operation_status", "facility.entrance_status", "facility.accessibility_status", "facility.safety_status"];
const FUJISAWA_FACILITY_ATTRIBUTES = ["facility.geometry", "facility.accessible_entrance", "facility.wheelchair_accessible", "facility.step_free", "facility.opening_status", "facility.disaster_availability"];
// D1: the only status conversion table. Tests import it instead of restating it.
export const ADMIN_NOT_CONNECTED_WORDS = Object.freeze(["NOT_ENUMERATED", "NO_CANDIDATE_IN_PACKAGE_BUFFER", "MISSING"]);
// D6: attribute -> verification method. CONFIRMED rows override this with NOT_APPLICABLE.
export const ADMIN_VERIFICATION_METHOD_BY_ATTRIBUTE = Object.freeze({
  clear_width_m: "FIELD_MEASUREMENT", setback_m: "FIELD_MEASUREMENT",
  official_closure: "OFFICIAL_QUERY", hazard_data_status: "OFFICIAL_QUERY",
  damage_state: "DOCUMENT_REVIEW", debris_present: "DOCUMENT_REVIEW", height_m: "DOCUMENT_REVIEW", side_coverage: "DOCUMENT_REVIEW",
});
const NO_TARGET = "NO_TARGET_IN_RECEIPTS";
const ADMIN_RECEIPT_PATHS = Object.freeze({
  R1: "reports/M7_ALL_EDGE_EVIDENCE_READINESS_V2.json",
  R2: "reports/M7_PILOT_EXPOSURE_ONLY_JOIN_V1.json",
  R3: "inputs/staging/M7-CLOSURE-STATUS-RECEIPTS-V1/closure_and_hazard_status_receipts.json",
  R4_records: "inputs/staging/KYOTO-OFFICIAL-PARITY-V1/facility_records.json",
  R4_categories: "inputs/staging/KYOTO-OFFICIAL-PARITY-V1/facility_category_status.json",
  R5_receipt: "cities/fujisawa_enoshima/facilities/official/facility_source_receipt.json",
  R5_table: "cities/fujisawa_enoshima/facilities/official/FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json",
  R6: "reports/M7_PILOT_FIELD_MEASUREMENT_PLAN.csv",
  R7: "reports/PHASE4_DATA_ACQUISITION_MATRIX.csv",
  R8: "reports/KYOTO_TARGET_AREA_WIDTH_SOURCE_SEARCH.json",
  R9: "reports/KYOTO_M7_DEEP_PILOT_STATUS.json",
});

/** The subarea value a receipt uses for the Kiyomizu/Gion connector. */
export const ADMIN_CONNECTOR_SUBAREA_ID = "kiyomizu_gion_connector";

/**
 * D8: the ordering rule. This is a machine ordering rule, not a ranking of
 * importance. Rules are applied in order and the first match wins.
 * Rule 2 (CONNECTOR_SCOPED) fires whenever a receipt assigns the object to the
 * connector subarea; no current receipt does, so its row count is counted from
 * the data rather than assumed.
 */
export function adminPriorityRule({ deepPilot = false, subareaId = null, facilityCoordinateConfirmed = false } = {}) {
  if (deepPilot === true) return { priority_rank: 1, priority_rule: "PILOT_EDGE" };
  if (subareaId === ADMIN_CONNECTOR_SUBAREA_ID) return { priority_rank: 2, priority_rule: "CONNECTOR_SCOPED" };
  if (facilityCoordinateConfirmed === true) return { priority_rank: 2, priority_rule: "FACILITY_WITH_SOURCE_COORDINATES" };
  return { priority_rank: 3, priority_rule: "DEFAULT" };
}

/**
 * R7 (PHASE4_DATA_ACQUISITION_MATRIX) has no contact column: it lists the
 * outstanding acquisition work per city/subarea/category. The label is therefore
 * a limitation note copied verbatim from the receipt, not the name of a contact.
 * Rows are selected deterministically (sorted by subarea_id, then by note) and
 * every distinct note is kept, so the result never depends on row order.
 */
export function adminMatrixLabel(rows) {
  const notes = [...new Set(rows.map((row) => row.notes).filter((note) => typeof note === "string" && note !== ""))].sort(compareCodePoints);
  return notes.length === 0 ? NO_TARGET : notes.join(" / ");
}

function parseCsv(text) {
  const rows = []; let row = []; let field = ""; let quoted = false;
  const source = text.replaceAll("\r\n", "\n");
  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    if (quoted) {
      if (character !== '"') { field += character; continue; }
      if (source[index + 1] === '"') { field += '"'; index += 1; continue; }
      quoted = false; continue;
    }
    if (character === '"') { quoted = true; continue; }
    if (character === ",") { row.push(field); field = ""; continue; }
    if (character === "\n") { row.push(field); rows.push(row); row = []; field = ""; continue; }
    field += character;
  }
  if (field !== "" || row.length) { row.push(field); rows.push(row); }
  const [header, ...body] = rows;
  return body.filter((entry) => entry.some((value) => value !== "")).map((entry) => Object.fromEntries(header.map((name, position) => [name, entry[position] ?? ""])));
}

function emptyHumanFields() { return { assignee: null, due: null, result: null, note: null }; }
function target(label, receiptPath, datasetIds, note) { return { label, receipt_path: receiptPath, dataset_ids: datasetIds, note }; }

function exposureFlagsFor(edgeId, exposureByEdge) {
  const records = exposureByEdge.get(edgeId) ?? [];
  const counts = {};
  for (const record of records) {
    const key = record.a31b_flood_overlap ?? "NOT_JOINED";
    counts[key] = (counts[key] ?? 0) + 1;
  }
  const distinct = (field) => [...new Set(records.map((record) => record[field]).filter((value) => typeof value === "string"))].sort(compareCodePoints).join("|") || "NOT_JOINED";
  return {
    records: records.length,
    a31b_overlap_counts: Object.fromEntries(Object.keys(counts).sort(compareCodePoints).map((key) => [key, counts[key]])),
    landslide: distinct("landslide_status"),
    earthquake: distinct("earthquake_scenario_status"),
    // R2 carries no liquefaction or tsunami field; no number is invented for them.
    liquefaction: "NOT_CONNECTED",
    tsunami: "NOT_CONNECTED",
    note: EXPOSURE_NOTE,
  };
}

function buildCityChecklist(root, cityId, sources, includeInternalUseOnly) {
  const { r1, r2, r3, r4Records, r4Categories, r5Receipt, r5Table, r6, r7, r8, r9 } = sources;
  const items = [];
  const exposureByEdge = new Map();
  for (const record of r2.records ?? []) {
    if (!exposureByEdge.has(record.edge_id)) exposureByEdge.set(record.edge_id, []);
    exposureByEdge.get(record.edge_id).push(record);
  }
  const closureByEdge = new Map((r3.edges ?? []).map((edge) => [edge.edge_id, edge]));
  const pilotPlanByEdge = new Map(r6.map((row) => [row.edge_id, row]));
  const deepPilotByEdge = new Map((r9.edges ?? []).map((edge) => [edge.edge_id, edge]));
  const widthCandidateIds = (r8.candidates ?? []).filter((candidate) => candidate.classification !== "EXCLUDED_PROHIBITED").map((candidate) => candidate.id);
  const matrixRows = r7.filter((row) => row.city_id === cityId && row.completeness === "HUMAN_ACTION_REQUIRED");

  // D1 / D2 / D6 / D7 / D8 / D9 — edge rows.
  for (const edge of r1.edges ?? []) {
    if (edge.city_id !== cityId) continue;
    const contract = edge.contract_v2 ?? {};
    for (const attribute of EDGE_ATTRIBUTES) {
      const word = contract[attribute];
      if (typeof word !== "string") throw new Error(`${cityId} ${edge.edge_id}.${attribute} has no contract_v2 status word`);
      const status = ADMIN_NOT_CONNECTED_WORDS.includes(word) ? "NOT_CONNECTED" : "UNKNOWN";
      const method = ADMIN_VERIFICATION_METHOD_BY_ATTRIBUTE[attribute];
      const plan = pilotPlanByEdge.get(edge.edge_id);
      const closure = closureByEdge.get(edge.edge_id);
      let verificationTarget = null;
      if (method === "FIELD_MEASUREMENT" && plan) {
        verificationTarget = target(plan.location_description, ADMIN_RECEIPT_PATHS.R6, [], `${plan.measurement_stations} / ${plan.instrument}`);
      } else if (method === "OFFICIAL_QUERY" && closure) {
        const checks = closure.automated_source_checks ?? [];
        const human = checks.find((check) => check.result === "NOT_EXECUTED_REQUIRES_HUMAN_QUERY");
        const internal = checks.find((check) => check.check_type === "REPO_INTERNAL_OFFICIAL_ARTIFACT");
        const label = human?.source ?? internal?.source ?? NO_TARGET;
        const note = attribute === "official_closure" ? closure.official_closure_receipt?.note ?? null : closure.hazard_data_status_receipt?.basis ?? null;
        verificationTarget = target(label, ADMIN_RECEIPT_PATHS.R3, [], note);
      } else if (attribute === "clear_width_m" && cityId.startsWith("kyoto_")) {
        const label = deepPilotByEdge.get(edge.edge_id)?.field_resolution?.clear_width_m?.next_acquisition_method ?? NO_TARGET;
        verificationTarget = target(label, ADMIN_RECEIPT_PATHS.R8, widthCandidateIds, null);
      }
      const resolved = verificationTarget !== null && verificationTarget.label !== NO_TARGET;
      if (!resolved) verificationTarget = target(NO_TARGET, ADMIN_RECEIPT_PATHS.R1, [], null);
      // No receipt assigns an edge to a subarea, so CONNECTOR_SCOPED cannot fire here today.
      const priority = adminPriorityRule({ deepPilot: edge.deep_pilot === true, subareaId: "SUBAREA_NOT_ASSIGNED_IN_RECEIPTS" });
      items.push({
        item_id: `${cityId}:edge:${edge.edge_id}:${attribute}`,
        city_id: cityId,
        // No receipt assigns a subarea to an edge; geometry is never used to guess one.
        subarea_id: "SUBAREA_NOT_ASSIGNED_IN_RECEIPTS",
        object_type: "edge", object_id: edge.edge_id, attribute, status,
        source_id: null, source_revision: null, source_sha256: null,
        unknown_reason: word,
        verification_method: method,
        verification_target: verificationTarget,
        ...priority,
        exposure_flags: exposureFlagsFor(edge.edge_id, exposureByEdge),
        human_fields: emptyHumanFields(),
        export_ready: resolved,
        internal_use_only: false,
      });
    }
  }

  // D3 — Kyoto facility rows.
  if (cityId.startsWith("kyoto_")) {
    const group = cityId === "kyoto_kiyomizu" ? "kiyomizu_gion" : "arashiyama";
    const facilitySha = canonicalTextHash(join(root, ADMIN_RECEIPT_PATHS.R4_records));
    const facilityMatrix = matrixRows.filter((row) => row.category === "accessibility facilities").sort((left, right) => compareCodePoints(left.subarea_id, right.subarea_id) || compareCodePoints(left.notes, right.notes));
    const facilityLabel = adminMatrixLabel(facilityMatrix);
    const facilityDatasetIds = [...new Set(facilityMatrix.flatMap((row) => row.dataset_ids.split(";").filter(Boolean)))].sort(compareCodePoints);
    for (const record of r4Records.records ?? []) {
      if (record.aoi_group !== group) continue;
      const coordinateConfirmed = record.coordinate_method === "SOURCE_PROVIDED_LONGITUDE_LATITUDE" && record.silent_geocoding === false;
      for (const attribute of KYOTO_FACILITY_ATTRIBUTES) {
        const confirmed = attribute === "facility.coordinate" && coordinateConfirmed;
        const field = attribute.slice("facility.".length);
        const word = confirmed ? null : attribute === "facility.coordinate" ? String(record.coordinate_method ?? "UNKNOWN") : String(record[field] ?? "UNKNOWN");
        items.push({
          item_id: `${cityId}:facility:${record.facility_record_id}:${attribute}`,
          city_id: cityId, subarea_id: record.aoi_group,
          object_type: "facility", object_id: record.facility_record_id, attribute,
          status: confirmed ? "CONFIRMED" : "UNKNOWN",
          source_id: confirmed ? record.source_id : null,
          source_revision: confirmed ? record.source_version_or_valid_as_of : null,
          source_sha256: confirmed ? facilitySha : null,
          unknown_reason: confirmed ? null : word,
          verification_method: confirmed ? "NOT_APPLICABLE" : "OFFICIAL_QUERY",
          verification_target: confirmed
            ? target(NO_TARGET, ADMIN_RECEIPT_PATHS.R4_records, [], record.limitations ?? null)
            : target(facilityLabel, ADMIN_RECEIPT_PATHS.R7, facilityDatasetIds, record.limitations ?? null),
          ...adminPriorityRule({ subareaId: record.aoi_group, facilityCoordinateConfirmed: coordinateConfirmed }),
          exposure_flags: null,
          human_fields: emptyHumanFields(),
          export_ready: confirmed || facilityLabel !== NO_TARGET,
          internal_use_only: false,
        });
      }
    }
    // D5 — plaza rows for categories the receipt marks map_connected=false.
    const plazaDatasetIds = [...new Set(matrixRows.flatMap((row) => row.dataset_ids.split(";").filter(Boolean)))].sort(compareCodePoints);
    for (const [category, entry] of Object.entries(r4Categories.categories ?? {}).sort(([left], [right]) => compareCodePoints(left, right))) {
      if (entry.map_connected !== false) continue;
      const objectId = `${cityId}:${category}`;
      items.push({
        item_id: `${cityId}:plaza:${objectId}:plaza.category_row_connection`,
        city_id: cityId, subarea_id: group,
        object_type: "plaza", object_id: objectId, attribute: "plaza.category_row_connection",
        status: "NOT_CONNECTED",
        source_id: null, source_revision: null, source_sha256: null,
        unknown_reason: entry.status,
        verification_method: "OFFICIAL_QUERY",
        verification_target: target(entry.next_acquisition_method ?? NO_TARGET, ADMIN_RECEIPT_PATHS.R4_categories, plazaDatasetIds, entry.reason ?? null),
        ...adminPriorityRule({ subareaId: group }),
        exposure_flags: null,
        human_fields: emptyHumanFields(),
        export_ready: (entry.next_acquisition_method ?? NO_TARGET) !== NO_TARGET,
        internal_use_only: false,
      });
    }
  }

  // D4 — Fujisawa facility rows. Every row is internal_use_only: the dataset is
  // LICENSE_REVIEW_REQUIRED and must not reach the public build.
  let fujisawaFacilityStatus = null;
  if (cityId === "fujisawa_enoshima") {
    if (r5Table === null) {
      // Deviation recorded in docs: the row-bearing table is not present at the
      // public Git tip (facility_source_receipt.public_git_current_tip_status).
      // No row is fabricated from the receipt's counts.
      fujisawaFacilityStatus = r5Receipt.public_git_current_tip_status;
    } else {
      fujisawaFacilityStatus = "ROW_SOURCE_PRESENT";
      const matrix = matrixRows.filter((row) => row.category === "accessibility facilities").sort((left, right) => compareCodePoints(left.subarea_id, right.subarea_id) || compareCodePoints(left.notes, right.notes));
      const matrixLabel = adminMatrixLabel(matrix);
      const datasetIds = [...new Set(matrix.flatMap((row) => row.dataset_ids.split(";").filter(Boolean)))].sort(compareCodePoints);
      const rows = Array.isArray(r5Table) ? r5Table : r5Table.records ?? r5Table.rows ?? [];
      for (const record of rows) {
        const recordId = String(record.facility_record_id ?? record.id ?? record.record_id ?? "");
        if (!recordId) throw new Error("fujisawa facility record has no stable identifier");
        for (const attribute of FUJISAWA_FACILITY_ATTRIBUTES) {
          const geometry = attribute === "facility.geometry";
          items.push({
            item_id: `fujisawa_enoshima:facility:${recordId}:${attribute}`,
            city_id: cityId, subarea_id: "enoshima_katase",
            object_type: "facility", object_id: recordId, attribute,
            // ADDRESS_ONLY stays ADDRESS_ONLY: no coordinate is derived from the address.
            status: geometry ? "NOT_CONNECTED" : "PERMISSION_REQUIRED",
            source_id: null, source_revision: null, source_sha256: null,
            unknown_reason: geometry ? r5Receipt.geometry_status : r5Receipt.license_status,
            verification_method: "OFFICIAL_QUERY",
            verification_target: target(matrixLabel, ADMIN_RECEIPT_PATHS.R7, datasetIds, r5Receipt.semantic_guard),
            ...adminPriorityRule({ subareaId: "enoshima_katase" }),
            exposure_flags: null,
            human_fields: emptyHumanFields(),
            export_ready: matrixLabel !== NO_TARGET,
            internal_use_only: true,
          });
        }
      }
    }
  }

  const visible = includeInternalUseOnly ? items : items.filter((item) => item.internal_use_only !== true);
  if (!includeInternalUseOnly && visible.some((item) => item.internal_use_only === true)) throw new Error(`${cityId} default admin checklist build contains internal_use_only rows`);
  const sorted = sortChecklistItems(visible);
  const countBy = (key) => {
    const counts = {};
    for (const item of sorted) counts[item[key]] = (counts[item[key]] ?? 0) + 1;
    return Object.fromEntries(Object.keys(counts).sort(compareCodePoints).map((name) => [name, counts[name]]));
  };
  return {
    schema_version: "1.0.0",
    city_id: cityId,
    generated_at: r1.generated_at ?? null,
    generator: "viewer/scripts/build-map-artifacts.mjs",
    include_internal_use_only: includeInternalUseOnly === true,
    fujisawa_facility_row_source_status: fujisawaFacilityStatus,
    generated_from: Object.fromEntries(Object.values(ADMIN_RECEIPT_PATHS).filter((relative) => existsSync(join(root, relative))).sort(compareCodePoints).map((relative) => [relative, canonicalTextHash(join(root, relative))])),
    counts: { items: sorted.length, by_object_type: countBy("object_type"), by_status: countBy("status"), by_verification_method: countBy("verification_method"), by_priority_rank: countBy("priority_rank") },
    safety_claim: false,
    accessibility_claim: false,
    admin_validated: false,
    m6_status: "NOT_COMPUTED",
    m7_status: "NOT_COMPUTED",
    guard_texts: [...ADMIN_CHECKLIST_GUARD_TEXTS],
    schema: ADMIN_CHECKLIST_SCHEMA,
    items: sorted,
  };
}

/**
 * Portability cap for anything the browser fetches. The row payload is split
 * into shards under this cap; no row is dropped, summarised or reordered.
 */
export const ADMIN_SHARD_BYTE_CAP = 2 * 1024 * 1024;

/**
 * Split the deterministically ordered items into shards. A cut is made where the
 * section (object_type) changes and wherever another row would cross the cap, so
 * concatenating the shards in manifest order reproduces the same ordering.
 * Rows are serialised compactly: a serialisation choice, not a content change.
 */
export function shardChecklistItems(items, byteCap = ADMIN_SHARD_BYTE_CAP) {
  const shards = [];
  const partBySection = new Map();
  let current = null;
  const close = () => { if (current) shards.push(current); current = null; };
  for (const item of items) {
    const encoded = JSON.stringify(item);
    const addedBytes = Buffer.byteLength(encoded, "utf8") + 1;
    if (current && (current.section !== item.object_type || current.bytes + addedBytes > byteCap)) close();
    if (!current) {
      const part = (partBySection.get(item.object_type) ?? 0) + 1;
      partBySection.set(item.object_type, part);
      // "[" + "]" + trailing newline
      current = { section: item.object_type, part, items: [], bytes: 3 };
    }
    current.items.push(item);
    current.bytes += addedBytes;
  }
  close();
  return shards;
}

/**
 * Generate the admin-check checklists. Deterministic: same repository bytes in,
 * same output bytes out. `includeInternalUseOnly` defaults to false; a true
 * build must be given an output root outside `viewer/public/data`.
 */
export function buildAdminChecklists({ repoRoot, outputRoot, reportsRoot, includeInternalUseOnly = false }) {
  const root = repoRoot instanceof URL ? fileURLToPath(repoRoot) : resolve(repoRoot);
  const adminDirectory = outputRoot instanceof URL ? fileURLToPath(outputRoot) : resolve(outputRoot);
  if (includeInternalUseOnly && adminDirectory.startsWith(join(root, "viewer", "public", "data"))) throw new Error("internal_use_only builds must not be written into the public viewer data root");
  const readCsv = (relative) => parseCsv(readFileSync(join(root, relative), "utf8"));
  const r5TablePath = join(root, ADMIN_RECEIPT_PATHS.R5_table);
  const sources = {
    r1: json(join(root, ADMIN_RECEIPT_PATHS.R1)),
    r2: json(join(root, ADMIN_RECEIPT_PATHS.R2)),
    r3: json(join(root, ADMIN_RECEIPT_PATHS.R3)),
    r4Records: json(join(root, ADMIN_RECEIPT_PATHS.R4_records)),
    r4Categories: json(join(root, ADMIN_RECEIPT_PATHS.R4_categories)),
    r5Receipt: json(join(root, ADMIN_RECEIPT_PATHS.R5_receipt)),
    r5Table: existsSync(r5TablePath) ? json(r5TablePath) : null,
    r6: readCsv(ADMIN_RECEIPT_PATHS.R6),
    r7: readCsv(ADMIN_RECEIPT_PATHS.R7),
    r8: json(join(root, ADMIN_RECEIPT_PATHS.R8)),
    r9: json(join(root, ADMIN_RECEIPT_PATHS.R9)),
  };
  mkdirSync(adminDirectory, { recursive: true });
  const reports = reportsRoot === undefined ? null : reportsRoot instanceof URL ? fileURLToPath(reportsRoot) : resolve(reportsRoot);
  if (reports) mkdirSync(reports, { recursive: true });
  const files = [];
  const checklists = [];
  for (const cityId of ADMIN_CITY_IDS) {
    const checklist = buildCityChecklist(root, cityId, sources, includeInternalUseOnly);
    const bytes = `${JSON.stringify(checklist, null, 2)}\n`;
    const csv = toChecklistCsv(checklist.items);
    // The viewer reads a small manifest plus row shards, each under the portability
    // cap. The manifest carries no rows; `items` stays in the reports copy.
    const { items, ...header } = checklist;
    const cityDirectory = join(adminDirectory, cityId);
    mkdirSync(cityDirectory, { recursive: true });
    const shardRecords = [];
    for (const shard of shardChecklistItems(items)) {
      const filename = `${shard.section}.part${String(shard.part).padStart(2, "0")}.rows.json`;
      const shardPath = join(cityDirectory, filename);
      const shardBytes = `${JSON.stringify(shard.items)}\n`;
      writeFileSync(shardPath, shardBytes);
      const byteLength = Buffer.byteLength(shardBytes, "utf8");
      if (byteLength > ADMIN_SHARD_BYTE_CAP) throw new Error(`${cityId} shard ${filename} exceeds the portability cap`);
      shardRecords.push({ path: `./data/admin/${cityId}/${filename}`, section: shard.section, part: shard.part, row_count: shard.items.length, sha256: sha256(Buffer.from(shardBytes, "utf8")), bytes: byteLength });
      files.push(shardPath);
    }
    const manifest = { ...header, row_payload: "SHARDED", shard_byte_cap: ADMIN_SHARD_BYTE_CAP, shards: shardRecords };
    const manifestBytes = `${JSON.stringify(manifest, null, 2)}\n`;
    if (Buffer.byteLength(manifestBytes, "utf8") > ADMIN_SHARD_BYTE_CAP) throw new Error(`${cityId} admin checklist manifest exceeds the portability cap`);
    const checklistPath = join(adminDirectory, `${cityId}.checklist.json`);
    writeFileSync(checklistPath, manifestBytes);
    files.push(checklistPath);
    if (reports) {
      const reportJson = join(reports, `ADMIN_CHECKLIST_${cityId}.json`);
      const reportCsv = join(reports, `ADMIN_CHECKLIST_${cityId}.csv`);
      writeFileSync(reportJson, bytes);
      writeFileSync(reportCsv, csv);
      files.push(reportJson, reportCsv);
    }
    checklists.push(checklist);
  }
  return { files, checklists };
}

export function buildMapArtifacts({ repoRoot, outputRoot, analysisRoot, reportsRoot }) {
  const root = repoRoot instanceof URL ? fileURLToPath(repoRoot) : resolve(repoRoot); const output = outputRoot instanceof URL ? fileURLToPath(outputRoot) : resolve(outputRoot);
  const analysisDirectory = analysisRoot instanceof URL ? fileURLToPath(analysisRoot) : resolve(analysisRoot ?? join(root, "viewer", "public", "data", "analysis"));
  assertStaticAnalysisArtifacts({ repoRoot: root, analysisRoot: analysisDirectory });
  const built = CITY_INPUTS.map((input) => artifact(root, input)); mkdirSync(output, { recursive: true });
  for (const city of built) {
    const deliveredPath = join(output, `${city.city_id}.candidate_edges.geojson`);
    writeFileSync(deliveredPath, city.edgeBytes);
    city.real_2d.copied_sha256 = hash(deliveredPath);
  }
  // Production writes data/maps and data/official as siblings. Test callers
  // may pass a unique temporary directory directly; keep their official
  // copies inside that unique root so parallel tests never share temp/official.
  const officialDirectory = basename(output) === "maps" ? join(dirname(output), "official") : join(output, "official");
  mkdirSync(officialDirectory, { recursive: true });
  const parityRoot = join(root, "inputs", "staging", "KYOTO-OFFICIAL-PARITY-V1");
  for (const filename of ["a31b_kiyomizu_gion_display.geojson", "a31b_arashiyama_display.geojson", "facility_points_kiyomizu_gion.geojson", "facility_points_arashiyama.geojson"]) {
    writeFileSync(join(officialDirectory, filename), canonicalTextBytes(readFileSync(join(parityRoot, filename))));
  }
  const sourceOfficialDirectory = join(dirname(analysisDirectory), "official");
  for (const input of CITY_INPUTS) {
    const filename = `${input.id}.delivery_hazards.geojson`;
    writeFileSync(join(officialDirectory, filename), canonicalTextBytes(readFileSync(join(sourceOfficialDirectory, filename))));
  }
  assertDeliveredOfficialArtifacts(CITY_INPUTS.map((input) => json(join(analysisDirectory, `${input.id}.json`))), officialDirectory);
  const catalog = { viewer_map_schema_version: "2.0.0", generated_from: "HASH_VERIFIED_CITY_ARTIFACTS", cities: built.map(({ edgeBytes, edgeData, source_artifact_ids, source_revision_ids, input_sha256, input_hashes, snapshot_at, source_id, ...city }) => city) };
  assertSupportedMapCatalog(catalog); assertDeliveredMapArtifacts(catalog, output); writeFileSync(join(output, "map-layers.json"), `${JSON.stringify(catalog, null, 2)}\n`);
  // T-A: additional deterministic generation. Existing outputs above are unchanged.
  const adminDirectory = basename(output) === "maps" ? join(dirname(output), "admin") : join(output, "admin");
  const repoOutput = resolve(output) === resolve(join(root, "viewer", "public", "data", "maps"));
  const adminReportsRoot = reportsRoot ?? (repoOutput ? join(root, "reports") : join(dirname(adminDirectory), "reports"));
  const admin = buildAdminChecklists({ repoRoot: root, outputRoot: adminDirectory, reportsRoot: adminReportsRoot });
  return { files: [...built.map((city) => join(output, `${city.city_id}.candidate_edges.geojson`)), ...["a31b_kiyomizu_gion_display.geojson", "a31b_arashiyama_display.geojson", "facility_points_kiyomizu_gion.geojson", "facility_points_arashiyama.geojson", ...CITY_INPUTS.map((input) => `${input.id}.delivery_hazards.geojson`)].map((filename) => join(officialDirectory, filename)), join(output, "map-layers.json")], admin_files: admin.files };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) buildMapArtifacts({ repoRoot: resolve(".."), outputRoot: resolve("public/data/maps") });
