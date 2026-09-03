import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { assertSupportedMapCatalog, computeGeoJsonBounds } from "../src/mapDomain.mjs";

const CITY_INPUTS = [
  { id: "kyoto_kiyomizu", nodes: "cities/kyoto_kiyomizu/graph/real/candidate_nodes.geojson", edges: "cities/kyoto_kiyomizu/graph/real/candidate_edges.geojson", corridor: "cities/kyoto_kiyomizu/geography/real/corridor.osm.geojson", topology: "cities/kyoto_kiyomizu/graph/real/topology_qa.json", manifest: "cities/kyoto_kiyomizu/realdata/artifact_manifest.v2.json", source: "openstreetmap_kiyomizu_named_corridor_20260830", snapshot: "2026-08-30T00:00:00Z" },
  { id: "kyoto_arashiyama", nodes: "cities/kyoto_arashiyama/graph/walk_nodes.real.geojson", edges: "cities/kyoto_arashiyama/graph/walk_edges.real.geojson", corridor: "cities/kyoto_arashiyama/geography/corridor.real.geojson", topology: "cities/kyoto_arashiyama/graph/topology_qa.real.json", manifest: "cities/kyoto_arashiyama/sources/realdata_manifest.json", source: "openstreetmap-overpass-arashiyama-20260829", snapshot: "2026-08-29T00:00:00Z" },
  { id: "fujisawa_enoshima", nodes: "cities/fujisawa_enoshima/graph/candidate_walk_nodes.real.geojson", edges: "cities/fujisawa_enoshima/graph/candidate_walk_edges.real.geojson", corridor: "cities/fujisawa_enoshima/geography/corridor.real.geojson", topology: "cities/fujisawa_enoshima/graph/candidate_topology_qa.real.json", manifest: "cities/fujisawa_enoshima/realdata/artifact_manifest.v2.json", source: "OSM_CANDIDATE_SOURCE", snapshot: "2026-08-30T00:00:00Z" },
];
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const json = (path) => JSON.parse(readFileSync(path, "utf8"));
const hash = (path) => sha256(readFileSync(path));
function csvRows(path) {
  const text = readFileSync(path, "utf8").replace(/^\uFEFF/, "").trim(); const rows = []; let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) { const ch = text[i]; if (ch === '"') { if (quoted && text[i + 1] === '"') { field += ch; i += 1; } else quoted = !quoted; } else if (ch === "," && !quoted) { row.push(field); field = ""; } else if (ch === "\n" && !quoted) { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; } else field += ch; }
  row.push(field.replace(/\r$/, "")); rows.push(row); const [header, ...body] = rows; if (!header?.every(Boolean) || body.some((values) => values.length !== header.length)) throw new Error(`strict CSV parse failed: ${path}`); return body.map((values) => Object.fromEntries(header.map((key, index) => [key, values[index]])));
}

function readOfficialEvidence(root, cityId, override = {}, m7Override = {}) {
  const promotion = json(join(root, "reports", "OFFICIAL_LOCAL_ARTIFACT_PROMOTION_V2.json"));
  const kyoto = json(join(root, "reports", "KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json"));
  const plateau = json(join(root, "reports", "PLATEAU_BUILDING_EVIDENCE_V1.json"));
  const m7 = json(join(root, "reports", "M7_REAL_EDGE_STATUS.json"));
  const m7All = { ...json(join(root, "reports", "M7_ALL_EDGE_EVIDENCE_READINESS.json")), ...m7Override };
  const safety = { safe_route_claim: false, accessibility_claim: false, admin_validated: false, ...override };
  if (Object.values(safety).some(Boolean) || promotion.closure_derived || promotion.damage_derived || promotion.debris_derived) throw new Error("unsafe official evidence promotion is forbidden");
  if (m7All.edges.length !== m7All.all_edge_count || m7All.all_edge_count !== m7.all_edge_count || m7All.deep_pilot_count !== m7.deep_pilot_count || m7All.evidence_ready_count !== m7.evidence_ready_count || m7All.computed_count !== m7.computed_count || m7All.edges.some((edge) => edge.status !== "NOT_COMPUTED" || edge.m7_result !== null || edge.m7_computed || edge.m7_evidence_ready)) throw new Error("P3 M7 receipt binding is incomplete or promoted");
  const edgeReceipts = m7All.edges.filter((edge) => edge.city_id === cityId);
  const cityTruth = kyoto.cities[cityId];
  const kyotoParity = cityTruth ? json(join(root, "reports", "KYOTO_PARITY_STATUS.json")) : null;
  const kyotoPilot = cityTruth ? json(join(root, "reports", "KYOTO_M7_DEEP_PILOT_STATUS.json")) : null;
  const parityRoot = join(root, "inputs", "staging", "KYOTO-OFFICIAL-PARITY-V1");
  const parityGroup = cityId === "kyoto_kiyomizu" ? "kiyomizu_gion" : cityId === "kyoto_arashiyama" ? "arashiyama" : null;
  const parityAoi = cityId === "kyoto_kiyomizu" ? kyotoParity?.aois?.kiyomizu : cityId === "kyoto_arashiyama" ? kyotoParity?.aois?.arashiyama : null;
  const subareas = cityTruth?.subareas ?? (cityId === "fujisawa_enoshima" ? ["enoshima_katase"] : []);
  const terrainCandidate = join(root, "cities", cityId, "terrain", "official", "dem_product_inventory.csv");
  const terrainPath = existsSync(terrainCandidate) ? terrainCandidate : null;
  const terrainProducts = terrainPath ? csvRows(terrainPath).map(({ dataset_id, mesh_id, dem_class, horizontal_crs, vertical_datum, aoi, aoi_status, validation_result, terrain_connected, license_status }) => cityTruth ? ({ dataset_id, mesh_id, dem_class, horizontal_crs, vertical_datum, aoi: parityGroup, aoi_status: "AOI_INTERSECTS_REVIEWED_BOUNDS", validation_result: "HORIZONTAL_CRS_AXIS_AOI_VALIDATED_VERTICAL_DATUM_NOT_EXPLICIT", license_status, terrain_connected: false, status: "EVIDENCE_UI_ONLY_NOT_ELEVATION_ANALYSIS", legacy_inventory_status: { aoi, aoi_status, validation_result, terrain_connected: terrain_connected === "true" } }) : ({ dataset_id, mesh_id, dem_class, horizontal_crs, vertical_datum, aoi, aoi_status, validation_result, license_status, terrain_connected: terrain_connected === "true", status: "NOT_CONNECTED" })) : [];
  const fixedAbsentHazardReason = "No accepted source-traceable AOI artifact in P1; no closure, damage, debris, or FAIL state is derived.";
  const hazardLayers = cityTruth ? subareas.flatMap((subarea) => [["flood", cityTruth.flood_artifact_status, cityTruth.flood_reason], ["landslide", cityTruth.landslide_artifact_status, cityTruth.landslide_reason], ["earthquake", null, null], ["liquefaction", null, null], ["inner_flood", null, null]].map(([layer, artifact_status, reason]) => layer === "flood" && parityAoi ? ({ subarea, layer, status: "CONNECTED_FOR_INTERNAL_DISPLAY_ONLY", connected: true, artifact_status: "AOI_INTERSECTION_SELECTION_HASH_BOUND", reason: parityAoi.flood.reason }) : ({ subarea, layer, status: "NOT_CONNECTED", connected: false, artifact_status: artifact_status ?? "NOT_ACCEPTED", reason: reason ?? fixedAbsentHazardReason }))) : [];
  const scenarioPaths = cityId === "fujisawa_enoshima" ? [join(root, "cities", cityId, "hazards", "official", "earthquake_scenario_inventory.csv"), join(root, "cities", cityId, "hazards", "official", "liquefaction_scenario_inventory.csv")] : [];
  const scenarios = scenarioPaths.flatMap((path) => csvRows(path).map(({ dataset_id, scenario, layer_kind, official_source, official_url, version_date, license_review, validation_result, crs, bounds_native }) => ({ dataset_id, scenario, layer_kind, official_source, official_url, version_date, license_review, validation_result, crs, bounds_native, aoi_scope: "enoshima_katase", status: "NOT_CONNECTED", connected: false, reason: "Scenario inventory only; no AOI geometry connection or closure derivation." })));
  const facility = cityId === "fujisawa_enoshima"
    ? (() => {
      const table = json(join(root, "cities", cityId, "facilities", "official", "FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json"));
      return { status: promotion.fujisawa_accessibility_facilities.status, geometry_status: "ADDRESS_ONLY", marker_policy: "TABLE_ONLY_NO_MARKERS_OR_GEOCODING", record_count: table.records.length, records: table.records, reason: "57 address-only records are displayed as a table; coordinates, map markers, geocoding, accessibility, opening, and disaster availability are not inferred." };
    })()
    : cityTruth ? (() => {
      const categoryStatus = json(join(parityRoot, "facility_category_status.json"));
      const allRecords = json(join(parityRoot, "facility_records.json")).records;
      const records = allRecords.filter((record) => record.aoi_group === parityGroup);
      const categories = Object.fromEntries(Object.entries(categoryStatus.categories).map(([category, value]) => [category, {
        ...value,
        record_count: value.map_connected ? records.filter((record) => record.category === category).length : 0,
        count_scope: parityGroup,
      }]));
      const pointPath = join(parityRoot, `facility_points_${parityGroup}.geojson`);
      const pointData = json(pointPath);
      return {
        status: "PARTIAL_3_OF_5_CATEGORIES_SOURCE_COORDINATES",
        geometry_status: "SOURCE_PROVIDED_LONGITUDE_LATITUDE",
        marker_policy: "SOURCE_COORDINATES_ONLY_NO_GEOCODING",
        record_count: records.length,
        records,
        categories,
        display_layer: { data_path: `./data/official/facility_points_${parityGroup}.geojson`, artifact_sha256: hash(pointPath), copied_sha256: null, feature_count: pointData.features.length },
        reason: "Three official categories are displayed from source-provided longitude/latitude only. Emergency-open-space and temporary-stay rows remain metadata-only; opening, entrance, accessibility, safety, and disaster usability are UNKNOWN.",
      };
    })() : { status: "NOT_CONNECTED", record_count: 0, reason: "No official facility evidence is connected." };
  const plateauInventory = cityTruth ? csvRows(join(root, "inputs", "staging", "PLATEAU-BUILDING-EVIDENCE-V1", "PLATEAU_BUILDING_AOI_INVENTORY.csv")).filter((row) => row.city_id === cityId) : [];
  const kyotoPilotEdges = cityTruth ? kyotoPilot.edges.filter((row) => row.aoi_group === parityGroup) : [];
  const floodPath = parityGroup ? join(parityRoot, `a31b_${parityGroup}_display.geojson`) : null;
  const floodData = floodPath ? json(floodPath) : null;
  const terrainReason = cityTruth
    ? `DEM products were found, but terrain is NOT_CONNECTED: CRS/AOI/vertical datum review remains unresolved.`
    : "No terrain product has been connected to this city analysis.";
  const hazardReason = cityTruth
    ? `No closure is derived. Flood: ${cityTruth.flood_reason} Landslide: ${cityTruth.landslide_reason}`
    : "No official hazard geometry is connected; earthquake and liquefaction inventories remain scenario metadata and do not derive CLOSED or FAIL.";
  return {
    source_status: promotion.status,
    source_hashes: {
      promotion_sha256: hash(join(root, "reports", "OFFICIAL_LOCAL_ARTIFACT_PROMOTION_V2.json")),
      plateau_sha256: hash(join(root, "reports", "PLATEAU_BUILDING_EVIDENCE_V1.json")),
      m7_sha256: hash(join(root, "reports", "M7_REAL_EDGE_STATUS.json")),
      ...(cityTruth ? { kyoto_status_sha256: hash(join(root, "reports", "KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.json")) } : {}),
      ...(terrainPath ? { terrain_inventory_sha256: hash(terrainPath) } : {}),
      ...(cityTruth ? { kyoto_parity_sha256: hash(join(root, "reports", "KYOTO_PARITY_STATUS.json")), kyoto_m7_pilot_sha256: hash(join(root, "reports", "KYOTO_M7_DEEP_PILOT_STATUS.json")), kyoto_facility_sha256: hash(join(parityRoot, "facility_records.json")), kyoto_flood_display_sha256: hash(floodPath) } : {}),
      ...(cityId === "fujisawa_enoshima" ? { facility_receipt_sha256: hash(join(root, "cities", cityId, "facilities", "official", "facility_source_receipt.json")), facility_table_sha256: hash(join(root, "cities", cityId, "facilities", "official", "FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json")), earthquake_inventory_sha256: hash(join(root, "cities", cityId, "hazards", "official", "earthquake_scenario_inventory.csv")), liquefaction_inventory_sha256: hash(join(root, "cities", cityId, "hazards", "official", "liquefaction_scenario_inventory.csv")) } : {}),
    },
    subareas,
    terrain: { status: cityTruth ? "AOI_COVERAGE_VALIDATED_ELEVATION_NOT_SAMPLED" : "NOT_CONNECTED", reason: cityTruth ? parityAoi.terrain.reason : terrainReason, connected: false, evidence_ui_connected: Boolean(cityTruth), elevation_sampled: false, step_inferred: false, cross_slope_inferred: false, aoi_validation: cityTruth ? parityAoi.terrain : null, receipt_sha256: terrainPath ? hash(terrainPath) : null, products: terrainProducts },
    hazard: { status: cityTruth ? "A31B_DISPLAY_CONNECTED_LANDSLIDE_NOT_CONNECTED" : "NOT_CONNECTED", reason: cityTruth ? `A31b is connected for internal display only. Landslide remains NOT_CONNECTED: ${parityAoi.landslide.reason}` : hazardReason, connected: false, display_connected: Boolean(cityTruth), display_feature_count: floodData?.features.length ?? 0, display_layer: cityTruth ? { data_path: `./data/official/a31b_${parityGroup}_display.geojson`, artifact_sha256: hash(floodPath), copied_sha256: null, feature_count: floodData.features.length, display_only: true } : null, closure_derived: false, damage_or_debris_inferred: false, layers: hazardLayers, scenarios },
    facility,
    plateau: { status: "NOT_CONNECTED", aoi_count: subareas.length, aoi_scope: subareas, inventory: plateauInventory, inventory_connected: Boolean(cityTruth), fallback: plateau.fallback, m7_evidence_ready_count: plateau.m7_evidence_ready_count, m7_computed_count: plateau.m7_computed_count, reason: "The PLATEAU 2025 evidence inventory is connected, but verified package bytes, building IDs, footprints, direct height, side coverage, and real 3D remain unavailable. Existing source-traceable candidate 2D is the deterministic fallback, not a PLATEAU-derived footprint layer." },
    m7: { status: "NOT_COMPUTED", all_edge_count: m7.all_edge_count, deep_pilot_count: m7.deep_pilot_count, evidence_ready_count: m7.evidence_ready_count, computed_count: m7.computed_count, city_edge_count: edgeReceipts.length, edge_receipts_source_sha256: hash(join(root, "reports", "M7_ALL_EDGE_EVIDENCE_READINESS.json")), kyoto_deep_pilot_edges: kyotoPilotEdges, city_limitations: m7.subarea_limitations[cityId] ?? "No reviewed source-traceable per-edge M7 inputs are connected.", reason: "M7 is not connected to real candidate edges; every Kyoto pilot exposes field-level evidence candidates and next acquisition without inferring setback, damage, or debris." },
    m6: { status: "NOT_COMPUTED", reason: "M6/profile evaluation is not connected." },
    ...safety,
  };
}

export function shortestCandidateFixture(adjacency, lengths, from, to) {
  const best = new Map([[from, [0, []]]]); const queue = [[0, [], from]];
  while (queue.length) { queue.sort((a, b) => a[0] - b[0] || a[1].join("\0").localeCompare(b[1].join("\0"))); const [cost, route, current] = queue.shift(); const known = best.get(current); if (cost !== known[0] || route.join("\0") !== known[1].join("\0")) continue;
    for (const [next, edgeId] of (adjacency.get(current) ?? []).sort((a, b) => a[1].localeCompare(b[1]))) { const candidate = [cost + lengths.get(edgeId), [...route, edgeId]]; const prior = best.get(next); if (!prior || candidate[0] < prior[0] || (candidate[0] === prior[0] && candidate[1].join("\0") < prior[1].join("\0"))) { best.set(next, candidate); queue.push([candidate[0], candidate[1], next]); } }
  }
  if (!best.has(to)) return { status: "DISCONNECTED", edge_ids: [], geometric_length: null };
  return { status: "CONNECTED", edge_ids: best.get(to)[1], geometric_length: best.get(to)[0] };
}

function analysisFor(city) {
  const edgeFeatures = city.edgeData.features.map((feature) => ({ properties: feature.properties, coordinates: feature.geometry.coordinates }));
  const edges = edgeFeatures.map((feature) => feature.properties).sort((a, b) => a.edge_id.localeCompare(b.edge_id));
  const lengths = new Map(edgeFeatures.map(({ properties, coordinates }) => [properties.edge_id, coordinates.slice(1).reduce((sum, point, index) => sum + Math.hypot(point[0] - coordinates[index][0], point[1] - coordinates[index][1]), 0)]));
  const adjacency = new Map();
  for (const edge of edges) { for (const [from, to] of [[edge.from_node, edge.to_node], [edge.to_node, edge.from_node]]) adjacency.set(from, [...(adjacency.get(from) ?? []), [to, edge.edge_id]]); }
  const nodes = [...adjacency.keys()].sort(); const seen = new Set(); const components = [];
  for (const node of nodes) if (!seen.has(node)) { const component = []; const pending = [node]; seen.add(node); while (pending.length) { const current = pending.pop(); component.push(current); for (const [next] of adjacency.get(current) ?? []) if (!seen.has(next)) { seen.add(next); pending.push(next); } } components.push(component.sort()); }
  const disconnected = components.length > 1;
  const selectableNodeIds = components.length > 1 ? [components[0][0], components[0].at(-1), components[1][0]] : components[0].slice(0, 3);
  const start = selectableNodeIds[0] ?? null; const end = selectableNodeIds[1] ?? null;
  const previous = new Map([[start, null]]); const pending = [start]; while (pending.length && !previous.has(end)) { const current = pending.shift(); for (const [next, edgeId] of (adjacency.get(current) ?? []).sort((a, b) => a[1].localeCompare(b[1]))) if (!previous.has(next)) { previous.set(next, [current, edgeId]); pending.push(next); } }
  const route = []; for (let cursor = end; previous.get(cursor); ) { const [prior, edgeId] = previous.get(cursor); route.unshift(edgeId); cursor = prior; }
  const fixtureFor = (from, to) => {
    const selected = shortestCandidateFixture(adjacency, lengths, from, to);
    return { start_node_id: from, end_node_id: to, ...selected, unit: "coordinate_degree", reason: selected.status === "CONNECTED" ? "Candidate connectivity only; accessibility, safety, and operation are unconfirmed." : "No candidate-network connection exists between the selected nodes; accessibility, safety, and operation are unconfirmed." };
  };
  const pathMatrix = Object.fromEntries(selectableNodeIds.flatMap((from) => selectableNodeIds.filter((to) => to !== from).map((to) => [`${from}__${to}`, fixtureFor(from, to)])));
  const pathFixture = pathMatrix[`${start}__${end}`] ?? { start_node_id: start, end_node_id: end, status: "CONNECTED", unit: "coordinate_degree", edge_ids: route, geometric_length: route.reduce((sum, edgeId) => sum + lengths.get(edgeId), 0), reason: "Candidate connectivity only; accessibility, safety, and operation are unconfirmed." };
  const result = { topology: { node_count: nodes.length, edge_count: edges.length, connected_components: components.length, topology_status: "CANDIDATE_REVIEW_REQUIRED" }, selectable_node_ids: selectableNodeIds, path_matrix: pathMatrix, path_fixture: pathFixture, hazard_overlap: { status: "NOT_CONNECTED", value: null, reason: "No trusted official hazard geometry is connected; no closure is derived." }, m7: { status: city.official_evidence.m7.status, ready_edge_count: city.official_evidence.m7.evidence_ready_count, computed_edge_count: city.official_evidence.m7.computed_count }, m6: { status: "NOT_COMPUTED", reason: "M6/profile evaluation is not connected." } };
  return { analysis_id: `${city.city_id}:candidate-topology-v2`, analysis_type: "CANDIDATE_TOPOLOGY_STATIC_FIXTURE", city_id: city.city_id, source_artifact_ids: city.source_artifact_ids, source_revision_ids: city.source_revision_ids, input_sha256: city.input_sha256, algorithm: "deterministic-undirected-dijkstra-coordinate-degree", algorithm_version: "2.0.0", parameters: { coordinate_unit: "coordinate_degree", input_binding: "sha256(node_geojson_bytes + 0x00 + edge_geojson_bytes); input order=node,edge", tie_break: "lexical ordered edge-ID tuple" }, generated_at: city.snapshot_at, deterministic: true, result, official_evidence: city.official_evidence, limitations: ["Candidate connectivity only", "coordinate_degree is not a geographic or meter distance", "Hazard, M7, M6, accessibility, safety, operation, and administrative validation are unconnected or not computed"], provenance: { source_class: "VGI", source_id: city.source_id, input_binding: "node bytes then NUL then edge bytes", input_artifacts: city.source_artifact_ids, input_hashes: city.input_hashes }, safety_claim: false, accessibility_claim: false, admin_validated: false, ...result, m7: { ...result.m7, readiness: city.m7_readiness }, interpretation: "Candidate network connectivity only; accessibility, safety, and operation are unconfirmed." };
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
  return {
    city_id: input.id,
    real_2d: { data_path: dataPath, artifact_sha256: edgeSha, copied_sha256: null, corridor_sha256: hash(paths.corridor), source_sha256: input.id === "kyoto_kiyomizu" ? "3d21ce674776c5c3e37c507c09a9458e062d2d31f5718b3e702313838ef7d2ec" : input.id === "kyoto_arashiyama" ? "1cde93d68bebf633989e825cbd5ac1e772cee81508043f44beb311250a1e8013" : "c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04", query_sha256: input.id === "kyoto_kiyomizu" ? "f32964329548d7d715c79cf05da6a28a7ac8230781acc4852f9174ba9f4dfb7b" : input.id === "kyoto_arashiyama" ? "b5c52b3ea7542261159b5764956aa9662673c0422b3509dc59e4866f00c14603" : "c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04", topology_sha256: topologySha, manifest_sha256: manifestSha, source_id: input.source, source_class: "VGI", data_class: "REAL", geometry_status: "SOURCE_TRACEABLE_REAL", topology_status: "CANDIDATE_REVIEW_REQUIRED", route_continuity: "NOT_ESTABLISHED", snapshot_at: input.snapshot, feature_count: edgeData.features.length, bounds: computeGeoJsonBounds(edgeData), license: "Open Data Commons Open Database License (ODbL) 1.0", license_url: "https://opendatacommons.org/licenses/odbl/1-0/", copyright_url: "https://www.openstreetmap.org/copyright", attribution: "© OpenStreetMap contributors / Data available under ODbL 1.0", lineage: [`artifact:${edgeSha}`, "transform:EXACT_BYTE_COPY@1.0.0", `corridor:${hash(paths.corridor)}`, `topology:${topologySha}`, `manifest:${manifestSha}`, `manifest_schema:${manifest.schema_version ?? "unknown"}`] },
    cesium: input.id === "kyoto_kiyomizu" ? { available: true, data_class: "OFFICIAL_METADATA_ONLY", source_id: "plateau_26100_bldg_maxlod2_latest_20260830", source_class: "OFFICIAL", accessed_at: "2026-08-30", valid_as_of: null, valid_as_of_reason: "Latest endpoint is dynamic; retained ETag response must be rechecked", lod: "LOD2", tileset_url: "https://assets.cms.plateau.reearth.io/assets/25/dd4c50-5342-4a0b-ac51-05ffb138b8b5/26100_kyoto-shi_city_2025_citygml_1_op_bldg_3dtiles_26105_higashiyama-ku_lod2/tileset.json", license: "Public Data License 1.0 (PDL1.0), CC BY 4.0 compatible", license_url: "https://www.mlit.go.jp/plateau/site-policy/", attribution: "出典：国土交通省 3D都市モデル（Project PLATEAU）京都市2025 / PDL1.0", connected: false, requires_commercial_token: false, metadata_sha256: "2a1e4c71370f58f0f40dc8b6eb9ae120b7f694b6caca1260a8a0efbbfeda78d3", retained_response_sha256: "ce58a92bb9da595d9251cd72b7b77af6da9a3748628a0e8370ffc6fbc6312242", query_sha256: "eb9400f69b5ee88b802e972f426b4ff624ab759fe372776f67ecd83978221e40" } : null,
    edgeBytes, edgeData, source_artifact_ids: sourceArtifactIds, source_revision_ids: sourceRevisionIds, input_sha256: sha256(Buffer.concat([nodeBytes, Buffer.from([0]), edgeBytes])), input_hashes: { node_sha256: sha256(nodeBytes), edge_sha256: edgeSha }, snapshot_at: input.snapshot, source_id: input.source,
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

export function assertDeliveredOfficialArtifacts(built, officialDirectory) {
  // TK-04: copied_sha256 must be the SHA-256 of the DELIVERED bytes (re-read from the output directory),
  // never the staging/source path hash. artifact_sha256 stays the source hash; both must agree for an exact byte copy.
  for (const city of built) {
    for (const layer of [city.official_evidence.facility?.display_layer, city.official_evidence.hazard?.display_layer]) {
      if (!layer) continue;
      const deliveredPath = join(officialDirectory, layer.data_path.replace("./data/official/", ""));
      const actual = hash(deliveredPath);
      if (actual !== layer.artifact_sha256) throw new Error(`${city.city_id} official delivered byte SHA-256 mismatch: expected ${layer.artifact_sha256}, got ${actual}`);
      layer.copied_sha256 = actual;
    }
  }
  return built;
}

export function buildMapArtifacts({ repoRoot, outputRoot, officialEvidenceOverride, m7EvidenceOverride }) {
  const root = repoRoot instanceof URL ? fileURLToPath(repoRoot) : resolve(repoRoot); const output = outputRoot instanceof URL ? fileURLToPath(outputRoot) : resolve(outputRoot);
  const built = CITY_INPUTS.map((input) => { const official_evidence = readOfficialEvidence(root, input.id, officialEvidenceOverride, m7EvidenceOverride); const m7_readiness = json(join(root, "reports", "M7_ALL_EDGE_EVIDENCE_READINESS.json")).edges.filter((edge) => edge.city_id === input.id); return { ...artifact(root, input), official_evidence, m7_readiness }; }); mkdirSync(output, { recursive: true });
  for (const city of built) {
    const deliveredPath = join(output, `${city.city_id}.candidate_edges.geojson`);
    writeFileSync(deliveredPath, city.edgeBytes);
    city.real_2d.copied_sha256 = hash(deliveredPath);
  }
  const officialDirectory = join(dirname(output), "official"); mkdirSync(officialDirectory, { recursive: true });
  const parityRoot = join(root, "inputs", "staging", "KYOTO-OFFICIAL-PARITY-V1");
  for (const filename of ["a31b_kiyomizu_gion_display.geojson", "a31b_arashiyama_display.geojson", "facility_points_kiyomizu_gion.geojson", "facility_points_arashiyama.geojson"]) {
    copyFileSync(join(parityRoot, filename), join(officialDirectory, filename));
  }
  assertDeliveredOfficialArtifacts(built, officialDirectory);
  const analysisDirectory = join(dirname(output), "analysis"); mkdirSync(analysisDirectory, { recursive: true });
  for (const city of built) writeFileSync(join(analysisDirectory, `${city.city_id}.json`), `${JSON.stringify(analysisFor(city), null, 2)}\n`);
  const catalog = { viewer_map_schema_version: "2.0.0", generated_from: "HASH_VERIFIED_CITY_ARTIFACTS", cities: built.map(({ edgeBytes, edgeData, source_artifact_ids, source_revision_ids, input_sha256, input_hashes, snapshot_at, source_id, official_evidence, m7_readiness, ...city }) => city) };
  assertSupportedMapCatalog(catalog); assertDeliveredMapArtifacts(catalog, output); writeFileSync(join(output, "map-layers.json"), `${JSON.stringify(catalog, null, 2)}\n`);
  return { files: [...built.map((city) => join(output, `${city.city_id}.candidate_edges.geojson`)), ...["a31b_kiyomizu_gion_display.geojson", "a31b_arashiyama_display.geojson", "facility_points_kiyomizu_gion.geojson", "facility_points_arashiyama.geojson"].map((filename) => join(officialDirectory, filename)), join(output, "map-layers.json")] };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) buildMapArtifacts({ repoRoot: resolve(".."), outputRoot: resolve("public/data/maps") });
