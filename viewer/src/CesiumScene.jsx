import { useEffect, useRef, useState } from "react";
import {
  CesiumTerrainProvider, Cartographic, BoundingSphere, ClassificationType, HeightReference,
  PolygonHierarchy, PolylineDashMaterialProperty, Cartesian2, LabelStyle, sampleTerrain,
  Viewer,
  Cartesian3, Color, HeadingPitchRange, Matrix4, PolylineOutlineMaterialProperty,
  ScreenSpaceEventHandler, ScreenSpaceEventType, UrlTemplateImageryProvider,
} from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";

import { installCesiumFailureListeners, withTimeout } from "./mapAsync.mjs";
import { loadTilesetForSession, loadTerrainForSession } from "./plateauResource.mjs";
import { DISPLAY_TERRAIN, heightMethod, registeredPoints, selectDisplayEdges, photoBackground, cameraCoordinates } from "./displayScene.mjs";
import { loadOfficialOverlays } from "./MapLibreMap.jsx";
import { filterHazardDisplayFeatures, hazardDisplayIdentity } from "./workspaceSelection.mjs";

const DEFAULT_TILESET_TIMEOUT_MS = 12_000;

function runtimeTimeout() {
  const requested = Number(globalThis.__ABLEPATH_CESIUM_TIMEOUT_MS__);
  return Number.isFinite(requested) && requested >= 50 && requested <= DEFAULT_TILESET_TIMEOUT_MS
    ? requested
    : DEFAULT_TILESET_TIMEOUT_MS;
}

export default function CesiumScene({ config, geometry, bounds, selectedEdgeId, selectedPathEdgeIds = [], selectedNodeIds = [], registeredNodeIds = [], conditions, hazardLayers = [], sourceCatalog, showNetwork = false, cameraRequest, onSelectEdge, onConnected, onVisible, onFailure }) {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);
  const callbacks = useRef({ onSelectEdge, onVisible });
  callbacks.current = { onSelectEdge, onVisible };
  const [sceneReady, setSceneReady] = useState(false);
  const [visibleTiles, setVisibleTiles] = useState(0);
  const [visibleTriangles, setVisibleTriangles] = useState(0);
  const [renderedFrames, setRenderedFrames] = useState(0);
  const [terrainReady, setTerrainReady] = useState(false);
  const [terrainMeshLoaded, setTerrainMeshLoaded] = useState(false);
  const [hazards, setHazards] = useState(null);
  const [hazardError, setHazardError] = useState("");
  const [background, setBackground] = useState("map");
  const [backgroundError, setBackgroundError] = useState("");
  const viewSelection = useRef({ geometry, selectedEdgeId, selectedPathEdgeIds, selectedNodeIds });
  viewSelection.current = { geometry, selectedEdgeId, selectedPathEdgeIds, selectedNodeIds };
  const cameraTarget = useRef(null);
  const cameraSequence = useRef(0);

  async function fitCamera(scope = "path", top = false) {
    const viewer = viewerRef.current;
    if (!viewer || viewer.isDestroyed() || !terrainReady) return;
    const sequence = ++cameraSequence.current;
    const selection = viewSelection.current;
    const coordinates = cameraCoordinates(selection.geometry, scope, selection.selectedPathEdgeIds, selection.selectedEdgeId, selection.selectedNodeIds);
    if (!coordinates.length) return;
    const positions = coordinates.map(([lon, lat]) => Cartographic.fromDegrees(lon, lat));
    try {
      // Display terrain sampling only; these objects never enter analysis/export state.
      const samples = await withTimeout(sampleTerrain(viewer.terrainProvider, 14, positions), 12_000, "表示範囲の地形を取得できません");
      if (sequence !== cameraSequence.current || viewer.isDestroyed()) return;
      if (samples.some((p) => !Number.isFinite(p.height))) throw new Error("対象範囲の表示terrain高さが未取得です");
      const sphere = BoundingSphere.fromPoints(samples.map((p) => Cartesian3.fromRadians(p.longitude, p.latitude, p.height)));
      cameraTarget.current = sphere;
      const aspect = viewer.scene.canvas.clientWidth / viewer.scene.canvas.clientHeight;
      // Lens framing parameters only, not source/scientific constants.
      const fov = Math.min(viewer.camera.frustum.fovy, 2 * Math.atan(Math.tan(viewer.camera.frustum.fovy / 2) * aspect));
      const range = Math.max(sphere.radius, 25) / Math.sin(fov / 2) * 1.35;
      viewer.camera.lookAt(sphere.center, new HeadingPitchRange(0, top ? -Math.PI / 2 : -0.65, range));
      viewer.camera.lookAtTransform(Matrix4.IDENTITY);
      viewer.scene.requestRender();
    } catch (error) { if (!viewer.isDestroyed() && sequence === cameraSequence.current) onFailure(error.message); }
  }

  function cameraControl(action) {
    const viewer = viewerRef.current;
    if (!viewer || viewer.isDestroyed() || !cameraTarget.current) return;
    const camera = viewer.camera;
    const range = Cartesian3.distance(camera.positionWC, cameraTarget.current.center);
    if (action === "zoom-in") camera.moveForward(range * 0.2);
    else if (action === "zoom-out") camera.moveBackward(range * 0.2);
    else if (action === "pan-left") camera.moveLeft(range * 0.15);
    else if (action === "pan-right") camera.moveRight(range * 0.15);
    else if (action === "pan-up") camera.moveUp(range * 0.15);
    else if (action === "pan-down") camera.moveDown(range * 0.15);
    else {
      const heading = action === "rotate" ? camera.heading + Math.PI / 8 : camera.heading;
      const pitch = action === "tilt" ? (camera.pitch > -0.4 ? -1.2 : camera.pitch + 0.2) : camera.pitch;
      camera.lookAt(cameraTarget.current.center, new HeadingPitchRange(heading, pitch, range));
      camera.lookAtTransform(Matrix4.IDENTITY);
    }
    viewer.scene.requestRender();
  }

  useEffect(() => {
    let active = true;
    let viewer;
    let failureListeners;
    let contentDeadline;
    let clickHandler;
    const removers = [];
    const controller = new AbortController();
    let failed = false;
    const failOnce = (reason) => {
      if (!active || failed) return;
      failed = true;
      controller.abort();
      onFailure(reason);
    };
    try {
      viewer = new Viewer(containerRef.current, {
        animation: false,
        baseLayer: false,
        baseLayerPicker: false,
        fullscreenButton: false,
        geocoder: false,
        homeButton: false,
        infoBox: false,
        navigationHelpButton: false,
        sceneModePicker: false,
        selectionIndicator: false,
        timeline: false,
        requestRenderMode: false,
        skyBox: false,
        skyAtmosphere: false,
      });
      viewerRef.current = viewer;
      viewer.targetFrameRate = 30;
      viewer.scene.globe.baseColor = Color.fromCssColorString("#e8edf2");
      viewer.scene.backgroundColor = Color.fromCssColorString("#eef3f8");
      viewer.scene.globe.enableLighting = false;
      viewer.scene.globe.depthTestAgainstTerrain = true;
      setSceneReady(true);
      clickHandler = new ScreenSpaceEventHandler(viewer.scene.canvas);
      clickHandler.setInputAction((event) => {
        const entity = viewer.scene.pick(event.position)?.id;
        if (entity?.id?.startsWith("candidate:")) callbacks.current.onSelectEdge?.(entity.id.slice("candidate:".length));
      }, ScreenSpaceEventType.LEFT_CLICK);
      const loadTerrain = async () => {
        const provider = await loadTerrainForSession({ signal: controller.signal, isActive: () => active && !failed });
        if (!active || failed || viewer.isDestroyed()) return;
        viewer.terrainProvider = provider;
        removers.push(provider.errorEvent.addEventListener(() => failOnce("表示terrain配信エラー。楕円体を実地形とは扱わず2Dへ戻ります")));
        const center = Cartographic.fromDegrees((bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2);
        const samples = await sampleTerrain(provider, 14, [center]);
        if (!Number.isFinite(samples[0].height)) throw new Error("対象AOIの表示terrain contentがありません");
        if (active && !failed) setTerrainReady(true);
      };
      withTimeout(
        loadTilesetForSession(config, { signal: controller.signal, isActive: () => active && !failed }),
        runtimeTimeout(),
        "PLATEAU tilesetの通信がタイムアウトしました",
      ).then(async (tileset) => {
        if (!active || viewer.isDestroyed()) { if (!tileset.isDestroyed()) tileset.destroy(); return; }
        // The synthetic root-only harness has no hash-bound production source
        // and proves metadata lifecycle only. It never proves terrain/VISIBLE.
        if (config.root_sha256) {
          try { await withTimeout(loadTerrain(), runtimeTimeout(), "表示terrainの通信がタイムアウトしました"); }
          catch (error) { if (!tileset.isDestroyed()) tileset.destroy(); throw error; }
        }
        if (!active || failed || viewer.isDestroyed()) { if (!tileset.isDestroyed()) tileset.destroy(); return; }
        failureListeners = installCesiumFailureListeners({
          tileset,
          scene: viewer.scene,
          onFailure: failOnce,
        });
        viewer.scene.primitives.add(tileset);
        if (config.root_sha256) contentDeadline = setTimeout(() => failOnce("対象範囲の非空tile contentを30秒以内に描画できませんでした"), 30_000);
        let frameTiles = 0;
        let frameTriangles = 0;
        let frames = 0;
        let lastSignature = "";
        removers.push(viewer.scene.preRender.addEventListener(() => { frameTiles = 0; frameTriangles = 0; }));
        removers.push(tileset.tileVisible.addEventListener((tile) => {
          const triangles = tile.content?.trianglesLength ?? 0;
          if (triangles > 0) { frameTiles += 1; frameTriangles += triangles; }
        }));
        removers.push(viewer.scene.postRender.addEventListener(() => {
          if (!active || failed) return;
          frames += 1;
          if (frameTiles > 0) clearTimeout(contentDeadline);
          const signature = `${frameTiles}:${frameTriangles}`;
          if (signature !== lastSignature || frames % 30 === 0) {
            setVisibleTiles(frameTiles); setVisibleTriangles(frameTriangles); setRenderedFrames(frames);
            if (bounds) {
              const center = Cartographic.fromDegrees((bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2);
              setTerrainMeshLoaded(viewer.terrainProvider instanceof CesiumTerrainProvider && Number.isFinite(viewer.scene.globe.getHeight(center)));
            }
            callbacks.current.onVisible?.({ visible_tiles: frameTiles, visible_triangles: frameTriangles, rendered_frames: frames });
            lastSignature = signature;
          }
        }));
        if (!bounds) await viewer.zoomTo(tileset);
        if (active && !failed && !failureListeners.hasFailed()) onConnected();
      }).catch((error) => {
        failOnce(error.message);
      });
    } catch (error) {
      failOnce(error.message);
    }
    return () => {
      active = false;
      cameraSequence.current += 1;
      controller.abort();
      clearTimeout(contentDeadline);
      viewerRef.current = null;
      removers.forEach((remove) => remove());
      clickHandler?.destroy();
      failureListeners?.remove();
      if (viewer && !viewer.isDestroyed()) viewer.destroy();
    };
  }, [config, bounds, onConnected, onFailure]);

  useEffect(() => { if (terrainReady) fitCamera(cameraRequest ? "segment" : "path"); }, [terrainReady, geometry, selectedPathEdgeIds, selectedNodeIds]);
  useEffect(() => { if (cameraRequest) fitCamera("segment"); }, [cameraRequest]);
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!sceneReady || !viewer || viewer.isDestroyed()) return undefined;
    setBackgroundError("");
    const options = background === "photo" ? photoBackground(config.city_id) : { url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png", maximumLevel: 19, credit: "© OpenStreetMap contributors / ODbL 1.0（淡色表示）" };
    viewer.imageryLayers.removeAll();
    const provider = new UrlTemplateImageryProvider(options);
    const layer = viewer.imageryLayers.addImageryProvider(provider);
    if (background === "map") { layer.saturation = 0.35; layer.brightness = 1.05; }
    const remove = provider.errorEvent.addEventListener(() => setBackgroundError("背景画像の一部が未取得です。空白はcoverage・通信不足であり、対象物なしを意味しません。"));
    return remove;
  }, [sceneReady, background, config.city_id]);

  useEffect(() => {
    let active = true;
    setHazards(null); setHazardError("");
    loadOfficialOverlays(hazardLayers, "hazard").then((value) => { if (active) setHazards(value); }).catch((error) => { if (active) setHazardError(error.message); });
    return () => { active = false; };
  }, [hazardLayers]);

  useEffect(() => {
    const viewer = viewerRef.current;
    if (!terrainReady || !viewer || viewer.isDestroyed() || !hazards) return undefined;
    const entities = [];
    const visible = conditions?.scenario === "ALL" ? [] : filterHazardDisplayFeatures(hazards.features, conditions, sourceCatalog);
    visible.forEach((f) => {
      const identity = hazardDisplayIdentity(f);
      const polygons = f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates;
      polygons.forEach((rings, part) => {
        const ring = (coordinates) => coordinates.map(([lon, lat]) => Cartesian3.fromDegrees(lon, lat));
        entities.push(viewer.entities.add({ id: `hazard:${identity.sourceId}:${identity.scenarioId}:${identity.featureId}:${part}`, properties: { ...f.properties, source_revision: sourceCatalog?.[identity.sourceId]?.source_revision ?? null }, polygon: {
          hierarchy: new PolygonHierarchy(ring(rings[0]), rings.slice(1).map((hole) => new PolygonHierarchy(ring(hole)))),
          material: Color.fromCssColorString("#a653a8").withAlpha(0.22),
          classificationType: ClassificationType.TERRAIN,
          // Undefined height/extrudedHeight makes a ground polygon; do not
          // interpret source hazard classes as an altitude or water surface.
        } }));
      });
    });
    return () => { if (!viewer.isDestroyed()) entities.forEach((e) => viewer.entities.remove(e)); };
  }, [terrainReady, hazards, conditions?.scenario, conditions?.revision, sourceCatalog]);

  useEffect(() => {
    const viewer = viewerRef.current;
    if (!terrainReady || !viewer || viewer.isDestroyed() || !geometry) return undefined;
    const entities = selectDisplayEdges(geometry, selectedPathEdgeIds, selectedEdgeId, showNetwork).map((feature) => {
      const id = feature.properties.edge_id;
      const selected = id === selectedEdgeId;
      const inPath = selectedPathEdgeIds.includes(id);
      const color = Color.fromCssColorString(selected || inPath ? "#166ac7" : "#8998a9");
      const schematic = heightMethod(feature) === "SCHEMATIC_HEIGHT_UNKNOWN_USE_2D";
      return viewer.entities.add({ id: `candidate:${id}`, polyline: {
        positions: feature.geometry.coordinates.map(([lon, lat]) => Cartesian3.fromDegrees(lon, lat, 0)),
        width: selected ? 8 : inPath ? 6 : 2,
        material: schematic ? new PolylineDashMaterialProperty({ color }) : new PolylineOutlineMaterialProperty({ color, outlineColor: Color.WHITE, outlineWidth: inPath || selected ? 2 : 0 }),
        // Schematic dashed projection is explicitly not the bridge/tunnel road surface.
        clampToGround: true,
        classificationType: ClassificationType.TERRAIN,
      } });
    });
    registeredPoints(geometry, selectedNodeIds, registeredNodeIds).forEach((point, index) => entities.push(viewer.entities.add({ id: `endpoint:${point.id}`, position: Cartesian3.fromDegrees(...point.coordinates), point: { pixelSize: 14, color: Color.WHITE, outlineColor: Color.fromCssColorString("#166ac7"), outlineWidth: 3, heightReference: HeightReference.CLAMP_TO_TERRAIN }, label: { text: `${index === 0 ? "出発" : "到着"} ${point.label}`, font: "bold 14px sans-serif", fillColor: Color.fromCssColorString("#143f6c"), outlineColor: Color.WHITE, outlineWidth: 4, style: LabelStyle.FILL_AND_OUTLINE, pixelOffset: new Cartesian2(0, -24), heightReference: HeightReference.CLAMP_TO_TERRAIN } })));
    return () => { if (!viewer.isDestroyed()) entities.forEach((entity) => viewer.entities.remove(entity)); };
  }, [terrainReady, geometry, selectedEdgeId, selectedPathEdgeIds, selectedNodeIds, registeredNodeIds, showNetwork]);

  const visibleHazards = hazards && conditions?.scenario !== "ALL" ? filterHazardDisplayFeatures(hazards.features, conditions, sourceCatalog) : [];
  // Compact legend grouping only. Each scene entity retains its exact feature ID.
  const hazardLegend = Array.from(new Set(visibleHazards.map((f) => {
    const { sourceId, scenarioId, category } = hazardDisplayIdentity(f);
    return JSON.stringify({ sourceId, scenarioId, category });
  }))).map((encoded) => JSON.parse(encoded));
  return <><div className="scene-tools" aria-label="3D視点操作">
    <button onClick={() => fitCamera("all")}>全体</button><button onClick={() => fitCamera("path")}>経路</button><button onClick={() => fitCamera("segment")}>選択区間</button><button onClick={() => fitCamera("path", true)}>真上</button><button onClick={() => fitCamera("path")}>回転・傾きリセット</button>
    <button aria-label="3D拡大" onClick={() => cameraControl("zoom-in")}>＋</button><button aria-label="3D縮小" onClick={() => cameraControl("zoom-out")}>−</button><button onClick={() => cameraControl("rotate")}>回転</button><button onClick={() => cameraControl("tilt")}>傾き</button>
    <details className="camera-pan"><summary>移動</summary><button aria-label="3D左へ移動" onClick={() => cameraControl("pan-left")}>←</button><button aria-label="3D右へ移動" onClick={() => cameraControl("pan-right")}>→</button><button aria-label="3D上へ移動" onClick={() => cameraControl("pan-up")}>↑</button><button aria-label="3D下へ移動" onClick={() => cameraControl("pan-down")}>↓</button></details>
    <label>背景<select aria-label="3D背景" value={background} onChange={(e) => setBackground(e.target.value)}><option value="map">淡色地図</option><option value="photo">写真</option></select></label>
  </div>
  {!terrainReady && <p role="status">公式表示地形を検証中…</p>}
  <div ref={containerRef} className={`cesium-canvas ${terrainReady ? "terrain-ready" : "terrain-loading"}`} aria-label="CesiumによるPLATEAU 3D表示" />
  <div className="scene-legend"><span>青実線: 候補の地形投影（道路面未確認）</span><span>破線: 橋・トンネル等の図式投影／高さUNKNOWN、2D併用</span><span>紫: {conditions?.scenario === "ALL" ? "非表示 — 資料を1つ選択" : `${conditions?.scenario}（${visibleHazards.length}原典図形）`}</span></div>
  {(hazardError || backgroundError) && <p role="alert">{hazardError || backgroundError}</p>}
  <details className="map-provenance"><summary>根拠・開発者情報（地形・表示状態）</summary>
  <output className="cesium-render-evidence" aria-label="3D実描画のセッション証拠" data-visible-tiles={visibleTiles} data-visible-triangles={visibleTriangles} data-rendered-frames={renderedFrames} data-terrain-ready={terrainReady} data-terrain-mesh-loaded={terrainMeshLoaded} data-hazard-features={visibleHazards.length}>{visibleTiles > 0 ? "VISIBLE" : "LOADING"} · building content tiles {visibleTiles} · triangles {visibleTriangles} · frames {renderedFrames} · terrain metadata/sample {String(terrainReady)} · mesh loaded {String(terrainMeshLoaded)}（mesh読込は現在画面の実描画証明とは別）</output>
  <p>ハザード: 原典図形の地表投影、透過度22%。被害・水面高さ・安全判定ではありません。</p>
  {hazardLegend.map((identity) => { const source = sourceCatalog?.[identity.sourceId]; return <p key={JSON.stringify(identity)}>{identity.scenarioId} / 原典class {identity.category || "未記載"} / 版 {source?.source_revision ?? "UNKNOWN"} — {source?.attribution ?? identity.sourceId}</p>; })}
  <p>表示地形: {DISPLAY_TERRAIN.credit}。生成時固定ジオイド補正済み楕円体高。モデル版・生成日未確定。既存DEM1A/5A・道路面実測とは別資料です。補間表示位置はM6/M7・解析・exportに流しません。</p>
  <p>{background === "photo" ? photoBackground(config.city_id).label : "© OpenStreetMap contributors / ODbL 1.0（淡色表示）"}。背景写真は建物textureではありません。LOD2部分coverageの空白は建物不存在を意味しません。</p>
  <p>左drag: 移動、wheel/pinch: 拡大縮小、右drag: 回転・傾き。上のボタンはキーボード／タッチ代替です。</p></details></>;
}
