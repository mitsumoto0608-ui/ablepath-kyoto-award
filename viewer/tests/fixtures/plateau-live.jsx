// Local verification harness only; not included by Vite's production entry.
// Approved 20260914 master permits VERIFYING before the production receipt gate.
import { useCallback, useState } from "react";
import { createRoot } from "react-dom/client";
import "../../src/styles.css";
import "../../src/workspace.css";
globalThis.CESIUM_BASE_URL = "/cesium/";
const { default: CesiumScene } = await import("../../src/CesiumScene.jsx");
const sources = {
  kyoto_kiyomizu: { tileset_url: "https://assets.cms.plateau.reearth.io/assets/25/dd4c50-5342-4a0b-ac51-05ffb138b8b5/26100_kyoto-shi_city_2025_citygml_1_op_bldg_3dtiles_26105_higashiyama-ku_lod2/tileset.json", root_sha256: "bb6cd0c34fa411673054c3525d74b09d1cb48fc662ca2b97fdbb136498cb61ae", root_bytes: 44801 },
  kyoto_arashiyama: { tileset_url: "https://assets.cms.plateau.reearth.io/assets/64/cf6354-e5ff-4ee4-84d6-1751734da17c/26100_kyoto-shi_city_2025_citygml_1_op_bldg_3dtiles_26108_ukyo-ku_lod2/tileset.json", root_sha256: "332400888a9a61cb75caab75af885b5a1e5cfa66b08d56081a0f954bd941298c", root_bytes: 120022 },
  fujisawa_enoshima: { tileset_url: "https://assets.cms.plateau.reearth.io/assets/22/a4cda2-f741-43fb-8d75-a51b941b7577/14205_fujisawa-shi_city_2025_citygml_1_op_bldg_3dtiles_lod2/tileset.json", root_sha256: "29999d4af44f834ddf021ca53f10d73c446c449a94b5a4497825debfabe5b3d0", root_bytes: 420436 },
};
const cityId = new URLSearchParams(location.search).get("city") ?? "kyoto_kiyomizu";
if (!Object.hasOwn(sources, cityId)) throw new Error("Unsupported verification city");
const config = sources[cityId];
const catalog = await fetch("/data/maps/map-layers.json").then((r) => r.json());
const city = catalog.cities.find((item) => item.city_id === cityId);
const { loadGeoJson } = await import("../../src/MapLibreMap.jsx");
const geometry = await loadGeoJson({ ...city.real_2d, data_path: new URL(city.real_2d.data_path, location.origin).href });
const analysis = await fetch(`/data/analysis/${cityId}.json`).then((r) => r.json());

function LiveVerification() {
  const [root, setRoot] = useState(false);
  const [failure, setFailure] = useState("");
  const [selected, setSelected] = useState(analysis.path_fixture.edge_ids[0]);
  const onConnected = useCallback(() => setRoot(true), []);
  const onFailure = useCallback((message) => setFailure(message), []);
  return <main className="astra-shell"><h1>VERIFYING · {cityId} · official 2025 LOD2</h1><p>Live source test, not a mocked tileset or production connection receipt. root loaded: {String(root)}. {failure}</p><p>出典：Project PLATEAU／京都市・藤沢市 2025。候補経路重畳: AblePath。建物表示は安全判定ではありません。</p><p><a href={config.tileset_url}>公式root</a> · <a href="https://www.mlit.go.jp/plateau/site-policy/">PDL1.0 / attribution</a></p><p>Selected: {selected} · ordered path: {analysis.path_fixture.edge_ids.join(" → ")}</p>{!failure && <CesiumScene config={config} geometry={geometry} bounds={city.real_2d.bounds} selectedEdgeId={selected} selectedPathEdgeIds={analysis.path_fixture.edge_ids} onSelectEdge={setSelected} onConnected={onConnected} onFailure={onFailure} />}</main>;
}
createRoot(document.getElementById("root")).render(<LiveVerification />);
