import { selectSegmentEvidence } from "./workspaceSelection.mjs";

export function SegmentInspector({ feature, evidence, conditions, path, onSelectEdge, onView3d, onAdmin, onClose }) {
  const selected = selectSegmentEvidence(feature, evidence, conditions);
  const p = feature?.properties;
  const index = path?.edge_ids.indexOf(p?.edge_id) ?? -1;
  const products = (evidence?.terrain?.products ?? []).filter((product) => conditions.terrainProduct === "ALL" || product.dem_class === conditions.terrainProduct);
  return <aside className="segment-inspector" aria-labelledby="segment-title">
    <div className="inspector-heading"><div><p className="eyebrow">SEGMENT EVIDENCE</p><h2 id="segment-title">区間詳細</h2></div><button className="mobile-detail-close" type="button" onClick={onClose}>地図へ戻る</button></div>
    {!p ? <p>候補区間を地図または一覧から選んでください。</p> : <>
      <h3>{p.name_tag || p.name || "選択した候補区間"}</h3><code className="segment-id">{p.edge_id}</code>
      <p className="neutral-status">CANDIDATE · 通行条件は UNKNOWN</p>
      <div className="segment-actions"><button type="button" onClick={onView3d}>同じ区間を3Dで確認</button><a href="#review-export" onClick={onClose}>この候補経路を書き出す</a></div>
      <section><h3>原典から確認できること</h3>
        <dl className="compact-facts"><div><dt>道路名</dt><dd>{p.name_tag || p.name || "—（原典に記載なし）"}</dd></div><div><dt>道路種別 / 表面</dt><dd>{p.highway_tag ?? p.highway ?? "UNKNOWN"} / {p.surface_tag ?? p.source_tags?.surface ?? "UNKNOWN"}</dd></div><div><dt>幅（現地測定）</dt><dd>{p.base_clear_width_m ?? "—"} · 現地測定延期</dd></div></dl>
        <h4>DEMセル標高 · {conditions.terrainProduct}</h4>
        <p className="small-note">地表の資料値であり、道路面高さ・段差・横断勾配ではありません。</p>
        {products.map((product) => <p className="small-note" key={product.dataset_id}>{product.dem_class} · 標高基準: {product.vertical_datum ?? "UNKNOWN"}</p>)}
        <div className="inspector-samples" tabIndex="0" aria-label="選択区間のDEM標高"><table><thead><tr><th>地点 / product</th><th>標高 / 原典状態</th></tr></thead><tbody>{selected.terrain.map((sample) => <tr key={sample.sample_id}><th>{sample.node_id ?? `vertex ${sample.vertex_index}`}<small>{sample.product}</small></th><td>{sample.elevation_m ?? "null"} {sample.unit}<small>{sample.reason ?? sample.surface_type ?? sample.status}</small></td></tr>)}</tbody></table>{!selected.terrain.length && <p>未接続 · この区間・製品に一致する原典標本がありません。</p>}</div>
        <h4>ハザード原典 · {conditions.scenario}</h4><p className="small-note">資料条件の切替です。経路の再探索・安全判定は行いません。</p>
        <div className="inspector-hazards" aria-label="選択区間のハザード証拠">{selected.hazards.map((row) => {
          const source = evidence?.hazard?.source_catalog?.[row.source_id];
          return <details key={`${row.scenario_id}:${row.source_id}`}><summary>{row.scenario_id}<small>{row.relation}</small></summary><p>{row.overlap_length_m ?? "null"} m · {row.source_classes.join(" / ") || "原典classなし"}</p><p>{row.reason}</p><p>source revision: {row.source_revision}</p><code>{row.source_sha256}</code><p>{source?.source_url && <a href={source.source_url} target="_blank" rel="noreferrer">原典を確認</a>} {source?.license_url && <a href={source.license_url} target="_blank" rel="noreferrer">提供元の利用条件</a>}</p></details>;
        })}{!selected.hazards.length && <p>この資料条件の証拠はありません。NO_DATA ≠ 影響なし。</p>}</div>
      </section>
      <section className="unknown-box"><h3>まだ分からないこと</h3><p>幅・段差・横断勾配・入口・解錠・現在の運用は UNKNOWN。建物表示やハザードの重なりから補いません。</p><p>M7: NOT_COMPUTED / result null</p>{selected.readiness && <p>{selected.readiness.missing_fields.join(", ")}</p>}</section>
      <section><h3>次に確認すること</h3><p>原典の適用範囲・施設の利用条件・区間の現状を確認します。現地測定は延期中です。</p><button type="button" onClick={onAdmin}>この区間の行政確認へ</button></section>
      <details className="source-disclosure"><summary>出典・snapshot・照合SHA</summary><p>{p.source_id}</p><p>{p.revision_id}</p><p>{p.source_feature_id}</p><p>{p.lineage?.join(" / ")}</p>{Object.entries(evidence?.source_hashes ?? {}).map(([key, value]) => <p key={key}>{key}<br /><code>{value}</code></p>)}</details>
      <nav className="segment-pagination" aria-label="候補経路内の区間移動"><button type="button" disabled={index <= 0} onClick={() => onSelectEdge(path.edge_ids[index - 1])}>前の区間</button><span>{index < 0 ? "経路外の選択区間" : `${index + 1} / ${path.edge_ids.length}`}</span><button type="button" disabled={index < 0 || index >= path.edge_ids.length - 1} onClick={() => onSelectEdge(path.edge_ids[index + 1])}>次の区間</button></nav>
    </>}
  </aside>;
}
