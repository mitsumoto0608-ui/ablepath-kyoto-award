import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import { assertSupportedMapCatalog, computeGeoJsonBounds } from "../src/mapDomain.mjs";

const EXPECTED_EDGE_SHA = "73e4f2d6965be2c8bb7a13229b4352fdef6886510219ebf9855d9581bbc3da7b";
const EXPECTED_CORRIDOR_SHA = "48b08553a9c2d7f8388bd893e83133287e01ad2efa9326116f5e8d3a31836dc7";
const EXPECTED_SOURCE_SHA = "3d21ce674776c5c3e37c507c09a9458e062d2d31f5718b3e702313838ef7d2ec";
const EXPECTED_QUERY_SHA = "f32964329548d7d715c79cf05da6a28a7ac8230781acc4852f9174ba9f4dfb7b";
const EXPECTED_TOPOLOGY_SHA = "ea6a7b9257dd49147076af0bdec36a5ce189b87ce87ef1b763574d5b4ae9bb4e";
const EXPECTED_MANIFEST_SHA = "e83176c1396c3fd13001f3730f7017cd28bcfd2576c90104b971d401f83eb958";
const EXPECTED_PLATEAU_METADATA_SHA = "2a1e4c71370f58f0f40dc8b6eb9ae120b7f694b6caca1260a8a0efbbfeda78d3";
const EXPECTED_PLATEAU_RESPONSE_SHA = "ce58a92bb9da595d9251cd72b7b77af6da9a3748628a0e8370ffc6fbc6312242";
const EXPECTED_PLATEAU_QUERY_SHA = "eb9400f69b5ee88b802e972f426b4ff624ab759fe372776f67ecd83978221e40";

function asPath(value) {
  return value instanceof URL ? fileURLToPath(value) : resolve(value);
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function assertHash(bytes, expected, label) {
  const actual = sha256(bytes);
  if (actual !== expected) throw new Error(`${label} SHA-256 mismatch: expected ${expected}, got ${actual}`);
  return actual;
}

function assertCandidateGraph(geojson, topology) {
  if (geojson.type !== "FeatureCollection" || geojson.features?.length !== 19) throw new Error("Kiyomizu candidate graph must contain exactly 19 reviewed-source edges");
  for (const feature of geojson.features) {
    const properties = feature?.properties;
    if (
      properties?.data_class !== "REAL"
      || properties?.geometry_status !== "SOURCE_TRACEABLE_REAL"
      || properties?.topology_status !== "CANDIDATE"
      || properties?.accessibility_state !== "UNKNOWN"
      || properties?.operation_status !== "UNKNOWN"
    ) {
      throw new Error(`candidate edge ${properties?.edge_id ?? "unknown"} violates the REAL/CANDIDATE/UNKNOWN display contract`);
    }
  }
  if (
    topology?.counts?.candidate_edge_count !== 19
    || topology?.counts?.candidate_node_count !== 21
    || topology?.counts?.connected_components !== 2
    || topology?.topology_status !== "CANDIDATE_REVIEW_REQUIRED"
    || topology?.route_continuity !== "NOT_ESTABLISHED"
  ) {
    throw new Error("Kiyomizu topology QA no longer matches the reviewed candidate contract");
  }
}

export function buildMapArtifacts({ repoRoot, outputRoot }) {
  const root = asPath(repoRoot);
  const output = asPath(outputRoot);
  const cityRoot = join(root, "cities", "kyoto_kiyomizu");
  const edgePath = join(cityRoot, "graph", "real", "candidate_edges.geojson");
  const corridorPath = join(cityRoot, "geography", "real", "corridor.osm.geojson");
  const topologyPath = join(cityRoot, "graph", "real", "topology_qa.json");
  const manifestPath = join(cityRoot, "realdata", "artifact_manifest.v2.json");
  const plateauPath = join(cityRoot, "sources", "plateau_26100_metadata.json");
  const plateauResponsePath = join(cityRoot, "sources", "retained", "plateau_26100_bldg_tileset_20260830.json");
  const plateauQueryPath = join(cityRoot, "sources", "queries", "plateau_26100_bldg_tileset_url.txt");
  for (const path of [edgePath, corridorPath, topologyPath, manifestPath, plateauPath, plateauResponsePath, plateauQueryPath]) {
    if (!existsSync(path)) throw new Error(`configured Kiyomizu map artifact is missing: ${path}`);
  }

  const edgeBytes = readFileSync(edgePath);
  const corridorBytes = readFileSync(corridorPath);
  const edgeSha = assertHash(edgeBytes, EXPECTED_EDGE_SHA, "candidate edge artifact");
  const corridorSha = assertHash(corridorBytes, EXPECTED_CORRIDOR_SHA, "corridor artifact");
  const topologySha = assertHash(readFileSync(topologyPath), EXPECTED_TOPOLOGY_SHA, "topology QA artifact");
  const manifestSha = assertHash(readFileSync(manifestPath), EXPECTED_MANIFEST_SHA, "artifact manifest");
  const plateauMetadataSha = assertHash(readFileSync(plateauPath), EXPECTED_PLATEAU_METADATA_SHA, "PLATEAU metadata");
  const plateauResponseSha = assertHash(readFileSync(plateauResponsePath), EXPECTED_PLATEAU_RESPONSE_SHA, "retained PLATEAU response");
  const plateauQuerySha = assertHash(readFileSync(plateauQueryPath), EXPECTED_PLATEAU_QUERY_SHA, "retained PLATEAU query");
  const geojson = JSON.parse(edgeBytes.toString("utf8"));
  const topology = readJson(topologyPath);
  const manifest = readJson(manifestPath);
  const plateau = readJson(plateauPath);
  assertCandidateGraph(geojson, topology);

  const corridorRows = manifest.artifacts?.filter((entry) => entry.artifact_path === "geography/real/corridor.osm.geojson") ?? [];
  if (
    manifest.schema_version !== "2.0.0"
    || manifest.city_id !== "kyoto_kiyomizu"
    || corridorRows.length !== 17
    || corridorRows.some((row) => row.sha256 !== corridorSha || row.source_sha256 !== EXPECTED_SOURCE_SHA || row.retrieval_query_sha256 !== EXPECTED_QUERY_SHA)
  ) {
    throw new Error("Kiyomizu corridor manifest does not bind the reviewed source/query/artifact hashes");
  }
  if (
    plateau.city_id !== "kyoto_kiyomizu"
    || plateau.data_class !== "OFFICIAL_METADATA_ONLY"
    || plateau.source_class !== "OFFICIAL"
    || plateau.plateau_3d_connected !== false
    || plateau.height_attribute_extracted !== false
    || plateau.retained_response_sha256 !== plateauResponseSha
    || plateau.query_sha256 !== plateauQuerySha
  ) {
    throw new Error("PLATEAU metadata must remain metadata-only and disconnected");
  }

  mkdirSync(output, { recursive: true });
  const copiedName = "kyoto_kiyomizu.candidate_edges.geojson";
  const copiedPath = join(output, copiedName);
  writeFileSync(copiedPath, edgeBytes);
  const copiedSha = assertHash(readFileSync(copiedPath), edgeSha, "copied candidate edge artifact");

  const catalog = {
    viewer_map_schema_version: "1.1.0",
    generated_from: "HASH_VERIFIED_CITY_ARTIFACTS",
    cities: [
      {
        city_id: "kyoto_kiyomizu",
        real_2d: {
          data_path: `./data/maps/${copiedName}`,
          artifact_sha256: edgeSha,
          copied_sha256: copiedSha,
          corridor_sha256: corridorSha,
          source_sha256: EXPECTED_SOURCE_SHA,
          query_sha256: EXPECTED_QUERY_SHA,
          topology_sha256: topologySha,
          manifest_sha256: manifestSha,
          source_id: topology.source_id,
          source_class: "VGI",
          data_class: "REAL",
          geometry_status: "SOURCE_TRACEABLE_REAL",
          topology_status: topology.topology_status,
          route_continuity: topology.route_continuity,
          snapshot_at: corridorRows[0].snapshot_at,
          feature_count: geojson.features.length,
          bounds: computeGeoJsonBounds(geojson),
          license: corridorRows[0].license,
          license_url: corridorRows[0].license_terms_url,
          copyright_url: "https://www.openstreetmap.org/copyright",
          attribution: "© OpenStreetMap contributors / Data available under ODbL 1.0",
          lineage: [
            `artifact:${edgeSha}`,
            `corridor:${corridorSha}`,
            `source:${EXPECTED_SOURCE_SHA}`,
            `query:${EXPECTED_QUERY_SHA}`,
          ],
        },
        cesium: {
          available: true,
          data_class: "OFFICIAL_METADATA_ONLY",
          source_id: plateau.source_id,
          source_class: plateau.source_class,
          accessed_at: plateau.accessed_at,
          valid_as_of: plateau.valid_as_of,
          valid_as_of_reason: plateau.valid_as_of_reason,
          lod: "LOD2",
          tileset_url: plateau.higashiyama_building_lod2_tileset_url,
          license: plateau.license,
          license_url: plateau.license_terms_url,
          attribution: "出典：国土交通省 3D都市モデル（Project PLATEAU）京都市2025 / PDL1.0",
          connected: false,
          requires_commercial_token: false,
          metadata_sha256: plateauMetadataSha,
          retained_response_sha256: plateauResponseSha,
          query_sha256: plateauQuerySha,
        },
      },
      { city_id: "kyoto_arashiyama", real_2d: null, cesium: null },
      { city_id: "fujisawa_enoshima", real_2d: null, cesium: null },
    ],
  };
  assertSupportedMapCatalog(catalog);
  const catalogPath = join(output, "map-layers.json");
  writeFileSync(catalogPath, `${JSON.stringify(catalog, null, 2)}\n`, "utf8");
  return { catalog, files: [copiedPath, catalogPath] };
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : "";
if (import.meta.url === invokedPath) {
  const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
  const outputRoot = join(repoRoot, "viewer", "public", "data", "maps");
  const result = buildMapArtifacts({ repoRoot, outputRoot });
  process.stdout.write(`Built ${result.files.length} deterministic map artifacts.\n`);
}
