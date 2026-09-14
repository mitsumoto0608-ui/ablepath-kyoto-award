import { useCallback, useState } from "react";
import { createRoot } from "react-dom/client";

globalThis.CESIUM_BASE_URL = "/cesium/";
const { default: CesiumScene } = await import("../../src/CesiumScene.jsx");

// Test the renderer lifecycle directly. This synthetic fixture deliberately
// does not satisfy the production source/receipt gate.
const VERIFIED_FIXTURE = {
  tileset_url: "https://assets.cms.plateau.reearth.io/test-fixture/tileset.json",
  lod: "LOD2",
  accessed_at: "2099-01-01",
  license_url: "https://www.mlit.go.jp/plateau/site-policy/",
  attribution: "TEST FIXTURE — not real evidence",
};

function VerifiedCesiumFixture() {
  const [fallback, setFallback] = useState("");
  const [announcement, setAnnouncement] = useState("");
  const onFallback = useCallback((reason) => setFallback(reason), []);
  const onAnnouncement = useCallback((message) => setAnnouncement(message), []);
  const [rootLoaded, setRootLoaded] = useState(false);
  const onConnected = useCallback(() => { setRootLoaded(true); setAnnouncement("PLATEAU root tileset metadata — TEST FIXTURE only"); }, []);

  if (fallback) {
    return (
      <section aria-label="2D fallback fixture">
        <h1>2Dへfallback</h1>
        <p role="status">{fallback}</p>
        <p>TEST FIXTURE — no official connection claim</p>
      </section>
    );
  }
  return (
    <>
      <p>TEST FIXTURE — verified-connection control path only</p>
      <CesiumScene
        config={VERIFIED_FIXTURE}
        onFailure={onFallback}
        onConnected={onConnected}
      />
      {rootLoaded && <output>SESSION_ROOT_TILESET_LOADED</output>}
      <output aria-label="runtime announcement">{announcement}</output>
    </>
  );
}

createRoot(document.getElementById("root")).render(<VerifiedCesiumFixture />);
