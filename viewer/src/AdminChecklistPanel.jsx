import { useMemo, useState } from "react";
import { ADMIN_CHECKLIST_GUARD_TEXTS, adminChecklistPrintHeaderLines, sortChecklistItems, toChecklistCsv, validateExposureFlags } from "./adminChecklistCsv.mjs";
import { AdminChecklistDetail, AdminChecklistTable } from "./AdminChecklistTable.jsx";

// T-A2: the admin-check workflow screen. It renders the generated checklist as
// it is: no judgement, no rounding, no filling of UNKNOWN, no re-ranking.

const OBJECT_TYPES = ["edge", "facility", "plaza"];
const STATUSES = ["CONFIRMED", "UNKNOWN", "NOT_CONNECTED", "PERMISSION_REQUIRED"];
const METHODS = ["FIELD_MEASUREMENT", "OFFICIAL_QUERY", "DOCUMENT_REVIEW", "NOT_APPLICABLE"];

const SHARD_BYTE_CAP = 2 * 1024 * 1024;
// Public-subset manifest bytes (scope: PUBLIC_SAFE_SNAPSHOT_SCOPE.json). Like the analysis loader, this
// anchor belongs to the reviewed application; it is not a signature of the app.
export const ADMIN_MANIFEST_SHA256 = {
  kyoto_kiyomizu: "9fb85f77626a5744af0429b9cf6a38408cf00e788e3881be864cda60183bc01a",
  kyoto_arashiyama: "f0930bc8ba9efb692d1a89269816e398e6d2f6627983659fd50ff733707aa0f6",
  fujisawa_enoshima: "302ff068615a37e627b5570dcbf20852047e02bc379fbde317077392e7dfa456",
};

async function sha256Bytes(bytes) {
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
}

/**
 * Load the generated checklist: a small manifest plus row shards, each under the
 * portability cap. Every shard is verified by SHA-256 and row_count before any
 * row is used, and the rows are concatenated in manifest order, which is the
 * same deterministic order the build script wrote. Fails closed: a bad or
 * missing shard raises instead of rendering a partial table.
 */
export async function loadAdminChecklist(fetchImpl, path, expectedCityId, timeoutMs = 5000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetchImpl(path, { signal: controller.signal });
    if (!response.ok) throw new Error(`admin checklist HTTP ${response.status}`);
    const manifestBytes = await response.arrayBuffer();
    if (manifestBytes.byteLength > SHARD_BYTE_CAP) throw new Error("admin checklist manifest exceeds the portability cap");
    if (await sha256Bytes(manifestBytes) !== ADMIN_MANIFEST_SHA256[expectedCityId]) throw new Error("admin checklist manifest differs from the reviewed application binding");
    const manifest = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(manifestBytes));
    if (manifest?.city_id !== expectedCityId) throw new Error("admin checklist city binding mismatch");
    if (!Array.isArray(manifest.shards)) throw new Error("admin checklist manifest carries no shard list");
    const base = path.slice(0, path.lastIndexOf("/data/admin/"));
    const items = [];
    const paths = new Set();
    const itemIds = new Set();
    for (const shard of manifest.shards) {
      if (typeof shard.path !== "string" || !/^\.\/data\/admin\/[A-Za-z0-9_]+\/[A-Za-z0-9_]+\.part[0-9]+\.rows\.json$/.test(shard.path) || !shard.path.startsWith(`./data/admin/${expectedCityId}/`) || paths.has(shard.path)) throw new Error("admin checklist shard path is not unique and city-confined");
      paths.add(shard.path);
      const shardResponse = await fetchImpl(`${base}${shard.path.slice(1)}`, { signal: controller.signal });
      if (!shardResponse.ok) throw new Error(`admin checklist shard HTTP ${shardResponse.status}`);
      const shardBytes = await shardResponse.arrayBuffer();
      if (shardBytes.byteLength > SHARD_BYTE_CAP || shardBytes.byteLength !== shard.bytes) throw new Error("admin checklist shard byte count does not match the manifest/cap");
      if (await sha256Bytes(shardBytes) !== shard.sha256) throw new Error(`admin checklist shard bytes do not match the manifest: ${shard.path}`);
      const rows = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(shardBytes));
      if (!Array.isArray(rows) || rows.length !== shard.row_count) throw new Error(`admin checklist shard row count does not match the manifest: ${shard.path}`);
      for (const row of rows) {
        if (row?.city_id !== expectedCityId || row.item_id !== `${row.city_id}:${row.object_type}:${row.object_id}:${row.attribute}` || itemIds.has(row.item_id) || row.internal_use_only !== false) throw new Error("admin checklist row identity/city/public boundary mismatch");
        itemIds.add(row.item_id);
        if (row.object_type === "edge") validateExposureFlags(row.exposure_flags);
        items.push(row);
      }
    }
    if (items.length !== manifest.counts?.items) throw new Error("admin checklist row total does not match the manifest count");
    if (items.some((item) => item.internal_use_only === true)) throw new Error("admin checklist contains internal_use_only rows");
    return { ...manifest, items };
  } finally {
    clearTimeout(timer);
  }
}

function toggle(values, value) {
  return values.includes(value) ? values.filter((entry) => entry !== value) : [...values, value];
}

function FilterGroup({ legend, options, selected, onChange }) {
  return (
    <fieldset className="admin-filter">
      <legend>{legend}</legend>
      {options.map((option) => (
        <label key={option}>
          <input type="checkbox" checked={selected.includes(option)} onChange={() => onChange(toggle(selected, option))} />
          <span>{option}</span>
        </label>
      ))}
    </fieldset>
  );
}

export function AdminChecklistPanel({ checklist, notice }) {
  const [objectTypes, setObjectTypes] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [methods, setMethods] = useState([]);
  const [selectedItemId, setSelectedItemId] = useState(null);
  // App keys this panel by the selected city. Do not schedule a second complete
  // table render merely because the same city's null placeholder became loaded.

  const visible = useMemo(() => {
    if (!checklist) return [];
    return sortChecklistItems(checklist.items.filter((item) =>
      (objectTypes.length === 0 || objectTypes.includes(item.object_type))
      && (statuses.length === 0 || statuses.includes(item.status))
      && (methods.length === 0 || methods.includes(item.verification_method))));
  }, [checklist, objectTypes, statuses, methods]);

  if (!checklist) {
    return (
      <section className="admin-checklist" aria-labelledby="admin-checklist-title">
        <div className="section-heading"><p className="eyebrow">ADMIN CHECK WORKFLOW</p><h2 id="admin-checklist-title">行政確認ワークフロー</h2></div>
        <p>{notice ?? "確認票を読み込み中です。"}</p>
      </section>
    );
  }

  const headerLines = adminChecklistPrintHeaderLines(checklist);
  const selected = checklist.items.find((item) => item.item_id === selectedItemId) ?? null;
  const internalRows = checklist.items.filter((item) => item.internal_use_only === true).length;

  function saveCsv() {
    // The exported bytes are the generated bytes: the whole item list through the
    // same serializer the build script uses, not the filtered view.
    const url = URL.createObjectURL(new Blob([toChecklistCsv(checklist.items)], { type: "text/csv;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `ADMIN_CHECKLIST_${checklist.city_id}.csv`;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1_000);
  }

  return (
    <section className="admin-checklist" aria-labelledby="admin-checklist-title">
      <div className="section-heading"><p className="eyebrow">ADMIN CHECK WORKFLOW</p><h2 id="admin-checklist-title">行政確認ワークフロー</h2></div>
      <div className="admin-print-header">
        {headerLines.map((line) => <p key={line}>{line}</p>)}
      </div>
      <p className="admin-internal-note">
        {checklist.city_id === "fujisawa_enoshima"
          ? `既定の公開ビルドです。internal_use_only の行は含まれていません（この画面の内部利用行 ${internalRows} 件）。藤沢の施設行は LICENSE_REVIEW_REQUIRED のため既定ビルドから除外されます。行データの状態: ${checklist.fujisawa_facility_row_source_status ?? "null"}。`
          : `既定の公開ビルドです。internal_use_only の行は含まれていません（この画面の内部利用行 ${internalRows} 件）。`}
      </p>
      <div className="admin-filters">
        <FilterGroup legend="object_type" options={OBJECT_TYPES} selected={objectTypes} onChange={setObjectTypes} />
        <FilterGroup legend="status" options={STATUSES} selected={statuses} onChange={setStatuses} />
        <FilterGroup legend="verification_method" options={METHODS} selected={methods} onChange={setMethods} />
      </div>
      <p className="admin-counts">絞り込み後 / 全体: <b>{visible.length}</b> / {checklist.counts.items}</p>
      <div className="admin-actions">
        <button type="button" onClick={() => window.print()}>印刷</button>
        <button type="button" onClick={saveCsv}>CSVを保存（全{checklist.counts.items}行）</button>
        <a href={`./data/admin/${checklist.city_id}.checklist.json`} download={`${checklist.city_id}.checklist.json`}>JSON manifest（生成済みファイル）</a>
      </div>
      <AdminChecklistTable items={visible} selectedItemId={selectedItemId} onSelect={setSelectedItemId} />
      <div className="admin-detail">
        <h3>行詳細</h3>
        <AdminChecklistDetail item={selected} />
      </div>
    </section>
  );
}
