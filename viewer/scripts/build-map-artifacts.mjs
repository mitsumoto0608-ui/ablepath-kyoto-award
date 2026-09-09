import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { assertSupportedMapCatalog, computeGeoJsonBounds } from "../src/mapDomain.mjs";
import { validateDeliveryAnalysis } from "../src/analysisDomain.mjs";

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
    facility_table_sha256: join(root, "cities", cityId, "facilities", "official", "FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json"),
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
    const revisions = [...new Set([...JSON.parse(nodeBytes).features, ...JSON.parse(edgeBytes).features].map((feature) => feature.properties?.revision_id).filter(Boolean))].sort();
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
  const nodeBytes = readFileSync(paths.nodes); const nodeData = JSON.parse(nodeBytes); const sourceArtifactIds = [input.nodes, input.edges]; const sourceRevisionIds = [...new Set([...(nodeData.features ?? []), ...edgeData.features].map((feature) => feature.properties?.revision_id).filter(Boolean))].sort();
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

export function buildMapArtifacts({ repoRoot, outputRoot, analysisRoot }) {
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
    copyFileSync(join(parityRoot, filename), join(officialDirectory, filename));
  }
  const sourceOfficialDirectory = join(dirname(analysisDirectory), "official");
  for (const input of CITY_INPUTS) {
    const filename = `${input.id}.delivery_hazards.geojson`;
    copyFileSync(join(sourceOfficialDirectory, filename), join(officialDirectory, filename));
  }
  assertDeliveredOfficialArtifacts(CITY_INPUTS.map((input) => json(join(analysisDirectory, `${input.id}.json`))), officialDirectory);
  const catalog = { viewer_map_schema_version: "2.0.0", generated_from: "HASH_VERIFIED_CITY_ARTIFACTS", cities: built.map(({ edgeBytes, edgeData, source_artifact_ids, source_revision_ids, input_sha256, input_hashes, snapshot_at, source_id, ...city }) => city) };
  assertSupportedMapCatalog(catalog); assertDeliveredMapArtifacts(catalog, output); writeFileSync(join(output, "map-layers.json"), `${JSON.stringify(catalog, null, 2)}\n`);
  return { files: [...built.map((city) => join(output, `${city.city_id}.candidate_edges.geojson`)), ...["a31b_kiyomizu_gion_display.geojson", "a31b_arashiyama_display.geojson", "facility_points_kiyomizu_gion.geojson", "facility_points_arashiyama.geojson", ...CITY_INPUTS.map((input) => `${input.id}.delivery_hazards.geojson`)].map((filename) => join(officialDirectory, filename)), join(output, "map-layers.json")] };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) buildMapArtifacts({ repoRoot: resolve(".."), outputRoot: resolve("public/data/maps") });
