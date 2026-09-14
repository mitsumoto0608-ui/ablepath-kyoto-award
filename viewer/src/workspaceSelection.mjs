// Selection and exact record lookup only. No graph, metric, hazard or M7 computation.
export const DEFAULT_CONDITIONS = Object.freeze({ scenario: "ALL", revision: "ALL", coverage: "ALL", unknown: "ALL", owner: "ALL", reasonQuery: "", sortBy: "EDGE", terrainProduct: "ALL" });

export function readWorkspaceSelection(analysis, search) {
  const params = new URLSearchParams(search);
  const requested = [params.get("from"), params.get("to")];
  const nodes = requested.every((id) => analysis.selectable_node_ids.includes(id)) && analysis.path_matrix[requested.join("__")]
    ? requested : [analysis.path_fixture.start_node_id, analysis.path_fixture.end_node_id];
  const conditions = { ...DEFAULT_CONDITIONS };
  for (const key of Object.keys(conditions)) {
    const value = params.get(key);
    if (value !== null && value.length <= 256) conditions[key] = value;
  }
  if (!["EDGE", "REVISION", "COVERAGE", "REASON", "OWNER"].includes(conditions.sortBy)) conditions.sortBy = "EDGE";
  if (!["ALL", "DEM1A", "DEM5A", "DEM5B"].includes(conditions.terrainProduct)) conditions.terrainProduct = "ALL";
  return { nodes, conditions };
}

export function serializeWorkspaceSelection(search, nodes, conditions) {
  const params = new URLSearchParams(search);
  if (nodes.every(Boolean)) { params.set("from", nodes[0]); params.set("to", nodes[1]); }
  for (const [key, value] of Object.entries(conditions)) {
    if (value !== DEFAULT_CONDITIONS[key]) params.set(key, value);
  }
  return `?${params.toString()}`;
}

export function selectSegmentEvidence(feature, evidence, conditions) {
  if (!feature) return { terrain: [], hazards: [], readiness: null };
  const p = feature.properties;
  const nodeIds = [p.from_node, p.to_node].filter((id) => typeof id === "string" && id.length > 0);
  return {
    terrain: (evidence?.terrain?.samples ?? []).filter((row) => (row.edge_id === p.edge_id || nodeIds.includes(row.node_id)) && (conditions.terrainProduct === "ALL" || row.product === conditions.terrainProduct)),
    hazards: (evidence?.hazard?.edge_exposures ?? []).filter((row) => row.edge_id === p.edge_id && (conditions.scenario === "ALL" || row.scenario_id === conditions.scenario) && (conditions.revision === "ALL" || row.source_revision === conditions.revision)),
    readiness: (evidence?.m7?.kyoto_deep_pilot_edges ?? []).find((row) => row.edge_id === p.edge_id) ?? null,
  };
}

// Display-only identity lookup. A31b's original copy predates generic source_id
// properties; preserve its bytes and use its exact existing AOI/layer metadata.
// No class mapping, threshold, overlap, union, or route calculation occurs here.
export function isHazardDisplayFeature(feature, config) {
  const p = feature?.properties;
  // The byte-bound manifest owns display scope. Some retained Fujisawa rows
  // use source/scenario identities, not Kyoto's redundant per-feature marker.
  const scoped = p?._ablepath_display_only === true || (p?._ablepath_display_only === undefined
    && [p?.source_id, p?.scenario_id, p?.source_feature_id].every((id) => typeof id === "string" && id.length > 0));
  return config?.display_only === true && ["Polygon", "MultiPolygon"].includes(feature?.geometry?.type) && scoped
    && !["official_closure", "damage_state", "debris_present", "setback_m"].some((field) => Object.hasOwn(p, field));
}

export function filterHazardDisplayFeatures(features, conditions, sourceCatalog) {
  return features.filter(({ properties: p }) => {
    const a31b = ["kiyomizu_gion", "arashiyama"].includes(p._ablepath_aoi_id)
      && ["A31b-10", "A31b-20", "A31b-30", "A31b-41", "A31b-42"].includes(p._ablepath_layer_id);
    const sourceId = p.source_id ?? (a31b ? "nlni_a31b_2025_kyoto_flood" : null);
    const scenarioId = p.scenario_id ?? (a31b ? `A31B_FLOOD_2025_${p._ablepath_aoi_id}_${p._ablepath_layer_id}` : null);
    return (conditions.scenario === "ALL" || conditions.scenario === scenarioId)
      && (conditions.revision === "ALL" || conditions.revision === sourceCatalog?.[sourceId]?.source_revision);
  });
}
