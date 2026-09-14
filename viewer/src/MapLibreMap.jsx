import { useEffect, useRef, useState } from "react";
import { Map, NavigationControl, setWorkerUrl } from "maplibre-gl";
import mapWorkerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import "maplibre-gl/dist/maplibre-gl.css";
import { filterHazardDisplayFeatures, isHazardDisplayFeature } from "./workspaceSelection.mjs";

const MAP_DATA_TIMEOUT_MS = 5_000;
// MapLibre v6's worker imports its shared sibling; Vite must bundle both.
// Plain ?url would copy only the entry and strand GeoJSON loads in production.
setWorkerUrl(mapWorkerUrl);

function validateRuntimeGeoJson(value, config) {
  if (value?.type !== "FeatureCollection" || !Array.isArray(value.features) || value.features.length !== config.feature_count) {
    throw new Error("実座標artifactのfeature数がbuild済みmanifestと一致しません");
  }
  for (const feature of value.features) {
    const properties = feature?.properties;
    if (
      feature?.geometry?.type !== "LineString"
      || properties?.geometry_status !== "SOURCE_TRACEABLE_REAL"
      || properties?.topology_status !== "CANDIDATE"
    ) {
      throw new Error(`実座標edge ${properties?.edge_id ?? "unknown"} がCANDIDATE / UNKNOWN契約を満たしません`);
    }
  }
  return value;
}

export async function loadGeoJson(config) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), MAP_DATA_TIMEOUT_MS);
  try {
    const response = await fetch(config.data_path, { signal: controller.signal });
    if (!response.ok) throw new Error(`実座標artifactの取得に失敗しました（HTTP ${response.status}）`);
    const bytes = await response.arrayBuffer();
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), (value) => value.toString(16).padStart(2, "0")).join("");
    if (digest !== config.copied_sha256) throw new Error("実座標artifactのSHA-256がmanifestと一致しません");
    return validateRuntimeGeoJson(JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes)), config);
  } catch (error) {
    if (error?.name === "AbortError") throw new Error("実座標artifactの取得がタイムアウトしました");
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

async function loadOfficialOverlay(config, kind) {
  if (!config) return null;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), MAP_DATA_TIMEOUT_MS);
  try {
    const response = await fetch(config.data_path, { signal: controller.signal });
    if (!response.ok) throw new Error(`${kind} artifactの取得に失敗しました（HTTP ${response.status}）`);
    const bytes = await response.arrayBuffer();
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), (value) => value.toString(16).padStart(2, "0")).join("");
    if (digest !== config.copied_sha256) throw new Error(`${kind} display bytes differ from the source-bound receipt`);
    const value = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
    if (value?.type !== "FeatureCollection" || !Array.isArray(value.features) || value.features.length !== config.feature_count) throw new Error(`${kind} artifactのfeature数がbuild receiptと一致しません`);
    for (const feature of value.features) {
      if (kind === "hazard") {
        if (!isHazardDisplayFeature(feature, config)) throw new Error("hazard display artifactがfail-closed契約を満たしません");
      } else if (feature?.geometry?.type !== "Point" || feature?.properties?.coordinate_method !== "SOURCE_PROVIDED_LONGITUDE_LATITUDE" || feature?.properties?.silent_geocoding !== false) {
        throw new Error("facility display artifactがsource-coordinate契約を満たしません");
      }
    }
    return value;
  } finally {
    clearTimeout(timer);
  }
}

async function loadOfficialOverlays(configs, kind) {
  const list = Array.isArray(configs) ? configs : configs ? [configs] : [];
  if (!list.length) return null;
  const loaded = await Promise.all(list.map((config) => loadOfficialOverlay(config, kind)));
  return { type: "FeatureCollection", features: loaded.flatMap((value) => value.features) };
}

function RealEdgeDetails({ feature, m7Readiness }) {
  if (!feature) return <p className="real-edge-empty">地図または表から候補edgeを選択すると、source属性を確認できます。</p>;
  const properties = feature.properties;
  return (
    <dl className="real-edge-details" aria-label="選択した実座標候補edge">
      <div><dt>edge ID</dt><dd><code>{properties.edge_id}</code></dd></div>
      <div><dt>geometry</dt><dd>{properties.geometry_status}</dd></div>
      <div><dt>graph</dt><dd>{properties.topology_status}</dd></div>
      <div><dt>accessibility</dt><dd>{properties.accessibility_state} — M6 NOT_COMPUTED</dd></div>
      <div><dt>operation</dt><dd>{properties.operation_status}</dd></div>
      <div><dt>source feature</dt><dd><code>{properties.source_feature_id}</code></dd></div>
      <div><dt>M7 status</dt><dd>{m7Readiness?.status ?? "NOT_COMPUTED"}</dd></div>
      <div><dt>M7 result</dt><dd>{String(m7Readiness?.m7_result ?? null)}</dd></div>
      <div><dt>M7 missing fields</dt><dd>{m7Readiness?.missing_fields?.join(", ") ?? "—"}</dd></div>
      <div><dt>M7 reason</dt><dd>{m7Readiness?.reason ?? "Required source-traceable M7 inputs are incomplete."}</dd></div>
      {Object.entries(m7Readiness?.field_resolution ?? {}).map(([field, resolution]) => <div key={field}><dt>{field} evidence</dt><dd>{resolution.evidence_candidates.join(" / ")}。次: {resolution.next_acquisition_method}</dd></div>)}
    </dl>
  );
}

export function MapLibreMap({ config, geometry, conditions = { scenario: "ALL", revision: "ALL" }, officialLayers = {}, selectedEdgeId, selectedPathEdgeIds = [], m7Readiness = [], onSelectEdge, onAnnouncement }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const [geojson, setGeojson] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [rendererError, setRendererError] = useState("");
  const [basemapState, setBasemapState] = useState("LOADING");
  const [overlayReady, setOverlayReady] = useState(false);
  const [visibleCandidateFragments, setVisibleCandidateFragments] = useState(0);
  const [officialOverlays, setOfficialOverlays] = useState({ hazard: null, facility: null });
  const selectionRef = useRef({ selectedEdgeId, selectedPathEdgeIds, conditions });
  selectionRef.current = { selectedEdgeId, selectedPathEdgeIds, conditions };

  useEffect(() => {
    let active = true;
    setLoadError("");
    if (geometry !== undefined) { setGeojson(geometry); return undefined; }
    loadGeoJson(config)
      .then((loaded) => {
        if (!active) return;
        setGeojson(loaded);
      })
      .catch((error) => active && setLoadError(error.message));
    return () => { active = false; };
  }, [config, geometry]);

  useEffect(() => {
    let active = true;
    Promise.all([loadOfficialOverlays(officialLayers.hazard, "hazard"), loadOfficialOverlay(officialLayers.facility, "facility")])
      .then(([hazard, facility]) => {
        if (active) setOfficialOverlays({ hazard, facility });
      })
      .catch((error) => active && setLoadError(error.message));
    return () => { active = false; };
  }, [officialLayers.hazard, officialLayers.facility]);

  useEffect(() => {
    if (!geojson || !containerRef.current) return undefined;
    setOverlayReady(false);
    setVisibleCandidateFragments(0);
    setRendererError("");
    setBasemapState("LOADING");
    let map;
    try {
      map = new Map({
        container: containerRef.current,
        style: {
          version: 8,
          sources: {},
          layers: [{ id: "local-background", type: "background", paint: { "background-color": "#dce6de" } }],
        },
        attributionControl: false,
        renderWorldCopies: false,
      });
      if (!map.getCanvas().getContext("webgl2")) throw new Error("WebGL2 renderer unavailable; use the candidate table");
      mapRef.current = map;
      map.addControl(new NavigationControl({ showCompass: false }), "top-right");
      map.on("load", () => {
        if (officialOverlays.hazard) {
          map.addSource("official-hazard", { type: "geojson", data: officialOverlays.hazard });
          map.addLayer({ id: "official-hazard-fill", type: "fill", source: "official-hazard", paint: { "fill-color": "#3b82c4", "fill-opacity": 0.22, "fill-outline-color": "#235a87" } });
        }
        if (officialOverlays.facility) {
          map.addSource("official-facilities", { type: "geojson", data: officialOverlays.facility });
          map.addLayer({ id: "official-facility-points", type: "circle", source: "official-facilities", paint: { "circle-radius": 5, "circle-color": "#7a3e9d", "circle-stroke-color": "#ffffff", "circle-stroke-width": 1.5 } });
        }
        map.addSource("candidate-edges", { type: "geojson", data: geojson, generateId: false });
        map.addLayer({
          id: "candidate-edges-line",
          type: "line",
          source: "candidate-edges",
          paint: { "line-color": "#ffb000", "line-width": 5, "line-opacity": 0.94 },
        });
        map.addLayer({ id: "candidate-path-line", type: "line", source: "candidate-edges", filter: ["in", ["get", "edge_id"], ["literal", selectionRef.current.selectedPathEdgeIds]], paint: { "line-color": "#2466bc", "line-width": 7, "line-opacity": 0.96 } });
        map.addLayer({ id: "selected-edge-line", type: "line", source: "candidate-edges", filter: ["==", ["get", "edge_id"], selectionRef.current.selectedEdgeId ?? ""], paint: { "line-color": "#153964", "line-width": 10 } });
        map.addLayer({
          id: "candidate-edges-hit",
          type: "line",
          source: "candidate-edges",
          paint: { "line-color": "#ffffff", "line-width": 18, "line-opacity": 0.01 },
        });
        map.fitBounds(config.bounds, { padding: 42, duration: 0, maxZoom: 17 });
        map.addSource("osm-raster", {
          type: "raster",
          tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize: 256,
          attribution: config.attribution,
        });
        map.addLayer(
          { id: "osm-basemap", type: "raster", source: "osm-raster", minzoom: 0, maxzoom: 19 },
          officialOverlays.hazard ? "official-hazard-fill" : officialOverlays.facility ? "official-facility-points" : "candidate-edges-line",
        );
        map.on("click", "candidate-edges-hit", (event) => {
          const edgeId = event.features?.[0]?.properties?.edge_id;
          if (edgeId) {
            onSelectEdge(edgeId);
            onAnnouncement(`${edgeId}の実座標候補edgeを選択しました`);
          }
        });
        map.on("mouseenter", "candidate-edges-hit", () => { map.getCanvas().style.cursor = "pointer"; });
        map.on("mouseleave", "candidate-edges-hit", () => { map.getCanvas().style.cursor = ""; });
      });
      map.on("idle", () => {
        setBasemapState((current) => current === "DEGRADED" ? current : "AVAILABLE");
      });
      // A failed raster can keep the whole map from becoming idle. Candidate
      // proof belongs to its rendered frame, independently of the basemap.
      map.on("render", () => {
        if (map.getLayer("candidate-edges-line")) setVisibleCandidateFragments(map.queryRenderedFeatures({ layers: ["candidate-edges-line"] }).length);
      });
      map.on("sourcedata", (event) => {
        if (event.sourceId === "candidate-edges" && event.isSourceLoaded) setOverlayReady(true);
      });
      map.on("error", (event) => {
        if (event?.sourceId === "osm-raster") {
          setBasemapState("DEGRADED");
          onAnnouncement("背景地図の通信に失敗しました。ローカル候補edgeと表は継続表示します");
        } else {
          setRendererError(event?.error?.message ?? "Map source rendering failed");
          onAnnouncement("地図の描画に失敗しました。候補区間の表と証拠情報を利用してください");
        }
      });
    } catch (error) {
      setRendererError(error.message);
      onAnnouncement("MapLibreを開始できないため、実座標の表形式代替を表示します");
      // A failed WebGL constructor can return a partially initialized Map.
      // Its resize/remove must not take down the evidence and export UI.
      try { map?.remove(); } catch { containerRef.current?.replaceChildren(); }
      mapRef.current = null;
      return undefined;
    }
    const resize = new ResizeObserver(() => {
      try { map.resize(); } catch (error) { setRendererError(error.message); }
    });
    if (containerRef.current) resize.observe(containerRef.current);
    return () => {
      resize.disconnect();
      mapRef.current = null;
      if (map && !map._removed) { try { map.remove(); } catch { containerRef.current?.replaceChildren(); } }
    };
  }, [config, geojson, officialOverlays, onAnnouncement, onSelectEdge]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return undefined;
    const update = () => {
      if (!map.getLayer("candidate-path-line")) return;
      map.setFilter("candidate-path-line", ["in", ["get", "edge_id"], ["literal", selectedPathEdgeIds]]);
      map.setFilter("selected-edge-line", ["==", ["get", "edge_id"], selectedEdgeId ?? ""]);
      if (map.getLayer("official-hazard-fill")) {
        map.getSource("official-hazard").setData({ ...officialOverlays.hazard, features: filterHazardDisplayFeatures(officialOverlays.hazard.features, conditions, officialLayers.sourceCatalog) });
      }
    };
    update(); map.on("load", update);
    return () => { if (!map._removed) map.off("load", update); };
  }, [selectedEdgeId, selectedPathEdgeIds, conditions.scenario, conditions.revision, geojson, officialOverlays, officialLayers.sourceCatalog]);

  const selectedFeature = geojson?.features.find((feature) => feature.properties.edge_id === selectedEdgeId) ?? null;
  if (loadError) {
    return <section className="map-fail-closed" role="alert"><h2>実座標layerを開始できません</h2><p>{loadError}</p><p>設定済みartifactの欠落を合成図へ自動置換せず停止しました。</p></section>;
  }

  return (
    <section className="real-map-shell" aria-labelledby="real-map-title">
      <div className="map-toolbar">
        <div><p className="eyebrow">MAPLIBRE / SOURCE-TRACEABLE COORDINATES</p><h2 id="real-map-title">実座標候補graph</h2></div>
        <span className="status-badge status-real">REAL COORDINATES / CANDIDATE</span>
      </div>
      <details className="map-provenance"><summary>候補geometryの出典・通信状態</summary><div className="layer-facts" aria-label="実座標layer provenance">
        <span>source {config.source_class}</span><span>geometry {config.data_class}</span><span>{config.geometry_status}</span>
        <span>{config.topology_status}</span><span>continuity {config.route_continuity}</span><span>{config.snapshot_at}</span>
      </div>
      </details>
      <div className="map-runtime-status" role="status" data-visible-candidate-fragments={visibleCandidateFragments}>
        <span>background {basemapState}</span><span>candidate overlay {rendererError ? "DEGRADED_TABLE_AVAILABLE" : overlayReady ? "AVAILABLE" : "LOADING"}</span><span>official hazard {officialOverlays.hazard ? `AVAILABLE (${officialOverlays.hazard.features.length})` : "NOT_CONNECTED"}</span><span>official facilities {officialOverlays.facility ? `AVAILABLE (${officialOverlays.facility.features.length})` : "NOT_CONNECTED"}</span>
      </div>
      {rendererError && <div className="map-renderer-warning" role="alert">MapLibre renderer: {rendererError}。表形式代替は利用できます。</div>}
      <div ref={containerRef} className="maplibre-canvas" aria-label="MapLibre実座標地図。操作の代替として直後のedge表を利用できます" />
      <p className="map-caption">固定OSM snapshot由来の座標です。候補network connectivity onlyであり、accessibility・safety・operationはunconfirmedです。</p>
      <p className="map-attribution">
        <a href={config.copyright_url} target="_blank" rel="noreferrer">© OpenStreetMap contributors</a>
        {" / Data available under "}
        <a href={config.license_url} target="_blank" rel="noreferrer">ODbL 1.0</a>
      </p>
      <details className="map-table-disclosure"><summary>区間一覧・原典属性（地図の操作代替）</summary>
      <RealEdgeDetails feature={selectedFeature} m7Readiness={m7Readiness.find((row) => row.edge_id === selectedFeature?.properties?.edge_id)} />
      <div id="edge-table" className="table-scroll" tabIndex="-1" aria-label="実座標候補edgeの表形式代替">
        <table>
          <caption>実座標候補edge（全件 CANDIDATE / UNKNOWN）</caption>
          <thead><tr><th scope="col">edge ID</th><th scope="col">source way</th><th scope="col">状態</th><th scope="col">操作</th></tr></thead>
          <tbody>{geojson?.features.map((feature) => {
            const properties = feature.properties;
            return <tr key={properties.edge_id} className={properties.edge_id === selectedEdgeId ? "active-row" : ""}><th scope="row"><code>{properties.edge_id}</code></th><td><code>{properties.source_feature_id}</code></td><td>CANDIDATE / UNKNOWN</td><td><button type="button" onClick={() => { onSelectEdge(properties.edge_id); onAnnouncement(`${properties.edge_id}の実座標候補edgeを選択しました`); }}>属性を表示</button></td></tr>;
          })}</tbody>
        </table>
      </div>
      <p className="map-caption">描画中の候補線fragment: {visibleCandidateFragments}（画面内の描画単位。独立edge数ではありません）</p>
      </details>
    </section>
  );
}
