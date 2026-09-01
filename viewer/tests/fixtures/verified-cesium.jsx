import { useCallback, useState } from "react";
import { createRoot } from "react-dom/client";

globalThis.CESIUM_BASE_URL = "/cesium/";
const { CesiumPanel } = await import("../../src/CesiumPanel.jsx");

const VERIFIED_FIXTURE = {
  connected: true,
  data_class: "OFFICIAL_REMOTE_TILESET",
  source_class: "OFFICIAL",
  connection_receipt_sha256: "a".repeat(64),
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
      <CesiumPanel
        config={VERIFIED_FIXTURE}
        onFallback={onFallback}
        onAnnouncement={onAnnouncement}
      />
      <output aria-label="runtime announcement">{announcement}</output>
    </>
  );
}

createRoot(document.getElementById("root")).render(<VerifiedCesiumFixture />);
