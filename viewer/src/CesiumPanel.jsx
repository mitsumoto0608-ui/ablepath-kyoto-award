import { useCallback, useEffect, useState } from "react";

export function CesiumPanel({ config, onFallback, onAnnouncement }) {
  const [Scene, setScene] = useState(null);
  const [runtimeStatus, setRuntimeStatus] = useState("LAZY_LOADING_RUNTIME");
  const handleConnected = useCallback(() => {
    setRuntimeStatus("SESSION_ROOT_TILESET_LOADED");
    onAnnouncement("PLATEAU root tileset metadataをこのセッションで読み込みました");
  }, [onAnnouncement]);
  const handleFailure = useCallback((reason) => onFallback(`3D通信失敗: ${reason}`), [onFallback]);

  useEffect(() => {
    let active = true;
    import("./CesiumScene.jsx")
      .then((module) => active && setScene(() => module.default))
      .catch((error) => active && onFallback(`Cesium runtimeの読込に失敗しました: ${error.message}`));
    return () => { active = false; };
  }, [onFallback]);

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

  return (
    <section className="cesium-shell" aria-labelledby="cesium-title">
      <div className="map-toolbar">
        <div><p className="eyebrow">CESIUM / OPTIONAL PLATEAU RUNTIME</p><h2 id="cesium-title">東山区 PLATEAU 建物LOD2</h2></div>
        <span className="status-badge status-metadata_only">{runtimeStatus}</span>
      </div>
      <div className="layer-facts">
        <span>{config.data_class}</span><span>{config.source_class}</span><span>{config.lod}</span><span>accessed {config.accessed_at}</span>
      </div>
      <p className="map-caption">実URLのruntime読込成功はこのセッションの表示状態です。citypackの静的truthは <code>PLATEAU_3D_CONNECTED=false</code> のままです。</p>
      {Scene ? (
        <Scene
          config={config}
          onConnected={handleConnected}
          onFailure={handleFailure}
        />
      ) : <div className="cesium-loading" role="status">Cesium runtimeを3Dタブでのみ読み込んでいます</div>}
      <p className="map-attribution"><a href={config.license_url} target="_blank" rel="noreferrer">{config.attribution}</a></p>
      <button type="button" onClick={() => onFallback("2Dへ戻りました")}>2Dへ戻る</button>
    </section>
  );
}
