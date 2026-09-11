import { useCallback, useEffect, useMemo, useState } from "react";
import {
  formatKpi,
  loadCatalog,
  selectInitialState,
  serializeState,
} from "./domain.mjs";
import { CesiumPanel } from "./CesiumPanel.jsx";
import { MapLibreMap } from "./MapLibreMap.jsx";
import {
  loadMapCatalog,
  mapConfigForCity,
  selectInitialMapMode,
} from "./mapDomain.mjs";
import {
  checklistToCsv,
  checklistToJson,
  checklistToPrintableHtml,
  loadDeliveryAnalysis,
  selectChecklistRows,
  selectUnresolvedTerrainRecords,
} from "./analysisDomain.mjs";
import { AdminChecklistPanel, loadAdminChecklist } from "./AdminChecklistPanel.jsx";

const KPI_LABELS = {
  physically_reachable: "物理的に到達可能",
  accommodated: "受入可能",
  overflow_waiting: "受入超過・待機",
  unreachable: "到達不能",
  unknown_affected_upper_bound: "UNKNOWN影響上限",
};

const STATE_LABELS = {
  PASS: "通行条件内",
  CONDITIONAL: "条件付き",
  FAIL: "不成立",
  UNKNOWN: "不明",
};

const STATE_MARKS = { PASS: "P", CONDITIONAL: "C", FAIL: "F", UNKNOWN: "?" };

function formatOptional(value, reason) {
  if (value === null || value === undefined) return `—（${reason}）`;
  return `${Number(value).toFixed(2)} m`;
}

function Header({ city, catalog }) {
  return (
    <header className="masthead">
      <div className="brand-lockup">
        <span className="brand-mark" aria-hidden="true">AP</span>
        <div>
          <p className="eyebrow">MULTI-CITY EVIDENCE VIEWER</p>
          <h1>AblePath</h1>
        </div>
      </div>
      <div className="status-cluster" aria-label="データ状態">
        <span className={`status-badge status-${city.data_status.toLowerCase()}`}>{city.data_status}</span>
        <span>確認日 {city.last_verified_at}</span>
        <span>viewer schema {catalog.viewer_data_schema_version}</span>
      </div>
    </header>
  );
}

function Controls({ catalog, mapCatalog, state, onStateChange, analysis, selectedStart, selectedEnd, onPathChange }) {
  const { city, scenario, evidenceMode, phase, view, mapMode } = state;
  function changeCity(cityId) {
    const nextCity = catalog.cities.find((candidate) => candidate.city_id === cityId);
    onStateChange({
      ...state,
      city: nextCity,
      scenario: nextCity.scenarios[0],
      selectedEdge: nextCity.map.edges[0] ?? null,
      selectedRealEdgeId: null,
      mapMode: "synthetic",
    }, `${nextCity.display_name}へ切り替えました`);
  }
  const realMapAvailable = Boolean(mapConfigForCity(mapCatalog, city.city_id)?.real_2d);
  return (
    <section className="controls" aria-labelledby="controls-title">
      <div className="section-heading">
        <p className="eyebrow">SCENARIO CONTROL</p>
        <h2 id="controls-title">表示条件</h2>
      </div>
      <div className="control-grid">
        <label>
          都市・回廊
          <select aria-label="都市・回廊" value={city.city_id} onChange={(event) => changeCity(event.target.value)}>
            {catalog.cities.map((candidate) => <option key={candidate.city_id} value={candidate.city_id}>{candidate.display_name}</option>)}
          </select>
        </label>
        <label>
          ハザード・固定シナリオ（未接続）
          <select aria-label="ハザード・固定シナリオ（未接続）" value={scenario.scenario_id} disabled>
            <option value={scenario.scenario_id}>NOT_COMPUTED — scenario output未接続</option>
          </select>
        </label>
        <label>
          歩行profile
          <select aria-label="歩行profile（未計算）" value="NOT_COMPUTED" disabled>
            <option value="NOT_COMPUTED">NOT_COMPUTED — M6未実装</option>
          </select>
        </label>
        <label>出発node（candidate fixture）<select aria-label="出発node（candidate fixture）" value={selectedStart ?? "NOT_AVAILABLE"} onChange={(event) => onPathChange(event.target.value, selectedEnd)}>{(analysis?.selectable_node_ids ?? ["NOT_AVAILABLE"]).map((nodeId) => <option key={nodeId} value={nodeId}>{nodeId}</option>)}</select></label>
        <label>目的node（candidate fixture）<select aria-label="目的node（candidate fixture）" value={selectedEnd ?? "NOT_AVAILABLE"} onChange={(event) => onPathChange(selectedStart, event.target.value)}>{(analysis?.selectable_node_ids ?? ["NOT_AVAILABLE"]).map((nodeId) => <option key={nodeId} value={nodeId}>{nodeId}</option>)}</select></label>
        <label>
          比較断面（未接続）
          <select aria-label="Before/After比較（未接続）" value={phase} disabled>
            <option value="before">NOT_COMPUTED — Before/After output未接続</option>
          </select>
        </label>
      </div>
      <fieldset className="segmented-fieldset">
        <legend>UNKNOWNの証拠取扱い</legend>
        <div className="segmented">
          <label><input type="radio" name="evidence" value="strict" checked={evidenceMode === "strict"} disabled readOnly /><span>厳格</span></label>
          <label><input type="radio" name="evidence" value="optimistic" checked={evidenceMode === "optimistic"} disabled readOnly /><span>参考</span></label>
        </div>
        <p>NOT_COMPUTED — evidence treatment別のprecomputed outputがないため切替できません。</p>
      </fieldset>
      <div className="view-tabs" role="group" aria-label="地図表示">
        <button type="button" aria-pressed={view === "2d"} onClick={() => onStateChange({ ...state, view: "2d" }, "2D表示へ切り替えました")}>2D</button>
        <button type="button" aria-pressed={view === "3d"} onClick={() => onStateChange({ ...state, view: "3d" }, "3D可用性情報を表示しました")}>3D</button>
      </div>
      <fieldset className="map-mode-fieldset">
        <legend>2D geometry layer</legend>
        <div className="view-tabs" role="group" aria-label="実データと合成データの表示切替">
          <button type="button" aria-pressed={mapMode === "real"} disabled={!realMapAvailable} onClick={() => onStateChange({ ...state, view: "2d", mapMode: "real" }, "実座標候補graphへ切り替えました")}>実座標 / CANDIDATE</button>
          <button type="button" aria-pressed={mapMode === "synthetic"} onClick={() => onStateChange({ ...state, view: "2d", mapMode: "synthetic" }, "合成模式図へ切り替えました")}>SYNTHETIC_DEMO</button>
        </div>
        {!realMapAvailable && <p>この都市にhash検証済み実座標artifactはありません。合成模式図を明示表示します。</p>}
      </fieldset>
    </section>
  );
}

function KpiGrid({ city }) {
  return (
    <section className="kpi-section" aria-labelledby="kpi-title">
      <div className="section-heading inline-heading">
        <div><p className="eyebrow">READINESS-GATED KPI</p><h2 id="kpi-title">KPI</h2></div>
        <span className="not-computed-pill">{city.kpi_status}</span>
      </div>
      <div className="kpi-grid">
        {Object.entries(city.kpis).map(([key, entry]) => {
          const formatted = formatKpi(entry);
          return (
            <article className="kpi-card" key={key}>
              <p>{KPI_LABELS[key] ?? key}</p>
              <strong>{formatted.value}</strong>
              <span>{formatted.status}</span>
              <small>{formatted.reason}</small>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function StateLegend() {
  return (
    <ul className="legend" aria-label="状態凡例">
      {Object.entries(STATE_LABELS).map(([state, label]) => (
        <li key={state}><span className={`legend-line edge-${state.toLowerCase()}`} aria-hidden="true"></span><b>{STATE_MARKS[state]}</b><span>{label}</span></li>
      ))}
    </ul>
  );
}

function Map2D({ city, selectedEdge, onSelectEdge }) {
  return (
    <div className="map-shell">
      <div className="map-toolbar">
        <div><p className="eyebrow">PRECOMPUTED 2D SNAPSHOT</p><h2>{city.corridor_name}</h2></div>
        <span>{city.map.geometry_status}</span>
      </div>
      <svg className="route-map" viewBox="0 0 1000 620" role="group" aria-labelledby="map-title map-description">
        <title id="map-title">{city.display_name}のシナリオ回廊図</title>
        <desc id="map-description">合成座標の回廊を線分で示す。各線分は文字記号と線種を併用し、選択すると証拠パネルが更新される。</desc>
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="1" /></pattern>
        </defs>
        <rect width="1000" height="620" className="map-ground" />
        <rect width="1000" height="620" fill="url(#grid)" className="map-grid" />
        <path d="M0 510 C210 430, 410 560, 1030 370" className="terrain-line" />
        <path d="M-20 180 C180 260, 350 80, 1030 210" className="terrain-line secondary" />
        {city.map.edges.map((edge) => {
          const points = edge.points.map((point) => point.join(",")).join(" ");
          const midpoint = edge.points[Math.floor(edge.points.length / 2)];
          const selected = selectedEdge?.edge_id === edge.edge_id;
          return (
            <g key={edge.edge_id} className={selected ? "edge-group selected" : "edge-group"}>
              <polyline
                points={points}
                className="edge-hit"
                role="button"
                tabIndex="0"
                aria-label={`${edge.edge_id}、${STATE_LABELS[edge.display_state]}。証拠を表示`}
                aria-pressed={selected}
                onClick={() => onSelectEdge(edge)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onSelectEdge(edge);
                  }
                }}
              />
              <polyline
                points={points}
                className={`route-edge edge-${edge.display_state.toLowerCase()}`}
                aria-hidden="true"
              />
              <circle cx={midpoint[0]} cy={midpoint[1]} r="16" className={`edge-marker edge-${edge.display_state.toLowerCase()}`} aria-hidden="true" />
              <text x={midpoint[0]} y={midpoint[1] + 6} textAnchor="middle" className="edge-mark-text" aria-hidden="true">{STATE_MARKS[edge.display_state]}</text>
            </g>
          );
        })}
      </svg>
      <StateLegend />
      <p className="map-caption">縮尺・実座標を持たないUI連続性用の合成図です。実地経路、避難可否、所要時間を示しません。</p>
    </div>
  );
}

function ThreeDNotice({ onReturn }) {
  return (
    <section className="three-d-notice" aria-labelledby="three-d-title">
      <p className="eyebrow">NON-FATAL OPTIONAL LAYER</p>
      <h2 id="three-d-title">3Dは未接続です</h2>
      <p>検証済みtileset URLとattributionが未確定のため、Cesium/PLATEAUをロードしていません。2D表示と証拠情報は引き続き利用できます。</p>
      <button type="button" onClick={onReturn}>2Dへ戻る</button>
    </section>
  );
}

function EvidencePanel({ city, selectedEdge }) {
  if (!selectedEdge) return <aside className="evidence-panel"><h2>edge証拠</h2><p>edgeがありません。</p></aside>;
  const selectedSources = selectedEdge.source_ids.map((sourceId) => city.sources.find((source) => source.source_id === sourceId));
  return (
    <aside className="evidence-panel" aria-labelledby="evidence-title">
      <div className="section-heading">
        <p className="eyebrow">TRACEABLE EDGE EVIDENCE</p>
        <h2 id="evidence-title">edge証拠</h2>
      </div>
      <dl>
        <div><dt>edge ID</dt><dd><code>{selectedEdge.edge_id}</code></dd></div>
        <div><dt>表示状態</dt><dd><span className={`state-word state-${selectedEdge.display_state.toLowerCase()}`}>{STATE_MARKS[selectedEdge.display_state]} {STATE_LABELS[selectedEdge.display_state]}</span></dd></div>
        <div><dt>シナリオ</dt><dd>NOT_COMPUTED — precomputed scenario output未接続</dd></div>
        <div><dt>証拠取扱い</dt><dd>NOT_COMPUTED — strict/optimistic output未接続</dd></div>
        <div><dt>比較断面</dt><dd>NOT_COMPUTED — Before/After output未接続</dd></div>
        <div><dt>base/static幅</dt><dd>{formatOptional(selectedEdge.base_clear_width_m, selectedEdge.width_reason)}</dd></div>
        <div><dt>M7残存幅</dt><dd>{formatOptional(selectedEdge.remaining_clear_width_m, selectedEdge.width_reason)}</dd></div>
        <div><dt>左右瓦礫侵入</dt><dd>{formatOptional(selectedEdge.debris_intrusion_left_m, selectedEdge.width_reason)} / {formatOptional(selectedEdge.debris_intrusion_right_m, selectedEdge.width_reason)}</dd></div>
        <div><dt>hazard overlap/depth</dt><dd>{selectedEdge.hazard_overlap} / {formatOptional(selectedEdge.max_depth_m, selectedEdge.hazard_reason)}</dd></div>
        <div><dt>official closure</dt><dd>{selectedEdge.official_closure === null ? "UNKNOWN (null)" : String(selectedEdge.official_closure)}</dd></div>
        <div><dt>hazard data</dt><dd>{selectedEdge.hazard_data_status}</dd></div>
        <div><dt>profile result</dt><dd>NOT_COMPUTED — M6未実装</dd></div>
        <div><dt>observation</dt><dd>{selectedEdge.evidence_status}</dd></div>
        <div><dt>city data class</dt><dd>{city.data_status}</dd></div>
        <div><dt>official metadata</dt><dd>{city.official_metadata_status}</dd></div>
        <div><dt>source確認日</dt><dd>{city.last_verified_at}</dd></div>
        <div><dt>geometry status</dt><dd>{city.map.geometry_status}</dd></div>
      </dl>
      <div className="source-block">
        <h3>selected edge sources</h3>
        <ul>{selectedSources.map((source) => <li key={source.source_id}><code>{source.source_id}</code> — {source.data_class} / {source.last_verified_at} / {source.status}<br /><span>{source.note}</span></li>)}</ul>
      </div>
      <p className="model-caveat">表示geometryはcity-level SYNTHETIC_DEMO fixtureです。scenario・証拠取扱い・比較断面別の結果を示しません。</p>
    </aside>
  );
}

function RealLayerPanel({ config }) {
  return (
    <aside className="evidence-panel real-layer-panel" aria-labelledby="real-layer-evidence-title">
      <div className="section-heading">
        <p className="eyebrow">LAYER-LEVEL PROVENANCE</p>
        <h2 id="real-layer-evidence-title">実座標layerの証拠</h2>
      </div>
      <dl>
        <div><dt>source ID</dt><dd><code>{config.source_id}</code></dd></div>
        <div><dt>source class</dt><dd>{config.source_class}</dd></div>
        <div><dt>data class</dt><dd>{config.data_class}</dd></div>
        <div><dt>geometry</dt><dd>{config.geometry_status}</dd></div>
        <div><dt>graph</dt><dd>{config.topology_status}</dd></div>
        <div><dt>route continuity</dt><dd>{config.route_continuity}</dd></div>
        <div><dt>snapshot</dt><dd>{config.snapshot_at}</dd></div>
        <div><dt>edge count</dt><dd>{config.feature_count}</dd></div>
        <div><dt>artifact SHA</dt><dd><code>{config.artifact_sha256}</code></dd></div>
        <div><dt>corridor SHA</dt><dd><code>{config.corridor_sha256}</code></dd></div>
        <div><dt>license</dt><dd>{config.license}</dd></div>
      </dl>
      <p className="model-caveat">座標bytesはsource-traceableです。ただし候補graphの連続性・通行可否・幅・運用・M6/M7/KPIは未確認または未計算です。</p>
    </aside>
  );
}

function EdgeTable({ city, selectedEdge, onSelectEdge }) {
  return (
    <section id="edge-table" className="edge-table-section" tabIndex="-1" aria-labelledby="edge-table-title">
      <h2 id="edge-table-title">edge一覧（地図の表形式代替）</h2>
      <div className="table-scroll" tabIndex="0" aria-label="横スクロール可能なedge一覧">
        <table>
          <caption className="sr-only">各edgeの状態と証拠を選択する表</caption>
          <thead><tr><th scope="col">edge ID</th><th scope="col">状態</th><th scope="col">証拠</th><th scope="col">操作</th></tr></thead>
          <tbody>{city.map.edges.map((edge) => <tr key={edge.edge_id} className={selectedEdge?.edge_id === edge.edge_id ? "active-row" : ""}><th scope="row"><code>{edge.edge_id}</code></th><td>{STATE_MARKS[edge.display_state]} {STATE_LABELS[edge.display_state]}</td><td>{edge.evidence_status}</td><td><button type="button" onClick={() => onSelectEdge(edge)}>証拠を表示</button></td></tr>)}</tbody>
        </table>
      </div>
    </section>
  );
}

function EvidenceTables({ city }) {
  const readinessRows = [
    ["facility", city.facility_status, city.facility_reason],
    ["entrance", city.entrance_status, city.entrance_reason],
    ["capacity", city.capacity_status, city.capacity_reason],
    ["operation", city.operation_status, city.operation_reason],
    ["demand", city.demand_status, city.demand_reason],
    ["origin", city.origin_status, city.origin_reason],
    ["profile (M6)", city.profile_status, city.profile_reason],
  ];
  return (
    <section className="evidence-tables" aria-labelledby="evidence-tables-title">
      <div className="section-heading">
        <p className="eyebrow">NON-MAP EVIDENCE ALTERNATIVES</p>
        <h2 id="evidence-tables-title">source・facility・gap一覧</h2>
      </div>
      <div className="evidence-table-grid">
        <div className="table-scroll" tabIndex="0" aria-label="横スクロール可能なsource一覧">
          <table>
            <caption>表示中の都市に紐づくsource metadataと合成fixture</caption>
            <thead><tr><th scope="col">source ID</th><th scope="col">区分</th><th scope="col">確認日</th><th scope="col">状態・限界</th></tr></thead>
            <tbody>{city.sources.map((source) => <tr key={source.source_id}><th scope="row"><code>{source.source_id}</code></th><td>{source.data_class}</td><td>{source.last_verified_at}</td><td>{source.status} — {source.note}</td></tr>)}</tbody>
          </table>
        </div>
        <div className="table-scroll" tabIndex="0" aria-label="横スクロール可能なfacility readiness一覧">
          <table>
            <caption>施設・入口・容量・運用のreadiness</caption>
            <thead><tr><th scope="col">対象</th><th scope="col">状態</th><th scope="col">理由</th></tr></thead>
            <tbody>{readinessRows.map(([name, status, reason]) => <tr key={name}><th scope="row">{name}</th><td>{status}</td><td lang="en">{reason}</td></tr>)}</tbody>
          </table>
        </div>
        <div className="table-scroll" tabIndex="0" aria-label="横スクロール可能なdata gap一覧">
          <table>
            <caption>KPIを未計算に保つdata gap</caption>
            <thead><tr><th scope="col">KPI</th><th scope="col">value</th><th scope="col">reason</th></tr></thead>
            <tbody>{Object.entries(city.kpis).map(([key, entry]) => <tr key={key}><th scope="row">{KPI_LABELS[key] ?? key}</th><td>{entry.value === null ? "null" : String(entry.value)}</td><td lang="en">{entry.reason}</td></tr>)}</tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function OfficialEvidencePanel({ evidence }) {
  if (!evidence) return null;
  const rows = [
    ["terrain", evidence.terrain.status, evidence.terrain.reason],
    ["hazard", evidence.hazard.status, evidence.hazard.reason],
    ["PLATEAU", evidence.plateau.status, evidence.plateau.reason],
    ["M7", evidence.m7.status, `${evidence.m7.all_edge_count} edges / deep pilot ${evidence.m7.deep_pilot_count} / ready ${evidence.m7.evidence_ready_count} / computed ${evidence.m7.computed_count}. ${evidence.m7.city_limitations}`],
    ["M6/profile", evidence.m6.status, evidence.m6.reason],
    ["facility", evidence.facility.status, evidence.facility.reason],
  ];
  return (
    <section className="evidence-tables official-evidence" aria-labelledby="official-evidence-title">
      <div className="section-heading"><p className="eyebrow">SOURCE-BOUND OFFICIAL EVIDENCE</p><h2 id="official-evidence-title">公式データの接続状態</h2></div>
      <p>source receiptに結合した表示です。未接続の地形・ハザードからCLOSED/FAILを導出せず、建物setback・damage・debrisも推定しません。</p>
      <div className="table-scroll" tabIndex="0" aria-label="公式データ接続状態一覧"><table><caption>subareas: {evidence.subareas.join(" / ") || "not specified"}</caption><thead><tr><th scope="col">対象</th><th scope="col">状態</th><th scope="col">根拠・未解決理由</th></tr></thead><tbody>{rows.map(([name, status, reason]) => <tr key={name}><th scope="row">{name}</th><td>{status}</td><td>{reason}</td></tr>)}</tbody></table></div>
      <div className="table-scroll" tabIndex="0" aria-label="source hash binding"><table><caption>source hash binding</caption><tbody>{Object.entries(evidence.source_hashes).map(([name, value]) => <tr key={name}><th scope="row">{name}</th><td><code>{value}</code></td></tr>)}</tbody></table></div>
      {evidence.terrain.products.length > 0 && <div className="table-scroll" tabIndex="0" aria-label="terrain product inventory"><table><caption>terrain products — receipt <code>{evidence.terrain.receipt_sha256}</code></caption><thead><tr><th>mesh</th><th>DEM</th><th>horizontal CRS</th><th>vertical datum</th><th>AOI</th><th>validation</th><th>license</th><th>records / locations / null</th></tr></thead><tbody>{evidence.terrain.products.map((row) => <tr key={row.dataset_id}><td>{(row.mesh_ids ?? [row.mesh_id]).join(", ")}</td><td>{row.dem_class}</td><td>{row.horizontal_crs}</td><td>{row.vertical_datum}</td><td>{row.aoi}</td><td>{row.validation_result}</td><td>{row.license_status}</td><td>{row.status}: records {row.sample_record_count}, unique locations {row.unique_coordinate_count}, numeric {row.numeric_sample_count}, null records {row.null_record_count}, null locations {row.null_coordinate_count}</td></tr>)}</tbody></table></div>}
      {evidence.terrain.samples.some((sample) => sample.elevation_m === null) && <div className="table-scroll" tabIndex="0" aria-label="terrain unresolved native-cell records"><table><caption>unresolved native-cell records（record数と独立地点数を分離）</caption><thead><tr><th>sample</th><th>DEM</th><th>status</th><th>reason</th></tr></thead><tbody>{evidence.terrain.samples.filter((sample) => sample.elevation_m === null).map((sample) => <tr key={sample.sample_id}><td><code>{sample.sample_id}</code></td><td>{sample.product}</td><td>{sample.status}</td><td>{sample.reason}</td></tr>)}</tbody></table></div>}
      {evidence.hazard.layers.length > 0 && <div className="table-scroll" tabIndex="0" aria-label="Kyoto hazard layer status"><table><caption>Kyoto subarea hazard layers</caption><thead><tr><th>subarea</th><th>layer</th><th>artifact</th><th>status</th><th>reason</th></tr></thead><tbody>{evidence.hazard.layers.map((row) => <tr key={`${row.subarea}-${row.layer}`}><td>{row.subarea}</td><td>{row.layer}</td><td>{row.artifact_status}</td><td>{row.status}</td><td>{row.reason}</td></tr>)}</tbody></table></div>}
      {evidence.hazard.scenarios.length > 0 && <div className="table-scroll" tabIndex="0" aria-label="Fujisawa hazard scenario inventory"><table><caption>Fujisawa scenario inventory (AOI: enoshima_katase)</caption><thead><tr><th>dataset</th><th>scenario</th><th>layer</th><th>source</th><th>version</th><th>license/validation</th><th>CRS/bounds</th><th>status</th><th>reason</th></tr></thead><tbody>{evidence.hazard.scenarios.map((row) => <tr key={row.dataset_id}><td>{row.dataset_id}</td><td>{row.scenario}</td><td>{row.layer_kind}</td><td>{row.official_source} / {row.official_url}</td><td>{row.version_date}</td><td>{row.license_review} / {row.validation_result}</td><td>{row.crs} / {row.bounds_native}</td><td>{row.status}</td><td>{row.reason}</td></tr>)}</tbody></table></div>}
      <p className="model-caveat">PLATEAU: {evidence.plateau.aoi_count} AOIs ({evidence.plateau.aoi_scope.join(" / ")}) / {evidence.plateau.fallback}。実tilesは接続していません。</p>
      {evidence.plateau.inventory?.length > 0 && <div className="table-scroll" tabIndex="0" aria-label="京都PLATEAU 2025 building evidence inventory"><table><caption>京都PLATEAU 2025 building evidence inventory（実3D未接続・既存candidate 2D fallback）</caption><thead><tr><th>AOI</th><th>package</th><th>CRS</th><th>building ID</th><th>footprint</th><th>height</th><th>coverage</th><th>status</th><th>reason</th></tr></thead><tbody>{evidence.plateau.inventory.map((row) => <tr key={row.subarea_id}><td>{row.subarea_id}</td><td>{row.package_verification_status}</td><td>{row.source_crs}</td><td>{row.stable_building_id_status}</td><td>{row.footprint_status}</td><td>{row.official_height_attribute_status}</td><td>{row.aoi_coverage_status}</td><td>{row.connection_mode} / {row.fallback}</td><td>{row.reason}</td></tr>)}</tbody></table></div>}
      {evidence.facility.categories && <div className="table-scroll" tabIndex="0" aria-label="京都公式施設5カテゴリ接続状態"><table><caption>京都公式施設5カテゴリ（住所geocodingなし）</caption><thead><tr><th>category</th><th>status</th><th>records</th><th>map</th><th>reason / next</th></tr></thead><tbody>{Object.entries(evidence.facility.categories).map(([category, value]) => <tr key={category}><th scope="row">{category}</th><td>{value.status}</td><td>{value.record_count}</td><td>{String(value.map_connected)}</td><td>{value.reason ?? "Source-provided longitude/latitude only; opening, entrance, accessibility, safety, and disaster usability remain UNKNOWN."} {value.next_acquisition_method ?? ""}</td></tr>)}</tbody></table></div>}
      {evidence.facility.marker_policy === "SOURCE_COORDINATES_ONLY_NO_GEOCODING" && <div className="table-scroll" tabIndex="0" aria-label="京都の公式座標施設一覧"><table><caption>京都公式施設 {evidence.facility.record_count}件（原本提供経緯度のみ、silent geocodingなし。原本記載値は現在の開設・入口・利用可能性を意味しません）</caption><thead><tr><th>ID</th><th>category</th><th>name</th><th>address</th><th>source/version/hash</th><th>coordinate method</th><th>原本記載属性</th><th>入口/施錠/現在運用/accessibility</th></tr></thead><tbody>{evidence.facility.records.map((record) => <tr key={record.facility_record_id}><th scope="row"><code>{record.facility_record_id}</code></th><td>{record.category}</td><td>{record.name}</td><td>{record.address}</td><td>{record.source_id} / {record.source_version_or_valid_as_of}<br /><code>{record.source_sha256}</code></td><td>{record.coordinate_method}</td><td>{Object.entries(record.source_attributes ?? {}).map(([key, value]) => <p key={key}><b>{key}</b>: {value ?? "null"}</p>)}</td><td>{record.entrance_status} / {record.unlock_status} / {record.current_operation_status} / {record.accessibility_status}</td></tr>)}</tbody></table></div>}
      {evidence.facility.marker_policy === "TABLE_ONLY_NO_MARKERS_OR_GEOCODING" && <div className="table-scroll" tabIndex="0" aria-label="藤沢の住所のみ施設一覧"><table><caption>藤沢・江の島／片瀬の公式施設 {evidence.facility.record_count}件（ADDRESS_ONLY、地図markerなし）。ostomate detailは車いす・入口・段差・開設・災害利用可能性を意味しません。</caption><thead><tr><th scope="col">ID</th><th scope="col">施設名</th><th scope="col">住所</th><th scope="col">電話</th><th scope="col">source/currentness/hash</th><th scope="col">原本記載属性</th><th scope="col">車いす/入口/解錠/段差/現在開設/災害利用</th></tr></thead><tbody>{evidence.facility.records.map((record) => <tr key={record.facility_record_id}><th scope="row"><code>{record.facility_record_id}</code></th><td>{record.name}</td><td>{record.address}</td><td>{record.phone ?? "null"}</td><td>{record.source_id} / {record.source_version_or_valid_as_of ?? "null"}<br /><code>{record.source_sha256}</code></td><td>ostomate detail: {String(record.ostomate_detail_available)}</td><td>UNKNOWN / UNKNOWN / UNKNOWN / UNKNOWN / UNKNOWN / UNKNOWN</td></tr>)}</tbody></table></div>}
      {evidence.m7.kyoto_deep_pilot_edges?.length > 0 && <div className="table-scroll" tabIndex="0" aria-label="京都M7 deep pilot reasoned null"><table><caption>京都M7 deep pilot {evidence.m7.kyoto_deep_pilot_edges.length} edge（computed 0、field別取得方法）</caption><thead><tr><th>edge</th><th>group</th><th>status/result</th><th>missing</th><th>evidence candidates / next acquisition</th></tr></thead><tbody>{evidence.m7.kyoto_deep_pilot_edges.map((row) => <tr key={row.edge_id}><th scope="row"><code>{row.edge_id}</code></th><td>{row.aoi_group} / {row.subarea_partition_status}</td><td>{row.status} / {String(row.m7_result)}</td><td>{row.missing_fields.join(", ")}</td><td>{Object.entries(row.field_resolution).map(([field, value]) => <p key={field}><b>{field}</b>: {value.evidence_candidates.join(" / ")}。次: {value.next_acquisition_method}</p>)}</td></tr>)}</tbody></table></div>}
    </section>
  );
}

function downloadText(filename, type, content) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  // Keep the object URL alive long enough for slower browsers to begin reading it.
  setTimeout(() => URL.revokeObjectURL(url), 1_000);
}

function ReviewChecklistPanel({ checklist, facilityRecords, facilitySourceCatalog, hazardExposures, terrainSamples }) {
  const [scenario, setScenario] = useState("ALL");
  const [revision, setRevision] = useState("ALL");
  const [coverage, setCoverage] = useState("ALL");
  const [unknown, setUnknown] = useState("ALL");
  const [owner, setOwner] = useState("ALL");
  const [reasonQuery, setReasonQuery] = useState("");
  const [sortBy, setSortBy] = useState("EDGE");
  const [terrainProduct, setTerrainProduct] = useState("ALL");
  useEffect(() => { setScenario("ALL"); setRevision("ALL"); setCoverage("ALL"); setUnknown("ALL"); setOwner("ALL"); setReasonQuery(""); setSortBy("EDGE"); setTerrainProduct("ALL"); }, [checklist?.checklist_id]);
  if (!checklist) return null;
  const sourceCatalog = checklist.source_catalog ?? {};
  const exposureByRef = new Map(hazardExposures.map((hazard) => [`${hazard.edge_id}\0${hazard.scenario_id}\0${hazard.source_id}`, { ...hazard, ...sourceCatalog[hazard.source_id] }]));
  const terrainById = new Map(terrainSamples.map((sample) => [sample.sample_id, sample]));
  for (const row of checklist.rows) {
    for (const id of row.terrain_sample_ids ?? []) {
      if (!terrainById.has(id)) throw new Error(`Missing required terrain sample: ${id}`);
    }
  }
  const terrainProducts = [...new Set(terrainSamples.map((sample) => sample.product))].sort();
  const hydratedRows = checklist.rows.map((row) => ({ ...row, terrain_samples: (row.terrain_sample_ids ?? []).map((id) => terrainById.get(id)).filter((sample) => terrainProduct === "ALL" || sample.product === terrainProduct), hazards: row.hazard_refs.map((ref) => exposureByRef.get(ref)).filter(Boolean) }));
  const allHazards = hydratedRows.flatMap((row) => row.hazards);
  const scenarios = [...new Set(allHazards.map((hazard) => hazard.scenario_id))].sort();
  const revisions = [...new Set(allHazards.map((hazard) => hazard.source_revision))].sort();
  const coverageStatuses = [...new Set(allHazards.map((hazard) => hazard.coverage_status))].sort();
  const unknowns = [...new Set(hydratedRows.flatMap((row) => row.unknowns))].sort();
  const owners = [...new Set(hydratedRows.flatMap((row) => row.owner_candidate_types))].sort();
  const visibleRows = selectChecklistRows(hydratedRows, { scenario, revision, coverage, unknown, owner, reason: reasonQuery }, sortBy);
  const exportFacilityRecords = facilityRecords.map((record) => {
    const source = facilitySourceCatalog[record.source_id];
    return {
      ...record,
      source_url: source.source_url,
      license_status: source.license_status,
      source_published_at: source.published_at,
      source_valid_as_of: source.valid_as_of,
      source_acquired_at: source.acquired_at,
      source_temporal_status_reason: source.temporal_status_reason,
    };
  });
  const terrainUnresolved = selectUnresolvedTerrainRecords(terrainSamples, terrainProduct);
  const exportedChecklist = { ...checklist, facility: { ...checklist.facility, records: exportFacilityRecords }, rows: visibleRows.map((row) => ({ ...row, hazard_refs: row.hazards.map((hazard) => `${hazard.edge_id}\0${hazard.scenario_id}\0${hazard.source_id}`) })), terrain_unresolved_records: terrainUnresolved.records, terrain_unresolved_summary: terrainUnresolved.summary, filters: { scenario, revision, coverage, terrain_product: terrainProduct, unknown, owner, reason: reasonQuery }, sort_by: sortBy };
  const filename = checklist.checklist_id.replace(/[^A-Za-z0-9._-]+/g, "_").replace(/[. ]+$/g, "") || "ablepath-review";
  return (
    <section className="review-checklist" aria-labelledby="review-checklist-title">
      <div className="section-heading"><p className="eyebrow">SOURCE-BOUND REVIEW EXPORT</p><h2 id="review-checklist-title">地域・区間の確認リスト</h2></div>
      <p><code>{checklist.checklist_id}</code> — {checklist.status} / candidate path {checklist.path_status}</p>
      <p>候補道路と公式証拠の空間的な重なりを確認する資料です。安全性・アクセシビリティ・通行可能性・行政検証を示しません。</p>
      <label>確認リスト・exportのsource scenario<select aria-label="確認リスト・exportのsource scenario" value={scenario} onChange={(event) => setScenario(event.target.value)}><option value="ALL">ALL（scenario別、相互unionなし）</option>{scenarios.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
      <label>source revision<select aria-label="source revision" value={revision} onChange={(event) => setRevision(event.target.value)}><option value="ALL">ALL</option>{revisions.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
      <label>DEM product<select aria-label="DEM product" value={terrainProduct} onChange={(event) => setTerrainProduct(event.target.value)}><option value="ALL">ALL（product別、優先順位なし）</option>{terrainProducts.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
      <label>coverage status<select aria-label="coverage status" value={coverage} onChange={(event) => setCoverage(event.target.value)}><option value="ALL">ALL</option>{coverageStatuses.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
      <label>missing field<select aria-label="missing field" value={unknown} onChange={(event) => setUnknown(event.target.value)}><option value="ALL">ALL</option>{unknowns.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
      <label>担当候補の種別<select aria-label="担当候補の種別" value={owner} onChange={(event) => setOwner(event.target.value)}><option value="ALL">ALL</option>{owners.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
      <label>reason/source検索<input aria-label="reason/source検索" value={reasonQuery} onChange={(event) => setReasonQuery(event.target.value)} /></label>
      <label>並び順<select aria-label="確認リストの並び順" value={sortBy} onChange={(event) => setSortBy(event.target.value)}><option value="EDGE">edge</option><option value="REVISION">source revision</option><option value="COVERAGE">coverage</option><option value="REASON">reason</option><option value="OWNER">owner candidate</option></select></label>
      <p>Map overlayは接続済みの全official layerを表示します。このselectorは確認リストとexportだけを絞り込みます。</p>
      <dl className="checklist-summary">
        <div><dt>terrain</dt><dd>{checklist.terrain.status} — {checklist.terrain.reason}</dd></div>
        <div><dt>facility</dt><dd>{checklist.facility.status} / {checklist.facility.record_count} records — {checklist.facility.reason}</dd></div>
        <div><dt>candidate distance</dt><dd>{checklist.candidate_distance ?? "null"} {checklist.candidate_distance_unit}</dd></div>
      </dl>
      <div className="export-actions" role="group" aria-label="確認リストexport">
        <button type="button" onClick={() => downloadText(`${filename}.csv`, "text/csv;charset=utf-8", checklistToCsv(exportedChecklist))}>CSVを保存</button>
        <button type="button" onClick={() => downloadText(`${filename}.json`, "application/json", checklistToJson(exportedChecklist))}>JSONを保存</button>
        <button type="button" onClick={() => downloadText(`${filename}.html`, "text/html;charset=utf-8", checklistToPrintableHtml(exportedChecklist))}>印刷用HTMLを保存</button>
      </div>
      <div className="table-scroll" tabIndex="0" aria-label="選択区間の確認リスト"><table><caption>{scenario} / {visibleRows.length} candidate edges</caption><thead><tr><th>edge</th><th>hazard evidence</th><th>terrain</th><th>facility</th><th>unknowns</th></tr></thead><tbody>{visibleRows.map((row) => <tr key={row.edge_id}><th scope="row"><code>{row.edge_id}</code></th><td>{row.hazards.length ? row.hazards.map((hazard) => <p key={`${hazard.scenario_id}-${hazard.source_id}`}>{hazard.scenario_id}: {hazard.relation} / {hazard.overlap_length_m ?? "null"} m / {hazard.source_classes.join(" | ") || "class none"}<br /><code>{hazard.source_id}@{hazard.source_revision} / {hazard.source_sha256}</code><br />{hazard.reason}</p>) : "NO_DATA for selected scenario"}</td><td>{row.terrain_status} — {row.terrain_reason}{(row.terrain_samples ?? []).map((sample) => <p key={sample.sample_id}><code>{sample.node_id ?? `${sample.edge_id}#${sample.vertex_index}`} / {sample.product}</code>: {sample.elevation_m ?? "null"} {sample.unit} ({sample.surface_type ?? sample.status})</p>)}</td><td>{row.facility_status}</td><td>UNKNOWN: {row.unknowns.join(", ")}</td></tr>)}</tbody></table></div>
    </section>
  );
}

function Loading() {
  return <main id="main-content" className="center-state" tabIndex="-1" aria-busy="true" role="status" aria-live="polite"><p className="eyebrow">LOADING PRECOMPUTED DATA</p><h2>都市データを確認しています</h2></main>;
}

function ErrorState({ message }) {
  return <main id="main-content" className="center-state error-state" tabIndex="-1" role="alert" aria-live="assertive"><p className="eyebrow">FAIL CLOSED</p><h2>ビューアを開始できません</h2><p>{message}</p><p>欠落データを0・安全・OPENへ置き換えず停止しました。</p></main>;
}

export function App() {
  const [catalog, setCatalog] = useState(null);
  const [mapCatalog, setMapCatalog] = useState(null);
  const [state, setState] = useState(null);
  const [error, setError] = useState("");
  const [announcement, setAnnouncement] = useState("起動中");
  const [fallbackNotice, setFallbackNotice] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [adminChecklist, setAdminChecklist] = useState(null);
  const [adminNotice, setAdminNotice] = useState(null);
  const [selectedPathNodes, setSelectedPathNodes] = useState([null, null]);

  useEffect(() => {
    let active = true;
    Promise.all([
      loadCatalog(fetch, "./data/cities.json", 5000),
      loadMapCatalog(fetch, "./data/maps/map-layers.json", 5000).catch(() => ({ cities: [] })),
    ])
      .then(([loaded, loadedMapCatalog]) => {
        if (!active) return;
        const initial = selectInitialState(loaded, window.location.search);
        setCatalog(loaded);
        setMapCatalog(loadedMapCatalog);
        setState({
          ...initial,
          mapMode: selectInitialMapMode(loadedMapCatalog, initial.city.city_id, window.location.search),
        });
        setAnnouncement(loadedMapCatalog.cities.length ? "precomputed city dataとhash検証済みmap catalogを読み込みました" : "実座標catalogが欠落またはhash不一致のため、合成図を表示します");
      })
      .catch((loadError) => active && setError(loadError.message));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!state) return undefined;
    let active = true;
    setAnalysis(null);
    loadDeliveryAnalysis(fetch, `./data/analysis/${state.city.city_id}.json`, state.city.city_id).then((data) => { if (!active) return; setAnalysis(data); setSelectedPathNodes([data.path_fixture.start_node_id, data.path_fixture.end_node_id]); }).catch((loadError) => active && setError(loadError.message));
    return () => { active = false; };
  }, [state?.city.city_id]);

  useEffect(() => {
    if (!state) return undefined;
    let active = true;
    setAdminChecklist(null);
    setAdminNotice(null);
    loadAdminChecklist(fetch, `./data/admin/${state.city.city_id}.checklist.json`, state.city.city_id)
      .then((data) => { if (active) setAdminChecklist(data); })
      .catch((loadError) => { if (active) setAdminNotice(`行政確認ワークフローの確認票を読み込めませんでした: ${loadError.message}`); });
    return () => { active = false; };
  }, [state?.city.city_id]);

  useEffect(() => {
    if (!state) return;
    window.history.replaceState(null, "", serializeState(state));
    document.title = `${state.city.display_name} / scenario output NOT_COMPUTED | AblePath`;
  }, [state]);

  const sourceCount = useMemo(() => state?.city.source_ids.length ?? 0, [state]);
  const selectRealEdge = useCallback((edgeId) => {
    setState((current) => current ? { ...current, selectedRealEdgeId: edgeId } : current);
  }, []);
  const announce = useCallback((message) => setAnnouncement(message), []);
  const fallbackTo2d = useCallback((reason) => {
    setState((current) => current ? { ...current, view: "2d" } : current);
    setFallbackNotice(reason);
    setAnnouncement(`${reason}。2D表示と証拠情報を継続します`);
  }, []);
  if (error) return <ErrorState message={error} />;
  if (!catalog || !mapCatalog || !state) return <Loading />;

  const cityMapConfig = mapConfigForCity(mapCatalog, state.city.city_id);
  const realMode = state.mapMode === "real" && Boolean(cityMapConfig?.real_2d);
  const cityAnalysis = analysis?.city_id === state.city.city_id ? analysis : null;
  const selectedPath = cityAnalysis?.path_matrix?.[`${selectedPathNodes[0]}__${selectedPathNodes[1]}`] ?? cityAnalysis?.path_fixture ?? null;
  const selectedChecklist = cityAnalysis?.review_checklists?.[`${selectedPathNodes[0]}__${selectedPathNodes[1]}`] ?? null;

  function updateState(nextState, message) {
    setState(nextState);
    setAnnouncement(message);
  }
  function selectEdge(edge) {
    updateState({ ...state, selectedEdge: edge }, `${edge.edge_id}の証拠を表示しました`);
  }
  return (
    <div className="app-shell">
      <Header city={state.city} catalog={catalog} />
      <div className="disclaimer" role="note"><b>静的スナップショット比較</b><span>シナリオ結果であり、リアルタイムの安全保証・個別建物の倒壊予測・行政判断ではありません。</span></div>
      {fallbackNotice && <div className="map-fallback-notice" role="status"><b>3Dから2Dへfallback</b><span>{fallbackNotice}。2D表示と証拠情報を継続します。</span></div>}
      <main id="main-content" tabIndex="-1">
        <section className="corridor-intro" aria-labelledby="corridor-title">
          <div><p className="eyebrow">{state.city.municipality} / SCENARIO OUTPUT NOT_COMPUTED</p><h2 id="corridor-title">{state.city.display_name}</h2><p>{state.city.corridor_name}</p></div>
          <dl><div><dt>公式metadata</dt><dd>{state.city.official_metadata_status}</dd></div><div><dt>表示geometry</dt><dd>{realMode ? cityMapConfig.real_2d.geometry_status : state.city.map.geometry_status}</dd></div><div><dt>layer</dt><dd>{realMode ? "REAL COORDINATES / CANDIDATE" : "SYNTHETIC_DEMO / SVG"}</dd></div><div><dt>{realMode ? "source ID" : "source IDs"}</dt><dd>{realMode ? <code>{cityMapConfig.real_2d.source_id}</code> : sourceCount}</dd></div></dl>
        </section>
        <Controls catalog={catalog} mapCatalog={mapCatalog} state={state} onStateChange={updateState} analysis={cityAnalysis} selectedStart={selectedPathNodes[0]} selectedEnd={selectedPathNodes[1]} onPathChange={(start, end) => setSelectedPathNodes([start, end])} />
        <KpiGrid city={state.city} />
        <div className="workspace-grid">
          <section className="map-column" role="region" aria-label={state.view === "2d" ? "2D地図" : "3D可用性"}>
            {state.view === "2d" ? (
              realMode ? (
                <MapLibreMap
                  key={`${state.cityId}:${cityMapConfig.real_2d.data_path}`}
                  config={cityMapConfig.real_2d}
                  officialLayers={{ hazard: cityAnalysis?.official_evidence?.hazard?.display_layers ?? [], facility: cityAnalysis?.official_evidence?.facility?.display_layer ?? null }}
                  selectedEdgeId={state.selectedRealEdgeId}
                  selectedPathEdgeIds={selectedPath?.edge_ids ?? []}
                  m7Readiness={cityAnalysis?.official_evidence?.m7?.kyoto_deep_pilot_edges?.length ? cityAnalysis.official_evidence.m7.kyoto_deep_pilot_edges : cityAnalysis?.m7?.readiness ?? []}
                  onSelectEdge={selectRealEdge}
                  onAnnouncement={announce}
                />
              ) : <Map2D city={state.city} selectedEdge={state.selectedEdge} onSelectEdge={selectEdge} />
            ) : (
              <CesiumPanel config={cityMapConfig?.cesium ?? null} onFallback={fallbackTo2d} onAnnouncement={announce} />
            )}
          </section>
          {realMode ? <RealLayerPanel config={cityMapConfig.real_2d} /> : <EvidencePanel city={state.city} selectedEdge={state.selectedEdge} />}
        </div>
        {!realMode && <EdgeTable city={state.city} selectedEdge={state.selectedEdge} onSelectEdge={selectEdge} />}
        {realMode && cityAnalysis && <section className="candidate-analysis" aria-label="candidate path analysis"><h2>candidate path fixture</h2><p>{selectedPath?.status} / {selectedPath?.unit}</p><p>coordinate-degree distance: {selectedPath?.geometric_length ?? "—"}</p><p>この coordinate_degree は地理距離・メートル距離ではありません。</p><p>{selectedPath?.reason}</p><p>ordered edge IDs: {selectedPath?.edge_ids.join(", ") || "—"}</p><p>hazard: {cityAnalysis.hazard_overlap.status} — {cityAnalysis.hazard_overlap.reason}</p><p>M7 {cityAnalysis.m7.status}; ready {cityAnalysis.m7.ready_edge_count}; computed {cityAnalysis.m7.computed_edge_count}; M6 {cityAnalysis.m6.status}</p></section>}
        {realMode && <ReviewChecklistPanel checklist={selectedChecklist ? { ...selectedChecklist, source_catalog: cityAnalysis?.official_evidence?.hazard?.source_catalog ?? {} } : null} facilityRecords={cityAnalysis?.official_evidence?.facility?.records ?? []} facilitySourceCatalog={cityAnalysis?.official_evidence?.facility?.source_catalog ?? {}} hazardExposures={cityAnalysis?.official_evidence?.hazard?.edge_exposures ?? []} terrainSamples={cityAnalysis?.official_evidence?.terrain?.samples ?? []} />}
        <AdminChecklistPanel checklist={adminChecklist} notice={adminNotice} />
        <OfficialEvidencePanel evidence={cityAnalysis?.official_evidence} />
        <EvidenceTables city={state.city} />
        <section className="method-note" aria-labelledby="method-title"><p className="eyebrow">INTERPRETATION BOUNDARY</p><h2 id="method-title">この画面で計算していないこと</h2><p>M6/profile評価、需要配分、施設容量、入口、開設・運用状態、時系列の避難成立性は未計算です。KPIは不足項目を0へ変換せず、理由付きnullとして表示します。都市間の順位比較は行いません。</p><p>Attribution: {realMode ? cityMapConfig.real_2d.attribution : <>source metadataは各city packの <code>sources/source_manifest.csv</code>、表示geometryは <code>SYNTHETIC_DEMO</code> fixture</>}。</p></section>
      </main>
      <footer><span>AblePath engineering demo</span><span>Human review required before main merge</span></footer>
      <p className="sr-only" aria-live="polite" aria-atomic="true">{announcement}</p>
    </div>
  );
}
