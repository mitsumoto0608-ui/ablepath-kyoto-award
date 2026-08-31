import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
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
const M7_FIELDS = ["clear_width_m", "building_height_m", "setback_m", "damage_state", "debris_present", "variant", "official_closure", "hazard_data_status"];

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
  const result = { topology: { node_count: nodes.length, edge_count: edges.length, connected_components: components.length, topology_status: "CANDIDATE_REVIEW_REQUIRED" }, selectable_node_ids: selectableNodeIds, path_matrix: pathMatrix, path_fixture: pathFixture, hazard_overlap: { status: "NOT_CONNECTED", value: null, reason: "No trusted official hazard geometry is connected; no closure is derived." }, m7: { status: "NOT_COMPUTED", ready_edge_count: 0, computed_edge_count: 0, readiness: edges.map((edge) => ({ edge_id: edge.edge_id, status: "NOT_COMPUTED", m7_result: null, missing_fields: M7_FIELDS.filter((field) => edge[field] === null || edge[field] === undefined || edge[field] === "UNKNOWN"), reason: "Required source-traceable M7 inputs are incomplete." })) }, m6: { status: "NOT_COMPUTED", reason: "M6/profile evaluation is not connected." } };
  return { analysis_id: `${city.city_id}:candidate-topology-v2`, analysis_type: "CANDIDATE_TOPOLOGY_STATIC_FIXTURE", city_id: city.city_id, source_artifact_ids: city.source_artifact_ids, source_revision_ids: city.source_revision_ids, input_sha256: city.input_sha256, algorithm: "deterministic-undirected-dijkstra-coordinate-degree", algorithm_version: "2.0.0", parameters: { coordinate_unit: "coordinate_degree", input_binding: "sha256(node_geojson_bytes + 0x00 + edge_geojson_bytes); input order=node,edge", tie_break: "lexical ordered edge-ID tuple" }, generated_at: city.snapshot_at, deterministic: true, result, limitations: ["Candidate connectivity only", "coordinate_degree is not a geographic or meter distance", "Hazard, M7, M6, accessibility, safety, operation, and administrative validation are unconnected or not computed"], provenance: { source_class: "VGI", source_id: city.source_id, input_binding: "node bytes then NUL then edge bytes", input_artifacts: city.source_artifact_ids, input_hashes: city.input_hashes }, safety_claim: false, accessibility_claim: false, admin_validated: false, ...result, interpretation: "Candidate network connectivity only; accessibility, safety, and operation are unconfirmed." };
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
    real_2d: { data_path: dataPath, artifact_sha256: edgeSha, copied_sha256: edgeSha, corridor_sha256: hash(paths.corridor), source_sha256: input.id === "kyoto_kiyomizu" ? "3d21ce674776c5c3e37c507c09a9458e062d2d31f5718b3e702313838ef7d2ec" : input.id === "kyoto_arashiyama" ? "1cde93d68bebf633989e825cbd5ac1e772cee81508043f44beb311250a1e8013" : "c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04", query_sha256: input.id === "kyoto_kiyomizu" ? "f32964329548d7d715c79cf05da6a28a7ac8230781acc4852f9174ba9f4dfb7b" : input.id === "kyoto_arashiyama" ? "b5c52b3ea7542261159b5764956aa9662673c0422b3509dc59e4866f00c14603" : "c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04", topology_sha256: topologySha, manifest_sha256: manifestSha, source_id: input.source, source_class: "VGI", data_class: "REAL", geometry_status: "SOURCE_TRACEABLE_REAL", topology_status: "CANDIDATE_REVIEW_REQUIRED", route_continuity: "NOT_ESTABLISHED", snapshot_at: input.snapshot, feature_count: edgeData.features.length, bounds: computeGeoJsonBounds(edgeData), license: "Open Data Commons Open Database License (ODbL) 1.0", license_url: "https://opendatacommons.org/licenses/odbl/1-0/", copyright_url: "https://www.openstreetmap.org/copyright", attribution: "© OpenStreetMap contributors / Data available under ODbL 1.0", lineage: [`artifact:${edgeSha}`, `corridor:${hash(paths.corridor)}`, `topology:${topologySha}`, `manifest:${manifestSha}`, `manifest_schema:${manifest.schema_version ?? "unknown"}`] },
    cesium: input.id === "kyoto_kiyomizu" ? { available: true, data_class: "OFFICIAL_METADATA_ONLY", source_id: "plateau_26100_bldg_maxlod2_latest_20260830", source_class: "OFFICIAL", accessed_at: "2026-08-30", valid_as_of: null, valid_as_of_reason: "Latest endpoint is dynamic; retained ETag response must be rechecked", lod: "LOD2", tileset_url: "https://assets.cms.plateau.reearth.io/assets/25/dd4c50-5342-4a0b-ac51-05ffb138b8b5/26100_kyoto-shi_city_2025_citygml_1_op_bldg_3dtiles_26105_higashiyama-ku_lod2/tileset.json", license: "Public Data License 1.0 (PDL1.0), CC BY 4.0 compatible", license_url: "https://www.mlit.go.jp/plateau/site-policy/", attribution: "出典：国土交通省 3D都市モデル（Project PLATEAU）京都市2025 / PDL1.0", connected: false, requires_commercial_token: false, metadata_sha256: "2a1e4c71370f58f0f40dc8b6eb9ae120b7f694b6caca1260a8a0efbbfeda78d3", retained_response_sha256: "ce58a92bb9da595d9251cd72b7b77af6da9a3748628a0e8370ffc6fbc6312242", query_sha256: "eb9400f69b5ee88b802e972f426b4ff624ab759fe372776f67ecd83978221e40" } : null,
    edgeData, source_artifact_ids: sourceArtifactIds, source_revision_ids: sourceRevisionIds, input_sha256: sha256(Buffer.concat([nodeBytes, Buffer.from([0]), edgeBytes])), input_hashes: { node_sha256: sha256(nodeBytes), edge_sha256: edgeSha }, snapshot_at: input.snapshot, source_id: input.source,
  };
}

export function buildMapArtifacts({ repoRoot, outputRoot }) {
  const root = repoRoot instanceof URL ? fileURLToPath(repoRoot) : resolve(repoRoot); const output = outputRoot instanceof URL ? fileURLToPath(outputRoot) : resolve(outputRoot);
  const built = CITY_INPUTS.map((input) => artifact(root, input)); mkdirSync(output, { recursive: true });
  for (const city of built) writeFileSync(join(output, `${city.city_id}.candidate_edges.geojson`), `${JSON.stringify(city.edgeData, null, 2)}\n`);
  const analysisDirectory = join(dirname(output), "analysis"); mkdirSync(analysisDirectory, { recursive: true });
  for (const city of built) writeFileSync(join(analysisDirectory, `${city.city_id}.json`), `${JSON.stringify(analysisFor(city), null, 2)}\n`);
  const catalog = { viewer_map_schema_version: "2.0.0", generated_from: "HASH_VERIFIED_CITY_ARTIFACTS", cities: built.map(({ edgeData, source_artifact_ids, source_revision_ids, input_sha256, input_hashes, snapshot_at, source_id, ...city }) => city) };
  assertSupportedMapCatalog(catalog); writeFileSync(join(output, "map-layers.json"), `${JSON.stringify(catalog, null, 2)}\n`);
  return { files: [...built.map((city) => join(output, `${city.city_id}.candidate_edges.geojson`)), join(output, "map-layers.json")] };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) buildMapArtifacts({ repoRoot: resolve(".."), outputRoot: resolve("public/data/maps") });
