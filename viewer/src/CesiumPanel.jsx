import { useCallback, useEffect, useState } from "react";
import { isVerifiedCesiumConnection } from "./mapDomain.mjs";

export function CesiumPanel({ config, geometry, bounds, selectedEdgeId, selectedPathEdgeIds, selectedNodeIds, registeredNodeIds, conditions, hazardLayers, sourceCatalog, showNetwork, cameraRequest, onSelectEdge, onFallback, onAnnouncement }) {
  const [Scene, setScene] = useState(null);
  const [runtimeStatus, setRuntimeStatus] = useState("LAZY_LOADING_RUNTIME");
  const verifiedConnection = isVerifiedCesiumConnection(config);
  const handleConnected = useCallback(() => {
    setRuntimeStatus("SESSION_ROOT_TILESET_LOADED");
    onAnnouncement("PLATEAU root tileset metadataをこのセッションで読み込みました");
  }, [onAnnouncement]);
  const handleFailure = useCallback((reason) => onFallback(`3D通信失敗: ${reason}`), [onFallback]);
  const handleVisible = useCallback((evidence) => {
    setRuntimeStatus(evidence.visible_tiles > 0 ? "VISIBLE" : "DEGRADED_NO_VISIBLE_CONTENT");
  }, []);

  useEffect(() => {
    if (!verifiedConnection) return undefined;
    let active = true;
    import("./CesiumScene.jsx")
      .then((module) => active && setScene(() => module.default))
      .catch((error) => active && onFallback(`Cesium runtimeの読込に失敗しました: ${error.message}`));
    return () => { active = false; };
  }, [onFallback, verifiedConnection]);

  if (!config) {
    return (
      <section className="three-d-notice" aria-labelledby="three-d-title">
        <p className="eyebrow">NO REVIEWED 3D METADATA</p>
        <h2 id="three-d-title">この都市の3D layerは未設定です</h2>
        <p>実在しないtilesetを補完せず、合成2Dへ戻せます。</p>
        <button type="button" onClick={() => onFallback("この都市に3D metadataがないため2Dへ戻りました")}>2Dへ戻る</button>
      </section>
    );
  }

  if (!verifiedConnection) {
    return (
      <section className="three-d-notice" aria-labelledby="three-d-title">
        <p className="eyebrow"><span>OFFICIAL PLATEAU METADATA</span> / <strong>NOT_CONNECTED</strong></p>
        <h2 id="three-d-title">3Dは未接続です</h2>
        <div className="layer-facts">
          <span>{config.data_class}</span><span>{config.source_class}</span><span>{config.lod}</span><span>accessed {config.accessed_at}</span>
        </div>
        <p>CORS・AOI・child tiles の検証 receipt が未完了のため、保持済みmetadataやmock tilesetを実PLATEAU接続として扱わず、Cesiumの通信は開始しません。</p>
        <p>施設の位置・容量・入口・開設／運用・fire_safe・accessibility の原典行データも未接続です。未確認値は null／理由付きのtable証跡に留めます。</p>
        <p className="map-attribution"><a href={config.license_url} target="_blank" rel="noreferrer">{config.attribution}</a></p>
        <button type="button" onClick={() => onFallback("検証済みPLATEAU connection receiptがないため2Dへ戻りました")}>2Dへ戻る</button>
      </section>
    );
  }

  return (
    <section className="cesium-shell" aria-labelledby="cesium-title">
      <div className="map-toolbar">
        <div><p className="eyebrow">OFFICIAL PLATEAU / DISPLAY ONLY</p><h2 id="cesium-title">{config.city_id === "kyoto_arashiyama" ? "嵐山・右京区" : config.city_id === "fujisawa_enoshima" ? "藤沢" : "清水・東山区"} · PLATEAU {config.year ?? ""} {config.lod}</h2></div>
        <span className="status-badge status-metadata_only">{runtimeStatus}</span>
      </div>
      <p className="map-caption">公式LOD2・部分coverage。候補線は表示用投影、道路面高さは未確認です。</p>
      {Scene ? (
        <Scene
          config={config}
          geometry={geometry}
          bounds={bounds}
          selectedEdgeId={selectedEdgeId}
          selectedPathEdgeIds={selectedPathEdgeIds}
          selectedNodeIds={selectedNodeIds}
          registeredNodeIds={registeredNodeIds}
          conditions={conditions}
          hazardLayers={hazardLayers}
          sourceCatalog={sourceCatalog}
          showNetwork={showNetwork}
          cameraRequest={cameraRequest}
          onSelectEdge={onSelectEdge}
          onConnected={handleConnected}
          onVisible={handleVisible}
          onFailure={handleFailure}
        />
      ) : <div className="cesium-loading" role="status">Cesium runtimeを3Dタブでのみ読み込んでいます</div>}
      <p className="map-attribution"><a href={config.license_url} target="_blank" rel="noreferrer">{config.attribution}</a></p>
      <details className="map-provenance"><summary>公式配信URL・検証receipt</summary><p>source: VERIFIED_SOURCE / session: {runtimeStatus}。{config.coverage_limitations} M7 ready / computed = 0 / 0。</p><a href={config.tileset_url} target="_blank" rel="noreferrer">公式tileset.json</a><p>root SHA-256: <code>{config.root_sha256}</code></p><p>receipt SHA-256: <code>{config.connection_receipt_sha256}</code></p></details>
      <button type="button" onClick={() => onFallback("2Dへ戻りました")}>2Dへ戻る</button>
    </section>
  );
}
