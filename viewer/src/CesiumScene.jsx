import { useEffect, useRef } from "react";
import {
  Cesium3DTileset,
  EllipsoidTerrainProvider,
  Viewer,
} from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";

import { installCesiumFailureListeners, withTimeout } from "./mapAsync.mjs";

const DEFAULT_TILESET_TIMEOUT_MS = 12_000;

function runtimeTimeout() {
  const requested = Number(globalThis.__ABLEPATH_CESIUM_TIMEOUT_MS__);
  return Number.isFinite(requested) && requested >= 50 && requested <= DEFAULT_TILESET_TIMEOUT_MS
    ? requested
    : DEFAULT_TILESET_TIMEOUT_MS;
}

export default function CesiumScene({ config, onConnected, onFailure }) {
  const containerRef = useRef(null);

  useEffect(() => {
    let active = true;
    let viewer;
    let failureListeners;
    let failed = false;
    const failOnce = (reason) => {
      if (!active || failed) return;
      failed = true;
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
        terrainProvider: new EllipsoidTerrainProvider(),
      });
      withTimeout(
        Cesium3DTileset.fromUrl(config.tileset_url),
        runtimeTimeout(),
        "PLATEAU tilesetの通信がタイムアウトしました",
      ).then(async (tileset) => {
        if (!active || viewer.isDestroyed()) return;
        failureListeners = installCesiumFailureListeners({
          tileset,
          scene: viewer.scene,
          onFailure: failOnce,
        });
        viewer.scene.primitives.add(tileset);
        await viewer.zoomTo(tileset);
        if (active && !failed && !failureListeners.hasFailed()) onConnected();
      }).catch((error) => {
        failOnce(error.message);
      });
    } catch (error) {
      failOnce(error.message);
    }
    return () => {
      active = false;
      failureListeners?.remove();
      if (viewer && !viewer.isDestroyed()) viewer.destroy();
    };
  }, [config, onConnected, onFailure]);

  return <div ref={containerRef} className="cesium-canvas" aria-label="CesiumによるPLATEAU 3D表示" />;
}
