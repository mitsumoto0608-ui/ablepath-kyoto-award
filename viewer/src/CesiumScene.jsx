import { useEffect, useRef, useState } from "react";
import {
  EllipsoidTerrainProvider,
  Viewer,
  Cartesian3, Color, HeadingPitchRange, Matrix4, PolylineOutlineMaterialProperty,
  ScreenSpaceEventHandler, ScreenSpaceEventType, UrlTemplateImageryProvider,
} from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";

import { installCesiumFailureListeners, withTimeout } from "./mapAsync.mjs";
import { loadTilesetForSession } from "./plateauResource.mjs";

const DEFAULT_TILESET_TIMEOUT_MS = 12_000;

function runtimeTimeout() {
  const requested = Number(globalThis.__ABLEPATH_CESIUM_TIMEOUT_MS__);
  return Number.isFinite(requested) && requested >= 50 && requested <= DEFAULT_TILESET_TIMEOUT_MS
    ? requested
    : DEFAULT_TILESET_TIMEOUT_MS;
}

export default function CesiumScene({ config, geometry, bounds, selectedEdgeId, selectedPathEdgeIds = [], onSelectEdge, onConnected, onVisible, onFailure }) {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);
  const callbacks = useRef({ onSelectEdge, onVisible });
  callbacks.current = { onSelectEdge, onVisible };
  const [sceneReady, setSceneReady] = useState(false);
  const [visibleTiles, setVisibleTiles] = useState(0);
  const [visibleTriangles, setVisibleTriangles] = useState(0);
  const [renderedFrames, setRenderedFrames] = useState(0);

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
        terrainProvider: new EllipsoidTerrainProvider(),
      });
      viewerRef.current = viewer;
      viewer.targetFrameRate = 30;
      viewer.scene.globe.baseColor = Color.fromCssColorString("#e8edf2");
      viewer.scene.backgroundColor = Color.fromCssColorString("#eef3f8");
      viewer.scene.globe.enableLighting = false;
      viewer.imageryLayers.addImageryProvider(new UrlTemplateImageryProvider({ url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png", maximumLevel: 19, credit: "© OpenStreetMap contributors / ODbL 1.0" }));
      if (bounds) {
        const center = [(bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2];
        // Camera range/pitch are display settings, not measured terrain or road height.
        viewer.camera.lookAt(Cartesian3.fromDegrees(center[0], center[1], 0), new HeadingPitchRange(0, -0.8, 1000));
        viewer.camera.lookAtTransform(Matrix4.IDENTITY);
      }
      setSceneReady(true);
      clickHandler = new ScreenSpaceEventHandler(viewer.scene.canvas);
      clickHandler.setInputAction((event) => {
        const entity = viewer.scene.pick(event.position)?.id;
        if (entity?.id?.startsWith("candidate:")) callbacks.current.onSelectEdge?.(entity.id.slice("candidate:".length));
      }, ScreenSpaceEventType.LEFT_CLICK);
      withTimeout(
        loadTilesetForSession(config, { signal: controller.signal, isActive: () => active && !failed }),
        runtimeTimeout(),
        "PLATEAU tilesetの通信がタイムアウトしました",
      ).then(async (tileset) => {
        if (!active || viewer.isDestroyed()) { if (!tileset.isDestroyed()) tileset.destroy(); return; }
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
      controller.abort();
      clearTimeout(contentDeadline);
      viewerRef.current = null;
      removers.forEach((remove) => remove());
      clickHandler?.destroy();
      failureListeners?.remove();
      if (viewer && !viewer.isDestroyed()) viewer.destroy();
    };
  }, [config, bounds, onConnected, onFailure]);

  useEffect(() => {
    const viewer = viewerRef.current;
    if (!sceneReady || !viewer || viewer.isDestroyed() || !geometry) return undefined;
    const entities = geometry.features.map((feature) => {
      const id = feature.properties.edge_id;
      const selected = id === selectedEdgeId;
      const inPath = selectedPathEdgeIds.includes(id);
      const color = Color.fromCssColorString(selected ? "#153964" : inPath ? "#287ce0" : "#8998a9");
      return viewer.entities.add({ id: `candidate:${id}`, polyline: {
        positions: feature.geometry.coordinates.map(([lon, lat]) => Cartesian3.fromDegrees(lon, lat, 0)),
        width: selected ? 8 : inPath ? 6 : 2,
        material: new PolylineOutlineMaterialProperty({ color, outlineColor: Color.WHITE, outlineWidth: inPath || selected ? 1 : 0 }),
        depthFailMaterial: color.withAlpha(inPath || selected ? 0.95 : 0.3),
        clampToGround: false,
      } });
    });
    return () => { if (!viewer.isDestroyed()) entities.forEach((entity) => viewer.entities.remove(entity)); };
  }, [sceneReady, geometry, selectedEdgeId, selectedPathEdgeIds]);

  return <><div ref={containerRef} className="cesium-canvas" aria-label="CesiumによるPLATEAU 3D表示" /><output className="cesium-render-evidence" aria-label="3D実描画のセッション証拠" data-visible-tiles={visibleTiles} data-visible-triangles={visibleTriangles} data-rendered-frames={renderedFrames}>{visibleTiles > 0 ? "VISIBLE" : "LOADING"} · content tiles {visibleTiles} · triangles {visibleTriangles} · frames {renderedFrames}</output><p className="map-caption">地形: WGS84楕円体（DEM地形meshではありません）。候補線はh=0の表示専用投影・遮蔽時重畳。建物の接地面とは一致しません。道路面高さ・建物屋根高さ・DEM標高を経路高さに変換していません。背景: © OpenStreetMap contributors / ODbL 1.0。</p></>;
}
