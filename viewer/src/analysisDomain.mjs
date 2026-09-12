const DANGEROUS_CELL = /^[\u0000-\u0020\u007f\u200b\ufeff]*[=+\-@]/;
const SHA256 = /^[0-9a-f]{64}$/;
const CHECKLIST_UNKNOWNS = ["accessibility", "passability", "current_facility_operation", "M6", "M7"];
const RELATIONS = new Set(["INTERSECTS", "TOUCHES", "ZERO_OVERLAP_WITHIN_KNOWN_COVERAGE", "OUTSIDE_COVERAGE", "PARTIAL_COVERAGE", "NO_DATA"]);
const EXPECTED_HAZARD_SOURCES = {
  kyoto_kiyomizu: {
    nlni_a31b_2025_kyoto_flood: ["https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip", "PERMITTED_WITH_OBLIGATIONS", "d10455a376ee3d89b9618b77be85c51da5ebcc6687d17e92c492573f056e699e", "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c", "2025"],
    kyoto_city_landslide_gis_20260830: ["https://www.bousaimap.city.kyoto.lg.jp/GisDownload", "PUBLIC_REUSE_ALLOWED_WITH_ATTRIBUTION", "a3a8976c8708b95f1ccc5d5b8aaefdb4c0d7aaa0e8eb879a64d28e812818fdd6", "ac40e0b7116d81516dc10e279f5ca67ba48bbece68dc1164ec8f1d3e0c095828", "2026-01-22"],
  },
  kyoto_arashiyama: {
    nlni_a31b_2025_kyoto_flood: ["https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip", "PERMITTED_WITH_OBLIGATIONS", "2f02464358d7671c82bf69c346914f9c765e6558a20dca9af233aa54a5bfdbd7", "5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c", "2025"],
    kyoto_city_landslide_gis_20260830: ["https://www.bousaimap.city.kyoto.lg.jp/GisDownload", "PUBLIC_REUSE_ALLOWED_WITH_ATTRIBUTION", "9935a4b22f656f3ef66d120bbc94c0d97e42e71a7956db181b6e8f0002700b4f", "ac40e0b7116d81516dc10e279f5ca67ba48bbece68dc1164ec8f1d3e0c095828", "2026-01-22"],
  },
  fujisawa_enoshima: {
    nlni_a40_2020_kanagawa_tsunami: ["https://nlftp.mlit.go.jp/ksj/gml/data/A40/A40-20/A40-20_14_GML.zip", "PUBLIC_REDISTRIBUTION_ALLOWED_WITH_ATTRIBUTION", "5dc5a3351b57f1b13b2a1d3571d82e789d8e7f859a1acf9c131749726260cb8c", "6b3192e4ed4f8f28d057e4738ecc0d2e7bef232d6adc3022f2d6aec8375f7479", "2020"],
    kanagawa_r7_intensity_distribution_01: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/704a2ee0-0040-4a96-b92a-c8e36b559d3d", "CC-BY-4.0", "1748165a3d296fac37f4c8298a3bc013e28d3869c24d8fc9b6af7d10db660595", "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_intensity_distribution_02: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/704a2ee0-0040-4a96-b92a-c8e36b559d3d", "CC-BY-4.0", "28636eefca222b65c5c29ec6e2f66dc63939864a3a1b185aa46b0c210811ca4d", "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_intensity_distribution_03: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/704a2ee0-0040-4a96-b92a-c8e36b559d3d", "CC-BY-4.0", "621401abd0c56324be78d97b34a63e1833e173cd178c66b101ec7ac65d128b1a", "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_intensity_distribution_04: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/704a2ee0-0040-4a96-b92a-c8e36b559d3d", "CC-BY-4.0", "f13dc5d92d7e7bd743da1c1567bee9f0cd03a12b2e9748f37a8a59586ebb7d3b", "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_intensity_distribution_05: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/704a2ee0-0040-4a96-b92a-c8e36b559d3d", "CC-BY-4.0", "acdef6ce4c816a8332966f9a35b119f4b60c4074af03eb75a0c4e649c8ac41d3", "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_intensity_distribution_06: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/704a2ee0-0040-4a96-b92a-c8e36b559d3d", "CC-BY-4.0", "fda1ba2847dfd9d9bfe1a69f3ea930f312db654d5f0d326f59d6c8a3ca2db195", "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_intensity_distribution_07: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/704a2ee0-0040-4a96-b92a-c8e36b559d3d", "CC-BY-4.0", "eb3ca595ee5976f36b340acdcd07f913134cdb422aeb7acdd58079cb1ef20b36", "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_intensity_distribution_08: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/704a2ee0-0040-4a96-b92a-c8e36b559d3d", "CC-BY-4.0", "c8be7d19522b39d81f058f5a5196f49408b6c60cd4db8afd6933b0729771df66", "03989508e8e715496c700f92e30ac8c3feaaec163d19438aa28b3bcb3738b442", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_liquefaction_distribution_01: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/1f94e194-1764-46db-baf9-e8b017ae458d", "CC-BY", "5d37e622abc6c4bf28b93362016f7d7bbe64c5c1103220cbe467ba94c577690d", "91f721e0f37114379d7535f5a9c09eac03ffa9c4d3dc1a2088d6d8ee5f47d023", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_liquefaction_distribution_02: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/1f94e194-1764-46db-baf9-e8b017ae458d", "CC-BY", "1cf28d1ce1b89873302deac16eee5ad429926307aa5889308fde765d68f5d029", "91f721e0f37114379d7535f5a9c09eac03ffa9c4d3dc1a2088d6d8ee5f47d023", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_liquefaction_distribution_03: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/1f94e194-1764-46db-baf9-e8b017ae458d", "CC-BY", "d0fa5f079eb18c1ac7971c6c75320239c83ada6767e53458d7696357bf10e983", "91f721e0f37114379d7535f5a9c09eac03ffa9c4d3dc1a2088d6d8ee5f47d023", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_liquefaction_distribution_04: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/1f94e194-1764-46db-baf9-e8b017ae458d", "CC-BY", "86a375a1981712ff30ae1f2e547d120ef32bd931d54bc21a7c05707223bc0949", "91f721e0f37114379d7535f5a9c09eac03ffa9c4d3dc1a2088d6d8ee5f47d023", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_liquefaction_distribution_05: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/1f94e194-1764-46db-baf9-e8b017ae458d", "CC-BY", "b37720d8c2dffcda8f292799e1486850cb45a52562a5fa1432d0a55d62fe6341", "91f721e0f37114379d7535f5a9c09eac03ffa9c4d3dc1a2088d6d8ee5f47d023", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_liquefaction_distribution_06: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/1f94e194-1764-46db-baf9-e8b017ae458d", "CC-BY", "c4f788db34ddccbc011167480ccecb64f0508db347a0591733565f3e1cab4fbf", "91f721e0f37114379d7535f5a9c09eac03ffa9c4d3dc1a2088d6d8ee5f47d023", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_liquefaction_distribution_07: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/1f94e194-1764-46db-baf9-e8b017ae458d", "CC-BY", "d0750f3a40e14c6d88fa4c8339d14a10a5207ddc2bd1a98fdb2b03876dd5aee9", "91f721e0f37114379d7535f5a9c09eac03ffa9c4d3dc1a2088d6d8ee5f47d023", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_liquefaction_distribution_08: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/1f94e194-1764-46db-baf9-e8b017ae458d", "CC-BY", "835c9e16cfd046f0c05cb20bf9d28d70babea0b610b3eb0ca736da4882315b67", "91f721e0f37114379d7535f5a9c09eac03ffa9c4d3dc1a2088d6d8ee5f47d023", "R7_MARCH_2025_SCENARIO_SET"],
    kanagawa_r7_shaking_susceptibility: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/0511f2b8-db28-4eae-a5a9-83ac58d31fbc", "CC-BY", "10298a53d8e5ab3084ee68d84fe727a5cb63f28812fd0578e55626b392e47de1", "281f43260b2a0d18f8b4afb4fdbfdba79464692ed175d1d0be3c8f88df6dcaa3", "R6_UPDATE_2025-02-05"],
    kanagawa_r7_liquefaction_hazard: ["https://catalog.opendata.pref.kanagawa.jp/dataset/fdc2ffe1fd3cb572d95d0f954f6c72eb/resource/cd7619e9-b6f8-48ad-a251-f8fa9cc84462", "CC-BY", "54af719e9815befcc950f9bacf40512eab57fe878014f191c5622ae9e870ae22", "fb18d09991f63eae642483334c2eb1657b139cc746aa4c4af083260a070146de", "R6_UPDATE_2025-02-15_V01"],
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
  kyoto_kiyomizu: { hazard_catalog: "16c9f626d7c72589", facility_catalog: "836dfce99eed520f", facility_records: "74cf3c70518f49ee" },
  kyoto_arashiyama: { hazard_catalog: "0668c41634ac0568", facility_catalog: "836dfce99eed520f", facility_records: "945123b3c5027bcb" },
  fujisawa_enoshima: { hazard_catalog: "413ca922a7058e41", facility_catalog: "92cbbf02e9cb3cba", facility_records: "09612b07b5ecb5a5", scenarios: "01e39c58b560fad8" },
};
const EXPECTED_ANALYSIS_SHA256 = {
  fujisawa_enoshima: "2f5ddf66b9bef56fb8982021224283b4bac978347df700b1f16c7474a9b7e858",
  kyoto_arashiyama: "f8db4e9f92df0b0d493831564ee9c2c79e629a738e75142c6368e65ba382d0b4",
  kyoto_kiyomizu: "3aaf4a791362069718c930673e432f67b8eeada7a9e6dad2b25c806f2aa25c51",
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
  assert(canonicalJson(binding.f1?.metric_crs) === canonicalJson({ kyoto: "EPSG:6674", fujisawa: "EPSG:6677" }), "F1 CRS is invalid");
  assert(new Set(binding.f1?.unapproved_details ?? []).size === 4 && ["tolerance", "station_interval", "long_edge_split", "unknown_rules"].every((value) => binding.f1.unapproved_details.includes(value)), "F1 unapproved details changed");
  assert(JSON.stringify(binding.f1?.rejected_inputs) === JSON.stringify(["CANDIDATE_CENTERLINE", "CENTROID_DISTANCE", "ARBITRARY_NEAREST_GEOMETRY"]), "F1 rejected inputs changed");
  assert(binding.f2?.concrete_taxonomy_mapping_approved === false && JSON.stringify(binding.f2?.eligible_source_classes) === JSON.stringify(["ACCEPTED_OBSERVED_POST_EVENT_STATE", "ACCEPTED_OFFICIAL_ASSET_LEVEL_SCENARIO_STATE"]), "F2 was promoted");
  assert(binding.f3?.probability_realization === "EXPERIMENTAL_ONLY" && JSON.stringify(binding.f3?.eligible_source_classes) === JSON.stringify(["ACCEPTED_OBSERVED_BOOL", "ACCEPTED_OFFICIAL_ASSET_LEVEL_BOOL"]), "F3 was promoted");
  assert(binding.f4?.methods_must_remain_distinct === true && binding.f4?.height_values_accepted === false && JSON.stringify(binding.f4?.conditional_candidates) === JSON.stringify(["KYOTO_POINT_CLOUD_MEDIAN", "FUJISAWA_AERIAL_PHOTOGRAMMETRY_MAXIMUM"]) && JSON.stringify(binding.f4?.excluded) === JSON.stringify(["UNIFORM_3M", "NEGATIVE_9999_SENTINEL"]), "F4 was promoted");
  assert(binding.f5?.field_measurement_deferred === true && binding.f5?.measurement_value_count === 0, "F5 field measurement changed");
  assert(binding.m7_ready_count === 0 && binding.m7_computed_count === 0, "decision binding promoted M7");
  assert(binding.f6?.private_internal === true && binding.f6?.private_git === false && binding.f6?.internal_rc === true && binding.f6?.public_git === true && binding.f6?.public_rc === false && binding.f6?.public_demo === false, "F6 public Git scope amendment is invalid");
  assert(binding.scope_amendment?.path === "reports/PUBLIC_GIT_SCOPE_AMENDMENT_20260910.json" && binding.scope_amendment?.sha256 === "1df66ac07ba476a2a2a412f034775559879206a685d6abb27fbe69e7e915f4f6" && binding.scope_amendment?.authority === "USER_EXPLICIT_OWNER_INSTRUCTION_IN_CODEX_SESSION", "F6 public Git amendment is missing");
  for (const key of ["safe_route_claim", "accessibility_claim", "passability_claim", "admin_validated", "public_release_ready"]) assert(binding[key] === false, `decision binding promoted ${key}`);
  const hazard = analysis.official_evidence?.hazard;
  assert(hazard?.status === "SOURCE_SIDE_EDGE_OVERLAP_CONNECTED", "hazard analysis contract is missing");
  assert(hazard.operational_state_connected === false && hazard.closure_derived === false && hazard.damage_or_debris_inferred === false, "hazard analysis promoted operational state");
  assert(hazard.numeric_serialization === "FULL_PYTHON_FLOAT_NO_DECISION_TOLERANCE" && hazard.decision_threshold_applied === false, "unapproved hazard threshold or serialization rule");
  const sourceCatalog = hazard.source_catalog;
  assert(sourceCatalog && Object.keys(sourceCatalog).length > 0 && Object.values(sourceCatalog).every((source) => /^https:\/\//.test(source.source_url) && typeof source.source_revision === "string" && source.source_revision.length > 0 && SHA256.test(source.source_sha256) && typeof source.license_status === "string" && source.license_status.length > 0 && typeof source.limitations === "string" && source.limitations.length > 0 && SHA256.test(source.coverage_selection_sha256)), "hazard source catalog is invalid");
  const expectedHazardSources = EXPECTED_HAZARD_SOURCES[expectedCityId];
  assert(expectedHazardSources && JSON.stringify(Object.keys(sourceCatalog).sort()) === JSON.stringify(Object.keys(expectedHazardSources).sort()) && Object.entries(expectedHazardSources).every(([sourceId, [url, license, selectionSha, sourceSha, revision]]) => sourceCatalog[sourceId].source_url === url && sourceCatalog[sourceId].license_status === license && sourceCatalog[sourceId].coverage_selection_sha256 === selectionSha && sourceCatalog[sourceId].source_sha256 === sourceSha && sourceCatalog[sourceId].source_revision === revision), "hazard source provenance is not exact");
  if (expectedCityId === "fujisawa_enoshima") {
    const memberBound = Object.entries(sourceCatalog).filter(([sourceId]) => sourceId.startsWith("kanagawa_r7_"));
    assert(memberBound.length === 18 && memberBound.every(([_sourceId, source]) => typeof source.source_member_id === "string" && source.source_member_id.length > 0 && ["member_path_sha256", "shp_sha256", "shx_sha256", "dbf_sha256", "txt_sha256"].every((key) => SHA256.test(source.source_member_receipt?.[key]))), "Fujisawa hazard member identity is invalid");
  }
  assert(contentFingerprint(sourceCatalog) === EXPECTED_CONTENT_FINGERPRINTS[expectedCityId]?.hazard_catalog, "hazard source catalog content is stale");
  const terrain = analysis.official_evidence?.terrain;
  assert(terrain?.status === "NATIVE_CELL_SAMPLES_CONNECTED" && terrain?.connected === true && terrain?.elevation_sampled === true && terrain?.step_inferred === false && terrain?.cross_slope_inferred === false, "terrain native-cell evidence is invalid");
  assert(Array.isArray(terrain.products) && terrain.products.length === 2 && terrain.products.every((product) => product.terrain_connected === true && product.status === "NATIVE_CELL_SAMPLES_CONNECTED" && product.vertical_datum === "JGD2024_VERTICAL_JAPAN_DATUM_2024" && product.implicit_precedence === false && product.mosaic_applied === false && Array.isArray(product.members) && product.members.length === product.member_count && product.members.every((member) => SHA256.test(member.member_sha256) && SHA256.test(member.nested_zip_sha256))), "terrain product evidence is invalid");
  const terrainMemberHashes = new Set(terrain.products.flatMap((product) => product.members.map((member) => member.member_sha256)));
  const terrainSampleIds = new Set();
  const terrainSamplesById = new Map();
  assert(Array.isArray(terrain.samples) && terrain.samples.length > 0 && terrain.samples.every((sample) => {
    const valid = typeof sample.sample_id === "string" && sample.sample_id.length > 0 && !terrainSampleIds.has(sample.sample_id)
      && ["DEM1A", "DEM5A"].includes(sample.product)
      && Number.isFinite(sample.query_longitude) && Number.isFinite(sample.query_latitude)
      && SHA256.test(sample.member_sha256) && terrainMemberHashes.has(sample.member_sha256)
      && ["GRAPH_NODE", "EDGE_VERTEX"].includes(sample.sample_role)
      && (sample.sample_role === "GRAPH_NODE" ? typeof sample.node_id === "string" && sample.node_id.length > 0 : typeof sample.edge_id === "string" && sample.edge_id.length > 0 && Number.isInteger(sample.vertex_index) && sample.vertex_index >= 0)
      && sample.unit === "m"
      && (sample.status === "SAMPLED_NATIVE_CELL" || typeof sample.reason === "string" && sample.reason.trim().length > 0)
      && (sample.status === "SAMPLED_NATIVE_CELL" ? Number.isFinite(sample.elevation_m) : sample.elevation_m === null);
    terrainSampleIds.add(sample.sample_id);
    terrainSamplesById.set(sample.sample_id, sample);
    return valid;
  }), "terrain samples are invalid");
  const coordinateCount = (samples) => new Set(samples.map((sample) => JSON.stringify([sample.query_longitude, sample.query_latitude]))).size;
  const nullSamples = terrain.samples.filter((sample) => sample.elevation_m === null);
  assert(terrain.sample_record_count === terrain.samples.length && terrain.unique_coordinate_count === coordinateCount(terrain.samples) && terrain.numeric_record_count === terrain.samples.length - nullSamples.length && terrain.null_record_count === nullSamples.length && terrain.null_coordinate_count === coordinateCount(nullSamples), "terrain record/location summary is stale");
  assert(terrain.products.every((product) => {
    const samples = terrain.samples.filter((sample) => sample.product === product.product);
    const nulls = samples.filter((sample) => sample.elevation_m === null);
    return product.sample_count === samples.length && product.sample_record_count === samples.length && product.unique_coordinate_count === coordinateCount(samples) && product.numeric_sample_count === samples.length - nulls.length && product.null_sample_count === nulls.length && product.null_record_count === nulls.length && product.null_coordinate_count === coordinateCount(nulls);
  }), "terrain product record/location summary is stale");
  assert(terrain.edge_samples && Object.entries(terrain.edge_samples).every(([edgeId, ids]) => Array.isArray(ids) && ids.length > 0 && new Set(ids).size === ids.length && ids.every((id) => terrainSamplesById.get(id)?.sample_role === "EDGE_VERTEX" && terrainSamplesById.get(id)?.edge_id === edgeId)), "terrain edge sample references are stale");
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
    assert(Array.isArray(hazard.scenarios) && contentFingerprint(hazard.scenarios) === EXPECTED_CONTENT_FINGERPRINTS.fujisawa_enoshima.scenarios && JSON.stringify(hazard.scenarios.map((row) => row.dataset_id).sort()) === JSON.stringify(EXPECTED_FUJISAWA_SCENARIO_IDS) && hazard.scenarios.filter((row) => row.connected === true).length === 18 && hazard.scenarios.filter((row) => row.connected === false).length === 0 && hazard.scenarios.every((row) => row.aoi_scope === "enoshima_katase" && typeof row.reason === "string" && row.reason.length > 0 && row.status === "SOURCE_SIDE_EDGE_OVERLAP_CONNECTED" && row.validation_result === "SOURCE_SHA_CRS_DEFINITION_AND_AOI_SELECTION_BOUND" && ["EPSG:4612", "EPSG:6668"].includes(row.crs) && row.license_review === (row.crs === "EPSG:6668" ? "CC-BY-4.0" : "CC-BY") && (row.crs !== "EPSG:6668" || (String(row.license_note ?? "").includes("CC-BY-4.0") && (row.crs_closure?.decision === "EPSG:6677_JGD2011_ZONE_IX_PROVIDER_DECLARED" && row.crs_closure.display_geometry_source === "JIS_X_0410_MESH_CODE_EPSG_6668" && row.crs_closure.tolerance_scope === "VERIFICATION_ONLY_NOT_REGISTRY_NOT_EVALUATION" && row.crs_closure.max_vertex_error_m <= row.crs_closure.tolerance_m && row.crs_closure.erroneous_sidecar?.status === "ERRONEOUS_SIDECAR_RECORDED_NOT_USED")))), "Fujisawa earthquake/liquefaction scenario contract is stale");
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
    if (path.status === "CONNECTED") {
      assert(checklist.status === "READY_FOR_REVIEW" && checklist.candidate_distance === path.geometric_length && checklist.candidate_distance_unit === path.unit && checklist.path_reason === path.reason && checklist.rows.length > 0, "connected review checklist is stale");
    } else {
      assert(path.status === "DISCONNECTED" && checklist.status === "SUPPORTED_UNCOMPUTED" && checklist.candidate_distance === null && checklist.candidate_distance_unit === path.unit && checklist.path_reason === path.reason && typeof checklist.path_reason === "string" && checklist.path_reason.length > 0 && checklist.rows.length === 0, "disconnected review checklist is stale");
    }
    assert(checklist.safe_route_claim === false && checklist.accessibility_claim === false && checklist.admin_validated === false, "review checklist contains a forbidden claim");
    assert(Array.isArray(checklist.rows) && Array.isArray(checklist.facility?.record_ids), "review checklist rows are invalid");
    assert(checklist.rows.every((row) => Array.isArray(row.owner_candidate_types) && row.owner_candidate_types.length > 0 && Array.isArray(row.hazard_refs) && JSON.stringify([...row.hazard_refs].sort()) === JSON.stringify([...(exposureRefsByEdge.get(row.edge_id) ?? [])].sort()) && Array.isArray(row.terrain_sample_ids) && JSON.stringify([...row.terrain_sample_ids].sort()) === JSON.stringify([...(terrain.edge_samples[row.edge_id] ?? [])].sort()) && row.terrain_sample_ids.every((id) => terrainSampleIds.has(id)) && Array.isArray(row.unknowns) && new Set(row.unknowns).size === CHECKLIST_UNKNOWNS.length && JSON.stringify([...row.unknowns].sort()) === JSON.stringify([...CHECKLIST_UNKNOWNS].sort())), "review checklist contains incomplete or orphan evidence references");
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
    const actualSha = await sha256Text(text);
    assert(SHA256.test(expectedSha) && actualSha === expectedSha, "analysis bytes do not match the committed manifest");
    assert(actualSha === EXPECTED_ANALYSIS_SHA256[expectedCityId], "analysis bytes do not match the canonical delivery artifact");
    return validateDeliveryAnalysis(JSON.parse(text), expectedCityId);
  } finally {
    clearTimeout(timer);
  }
}

function flatRows(checklist, includeFacilities = true) {
  const result = [];
  const selection = {
    city_id: checklist.city_id,
    path_key: checklist.path_key,
    path_status: checklist.path_status,
    checklist_status: checklist.status,
    candidate_distance: checklist.candidate_distance,
    candidate_distance_unit: checklist.candidate_distance_unit,
    path_reason: checklist.path_reason,
    filters: canonicalJson(checklist.filters ?? {}),
    sort_by: checklist.sort_by ?? null,
    safe_route_claim: checklist.safe_route_claim,
    accessibility_claim: checklist.accessibility_claim,
    admin_validated: checklist.admin_validated,
  };
  for (const row of checklist.rows) {
    const terrainSamples = canonicalJson(row.terrain_samples ?? []);
    if (!row.hazards.length) result.push({ ...selection, row_kind: "candidate_edge", ...row, terrain_samples: terrainSamples, scenario_id: "NO_CONNECTED_HAZARD_ROW", relation: "NO_DATA", overlap_length_m: null, source_id: null, source_revision: null, source_sha256: null, source_classes: [], official_closure: null, damage_state: null, debris_present: null });
    for (const hazard of row.hazards) result.push({ ...selection, row_kind: "candidate_edge", ...row, terrain_samples: terrainSamples, ...hazard });
  }
  if (!checklist.rows.length) result.push({ ...selection, row_kind: "path_summary", edge_id: null, scenario_id: null, relation: null, overlap_length_m: null, source_id: null, source_revision: null, source_sha256: null, source_classes: [], terrain_status: checklist.terrain?.status ?? null, terrain_sampled: checklist.terrain?.sampled ?? null, terrain_reason: checklist.terrain?.reason ?? null, facility_status: checklist.facility?.status ?? null, unknowns: [...CHECKLIST_UNKNOWNS] });
  if (includeFacilities) for (const facility of checklist.facility?.records ?? []) result.push({ ...selection, row_kind: "facility", edge_id: null, scenario_id: null, relation: null, overlap_length_m: null, source_id: facility.source_id, source_revision: facility.source_version_or_valid_as_of, source_sha256: facility.source_sha256 ?? null, source_url: facility.source_url, license_status: facility.license_status, limitations: facility.limitations, source_published_at: facility.source_published_at, source_valid_as_of: facility.source_valid_as_of, source_acquired_at: facility.source_acquired_at, source_temporal_status_reason: facility.source_temporal_status_reason, source_classes: [], terrain_status: null, terrain_sampled: null, terrain_reason: null, facility_status: checklist.facility.status, unknowns: ["current_operation", "entrance", "unlock", "accessibility", "step_free", "disaster_availability"], facility_record_id: facility.facility_record_id, facility_name: facility.name, facility_address: facility.address, facility_source_attributes: canonicalJson(facility.source_attributes ?? {}), facility_source_attribute_entries: canonicalJson(facility.source_attribute_entries ?? []), current_operation_status: facility.current_operation_status, entrance_status: facility.entrance_status, unlock_status: facility.unlock_status, accessibility_status: facility.accessibility_status, step_free_status: facility.step_free_status, disaster_availability_status: facility.disaster_availability_status });
  if (includeFacilities) for (const sample of checklist.terrain_unresolved_records ?? []) result.push({ ...selection, row_kind: "terrain_unresolved", edge_id: sample.edge_id ?? null, scenario_id: null, relation: null, overlap_length_m: null, source_id: sample.source_id ?? null, source_revision: sample.source_revision ?? null, source_sha256: sample.source_sha256 ?? null, source_classes: [], reason: sample.reason, terrain_status: sample.status, terrain_sampled: false, terrain_reason: sample.reason, terrain_sample_id: sample.sample_id, terrain_product: sample.product, terrain_node_id: sample.node_id ?? null, terrain_edge_id: sample.edge_id ?? null, terrain_vertex_index: sample.vertex_index ?? null, terrain_elevation_m: sample.elevation_m, terrain_unit: sample.unit, terrain_surface_type: sample.surface_type ?? null, terrain_record_status: sample.status, unknowns: ["terrain_elevation"] });
  return result;
}

export function selectChecklistRows(hydratedRows, filters = {}, sortBy = "EDGE") {
  const scenario = filters.scenario ?? "ALL";
  const revision = filters.revision ?? "ALL";
  const coverage = filters.coverage ?? "ALL";
  const unknown = filters.unknown ?? "ALL";
  const owner = filters.owner ?? "ALL";
  const normalizedReason = String(filters.reason ?? "").trim().toLocaleLowerCase("ja");
  const filteredRows = hydratedRows.map((row) => ({
    ...row,
    hazards: row.hazards.filter((hazard) =>
      (scenario === "ALL" || hazard.scenario_id === scenario)
      && (revision === "ALL" || hazard.source_revision === revision)
      && (coverage === "ALL" || hazard.coverage_status === coverage)
      && (!normalizedReason || [hazard.reason, hazard.limitations, hazard.source_id].some((value) => String(value).toLocaleLowerCase("ja").includes(normalizedReason))),
    ),
  })).filter((row) =>
    ((scenario === "ALL" && revision === "ALL" && coverage === "ALL" && !normalizedReason) || row.hazards.length > 0)
    && (unknown === "ALL" || row.unknowns.includes(unknown))
    && (owner === "ALL" || row.owner_candidate_types.includes(owner)),
  );
  const sortValue = (row) => sortBy === "REVISION" ? row.hazards[0]?.source_revision : sortBy === "COVERAGE" ? row.hazards[0]?.coverage_status : sortBy === "REASON" ? row.hazards[0]?.reason : sortBy === "OWNER" ? row.owner_candidate_types[0] : row.edge_id;
  return [...filteredRows].sort((left, right) => String(sortValue(left) ?? "").localeCompare(String(sortValue(right) ?? ""), "ja") || left.edge_id.localeCompare(right.edge_id));
}

export function selectUnresolvedTerrainRecords(terrainSamples, terrainProduct = "ALL") {
  const records = terrainSamples.filter((sample) => sample.elevation_m === null && (terrainProduct === "ALL" || sample.product === terrainProduct));
  return {
    records,
    summary: {
      record_count: records.length,
      unique_coordinate_count: new Set(records.map((sample) => `${sample.query_longitude}\0${sample.query_latitude}`)).size,
    },
  };
}

export function checklistToCsv(checklist) {
  const columns = ["row_kind", "city_id", "path_key", "path_status", "checklist_status", "candidate_distance", "candidate_distance_unit", "path_reason", "filters", "sort_by", "safe_route_claim", "accessibility_claim", "admin_validated", "edge_id", "scenario_id", "relation", "coverage_status", "overlap_length_m", "metric_crs", "source_id", "source_revision", "source_sha256", "source_url", "license_status", "source_published_at", "source_valid_as_of", "source_acquired_at", "source_temporal_status_reason", "coverage_selection_sha256", "source_feature_ids", "source_classes", "reason", "limitations", "interpretation", "official_closure", "damage_state", "debris_present", "terrain_status", "terrain_sampled", "terrain_reason", "terrain_samples", "terrain_sample_id", "terrain_product", "terrain_node_id", "terrain_edge_id", "terrain_vertex_index", "terrain_elevation_m", "terrain_unit", "terrain_surface_type", "terrain_record_status", "facility_status", "owner_candidate_types", "facility_record_id", "facility_name", "facility_address", "facility_source_attributes", "facility_source_attribute_entries", "current_operation_status", "entrance_status", "unlock_status", "accessibility_status", "step_free_status", "disaster_availability_status", "unknowns"];
  const explicitCandidateNullColumns = new Set(["official_closure", "damage_state", "debris_present"]);
  return [columns.join(","), ...flatRows(checklist).map((row) => columns.map((column) => csvCell((row.row_kind === "candidate_edge" && explicitCandidateNullColumns.has(column) || row.row_kind === "terrain_unresolved" && column === "terrain_elevation_m") && row[column] === null ? "null" : row[column])).join(","))].join("\n") + "\n";
}

export function checklistToJson(checklist) {
  return `${JSON.stringify(checklist, null, 2)}\n`;
}

export function checklistToPrintableHtml(checklist) {
  const rows = flatRows(checklist, false).map((row) => `<tr><th>${escapeHtml(row.edge_id ?? "null")}</th><td>${escapeHtml(row.scenario_id ?? "null")}</td><td>${escapeHtml(row.relation ?? "null")} / ${escapeHtml(row.coverage_status ?? "null")}<br>${escapeHtml(row.overlap_length_m ?? "null")} m (${escapeHtml(row.metric_crs ?? "null")})</td><td>${escapeHtml(row.source_id ?? "null")}@${escapeHtml(row.source_revision ?? "null")}<br>${escapeHtml(row.source_url ?? "null")}<br>${escapeHtml(row.license_status ?? "null")}<br><code>source ${escapeHtml(row.source_sha256 ?? "null")}<br>selection ${escapeHtml(row.coverage_selection_sha256 ?? "null")}</code></td><td>${escapeHtml(row.source_feature_ids)}<br>${escapeHtml(row.source_classes)}</td><td>${escapeHtml(row.reason)}<br>${escapeHtml(row.limitations)}<br>${escapeHtml(row.interpretation)}<br>official_closure=${escapeHtml(row.official_closure ?? "null")} / damage_state=${escapeHtml(row.damage_state ?? "null")} / debris_present=${escapeHtml(row.debris_present ?? "null")}</td><td>${escapeHtml(row.terrain_status)} — ${escapeHtml(row.terrain_reason)}<br><code>${escapeHtml(canonicalJson(row.terrain_samples ?? []))}</code></td><td>${escapeHtml(row.owner_candidate_types)} / ${escapeHtml(row.unknowns)}</td></tr>`).join("");
  const facilities = (checklist.facility?.records ?? []).map((record) => `<tr><th>${escapeHtml(record.facility_record_id)}</th><td>${escapeHtml(record.name)}</td><td>${escapeHtml(record.address)}</td><td>${escapeHtml(record.source_id)} / ${escapeHtml(record.source_version_or_valid_as_of)}<br>${escapeHtml(record.source_url)} / ${escapeHtml(record.license_status)}<br>published ${escapeHtml(record.source_published_at ?? "null")} / valid-as-of ${escapeHtml(record.source_valid_as_of ?? "null")} / acquired ${escapeHtml(record.source_acquired_at ?? "null")}<br>${escapeHtml(record.source_temporal_status_reason)}<br><code>${escapeHtml(record.source_sha256 ?? "null")}</code></td><td>${escapeHtml(canonicalJson(record.source_attributes ?? {}))}<br>entries ${escapeHtml(canonicalJson(record.source_attribute_entries ?? []))}<br>${escapeHtml(record.limitations)}</td><td>current_operation=${escapeHtml(record.current_operation_status)} / entrance=${escapeHtml(record.entrance_status)} / unlock=${escapeHtml(record.unlock_status)} / accessibility=${escapeHtml(record.accessibility_status)} / step_free=${escapeHtml(record.step_free_status)} / disaster_availability=${escapeHtml(record.disaster_availability_status)}</td></tr>`).join("");
  const unresolvedTerrain = (checklist.terrain_unresolved_records ?? []).map((sample) => `<tr><th>${escapeHtml(sample.sample_id)}</th><td>${escapeHtml(sample.product)}</td><td>${escapeHtml(sample.node_id ?? "null")}</td><td>${escapeHtml(sample.edge_id ?? "null")}</td><td>null ${escapeHtml(sample.unit)}</td><td>${escapeHtml(sample.status)}</td><td>${escapeHtml(sample.reason)}</td></tr>`).join("");
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'"><title>印刷用確認リスト ${escapeHtml(checklist.checklist_id)}</title><style>body{font-family:sans-serif;margin:24px;color:#17202a}table{border-collapse:collapse;width:100%;font-size:11px}th,td{border:1px solid #777;padding:5px;text-align:left;vertical-align:top}code{overflow-wrap:anywhere}@media print{button{display:none}}</style></head><body><h1>印刷用確認リスト</h1><p><b>${escapeHtml(checklist.city_id)}</b> / ${escapeHtml(checklist.path_key)} / ${escapeHtml(checklist.path_status)} / ${escapeHtml(checklist.status)}</p><p>distance: ${escapeHtml(checklist.candidate_distance ?? "null")} ${escapeHtml(checklist.candidate_distance_unit)}<br>reason: ${escapeHtml(checklist.path_reason)}<br>filters: ${escapeHtml(canonicalJson(checklist.filters ?? {}))}<br>sort: ${escapeHtml(checklist.sort_by ?? "null")}</p><p>safe_route_claim=${escapeHtml(checklist.safe_route_claim)} / accessibility_claim=${escapeHtml(checklist.accessibility_claim)} / admin_validated=${escapeHtml(checklist.admin_validated)}<br>候補接続の確認資料です。安全性、アクセシビリティ、通行可能性、行政検証を示しません。</p><p>terrain: ${escapeHtml(checklist.terrain.status)} — ${escapeHtml(checklist.terrain.reason)}<br>facility: ${escapeHtml(checklist.facility.status)} — ${escapeHtml(checklist.facility.reason)}</p><table><thead><tr><th>edge</th><th>scenario</th><th>relation / coverage / metric overlap</th><th>source / revision / URL / license / hashes</th><th>source feature / class</th><th>reason / limitations</th><th>terrain</th><th>owner candidates / unknowns</th></tr></thead><tbody>${rows}</tbody></table><h2>未解決native-cell標高</h2><p>records ${escapeHtml(checklist.terrain_unresolved_summary?.record_count ?? 0)} / unique locations ${escapeHtml(checklist.terrain_unresolved_summary?.unique_coordinate_count ?? 0)}</p><table><thead><tr><th>sample</th><th>product</th><th>node</th><th>edge</th><th>elevation</th><th>status</th><th>reason</th></tr></thead><tbody>${unresolvedTerrain}</tbody></table><h2>公式施設原本属性</h2><table><thead><tr><th>ID</th><th>name</th><th>address</th><th>source</th><th>listed attributes</th><th>unknown runtime state</th></tr></thead><tbody>${facilities}</tbody></table></body></html>`;
}
