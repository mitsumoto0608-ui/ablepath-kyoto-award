// T-A2: the checklist table and the row detail list.
// Status words are printed verbatim. Meaning is never carried by colour alone.

function exposureSummary(item) {
  if (item.exposure_flags === null) return "—";
  if (item.exposure_flags.status === "PUBLIC_PAYLOAD_EXCLUDED") return `records null / PUBLIC_PAYLOAD_EXCLUDED / ${item.exposure_flags.reason}`;
  const counts = Object.entries(item.exposure_flags.a31b_overlap_counts).map(([key, value]) => `${key}=${value}`).join(" / ");
  return `records ${item.exposure_flags.records}${counts ? ` / ${counts}` : ""} / landslide ${item.exposure_flags.landslide} / earthquake ${item.exposure_flags.earthquake}`;
}

export function AdminChecklistTable({ items, selectedItemId, onSelect }) {
  return (
    <div className="table-scroll admin-checklist-table" tabIndex="0" aria-label="行政確認ワークフロー 確認項目一覧">
      <table>
        <caption>確認項目 {items.length}件（priority_rank は並び順の機械規則であり、危険度・重要度ではありません。）</caption>
        <thead>
          <tr>
            <th scope="col">priority_rank</th>
            <th scope="col">object_type</th>
            <th scope="col">object_id</th>
            <th scope="col">attribute</th>
            <th scope="col">status</th>
            <th scope="col">unknown_reason</th>
            <th scope="col">verification_method</th>
            <th scope="col">verification_target.label</th>
            <th scope="col">exposure_flags</th>
            <th scope="col">assignee</th>
            <th scope="col">due</th>
            <th scope="col">result</th>
            <th scope="col">note</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.item_id} className={item.item_id === selectedItemId ? "admin-row-selected" : undefined}>
              <td>{item.priority_rank}</td>
              <td>{item.object_type}</td>
              <th scope="row">
                <button type="button" className="admin-row-button" onClick={() => onSelect(item.item_id)} aria-label={`${item.item_id} の詳細`}>
                  <code>{item.object_id}</code>
                </button>
              </th>
              <td>{item.attribute}</td>
              <td>{item.status}</td>
              <td>{item.unknown_reason ?? "null"}</td>
              <td>{item.verification_method}</td>
              <td>{item.verification_target.label}</td>
              <td className="admin-exposure-cell">{exposureSummary(item)}</td>
              <td className="admin-human-field" />
              <td className="admin-human-field" />
              <td className="admin-human-field" />
              <td className="admin-human-field" />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function AdminChecklistDetail({ item }) {
  if (!item) return <p className="admin-detail-empty">行を選ぶと全フィールドを表示します。</p>;
  return (
    <dl className="admin-checklist-detail">
      <div><dt>item_id</dt><dd><code>{item.item_id}</code></dd></div>
      <div><dt>city_id / subarea_id</dt><dd>{item.city_id} / {item.subarea_id}</dd></div>
      <div><dt>object_type / object_id</dt><dd>{item.object_type} / <code>{item.object_id}</code></dd></div>
      <div><dt>attribute</dt><dd>{item.attribute}</dd></div>
      <div><dt>status</dt><dd>{item.status}</dd></div>
      <div><dt>unknown_reason</dt><dd>{item.unknown_reason ?? "null"}</dd></div>
      <div><dt>source_id</dt><dd>{item.source_id ?? "null"}</dd></div>
      <div><dt>source_revision</dt><dd>{item.source_revision ?? "null"}</dd></div>
      <div><dt>source_sha256</dt><dd><code>{item.source_sha256 ?? "null"}</code></dd></div>
      <div><dt>verification_method</dt><dd>{item.verification_method}</dd></div>
      <div><dt>verification_target.label</dt><dd>{item.verification_target.label}</dd></div>
      <div><dt>verification_target.receipt_path</dt><dd><code>{item.verification_target.receipt_path ?? "null"}</code></dd></div>
      <div><dt>verification_target.dataset_ids</dt><dd>{item.verification_target.dataset_ids.join(", ") || "—"}</dd></div>
      <div><dt>verification_target.note</dt><dd>{item.verification_target.note ?? "null"}</dd></div>
      <div><dt>priority_rank / priority_rule</dt><dd>{item.priority_rank} / {item.priority_rule}</dd></div>
      <div><dt>exposure_flags</dt><dd><code>{item.exposure_flags === null ? "null" : JSON.stringify(item.exposure_flags)}</code></dd></div>
      <div><dt>human_fields</dt><dd>印刷して人が書く欄です。この画面では保存しません。</dd></div>
      <div><dt>export_ready / internal_use_only</dt><dd>{String(item.export_ready)} / {String(item.internal_use_only)}</dd></div>
    </dl>
  );
}
