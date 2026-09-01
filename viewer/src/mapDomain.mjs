const MAP_SCHEMA_VERSION = "2.0.0";
const CITY_IDS = new Set(["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"]);
const CITY_REAL_CONTRACTS = {
  kyoto_kiyomizu: {
  artifact_sha256: "73e4f2d6965be2c8bb7a13229b4352fdef6886510219ebf9855d9581bbc3da7b",
  copied_sha256: "73e4f2d6965be2c8bb7a13229b4352fdef6886510219ebf9855d9581bbc3da7b",
  corridor_sha256: "48b08553a9c2d7f8388bd893e83133287e01ad2efa9326116f5e8d3a31836dc7",
  source_sha256: "3d21ce674776c5c3e37c507c09a9458e062d2d31f5718b3e702313838ef7d2ec",
  query_sha256: "f32964329548d7d715c79cf05da6a28a7ac8230781acc4852f9174ba9f4dfb7b",
  topology_sha256: "ea6a7b9257dd49147076af0bdec36a5ce189b87ce87ef1b763574d5b4ae9bb4e",
  manifest_sha256: "e83176c1396c3fd13001f3730f7017cd28bcfd2576c90104b971d401f83eb958",
  source_id: "openstreetmap_kiyomizu_named_corridor_20260830",
  },
  kyoto_arashiyama: {
    artifact_sha256: "b8df66f59b5baefc0ba9dbd7d197546a4c93b0efa51f273d7ac465d832e08285", copied_sha256: "b8df66f59b5baefc0ba9dbd7d197546a4c93b0efa51f273d7ac465d832e08285",
    corridor_sha256: "81c727646b27ad33af0bc19c23bbe0d2e8465c6150ee6335b15214f55af18334", source_sha256: "1cde93d68bebf633989e825cbd5ac1e772cee81508043f44beb311250a1e8013", query_sha256: "b5c52b3ea7542261159b5764956aa9662673c0422b3509dc59e4866f00c14603",
    topology_sha256: "9a4cbc52a246eab14d4494903904457a33704954774d4558d2b2b1c000a75cc1", manifest_sha256: "c1f672d78e5184fdd74112b55e299abdcfcd015aefbd4738f194a45bb1327d67",
    source_id: "openstreetmap-overpass-arashiyama-20260829",
  },
  fujisawa_enoshima: {
    artifact_sha256: "630c2dbb74845b0ad30b064168b03d361115ed20955b325fb8f58b91034a0c47", copied_sha256: "630c2dbb74845b0ad30b064168b03d361115ed20955b325fb8f58b91034a0c47",
    corridor_sha256: "01eae54bac6385da4aa5d39c92c935fc25dc799e91be37b030943c1ae5016c32", source_sha256: "c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04", query_sha256: "c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04",
    topology_sha256: "1e89091d688b6ae3a0afa9ff7722e0b8210de9b0bb45c967e30b798b6088f516", manifest_sha256: "72f5ec956d935d2b0d6961275844eef5296a9642617f6f8b04acb9a4648dfb7e",
    source_id: "OSM_CANDIDATE_SOURCE",
  },
};
const REVIEWED_PLATEAU_HASHES = {
  metadata_sha256: "2a1e4c71370f58f0f40dc8b6eb9ae120b7f694b6caca1260a8a0efbbfeda78d3",
  retained_response_sha256: "ce58a92bb9da595d9251cd72b7b77af6da9a3748628a0e8370ffc6fbc6312242",
  query_sha256: "eb9400f69b5ee88b802e972f426b4ff624ab759fe372776f67ecd83978221e40",
};
const REAL_2D_FIELDS = [
  "data_path", "artifact_sha256", "copied_sha256", "corridor_sha256", "source_sha256",
  "query_sha256", "topology_sha256", "manifest_sha256", "source_id", "source_class", "data_class", "geometry_status",
  "topology_status", "route_continuity", "snapshot_at", "feature_count", "bounds",
  "license", "license_url", "copyright_url", "attribution", "lineage",
];
const CESIUM_FIELDS = [
  "available", "data_class", "source_id", "source_class", "accessed_at", "valid_as_of",
  "valid_as_of_reason", "lod", "tileset_url", "license", "license_url", "attribution",
  "connected", "requires_commercial_token", "metadata_sha256", "retained_response_sha256", "query_sha256",
];

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactKeys(value, expected, path) {
  if (!isRecord(value)) throw new Error(`${path} must be an object`);
  const actual = Object.keys(value);
  const missing = expected.filter((key) => !(key in value));
  const extra = actual.filter((key) => !expected.includes(key));
  if (missing.length || extra.length) {
    throw new Error(`${path} keys must be exact; missing=${missing.join(",") || "none"}; extra=${extra.join(",") || "none"}`);
  }
}

function nonEmptyString(value, path) {
  if (typeof value !== "string" || value.trim() === "" || value.length > 4_000) {
    throw new Error(`${path} must be a non-empty bounded string`);
  }
}

function sha256(value, path) {
  if (typeof value !== "string" || !/^[a-f0-9]{64}$/.test(value)) throw new Error(`${path} must be a lowercase SHA-256`);
}

function isoDate(value, path) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error(`${path} must be an ISO date`);
}

function validateBounds(bounds, path) {
  if (!Array.isArray(bounds) || bounds.length !== 2) throw new Error(`${path} must contain southwest and northeast coordinates`);
  const flat = bounds.flat();
  if (flat.length !== 4 || flat.some((value) => typeof value !== "number" || !Number.isFinite(value))) {
    throw new Error(`${path} must contain finite coordinates`);
  }
  const [[west, south], [east, north]] = bounds;
  if (west < -180 || east > 180 || south < -90 || north > 90 || west >= east || south >= north) {
    throw new Error(`${path} must be ordered EPSG:4326 longitude/latitude bounds`);
  }
}

function validateReal2d(layer, cityId) {
  exactKeys(layer, REAL_2D_FIELDS, `${cityId}.real_2d`);
  for (const field of ["artifact_sha256", "copied_sha256", "corridor_sha256", "source_sha256", "query_sha256", "topology_sha256", "manifest_sha256"]) {
    sha256(layer[field], `${cityId}.real_2d.${field}`);
  }
  if (layer.artifact_sha256 !== layer.copied_sha256) throw new Error(`${cityId}.real_2d copied bytes do not match the source artifact`);
  const contract = CITY_REAL_CONTRACTS[cityId];
  if (!contract) throw new Error(`${cityId}.real_2d has no exact allowlist contract`);
  for (const [field, expected] of Object.entries(contract)) {
    if (expected !== null && layer[field] !== expected) throw new Error(`${cityId}.real_2d.${field} is not the exact allowlisted artifact value`);
  }
  for (const field of ["data_path", "source_id", "license", "license_url", "copyright_url", "attribution"]) nonEmptyString(layer[field], `${cityId}.real_2d.${field}`);
  if (!/^\.\/data\/maps\/[A-Za-z0-9_.-]+\.geojson$/.test(layer.data_path)) throw new Error(`${cityId}.real_2d.data_path must remain same-origin and confined`);
  if (layer.source_class !== "VGI" || layer.data_class !== "REAL" || layer.geometry_status !== "SOURCE_TRACEABLE_REAL") {
    throw new Error(`${cityId}.real_2d provenance classes are unsupported`);
  }
  if (
    layer.source_id !== contract.source_id
    || layer.license !== "Open Data Commons Open Database License (ODbL) 1.0"
    || layer.license_url !== "https://opendatacommons.org/licenses/odbl/1-0/"
    || layer.copyright_url !== "https://www.openstreetmap.org/copyright"
    || layer.attribution !== "© OpenStreetMap contributors / Data available under ODbL 1.0"
  ) {
    throw new Error(`${cityId}.real_2d source and license identity must match the allowlisted OSM artifact`);
  }
  if (layer.topology_status !== "CANDIDATE_REVIEW_REQUIRED" || layer.route_continuity !== "NOT_ESTABLISHED") {
    throw new Error(`${cityId}.real_2d must not promote candidate topology or route continuity`);
  }
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(layer.snapshot_at)) throw new Error(`${cityId}.real_2d.snapshot_at must be a UTC timestamp`);
  if (!Number.isInteger(layer.feature_count) || layer.feature_count <= 0 || layer.feature_count > 2_000) throw new Error(`${cityId}.real_2d.feature_count is invalid`);
  validateBounds(layer.bounds, `${cityId}.real_2d.bounds`);
  if (!Array.isArray(layer.lineage) || layer.lineage.length === 0) throw new Error(`${cityId}.real_2d.lineage must be non-empty`);
  layer.lineage.forEach((entry, index) => nonEmptyString(entry, `${cityId}.real_2d.lineage[${index}]`));
}

function validateCesium(layer, cityId) {
  exactKeys(layer, CESIUM_FIELDS, `${cityId}.cesium`);
  if (typeof layer.available !== "boolean" || typeof layer.connected !== "boolean" || typeof layer.requires_commercial_token !== "boolean") {
    throw new Error(`${cityId}.cesium flags must be boolean`);
  }
  if (layer.data_class !== "OFFICIAL_METADATA_ONLY" || layer.source_class !== "OFFICIAL") throw new Error(`${cityId}.cesium must remain official metadata only`);
  if (layer.connected !== false || layer.requires_commercial_token !== false) throw new Error(`${cityId}.cesium must remain disconnected and token-free in static truth`);
  for (const field of ["metadata_sha256", "retained_response_sha256", "query_sha256"]) sha256(layer[field], `${cityId}.cesium.${field}`);
  for (const [field, expected] of Object.entries(REVIEWED_PLATEAU_HASHES)) {
    if (layer[field] !== expected) throw new Error(`${cityId}.cesium.${field} is not the reviewed artifact hash`);
  }
  for (const field of ["source_id", "lod", "tileset_url", "license", "license_url", "attribution", "valid_as_of_reason"]) {
    nonEmptyString(layer[field], `${cityId}.cesium.${field}`);
  }
  isoDate(layer.accessed_at, `${cityId}.cesium.accessed_at`);
  if (layer.valid_as_of !== null) throw new Error(`${cityId}.cesium.valid_as_of must remain null for the dynamic endpoint`);
  const url = new URL(layer.tileset_url);
  if (url.protocol !== "https:" || url.hostname !== "assets.cms.plateau.reearth.io") throw new Error(`${cityId}.cesium.tileset_url is outside the reviewed PLATEAU host`);
  if (
    layer.source_id !== "plateau_26100_bldg_maxlod2_latest_20260830"
    || layer.license !== "Public Data License 1.0 (PDL1.0), CC BY 4.0 compatible"
    || layer.license_url !== "https://www.mlit.go.jp/plateau/site-policy/"
    || layer.attribution !== "出典：国土交通省 3D都市モデル（Project PLATEAU）京都市2025 / PDL1.0"
  ) {
    throw new Error(`${cityId}.cesium source and license identity must match the reviewed PLATEAU metadata`);
  }
}

export function assertSupportedMapCatalog(catalog) {
  exactKeys(catalog, ["viewer_map_schema_version", "generated_from", "cities"], "map catalog");
  if (catalog.viewer_map_schema_version !== MAP_SCHEMA_VERSION) throw new Error(`unsupported viewer_map_schema_version: ${String(catalog.viewer_map_schema_version)}`);
  if (catalog.generated_from !== "HASH_VERIFIED_CITY_ARTIFACTS") throw new Error(`unsupported map catalog provenance: ${String(catalog.generated_from)}`);
  if (!Array.isArray(catalog.cities) || catalog.cities.length !== CITY_IDS.size) throw new Error("map catalog must contain exactly the three viewer cities");
  const seen = new Set();
  for (const city of catalog.cities) {
    exactKeys(city, ["city_id", "real_2d", "cesium"], "map city");
    if (!CITY_IDS.has(city.city_id) || seen.has(city.city_id)) throw new Error(`unsupported or duplicate map city ${String(city.city_id)}`);
    seen.add(city.city_id);
    if (city.real_2d !== null) validateReal2d(city.real_2d, city.city_id);
    if (city.cesium !== null) validateCesium(city.cesium, city.city_id);
  }
  return catalog;
}

export async function loadMapCatalog(fetchImpl, url = "./data/maps/map-layers.json", timeoutMs = 5_000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetchImpl(url, { signal: controller.signal });
    if (!response?.ok) throw new Error(`map catalog request failed: HTTP ${response?.status ?? "unknown"}`);
    return assertSupportedMapCatalog(await response.json());
  } catch (error) {
    if (error?.name === "AbortError") throw new Error(`map catalog request timed out after ${timeoutMs} ms`);
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

export function mapConfigForCity(catalog, cityId) {
  return catalog.cities.find((city) => city.city_id === cityId) ?? null;
}

// Static catalog metadata is deliberately not sufficient to make a network
// capability claim. Gate 8 requires a separate reviewed receipt for the root,
// child availability, CORS, and the target AOI before the Cesium runtime may
// request an official tileset.
export function isVerifiedCesiumConnection(layer) {
  return Boolean(
    layer
    && layer.connected === true
    && layer.data_class === "OFFICIAL_REMOTE_TILESET"
    && layer.connection_receipt_sha256,
  );
}

export function selectInitialMapMode(catalog, cityId, search = "") {
  const requested = new URLSearchParams(search).get("layer");
  const realAvailable = Boolean(mapConfigForCity(catalog, cityId)?.real_2d);
  if (requested === "real" && realAvailable) return "real";
  return "synthetic";
}

export function computeGeoJsonBounds(geojson) {
  if (!isRecord(geojson) || geojson.type !== "FeatureCollection" || !Array.isArray(geojson.features) || geojson.features.length === 0) {
    throw new Error("GeoJSON must be a non-empty FeatureCollection");
  }
  let west = Infinity;
  let south = Infinity;
  let east = -Infinity;
  let north = -Infinity;
  for (const feature of geojson.features) {
    if (feature?.geometry?.type !== "LineString" || !Array.isArray(feature.geometry.coordinates) || feature.geometry.coordinates.length < 2) {
      throw new Error("map artifact must contain non-empty LineString features");
    }
    for (const coordinate of feature.geometry.coordinates) {
      if (!Array.isArray(coordinate) || coordinate.length < 2 || !coordinate.slice(0, 2).every(Number.isFinite)) throw new Error("map artifact contains an invalid coordinate");
      const [longitude, latitude] = coordinate;
      if (longitude < -180 || longitude > 180 || latitude < -90 || latitude > 90) throw new Error("map artifact coordinate is outside EPSG:4326 bounds");
      west = Math.min(west, longitude);
      south = Math.min(south, latitude);
      east = Math.max(east, longitude);
      north = Math.max(north, latitude);
    }
  }
  const bounds = [[west, south], [east, north]];
  validateBounds(bounds, "GeoJSON bounds");
  return bounds;
}
