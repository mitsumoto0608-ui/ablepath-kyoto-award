// Rendering identity only: no routing, metric analysis, datum conversion or M7 input.
export const DISPLAY_TERRAIN = Object.freeze({
  url: "https://tile.plateauview.mlit.go.jp/terrain",
  metadata_sha256: "06c87b519cf3b4050eaf7d0fd23c637cb34f4ee96ffe137a6e1e9bcfb68c5398",
  metadata_bytes: 511,
  credit: "PLATEAU | Mapterhorn | 国土地理院",
  evidence_input: false,
  height_reference: "ELLIPSOIDAL_FIXED_GENERATION_GEOID_NOT_NATIVE_DEM",
});

export function heightMethod(feature) {
  const p = feature.properties;
  const tagged = (value) => value !== undefined && value !== null && ![false, "no", "false", "UNKNOWN", ""].includes(value);
  const nonzero = (value) => value !== null && value !== undefined && value !== "" && Number.isFinite(Number(value)) && Number(value) !== 0;
  return [p.bridge, p.bridge_tag, p.source_tags?.bridge, p.tunnel, p.tunnel_tag, p.source_tags?.tunnel].some(tagged)
    || [p.layer, p.level, p.source_tags?.layer, p.source_tags?.level].some(nonzero)
    ? "SCHEMATIC_HEIGHT_UNKNOWN_USE_2D" : "TERRAIN_PROJECTION_NOT_ROAD_HEIGHT";
}

export function selectDisplayEdges(geometry, pathIds, selectedId, showNetwork) {
  return (geometry?.features ?? []).filter((f) => showNetwork || pathIds.includes(f.properties.edge_id) || f.properties.edge_id === selectedId);
}

export function registeredPoints(geometry, ids, labelIds = ids) {
  return [...new Set(ids)].flatMap((id) => {
    if (typeof id !== "string") return [];
    const f = geometry?.features.find(({ properties: p }) => p.from_node === id || p.to_node === id);
    if (!f) return [];
    const coordinates = f.properties.from_node === id ? f.geometry.coordinates[0] : f.geometry.coordinates.at(-1);
    return [{ id, label: labelIds.includes(id) ? `地点${String.fromCharCode(65 + labelIds.indexOf(id))}` : "登録地点", coordinates }];
  });
}

// Camera framing only. A disconnected pair frames its existing endpoints;
// it never acquires a line or a path from an unrelated fixture.
export function cameraCoordinates(geometry, scope, pathIds, selectedId, nodeIds) {
  const features = (geometry?.features ?? []).filter((f) => scope === "all" || (scope === "segment" ? f.properties.edge_id === selectedId : pathIds.includes(f.properties.edge_id)));
  return features.length ? features.flatMap((f) => f.geometry.coordinates) : registeredPoints(geometry, nodeIds).map((p) => p.coordinates);
}

export function photoBackground(cityId) {
  return cityId === "fujisawa_enoshima"
    ? { url: "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg", maximumLevel: 18, credit: "地理院タイル（全国最新写真）／国土地理院", label: "地理院写真 · 撮影時点は場所により異なる" }
    : { url: "https://tile.plateauview.mlit.go.jp/tiles/ortho-2022/{z}/{x}/{y}.png", maximumLevel: 22, credit: "PLATEAU／京都市（2022提供年度）", label: "京都正射画像 · 2022提供年度（撮影年とは異なる）" };
}
