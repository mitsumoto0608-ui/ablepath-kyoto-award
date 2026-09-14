// Exact official catalog bindings, verified 2026-09-14. Display-only streaming;
// no individual building records or tile bytes are redistributed by AblePath.
export const PLATEAU_RECEIPT_SHA256 = "2fc1d121d88a8c9e6470a9d4ddf9d04a7da64578a198d05b85bd8fc0bbf63fba";
export const PLATEAU_SOURCE_BINDINGS = Object.freeze({
  kyoto_kiyomizu: { catalog_id: "26105_bldg_lod2", tileset_url: "https://assets.cms.plateau.reearth.io/assets/25/dd4c50-5342-4a0b-ac51-05ffb138b8b5/26100_kyoto-shi_city_2025_citygml_1_op_bldg_3dtiles_26105_higashiyama-ku_lod2/tileset.json", root_sha256: "bb6cd0c34fa411673054c3525d74b09d1cb48fc662ca2b97fdbb136498cb61ae", root_bytes: 44801 },
  kyoto_arashiyama: { catalog_id: "26108_bldg_lod2", tileset_url: "https://assets.cms.plateau.reearth.io/assets/64/cf6354-e5ff-4ee4-84d6-1751734da17c/26100_kyoto-shi_city_2025_citygml_1_op_bldg_3dtiles_26108_ukyo-ku_lod2/tileset.json", root_sha256: "332400888a9a61cb75caab75af885b5a1e5cfa66b08d56081a0f954bd941298c", root_bytes: 120022 },
  fujisawa_enoshima: { catalog_id: "14205_bldg_lod2", tileset_url: "https://assets.cms.plateau.reearth.io/assets/22/a4cda2-f741-43fb-8d75-a51b941b7577/14205_fujisawa-shi_city_2025_citygml_1_op_bldg_3dtiles_lod2/tileset.json", root_sha256: "29999d4af44f834ddf021ca53f10d73c446c449a94b5a4497825debfabe5b3d0", root_bytes: 420436 },
});
const EVIDENCE_FLAGS = ["cors_observed", "root_hash_verified", "child_content_decoded", "target_aoi_live_rendered", "post_interaction_rendered", "candidate_path_visible"];

function assertEvidence(row) {
  const binding = PLATEAU_SOURCE_BINDINGS[row?.city_id];
  if (!binding) throw new Error("PLATEAU receipt has no exact city binding");
  for (const [key, value] of Object.entries(binding)) if (row[key] !== value) throw new Error(`PLATEAU ${key} differs from the reviewed source`);
  for (const key of EVIDENCE_FLAGS) if (row[key] !== true) throw new Error(`PLATEAU receipt lacks ${key}`);
  for (const key of ["visible_tile_count", "visible_triangle_count"]) if (!Number.isInteger(row[key]) || row[key] < 1) throw new Error(`PLATEAU receipt has no non-empty ${key}`);
}

export function plateauConfigFromReceipt(row, receiptHash) {
  assertEvidence(row);
  if (receiptHash !== PLATEAU_RECEIPT_SHA256) throw new Error("PLATEAU receipt SHA-256 differs from independent live validation");
  const city = row.city_id === "fujisawa_enoshima" ? "藤沢市" : "京都市";
  return {
    available: true, data_class: "OFFICIAL_REMOTE_TILESET", source_status: "VERIFIED_SOURCE", session_status: "IDLE",
    city_id: row.city_id, source_id: row.catalog_id, source_class: "OFFICIAL", accessed_at: "2026-09-14", year: 2025, lod: "LOD2",
    tileset_url: row.tileset_url, root_sha256: row.root_sha256, root_bytes: row.root_bytes,
    license: "PDL1.0_REMOTE_VIEWING_ONLY", license_url: "https://www.mlit.go.jp/plateau/site-policy/",
    attribution: `出典：${city} 3D都市モデル（Project PLATEAU）2025年度 / 配信：国土交通省 / PDL1.0。候補経路重畳：AblePath。`,
    connected: true, requires_commercial_token: false, connection_receipt_sha256: receiptHash,
    coverage_limitations: "LOD2の建物範囲は部分的です。全回廊の建物網羅・現況・安全判定・M7証拠readyを意味しません。",
    live_validation: Object.fromEntries([...EVIDENCE_FLAGS, "visible_tile_count", "visible_triangle_count"].map((key) => [key, row[key]])),
  };
}

export function assertVerifiedPlateauSource(config, cityId) {
  if (config?.city_id !== cityId || config.source_status !== "VERIFIED_SOURCE" || config.session_status !== "IDLE") throw new Error("PLATEAU source/session scope mismatch");
  const expected = plateauConfigFromReceipt({ ...config.live_validation, ...config, catalog_id: config.source_id }, config.connection_receipt_sha256);
  if (Object.keys(config).length !== Object.keys(expected).length) throw new Error("PLATEAU connection keys differ from exact schema");
  for (const [key, value] of Object.entries(expected)) {
    if (JSON.stringify(config[key]) !== JSON.stringify(value)) throw new Error(`PLATEAU ${key} differs from validated source capability`);
  }
  return config;
}
