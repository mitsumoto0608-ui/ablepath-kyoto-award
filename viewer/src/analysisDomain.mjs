const DANGEROUS_CELL = /^[\u0000-\u0020\u007f\u200b\ufeff]*[=+\-@]/;
const SHA256 = /^[0-9a-f]{64}$/;
const RELATIONS = new Set(["INTERSECTS", "TOUCHES", "ZERO_OVERLAP_WITHIN_KNOWN_COVERAGE", "OUTSIDE_COVERAGE", "PARTIAL_COVERAGE", "NO_DATA"]);
const EXPECTED_HAZARD_SOURCES = {
  kyoto_kiyomizu: {
    nlni_a31b_2025_kyoto_flood: ["https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip", "PERMITTED_WITH_OBLIGATIONS", "d10455a376ee3d89b9618b77be85c51da5ebcc6687d17e92c492573f056e699e", "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c", "2025"],
    kyoto_city_landslide_gis_20260830: ["https://www.bousaimap.city.kyoto.lg.jp/GisDownload", "PRIVATE_INTERNAL_AND_PRIVATE_GIT_ONLY", "a3a8976c8708b95f1ccc5d5b8aaefdb4c0d7aaa0e8eb879a64d28e812818fdd6", "ac40e0b7116d81516dc10e279f5ca67ba48bbece68dc1164ec8f1d3e0c095828", "2026-01-22"],
  },
  kyoto_arashiyama: {
    nlni_a31b_2025_kyoto_flood: ["https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip", "PERMITTED_WITH_OBLIGATIONS", "2f02464358d7671c82bf69c346914f9c765e6558a20dca9af233aa54a5bfdbd7", "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c", "2025"],
    kyoto_city_landslide_gis_20260830: ["https://www.bousaimap.city.kyoto.lg.jp/GisDownload", "PRIVATE_INTERNAL_AND_PRIVATE_GIT_ONLY", "9935a4b22f656f3ef66d120bbc94c0d97e42e71a7956db181b6e8f0002700b4f", "ac40e0b7116d81516dc10e279f5ca67ba48bbece68dc1164ec8f1d3e0c095828", "2026-01-22"],
  },
  fujisawa_enoshima: {
    nlni_a40_2020_kanagawa_tsunami: ["https://nlftp.mlit.go.jp/ksj/gml/data/A40/A40-20/A40-20_14_GML.zip", "PRIVATE_INTERNAL_AND_PRIVATE_GIT_ONLY", "5dc5a3351b57f1b13b2a1d3571d82e789d8e7f859a1acf9c131749726260cb8c", "6b3192e4ed4f8f28d057e4738ecc0d2e7bef232d6adc3022f2d6aec8375f7479", "2020"],
  },
};
const EXPECTED_FUJISAWA_SCENARIO_IDS = [
  ...Array.from({ length: 8 }, (_, index) => `fujisawa_earthquake_intensity_scenario_${String(index + 1).padStart(2, "0")}`),
  "fujisawa_shaking_susceptibility_r6_01",
  ...Array.from({ length: 8 }, (_, index) => `fujisawa_liquefaction_distribution_scenario_${String(index + 1).padStart(2, "0")}`),
  "fujisawa_liquefaction_hazard_r6_01",
].sort();
const KYOTO_FACILITY_SOURCES = {
  kyoto_emergency_shelters_r80818: ["https://data.city.kyoto.lg.jp/resource/?id=7855", "LICENSE_REVIEW_REQUIRED", "R8.8.18", "e1c03e4e0f830d10430b6a0fb1e1669886c3708cdc61164e5471cea7f9a4d639", ["administrative_district", "community_disaster_group", "flood_evacuation_target_districts", "landslide_evacuation_target_districts", "official_number"]],
  kyoto_designated_shelters_r80818: ["https://data.city.kyoto.lg.jp/resource/?id=7854", "LICENSE_REVIEW_REQUIRED", "R8.8.18", "a30cf1556380359a1fa8fc69e4641fbfb7c3c099595818ac24c01417c9e28246", ["administrative_district", "community_disaster_group", "listed_maximum_capacity", "official_number"]],
  kyoto_public_toilets_00307: ["https://data.city.kyoto.lg.jp/resource/?id=20314", "CC BY 4.0", "2026-03-06", "a46448d7bb6fe814631b1230e69ce6d825d36ccf0ddb35dc339bc49ed60fc764", ["administrative_district", "listed_baby_support", "listed_fixture_count_text", "listed_opening_hours", "listed_ostomate_support", "listed_washlet_support", "listed_western_style", "listed_wheelchair_support", "official_map_number", "official_page_url"]],
};
const EXPECTED_FACILITY_SOURCES = {
  kyoto_kiyomizu: KYOTO_FACILITY_SOURCES,
  kyoto_arashiyama: KYOTO_FACILITY_SOURCES,
  fujisawa_enoshima: {
    fujisawa_webgis_toilets_accessibility: ["https://webgis.alandis.jp/fujisawa14/portal/index.html", "LICENSE_REVIEW_REQUIRED", null, "71bd70b0703086017e26d71cf4d73b76bcb0d14aaa0143c351e4763442b4530d", ["ostomate_detail_available"]],
  },
};
const EXPECTED_CONTENT_FINGERPRINTS = {
  kyoto_kiyomizu: { hazard_catalog: "84d869687bbb4621", facility_catalog: "836dfce99eed520f", facility_records: "135edb69fd555311" },
  kyoto_arashiyama: { hazard_catalog: "f2a23071675c5cdc", facility_catalog: "836dfce99eed520f", facility_records: "cea3061e9d13e1da" },
  fujisawa_enoshima: { hazard_catalog: "a5511ec143d37f66", facility_catalog: "92cbbf02e9cb3cba", facility_records: "5ad50528022431a3", scenarios: "fcec6c60971bf8fb" },
};
const APPROVED_DECISION_HASHES = {
  "F1_F6_DECISION_STATE.json": "101083468c4824de45260c1696a75786ce17e5996db1570eda14d1b50241c817",
  "F1_F6_ONE_PAGE_DECISION_FORM.md": "fa3aac71f5c8da692276f371170e76fc37a5abbdbf1f16f55da828bc9940b46d",
  "F1_SETBACK_CRS_DECISION.md": "bd7e58209e530be572a45ea22d300857ab32a5dd406c860638def31417562089",
  "F2_DAMAGE_MAPPING_DECISION.md": "55666534e2d531da428806ebda339c2ea5de822bee62c4a3f114cfef94ae5061",
  "F3_DEBRIS_REALIZATION_DECISION.md": "ff0ceba3028397356947626d215939ec6d6b7cf64ae6d2aeca4a35003051bae1",
  "F4_HEIGHT_PROVENANCE_DECISION.md": "52483cf23406fc0a8daea155d5902e8d2351b8ffb4b93ee925475955b706eb2b",
  "F5_DEFERRED_FIELD_MEASUREMENT_PLAN.md": "eb1ac0c8ef38504ee989bb7c9fa1d55f244c40ab93da1a69b58d3e146b7c62a3",
  "F6_LICENSE_SCOPE_BINDING.md": "30e4b4c865f2769a4c3a280d89187752817a7f8ae6e40383f644779786cf5c31",
  "POST_DECISION_IMPLEMENTATION_PLAN.md": "0f983ba84cc07101091e240e5df49cb4c69e705ed65800daa2b800122c1193a4",
  "ROLLBACK.md": "6b93637acbf9b06b026e37c54861140c365e74b4715d4c7054280ff3ecd21087",
};
const APPROVED_DECISION_ZIP_SHA256 = "d76c60e8285931bf61ffde05a48fda20cc107c845b89a6f83d42c80528911a9f";

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function csvCell(value) {
  const raw = value === null || value === undefined ? "" : Array.isArray(value) ? value.join(" | ") : String(value);
  const safe = DANGEROUS_CELL.test(raw) ? `'${raw}` : raw;
  return `"${safe.replaceAll('"', '""')}"`;
}

function escapeHtml(value) {
  return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}

function contentFingerprint(value) {
  let result = 14695981039346656037n;
  for (const byte of new TextEncoder().encode(canonicalJson(value))) {
    result ^= BigInt(byte);
    result = BigInt.asUintN(64, result * 1099511628211n);
  }
  return result.toString(16).padStart(16, "0");
}

export function validateDeliveryAnalysis(analysis, expectedCityId) {
  assert(analysis && typeof analysis === "object" && analysis.city_id === expectedCityId, "analysis city mismatch");
  for (const key of ["safety_claim", "accessibility_claim", "admin_validated"]) assert(analysis[key] === false, `forbidden ${key} claim`);
  const binding = analysis.decision_binding;
  assert(binding?.policy_approved === true && binding?.policy_bound === true && binding?.binding_implemented === true && binding?.production_value_implementation === false && binding?.value_available === false, "decision binding is invalid");
  assert(binding.source_zip_sha256 === APPROVED_DECISION_ZIP_SHA256, "decision ZIP provenance is invalid");
  assert(binding.source_sha256 === APPROVED_DECISION_HASHES["F1_F6_DECISION_STATE.json"] && JSON.stringify(binding.source_artifacts) === JSON.stringify(APPROVED_DECISION_HASHES), "decision provenance is invalid");
  assert(binding.f1?.target === "FIELD_CONFIRMED_WALKABLE_SPACE_BOUNDARY_TO_TARGET_BUILDING_FRONTAGE_GEOMETRY_SHORTEST_HORIZONTAL_DISTANCE", "F1 target is invalid");
  assert(JSON.stringify(binding.f1?.metric_crs) === JSON.stringify({ kyoto: "EPSG:6674", fujisawa: "EPSG:6677" }), "F1 CRS is invalid");
  assert(new Set(binding.f1?.unapproved_details ?? []).size === 4 && ["tolerance", "station_interval", "long_edge_split", "unknown_rules"].every((value) => binding.f1.unapproved_details.includes(value)), "F1 unapproved details changed");
  assert(JSON.stringify(binding.f1?.rejected_inputs) === JSON.stringify(["CANDIDATE_CENTERLINE", "CENTROID_DISTANCE", "ARBITRARY_NEAREST_GEOMETRY"]), "F1 rejected inputs changed");
  assert(binding.f2?.concrete_taxonomy_mapping_approved === false && JSON.stringify(binding.f2?.eligible_source_classes) === JSON.stringify(["ACCEPTED_OBSERVED_POST_EVENT_STATE", "ACCEPTED_OFFICIAL_ASSET_LEVEL_SCENARIO_STATE"]), "F2 was promoted");
  assert(binding.f3?.probability_realization === "EXPERIMENTAL_ONLY" && JSON.stringify(binding.f3?.eligible_source_classes) === JSON.stringify(["ACCEPTED_OBSERVED_BOOL", "ACCEPTED_OFFICIAL_ASSET_LEVEL_BOOL"]), "F3 was promoted");
  assert(binding.f4?.methods_must_remain_distinct === true && binding.f4?.height_values_accepted === false && JSON.stringify(binding.f4?.conditional_candidates) === JSON.stringify(["KYOTO_POINT_CLOUD_MEDIAN", "FUJISAWA_AERIAL_PHOTOGRAMMETRY_MAXIMUM"]) && JSON.stringify(binding.f4?.excluded) === JSON.stringify(["UNIFORM_3M", "NEGATIVE_9999_SENTINEL"]), "F4 was promoted");
  assert(binding.f5?.field_measurement_deferred === true && binding.f5?.measurement_value_count === 0, "F5 field measurement changed");
  assert(binding.m7_ready_count === 0 && binding.m7_computed_count === 0, "decision binding promoted M7");
  assert(binding.f6?.private_internal === true && binding.f6?.private_git === true && binding.f6?.internal_rc === true && binding.f6?.public_git === false && binding.f6?.public_rc === false && binding.f6?.public_demo === false, "F6 scope was promoted");
  for (const key of ["safe_route_claim", "accessibility_claim", "passability_claim", "admin_validated", "public_release_ready"]) assert(binding[key] === false, `decision binding promoted ${key}`);
  const hazard = analysis.official_evidence?.hazard;
  assert(hazard?.status === "SOURCE_SIDE_EDGE_OVERLAP_CONNECTED", "hazard analysis contract is missing");
  assert(hazard.operational_state_connected === false && hazard.closure_derived === false && hazard.damage_or_debris_inferred === false, "hazard analysis promoted operational state");
  assert(hazard.numeric_serialization === "FULL_PYTHON_FLOAT_NO_DECISION_TOLERANCE" && hazard.decision_threshold_applied === false, "unapproved hazard threshold or serialization rule");
  const sourceCatalog = hazard.source_catalog;
  assert(sourceCatalog && Object.keys(sourceCatalog).length > 0 && Object.values(sourceCatalog).every((source) => /^https:\/\//.test(source.source_url) && typeof source.source_revision === "string" && source.source_revision.length > 0 && SHA256.test(source.source_sha256) && typeof source.license_status === "string" && source.license_status.length > 0 && typeof source.limitations === "string" && source.limitations.length > 0 && SHA256.test(source.coverage_selection_sha256)), "hazard source catalog is invalid");
  const expectedHazardSources = EXPECTED_HAZARD_SOURCES[expectedCityId];
  assert(expectedHazardSources && JSON.stringify(Object.keys(sourceCatalog).sort()) === JSON.stringify(Object.keys(expectedHazardSources).sort()) && Object.entries(expectedHazardSources).every(([sourceId, [url, license, selectionSha, sourceSha, revision]]) => sourceCatalog[sourceId].source_url === url && sourceCatalog[sourceId].license_status === license && sourceCatalog[sourceId].coverage_selection_sha256 === selectionSha && sourceCatalog[sourceId].source_sha256 === sourceSha && sourceCatalog[sourceId].source_revision === revision), "hazard source provenance is not exact");
  assert(contentFingerprint(sourceCatalog) === EXPECTED_CONTENT_FINGERPRINTS[expectedCityId]?.hazard_catalog, "hazard source catalog content is stale");
  const terrain = analysis.official_evidence?.terrain;
  const expectedTerrainStatus = expectedCityId === "fujisawa_enoshima" ? "NOT_CONNECTED" : "AOI_COVERAGE_VALIDATED_ELEVATION_NOT_SAMPLED";
  const expectedProductStatus = expectedCityId === "fujisawa_enoshima" ? "NOT_CONNECTED" : "EVIDENCE_UI_ONLY_NOT_ELEVATION_ANALYSIS";
  assert(terrain?.status === expectedTerrainStatus && terrain?.connected === false && terrain?.elevation_sampled === false && terrain?.step_inferred === false && terrain?.cross_slope_inferred === false, "terrain evidence was promoted");
  assert(Array.isArray(terrain.products) && terrain.products.every((product) => product.terrain_connected === false && product.status === expectedProductStatus && product.vertical_datum === "NOT_EXPLICIT_IN_INSPECTED_GML"), "terrain product evidence was promoted");
  const facility = analysis.official_evidence?.facility;
  assert(facility && Array.isArray(facility.records) && facility.record_count === facility.records.length, "facility record count is stale");
  const facilityCatalog = facility.source_catalog;
  assert(facilityCatalog && Object.keys(facilityCatalog).length > 0 && Object.values(facilityCatalog).every((source) => /^https:\/\//.test(source.source_url) && ["LICENSE_REVIEW_REQUIRED", "CC BY 4.0"].includes(source.license_status) && typeof source.limitations === "string" && source.limitations.length > 0 && typeof source.temporal_status_reason === "string" && source.temporal_status_reason.length > 0 && SHA256.test(source.source_sha256) && Array.isArray(source.allowed_attribute_keys) && ["published_at", "valid_as_of", "acquired_at"].every((key) => source[key] === null || typeof source[key] === "string")), "facility source catalog is invalid");
  const expectedFacilitySources = EXPECTED_FACILITY_SOURCES[expectedCityId];
  assert(expectedFacilitySources && JSON.stringify(Object.keys(facilityCatalog).sort()) === JSON.stringify(Object.keys(expectedFacilitySources).sort()) && Object.entries(expectedFacilitySources).every(([sourceId, [url, license, validAsOf, sourceSha, allowedKeys]]) => {
    const source = facilityCatalog[sourceId];
    return source.source_url === url && source.license_status === license && source.valid_as_of === validAsOf && source.source_sha256 === sourceSha && JSON.stringify([...source.allowed_attribute_keys].sort()) === JSON.stringify([...allowedKeys].sort());
  }), "facility source provenance is not exact");
  assert(contentFingerprint(facilityCatalog) === EXPECTED_CONTENT_FINGERPRINTS[expectedCityId]?.facility_catalog && contentFingerprint(facility.records) === EXPECTED_CONTENT_FINGERPRINTS[expectedCityId]?.facility_records, "facility canonical content is stale");
  assert(facility.records.every((record) => {
    const source = facilityCatalog[record.source_id];
    const expectedEntries = Object.entries(record.source_attributes ?? {}).sort(([left], [right]) => left.localeCompare(right));
    return source && record.source_sha256 === source.source_sha256 && record.source_version_or_valid_as_of === source.valid_as_of && JSON.stringify(Object.keys(record.source_attributes ?? {}).sort()) === JSON.stringify([...source.allowed_attribute_keys].sort()) && JSON.stringify(record.source_attribute_entries) === JSON.stringify(expectedEntries) && typeof record.limitations === "string" && record.limitations.length > 0 && ["current_operation_status", "entrance_status", "unlock_status", "accessibility_status", "step_free_status", "disaster_availability_status"].every((key) => record[key] === "UNKNOWN");
  }), "facility source binding or current state is invalid");
  const facilityIds = facility.records.map((record) => record.facility_record_id).sort();
  assert(new Set(facilityIds).size === facilityIds.length, "facility IDs are duplicated");
  if (expectedCityId === "fujisawa_enoshima") {
    assert(facility.geometry_status === "ADDRESS_ONLY" && facility.marker_policy === "TABLE_ONLY_NO_MARKERS_OR_GEOCODING", "Fujisawa facility location was promoted");
    assert(Array.isArray(hazard.scenarios) && contentFingerprint(hazard.scenarios) === EXPECTED_CONTENT_FINGERPRINTS.fujisawa_enoshima.scenarios && JSON.stringify(hazard.scenarios.map((row) => row.dataset_id).sort()) === JSON.stringify(EXPECTED_FUJISAWA_SCENARIO_IDS) && hazard.scenarios.every((row) => row.connected === false && row.status === "NOT_CONNECTED" && row.aoi_scope === "enoshima_katase" && row.official_source === "Kanagawa Prefecture candidate; source binding requires receipt review" && row.official_url === "UNKNOWN_NO_SOURCE_URL_OR_ACQUISITION_RECEIPT_IN_SCOPED_FOLDER" && row.version_date === "2025-02-05/15 where encoded in layer name; otherwise source receipt required" && row.license_review === "LICENSE_REVIEW_REQUIRED" && typeof row.reason === "string" && row.reason.length > 0 && (row.layer_kind === "震度分布" ? row.validation_result === "CRS_REVIEW_REQUIRED" && row.crs.startsWith("CRS_CONTRADICTION:") && row.bounds_native === "[-83359.01999999999, -96822.555, -3306.66, -36059.1]" : row.validation_result === "LICENSE_REVIEW_REQUIRED" && row.crs === "EPSG:4612" && row.bounds_native === "[138.915625, 35.127083, 139.796875, 35.672917]")), "Fujisawa earthquake/liquefaction inventory was promoted");
  }
  const exposureKeys = new Set();
  const exposureByKey = new Map();
  const exposureRefsByEdge = new Map();
  assert(Array.isArray(hazard.edge_exposures) && hazard.edge_exposures.length > 0 && hazard.edge_exposures.every((row) => {
    const key = `${row.edge_id}\0${row.scenario_id}\0${row.source_id}`;
    const source = sourceCatalog[row.source_id];
    const valid = !exposureKeys.has(key) && SHA256.test(row.source_sha256) && source && row.source_sha256 === source.source_sha256 && row.source_revision === source.source_revision && RELATIONS.has(row.relation) && typeof row.reason === "string" && row.reason.length > 0 && row.official_closure === null && row.damage_state === null && row.debris_present === null && (row.overlap_length_m === null || (Number.isFinite(row.overlap_length_m) && row.overlap_length_m >= 0));
    exposureKeys.add(key);
    exposureByKey.set(key, row);
    exposureRefsByEdge.set(row.edge_id, [...(exposureRefsByEdge.get(row.edge_id) ?? []), key]);
    const relationValid = row.relation === "INTERSECTS"
      ? row.coverage_status === "WITHIN_KNOWN_COVERAGE" && row.overlap_length_m > 0
      : ["TOUCHES", "ZERO_OVERLAP_WITHIN_KNOWN_COVERAGE"].includes(row.relation)
        ? row.coverage_status === "WITHIN_KNOWN_COVERAGE" && row.overlap_length_m === 0
        : row.relation === "OUTSIDE_COVERAGE"
          ? row.coverage_status === "OUTSIDE_KNOWN_COVERAGE" && row.overlap_length_m === null
          : row.relation === "PARTIAL_COVERAGE"
            ? row.coverage_status === "PARTIAL_KNOWN_COVERAGE" && row.overlap_length_m === null
            : row.relation === "NO_DATA" && row.overlap_length_m === null;
    return valid && relationValid;
  }), "unsafe or invalid hazard exposure row");
  assert(analysis.path_matrix && analysis.review_checklists && JSON.stringify(Object.keys(analysis.path_matrix).sort()) === JSON.stringify(Object.keys(analysis.review_checklists).sort()), "review checklist contract is incomplete");
  for (const [key, checklist] of Object.entries(analysis.review_checklists)) {
    const path = analysis.path_matrix[key];
    assert(checklist.path_key === key && checklist.city_id === expectedCityId && checklist.path_status === path.status && JSON.stringify(checklist.rows.map((row) => row.edge_id)) === JSON.stringify(path.status === "CONNECTED" ? path.edge_ids : []), "review checklist path binding is stale");
    assert(checklist.safe_route_claim === false && checklist.accessibility_claim === false && checklist.admin_validated === false, "review checklist contains a forbidden claim");
    assert(Array.isArray(checklist.rows) && Array.isArray(checklist.facility?.record_ids), "review checklist rows are invalid");
    assert(checklist.rows.every((row) => Array.isArray(row.owner_candidate_types) && row.owner_candidate_types.length > 0 && Array.isArray(row.hazard_refs) && JSON.stringify([...row.hazard_refs].sort()) === JSON.stringify([...(exposureRefsByEdge.get(row.edge_id) ?? [])].sort())), "review checklist contains incomplete or orphan evidence references");
    assert(checklist.facility.record_count === facilityIds.length && JSON.stringify([...checklist.facility.record_ids].sort()) === JSON.stringify(facilityIds), "review checklist facility references are stale");
  }
  return analysis;
}

async function sha256Text(text) {
  const digest = await globalThis.crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
}

export async function loadDeliveryAnalysis(fetchImpl, path, expectedCityId, timeoutMs = 5000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const separator = path.lastIndexOf("/");
    const manifestPath = `${path.slice(0, separator + 1)}manifest.json`;
    const [response, manifestResponse] = await Promise.all([fetchImpl(path, { signal: controller.signal }), fetchImpl(manifestPath, { signal: controller.signal })]);
    if (!response.ok) throw new Error(`analysis HTTP ${response.status}`);
    if (!manifestResponse.ok) throw new Error(`analysis manifest HTTP ${manifestResponse.status}`);
    const [text, manifestText] = await Promise.all([response.text(), manifestResponse.text()]);
    if (new TextEncoder().encode(text).byteLength > 8_000_000) throw new Error("analysis payload exceeds static viewer byte limit");
    if (new TextEncoder().encode(manifestText).byteLength > 100_000) throw new Error("analysis manifest exceeds static viewer byte limit");
    const manifest = JSON.parse(manifestText);
    assert(manifest?.schema_version === "1.0.0" && manifest?.source_analysis_authority === "src/analysis" && manifest?.generator === "scripts/build_candidate_analysis.py", "analysis manifest authority is invalid");
    const expectedSha = manifest.artifacts?.[`${expectedCityId}.json`];
    assert(SHA256.test(expectedSha) && await sha256Text(text) === expectedSha, "analysis bytes do not match the committed manifest");
    return validateDeliveryAnalysis(JSON.parse(text), expectedCityId);
  } finally {
    clearTimeout(timer);
  }
}

function flatRows(checklist, includeFacilities = true) {
  const result = [];
  for (const row of checklist.rows) {
    if (!row.hazards.length) result.push({ row_kind: "candidate_edge", ...row, scenario_id: "NO_CONNECTED_HAZARD_ROW", relation: "NO_DATA", overlap_length_m: null, source_id: null, source_revision: null, source_sha256: null, source_classes: [] });
    for (const hazard of row.hazards) result.push({ row_kind: "candidate_edge", ...row, ...hazard });
  }
  if (includeFacilities) for (const facility of checklist.facility?.records ?? []) result.push({ row_kind: "facility", edge_id: null, scenario_id: null, relation: null, overlap_length_m: null, source_id: facility.source_id, source_revision: facility.source_version_or_valid_as_of, source_sha256: facility.source_sha256 ?? null, source_url: facility.source_url, license_status: facility.license_status, limitations: facility.limitations, source_published_at: facility.source_published_at, source_valid_as_of: facility.source_valid_as_of, source_acquired_at: facility.source_acquired_at, source_temporal_status_reason: facility.source_temporal_status_reason, source_classes: [], terrain_status: null, terrain_sampled: null, terrain_reason: null, facility_status: checklist.facility.status, unknowns: ["current_operation", "entrance", "unlock", "accessibility", "step_free", "disaster_availability"], facility_record_id: facility.facility_record_id, facility_name: facility.name, facility_address: facility.address, facility_source_attributes: JSON.stringify(facility.source_attributes ?? {}) });
  return result;
}

export function checklistToCsv(checklist) {
  const columns = ["row_kind", "edge_id", "scenario_id", "relation", "coverage_status", "overlap_length_m", "metric_crs", "source_id", "source_revision", "source_sha256", "source_url", "license_status", "source_published_at", "source_valid_as_of", "source_acquired_at", "source_temporal_status_reason", "coverage_selection_sha256", "source_feature_ids", "source_classes", "reason", "limitations", "interpretation", "terrain_status", "terrain_sampled", "terrain_reason", "facility_status", "owner_candidate_types", "facility_record_id", "facility_name", "facility_address", "facility_source_attributes", "unknowns"];
  return [columns.join(","), ...flatRows(checklist).map((row) => columns.map((column) => csvCell(row[column])).join(","))].join("\n") + "\n";
}

export function checklistToJson(checklist) {
  return `${JSON.stringify(checklist, null, 2)}\n`;
}

export function checklistToPrintableHtml(checklist) {
  const rows = flatRows(checklist, false).map((row) => `<tr><th>${escapeHtml(row.edge_id)}</th><td>${escapeHtml(row.scenario_id)}</td><td>${escapeHtml(row.relation)} / ${escapeHtml(row.coverage_status)}<br>${escapeHtml(row.overlap_length_m ?? "null")} m (${escapeHtml(row.metric_crs)})</td><td>${escapeHtml(row.source_id ?? "null")}@${escapeHtml(row.source_revision ?? "null")}<br>${escapeHtml(row.source_url ?? "null")}<br>${escapeHtml(row.license_status ?? "null")}<br><code>source ${escapeHtml(row.source_sha256 ?? "null")}<br>selection ${escapeHtml(row.coverage_selection_sha256 ?? "null")}</code></td><td>${escapeHtml(row.source_feature_ids)}<br>${escapeHtml(row.source_classes)}</td><td>${escapeHtml(row.reason)}<br>${escapeHtml(row.limitations)}<br>${escapeHtml(row.interpretation)}</td><td>${escapeHtml(row.terrain_status)} — ${escapeHtml(row.terrain_reason)}</td><td>${escapeHtml(row.owner_candidate_types)} / ${escapeHtml(row.unknowns)}</td></tr>`).join("");
  const facilities = (checklist.facility?.records ?? []).map((record) => `<tr><th>${escapeHtml(record.facility_record_id)}</th><td>${escapeHtml(record.name)}</td><td>${escapeHtml(record.address)}</td><td>${escapeHtml(record.source_id)} / ${escapeHtml(record.source_version_or_valid_as_of)}<br>${escapeHtml(record.source_url)} / ${escapeHtml(record.license_status)}<br>published ${escapeHtml(record.source_published_at ?? "null")} / valid-as-of ${escapeHtml(record.source_valid_as_of ?? "null")} / acquired ${escapeHtml(record.source_acquired_at ?? "null")}<br>${escapeHtml(record.source_temporal_status_reason)}<br><code>${escapeHtml(record.source_sha256 ?? "null")}</code></td><td>${escapeHtml(JSON.stringify(record.source_attributes ?? {}))}<br>${escapeHtml(record.limitations)}</td><td>UNKNOWN: current operation / entrance / unlock / accessibility / step-free / disaster availability</td></tr>`).join("");
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'"><title>印刷用確認リスト ${escapeHtml(checklist.checklist_id)}</title><style>body{font-family:sans-serif;margin:24px;color:#17202a}table{border-collapse:collapse;width:100%;font-size:11px}th,td{border:1px solid #777;padding:5px;text-align:left;vertical-align:top}code{overflow-wrap:anywhere}@media print{button{display:none}}</style></head><body><h1>印刷用確認リスト</h1><p><b>${escapeHtml(checklist.city_id)}</b> / ${escapeHtml(checklist.path_key)} / ${escapeHtml(checklist.path_status)}</p><p>候補接続の確認資料です。安全性、アクセシビリティ、通行可能性、行政検証を示しません。</p><p>terrain: ${escapeHtml(checklist.terrain.status)} — ${escapeHtml(checklist.terrain.reason)}<br>facility: ${escapeHtml(checklist.facility.status)} — ${escapeHtml(checklist.facility.reason)}</p><table><thead><tr><th>edge</th><th>scenario</th><th>relation / coverage / metric overlap</th><th>source / revision / URL / license / hashes</th><th>source feature / class</th><th>reason / limitations</th><th>terrain</th><th>owner candidates / unknowns</th></tr></thead><tbody>${rows}</tbody></table><h2>公式施設原本属性</h2><table><thead><tr><th>ID</th><th>name</th><th>address</th><th>source</th><th>listed attributes</th><th>unknown runtime state</th></tr></thead><tbody>${facilities}</tbody></table></body></html>`;
}
