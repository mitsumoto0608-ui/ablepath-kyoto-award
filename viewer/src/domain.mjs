export const SUPPORTED_VIEWER_MAJOR = 1;

const MAX_PAYLOAD_BYTES = 2_000_000;
const MAX_CITIES = 20;
const MAX_SOURCES_PER_CITY = 100;
const MAX_SCENARIOS_PER_CITY = 50;
const MAX_EDGES_PER_CITY = 2_000;
const MAX_POINTS_PER_EDGE = 1_000;
const SVG_BOUNDS = { minX: 0, maxX: 1000, minY: 0, maxY: 620 };

const DATA_CLASSES = new Set(["OFFICIAL_METADATA_ONLY", "VGI_METADATA_ONLY", "SYNTHETIC_DEMO", "UNKNOWN"]);
const CITY_DATA_STATUSES = new Set(["REAL", "METADATA_ONLY", "MIXED", "SYNTHETIC_DEMO", "UNKNOWN"]);
const MAP_STATUSES = new Set(["REAL", "MODEL_DERIVED", "SYNTHETIC_DEMO", "UNKNOWN"]);
const EDGE_STATES = new Set(["PASS", "CONDITIONAL", "FAIL", "UNKNOWN"]);
const HAZARD_DATA_STATUSES = new Set(["KNOWN", "UNKNOWN"]);
const HAZARD_OVERLAPS = new Set(["OVERLAP", "NO_OVERLAP", "UNKNOWN"]);
const OFFICIAL_METADATA_STATUSES = new Set(["OFFICIAL_METADATA_ONLY", "UNKNOWN"]);
const SOURCE_STATUSES = new Set(["CURRENT_CONFIRMED", "CURRENT_UNVERIFIED", "POSSIBLY_STALE", "SUPERSEDED", "UNKNOWN"]);
const HAZARD_TYPES = new Set(["EARTHQUAKE", "FLOOD", "TSUNAMI", "UNKNOWN"]);
const KPI_KEYS = new Set(["physically_reachable", "accommodated", "overflow_waiting", "unreachable", "unknown_affected_upper_bound"]);

const REQUIRED_CITY_FIELDS = [
  "city_id", "display_name", "municipality", "corridor_name", "data_status",
  "profile_status", "profile_reason", "official_metadata_status", "last_verified_at",
  "source_ids", "sources", "facility_status", "facility_reason", "entrance_status",
  "entrance_reason", "capacity_status", "capacity_reason", "operation_status",
  "operation_reason", "demand_status", "demand_reason", "origin_status", "origin_reason",
  "kpi_status", "scenarios", "map", "kpis",
];
const SOURCE_FIELDS = ["source_id", "data_class", "last_verified_at", "status", "note"];
const SCENARIO_FIELDS = ["scenario_id", "display_name", "hazard_type", "disclaimer"];
const MAP_FIELDS = ["geometry_status", "edges"];
const EDGE_FIELDS = [
  "edge_id", "points", "display_state", "base_clear_width_m", "remaining_clear_width_m",
  "debris_intrusion_left_m", "debris_intrusion_right_m", "width_reason", "hazard_overlap",
  "max_depth_m", "hazard_reason", "official_closure", "hazard_data_status",
  "evidence_status", "source_ids",
];

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function requireRecord(value, path) {
  if (!isRecord(value)) throw new Error(`${path} must be an object`);
  return value;
}

function requireExactKeys(value, expected, path) {
  requireRecord(value, path);
  const allowed = new Set(expected);
  const actual = Object.keys(value);
  const missing = expected.filter((key) => !(key in value));
  const extra = actual.filter((key) => !allowed.has(key));
  if (missing.length || extra.length) {
    throw new Error(`${path} keys must be exact; missing=${missing.join(",") || "none"}; extra=${extra.join(",") || "none"}`);
  }
}

function requireString(value, path) {
  if (typeof value !== "string" || value.trim() === "" || value.length > 2_000) {
    throw new Error(`${path} must be a non-empty bounded string`);
  }
  return value;
}

function requireId(value, path) {
  const id = requireString(value, path);
  if (!/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$/.test(id)) throw new Error(`${path} must be a stable identifier`);
  return id;
}

function requireEnum(value, allowed, path) {
  if (!allowed.has(value)) throw new Error(`${path} has unsupported value ${String(value)}`);
  return value;
}

function requireIsoDate(value, path) {
  requireString(value, path);
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  const date = match ? new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]))) : null;
  if (!date || date.getUTCFullYear() !== Number(match[1]) || date.getUTCMonth() + 1 !== Number(match[2]) || date.getUTCDate() !== Number(match[3])) {
    throw new Error(`${path} must be an ISO calendar date`);
  }
}

function requireUniqueIds(items, key, path) {
  const seen = new Set();
  for (const item of items) {
    const id = requireId(item?.[key], `${path}.${key}`);
    if (seen.has(id)) throw new Error(`${path} contains duplicate ${key} ${id}`);
    seen.add(id);
  }
  return seen;
}

function requireNullableNonnegativeNumber(value, path) {
  if (value === null) return;
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
    throw new Error(`${path} must be null or a finite non-negative number`);
  }
}

function validateSource(source, cityId) {
  requireExactKeys(source, SOURCE_FIELDS, `city ${cityId} source`);
  requireId(source.source_id, `city ${cityId} source_id`);
  requireEnum(source.data_class, DATA_CLASSES, `city ${cityId} source ${source.source_id}.data_class`);
  requireIsoDate(source.last_verified_at, `city ${cityId} source ${source.source_id}.last_verified_at`);
  requireEnum(source.status, SOURCE_STATUSES, `city ${cityId} source ${source.source_id}.status`);
  requireString(source.note, `city ${cityId} source ${source.source_id}.note`);
  if (source.data_class === "SYNTHETIC_DEMO" && source.status !== "UNKNOWN") throw new Error(`city ${cityId} synthetic source freshness must remain UNKNOWN`);
}

function validateScenario(scenario, cityId) {
  requireExactKeys(scenario, SCENARIO_FIELDS, `city ${cityId} scenario`);
  requireId(scenario.scenario_id, `city ${cityId} scenario_id`);
  requireString(scenario.display_name, `city ${cityId} scenario ${scenario.scenario_id}.display_name`);
  requireEnum(scenario.hazard_type, HAZARD_TYPES, `city ${cityId} scenario ${scenario.scenario_id}.hazard_type`);
  requireString(scenario.disclaimer, `city ${cityId} scenario ${scenario.scenario_id}.disclaimer`);
}

function validateEdge(edge, cityId, sourceIds) {
  requireExactKeys(edge, EDGE_FIELDS, `city ${cityId} edge`);
  requireId(edge.edge_id, `city ${cityId} edge_id`);
  requireEnum(edge.display_state, EDGE_STATES, `edge ${edge.edge_id}.display_state`);
  if (!Array.isArray(edge.points) || edge.points.length < 2 || edge.points.length > MAX_POINTS_PER_EDGE) {
    throw new Error(`edge ${edge.edge_id}.points must contain 2-${MAX_POINTS_PER_EDGE} coordinates`);
  }
  edge.points.forEach((point, index) => {
    if (!Array.isArray(point) || point.length !== 2 || !point.every((value) => typeof value === "number" && Number.isFinite(value))) {
      throw new Error(`edge ${edge.edge_id}.points[${index}] must be a finite [x,y] coordinate`);
    }
    if (point[0] < SVG_BOUNDS.minX || point[0] > SVG_BOUNDS.maxX || point[1] < SVG_BOUNDS.minY || point[1] > SVG_BOUNDS.maxY) {
      throw new Error(`edge ${edge.edge_id}.points[${index}] is outside the declared SVG bounds`);
    }
  });
  if (edge.points.every((point) => point[0] === edge.points[0][0] && point[1] === edge.points[0][1])) {
    throw new Error(`edge ${edge.edge_id}.points must not form a zero-length geometry`);
  }
  for (const field of ["base_clear_width_m", "remaining_clear_width_m", "debris_intrusion_left_m", "debris_intrusion_right_m", "max_depth_m"]) {
    requireNullableNonnegativeNumber(edge[field], `edge ${edge.edge_id}.${field}`);
  }
  requireString(edge.width_reason, `edge ${edge.edge_id}.width_reason`);
  requireEnum(edge.hazard_overlap, HAZARD_OVERLAPS, `edge ${edge.edge_id}.hazard_overlap`);
  requireString(edge.hazard_reason, `edge ${edge.edge_id}.hazard_reason`);
  if (edge.official_closure !== null && typeof edge.official_closure !== "boolean") {
    throw new Error(`edge ${edge.edge_id}.official_closure must be true, false, or null`);
  }
  requireEnum(edge.hazard_data_status, HAZARD_DATA_STATUSES, `edge ${edge.edge_id}.hazard_data_status`);
  requireEnum(edge.evidence_status, DATA_CLASSES, `edge ${edge.edge_id}.evidence_status`);
  if (edge.official_closure === true && edge.display_state === "PASS") {
    throw new Error(`edge ${edge.edge_id} official closure contradicts PASS`);
  }
  if (
    edge.display_state !== "UNKNOWN"
    && (
      edge.hazard_data_status !== "KNOWN"
      || ["UNKNOWN", "OFFICIAL_METADATA_ONLY", "VGI_METADATA_ONLY"].includes(edge.evidence_status)
    )
  ) {
    throw new Error(`edge ${edge.edge_id} cannot promote unknown or metadata-only evidence to ${edge.display_state}`);
  }
  if (!Array.isArray(edge.source_ids) || edge.source_ids.length === 0) throw new Error(`edge ${edge.edge_id}.source_ids must be non-empty`);
  const edgeSourceIds = new Set();
  for (const sourceId of edge.source_ids) {
    requireId(sourceId, `edge ${edge.edge_id}.source_ids`);
    if (edgeSourceIds.has(sourceId)) throw new Error(`edge ${edge.edge_id} contains duplicate source reference ${sourceId}`);
    if (!sourceIds.has(sourceId)) throw new Error(`edge ${edge.edge_id} references unknown source ${sourceId}`);
    edgeSourceIds.add(sourceId);
  }
}

function validateReadiness(city, cityId) {
  for (const prefix of ["facility", "entrance", "capacity", "operation", "demand", "origin"]) {
    if (city[`${prefix}_status`] !== "UNKNOWN") throw new Error(`city ${cityId}.${prefix}_status must remain UNKNOWN until source records are added`);
    requireString(city[`${prefix}_reason`], `city ${cityId}.${prefix}_reason`);
  }
  if (city.profile_status !== "NOT_COMPUTED") throw new Error(`city ${cityId} has an unsupported computed profile state`);
  requireString(city.profile_reason, `city ${cityId}.profile_reason`);
  if (city.kpi_status !== "NOT_COMPUTED") throw new Error(`city ${cityId} has an unsupported computed KPI state`);
}

function validateCity(city) {
  requireExactKeys(city, REQUIRED_CITY_FIELDS, "city");
  const cityId = requireId(city.city_id, "city.city_id");
  for (const field of ["display_name", "municipality", "corridor_name"]) requireString(city[field], `city ${cityId}.${field}`);
  requireEnum(city.official_metadata_status, OFFICIAL_METADATA_STATUSES, `city ${cityId}.official_metadata_status`);
  requireEnum(city.data_status, CITY_DATA_STATUSES, `city ${cityId}.data_status`);
  requireIsoDate(city.last_verified_at, `city ${cityId}.last_verified_at`);
  validateReadiness(city, cityId);

  if (!Array.isArray(city.sources) || city.sources.length === 0 || city.sources.length > MAX_SOURCES_PER_CITY) {
    throw new Error(`city ${cityId} must contain 1-${MAX_SOURCES_PER_CITY} traceable sources`);
  }
  city.sources.forEach((source) => validateSource(source, cityId));
  const sourceIds = requireUniqueIds(city.sources, "source_id", `city ${cityId} sources`);
  if (!Array.isArray(city.source_ids) || city.source_ids.length !== sourceIds.size || new Set(city.source_ids).size !== sourceIds.size || city.source_ids.some((id) => !sourceIds.has(id))) {
    throw new Error(`city ${cityId}.source_ids must exactly match source records`);
  }
  const sourceClasses = new Set(city.sources.map((source) => source.data_class));
  if (city.official_metadata_status === "OFFICIAL_METADATA_ONLY" && !sourceClasses.has("OFFICIAL_METADATA_ONLY")) {
    throw new Error(`city ${cityId} OFFICIAL_METADATA_ONLY status lacks official source provenance`);
  }
  if (city.data_status === "REAL" && !sourceClasses.has("REAL")) throw new Error(`city ${cityId} REAL status lacks REAL provenance`);
  if (city.data_status === "SYNTHETIC_DEMO" && !sourceClasses.has("SYNTHETIC_DEMO")) throw new Error(`city ${cityId} SYNTHETIC_DEMO status lacks synthetic provenance`);
  if (city.data_status === "METADATA_ONLY" && [...sourceClasses].some((value) => !["OFFICIAL_METADATA_ONLY", "UNKNOWN"].includes(value))) {
    throw new Error(`city ${cityId} METADATA_ONLY status conflicts with row provenance`);
  }

  if (!Array.isArray(city.scenarios) || city.scenarios.length === 0 || city.scenarios.length > MAX_SCENARIOS_PER_CITY) {
    throw new Error(`city ${cityId} must contain 1-${MAX_SCENARIOS_PER_CITY} scenarios`);
  }
  city.scenarios.forEach((scenario) => validateScenario(scenario, cityId));
  requireUniqueIds(city.scenarios, "scenario_id", `city ${cityId} scenarios`);

  requireExactKeys(city.map, MAP_FIELDS, `city ${cityId}.map`);
  requireEnum(city.map.geometry_status, MAP_STATUSES, `city ${cityId}.map.geometry_status`);
  if (["REAL", "MODEL_DERIVED"].includes(city.map.geometry_status)) {
    throw new Error(`city ${cityId}.map.geometry_status requires unavailable build-verified provenance`);
  }
  if (!Array.isArray(city.map.edges) || city.map.edges.length > MAX_EDGES_PER_CITY) throw new Error(`city ${cityId}.map.edges exceeds the ${MAX_EDGES_PER_CITY} edge limit`);
  city.map.edges.forEach((edge) => validateEdge(edge, cityId, sourceIds));
  requireUniqueIds(city.map.edges, "edge_id", `city ${cityId} edges`);
  for (const edge of city.map.edges) {
    const matchingClass = edge.source_ids.some((id) => city.sources.find((source) => source.source_id === id)?.data_class === edge.evidence_status);
    if (!matchingClass) throw new Error(`edge ${edge.edge_id} evidence_status lacks matching source provenance`);
  }
  if (city.data_status === "REAL" && (city.map.geometry_status !== "REAL" || city.map.edges.some((edge) => edge.evidence_status !== "REAL"))) {
    throw new Error(`city ${cityId} REAL status conflicts with displayed geometry provenance`);
  }
  if (city.data_status === "SYNTHETIC_DEMO" && (city.map.geometry_status !== "SYNTHETIC_DEMO" || city.map.edges.some((edge) => edge.evidence_status !== "SYNTHETIC_DEMO"))) {
    throw new Error(`city ${cityId} SYNTHETIC_DEMO status conflicts with displayed geometry provenance`);
  }
  if (city.data_status === "MIXED" && sourceClasses.size < 2) throw new Error(`city ${cityId} MIXED status requires multiple provenance classes`);

  requireRecord(city.kpis, `city ${cityId}.kpis`);
  const keys = Object.keys(city.kpis);
  if (keys.length !== KPI_KEYS.size || keys.some((key) => !KPI_KEYS.has(key))) throw new Error(`city ${cityId} must contain the exact five V4 KPI cards`);
  for (const [key, entry] of Object.entries(city.kpis)) {
    requireExactKeys(entry, ["value", "reason"], `city ${cityId} KPI ${key}`);
    if (entry.value !== null && (typeof entry.value !== "number" || !Number.isFinite(entry.value) || entry.value < 0)) {
      throw new Error(`city ${cityId} KPI ${key} value must be null or a finite non-negative number`);
    }
    if (city.kpi_status === "NOT_COMPUTED" && entry.value !== null) {
      throw new Error(`city ${cityId} KPI ${key} must remain null while kpi_status is NOT_COMPUTED`);
    }
    if (entry.value === null) requireString(entry.reason, `city ${cityId} KPI ${key}.reason`);
    else if (entry.reason !== undefined && typeof entry.reason !== "string") throw new Error(`city ${cityId} KPI ${key}.reason must be a string`);
  }
}

export function assertSupportedCatalog(catalog) {
  requireExactKeys(
    catalog,
    ["viewer_data_schema_version", "citypack_schema_version", "generated_from", "cities"],
    "viewer data",
  );
  const version = catalog.viewer_data_schema_version;
  if (typeof version !== "string" || !/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(version)) throw new Error(`invalid viewer_data_schema_version: ${String(version ?? "missing")}`);
  const major = Number(version.split(".")[0]);
  if (major !== SUPPORTED_VIEWER_MAJOR) throw new Error(`unsupported viewer_data_schema_version: ${version}`);
  if (catalog.citypack_schema_version !== "1.0.0") throw new Error(`unsupported citypack_schema_version: ${String(catalog.citypack_schema_version)}`);
  if (catalog.generated_from !== "PRECOMPUTED_SYNTHETIC_DEMO_FIXTURES") throw new Error(`unsupported generated_from: ${String(catalog.generated_from)}`);
  if (!Array.isArray(catalog.cities) || catalog.cities.length === 0 || catalog.cities.length > MAX_CITIES) throw new Error(`viewer data must contain 1-${MAX_CITIES} cities`);
  catalog.cities.forEach(validateCity);
  requireUniqueIds(catalog.cities, "city_id", "viewer cities");
  return catalog;
}

export async function loadCatalog(fetchImpl, url, timeoutMs = 5000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetchImpl(url, { signal: controller.signal });
    if (!response || !response.ok) throw new Error(`city data request failed: HTTP ${response?.status ?? "unknown"}`);
    const text = await response.text();
    if (new TextEncoder().encode(text).byteLength > MAX_PAYLOAD_BYTES) throw new Error(`city data exceeds ${MAX_PAYLOAD_BYTES} byte limit`);
    let parsed;
    try { parsed = JSON.parse(text); }
    catch (error) { throw new Error(`city data is invalid JSON: ${error.message}`); }
    return assertSupportedCatalog(parsed);
  } catch (error) {
    if (error?.name === "AbortError") throw new Error(`city data request timed out after ${timeoutMs} ms`);
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

export function selectInitialState(catalog, search = "") {
  const params = new URLSearchParams(search);
  const city = catalog.cities.find((candidate) => candidate.city_id === params.get("city")) ?? catalog.cities[0];
  const view = params.get("view") === "3d" ? "3d" : "2d";
  const selectedEdge = city.map.edges.find((edge) => edge.edge_id === params.get("edge")) ?? city.map.edges[0] ?? null;
  return { city, scenario: city.scenarios[0], evidenceMode: "strict", phase: "before", view, selectedEdge };
}

export function serializeState({ city, view, selectedEdge }) {
  const params = new URLSearchParams();
  params.set("city", city.city_id);
  params.set("view", view);
  if (selectedEdge) params.set("edge", selectedEdge.edge_id);
  return `?${params.toString()}`;
}

export function formatKpi(entry) {
  if (entry.value === null) return { value: "—", reason: entry.reason, status: "NOT_COMPUTED" };
  return { value: String(entry.value), reason: entry.reason ?? "", status: "COMPUTED" };
}
