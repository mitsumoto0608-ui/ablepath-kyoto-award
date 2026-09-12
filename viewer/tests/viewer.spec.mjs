import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";

const EXPORT_CITIES = ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"];
const EXPORT_BUTTONS = {
  CSV: "CSVを保存",
  JSON: "JSONを保存",
  HTML: "印刷用HTMLを保存",
};
const EXPORT_CASE_TIMEOUT_MS = 60_000;
const EXPORT_OPERATION_TIMEOUT_MS = 15_000;

// Acceptance map from the former 139-download mega-test. Each city/product/filter/sort
// case owns a fresh browser context and exactly one real CSV/JSON/HTML download triplet.
// This preserves every former assertion without crossing Chromium's repeated-download
// boundary inside a single page/context.
function parseCsvLine(line) {
  const cells = [];
  let cell = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"' && quoted && line[index + 1] === '"') { cell += '"'; index += 1; }
    else if (char === '"') quoted = !quoted;
    else if (char === "," && !quoted) { cells.push(cell); cell = ""; }
    else cell += char;
  }
  cells.push(cell);
  return cells;
}

async function openExportPage(page, cityId) {
  await page.goto(`/?city=${cityId}&layer=real`);
  await expect(page.getByRole("heading", { name: "地域・区間の確認リスト" })).toBeVisible({ timeout: 20_000 });
  await expect(page.getByLabel("選択区間の確認リスト")).toContainText("UNKNOWN");
  for (const label of ["確認リスト・exportのsource scenario", "source revision", "coverage status", "missing field", "担当候補の種別", "確認リストの並び順"]) {
    await expect(page.getByLabel(label)).toBeEnabled();
  }
}

function createDownloadObserver(page, cityId, caseId, projectName) {
  const caseStartedAt = Date.now();
  let sequence = 0;
  return async (format) => {
    sequence += 1;
    const downloadSequence = sequence;
    const elapsed = () => Date.now() - caseStartedAt;
    const log = (stage, detail = {}) => console.log(`[export-e2e] ${JSON.stringify({ city: cityId, case: caseId, format, download_sequence: downloadSequence, stage, elapsed_ms: elapsed(), project: projectName, ...detail })}`);
    return test.step(`${cityId}/${caseId}/${format}/${downloadSequence}`, async () => {
      const waiting = page.waitForEvent("download", { timeout: EXPORT_OPERATION_TIMEOUT_MS });
      log("waiter_registered");
      log("click_started");
      await page.getByRole("button", { name: EXPORT_BUTTONS[format], exact: true }).click();
      log("click_completed");
      const download = await waiting;
      log("download_started", { suggested_filename: download.suggestedFilename() });
      const failure = await download.failure();
      expect(failure).toBeNull();
      const savedPath = await download.path();
      expect(savedPath).not.toBeNull();
      const content = await readFile(savedPath, "utf8");
      expect(Buffer.byteLength(content, "utf8")).toBeGreaterThan(0);
      expect(download.suggestedFilename()).toMatch(new RegExp(`\\.${format === "HTML" ? "html" : format.toLowerCase()}$`));
      log("download_completed", { suggested_filename: download.suggestedFilename(), bytes: Buffer.byteLength(content, "utf8"), failure });
      return content;
    });
  };
}

async function assertScreenMatchesExports(page, download) {
  const screenEdges = await page.getByLabel("選択区間の確認リスト").locator("tbody th code").allTextContents();
  const json = await download("JSON");
  const payload = JSON.parse(json);
  expect(payload.rows.map((row) => row.edge_id)).toEqual(screenEdges);

  const csv = await download("CSV");
  const csvLines = csv.trimEnd().split("\n");
  const csvHeader = parseCsvLine(csvLines[0]);
  const rowKindIndex = csvHeader.indexOf("row_kind");
  const edgeIndex = csvHeader.indexOf("edge_id");
  const csvEdges = [...new Set(csvLines.slice(1).map(parseCsvLine).filter((row) => row[rowKindIndex] === "candidate_edge").map((row) => row[edgeIndex]))];
  expect(csvEdges).toEqual(screenEdges);

  const html = await download("HTML");
  const candidateTableStart = html.indexOf("<tbody>", html.indexOf("<table>"));
  expect(candidateTableStart).toBeGreaterThanOrEqual(0);
  const candidateTableEnd = html.indexOf("</tbody>", candidateTableStart);
  expect(candidateTableEnd).toBeGreaterThan(candidateTableStart);
  const candidateTable = html.slice(candidateTableStart, candidateTableEnd);
  const htmlEdges = [...new Set([...candidateTable.matchAll(/<tr><th>([^<]+)<\/th>/g)].map((match) => match[1]).filter((edgeId) => edgeId !== "null"))];
  expect(htmlEdges).toEqual(screenEdges);
  return { payload, csv, html };
}

function assertSourceFilterRows(payload, label, selected) {
  const field = {
    "確認リスト・exportのsource scenario": "scenario_id",
    "source revision": "source_revision",
    "coverage status": "coverage_status",
  }[label];
  expect(field).toBeTruthy();
  expect(payload.rows.length).toBeGreaterThan(0);
  expect(payload.rows.every((row) => row.hazards.length > 0 && row.hazards.every((hazard) => hazard[field] === selected))).toBe(true);
}

function assertSortOrder(payload, sortBy) {
  const sortValue = (row) => ({
    EDGE: row.edge_id,
    REVISION: row.hazards[0]?.source_revision,
    COVERAGE: row.hazards[0]?.coverage_status,
    REASON: row.hazards[0]?.reason,
    OWNER: row.owner_candidate_types[0],
  })[sortBy];
  const expected = [...payload.rows].sort((left, right) => String(sortValue(left) ?? "").localeCompare(String(sortValue(right) ?? ""), "ja") || left.edge_id.localeCompare(right.edge_id));
  expect(payload.rows.map((row) => row.edge_id)).toEqual(expected.map((row) => row.edge_id));
}

for (const cityId of EXPORT_CITIES) {
  test(`[ui_regression] ${cityId} exports baseline`, async ({ page }, testInfo) => {
    test.setTimeout(EXPORT_CASE_TIMEOUT_MS);
    await openExportPage(page, cityId);
    const download = createDownloadObserver(page, cityId, "baseline", testInfo.project.name);
    const baseline = await assertScreenMatchesExports(page, download);
    expect(baseline.csv).toContain("source_sha256");
    expect(baseline.payload.safe_route_claim).toBe(false);
    expect(baseline.html).toContain("印刷用確認リスト");
    for (const content of [baseline.csv, JSON.stringify(baseline.payload), baseline.html]) {
      expect(content).not.toContain("C:\\dev\\");
      expect(content).not.toContain("安全な避難ルート");
    }
    if (cityId === "fujisawa_enoshima") {
      expect(baseline.payload.terrain_unresolved_summary).toEqual({ record_count: 6, unique_coordinate_count: 1 });
      expect(baseline.payload.terrain_unresolved_records).toHaveLength(6);
      expect(baseline.payload.terrain_unresolved_records.every((sample) => sample.elevation_m === null && sample.status === "SURFACE_VALUE_UNRESOLVED" && sample.reason)).toBe(true);
      for (const sample of baseline.payload.terrain_unresolved_records) {
        expect(baseline.csv).toContain(sample.sample_id);
        expect(baseline.csv).toContain(sample.reason);
        expect(baseline.html).toContain(sample.sample_id);
        expect(baseline.html).toContain(sample.reason);
      }
    }
    if (testInfo.project.name === "desktop-chromium") await page.screenshot({ path: testInfo.outputPath(`delivery-${cityId}.png`), fullPage: true, animations: "disabled", caret: "hide" });
  });

  for (const [product, excludedProduct] of [["DEM1A", "DEM5A"], ["DEM5A", "DEM1A"]]) {
    test(`[ui_regression] ${cityId} exports ${product}`, async ({ page }, testInfo) => {
      test.setTimeout(EXPORT_CASE_TIMEOUT_MS);
      await openExportPage(page, cityId);
      const download = createDownloadObserver(page, cityId, `product-${product}`, testInfo.project.name);
      const terrainProduct = page.getByLabel("DEM product");
      await terrainProduct.selectOption(product);
      await expect(terrainProduct).toHaveValue(product);
      const displayedSamples = await page.getByLabel("選択区間の確認リスト").locator("tbody td:nth-child(3) code").allTextContents();
      expect(displayedSamples.length).toBeGreaterThan(0);
      expect(displayedSamples.every((value) => value.endsWith(` / ${product}`))).toBe(true);
      expect(displayedSamples.every((value) => !value.endsWith(` / ${excludedProduct}`))).toBe(true);
      const exported = await assertScreenMatchesExports(page, download);
      expect(exported.payload.filters.terrain_product).toBe(product);
      expect(exported.payload.rows.every((row) => row.terrain_samples.every((sample) => sample.product === product))).toBe(true);
      expect(exported.csv).toContain(product);
      expect(exported.html).toContain(product);
    });
  }

  for (const [caseId, label] of [["scenario-filter", "確認リスト・exportのsource scenario"], ["revision-filter", "source revision"], ["coverage-filter", "coverage status"]]) {
    test(`[ui_regression] ${cityId} exports ${caseId}`, async ({ page }, testInfo) => {
      test.setTimeout(EXPORT_CASE_TIMEOUT_MS);
      await openExportPage(page, cityId);
      const download = createDownloadObserver(page, cityId, caseId, testInfo.project.name);
      const selector = page.getByLabel(label);
      const optionCount = await selector.locator("option").count();
      expect(optionCount, `${cityId} must expose ${label}`).toBeGreaterThan(1);
      const selected = await selector.locator("option").nth(1).getAttribute("value");
      expect(selected, `${cityId} ${label} selection`).toBeTruthy();
      const excluded = label === "確認リスト・exportのsource scenario" && optionCount > 2
        ? await selector.locator("option").nth(2).getAttribute("value")
        : null;
      await selector.selectOption(selected);
      const exported = await assertScreenMatchesExports(page, download);
      assertSourceFilterRows(exported.payload, label, selected);
      for (const content of [exported.csv, JSON.stringify(exported.payload), exported.html]) {
        expect(content).toContain(selected);
        if (cityId === "kyoto_kiyomizu" && excluded) expect(content).not.toContain(excluded);
      }
    });
  }

  for (const [caseId, label] of [["missing-filter", "missing field"], ["owner-filter", "担当候補の種別"]]) {
    test(`[ui_regression] ${cityId} exports ${caseId}`, async ({ page }, testInfo) => {
      test.setTimeout(EXPORT_CASE_TIMEOUT_MS);
      await openExportPage(page, cityId);
      const download = createDownloadObserver(page, cityId, caseId, testInfo.project.name);
      const selector = page.getByLabel(label);
      expect(await selector.locator("option").count(), `${cityId} must expose ${label}`).toBeGreaterThan(1);
      const selected = await selector.locator("option").nth(1).getAttribute("value");
      expect(selected, `${cityId} ${label} selection`).toBeTruthy();
      await selector.selectOption(selected);
      const filtered = await assertScreenMatchesExports(page, download);
      expect(filtered.payload.rows.length).toBeGreaterThan(0);
      const field = label === "missing field" ? "unknowns" : "owner_candidate_types";
      expect(filtered.payload.rows.every((row) => row[field].includes(selected))).toBe(true);
    });
  }

  test(`[ui_regression] ${cityId} exports reason/source search`, async ({ page }, testInfo) => {
    test.setTimeout(EXPORT_CASE_TIMEOUT_MS);
    await openExportPage(page, cityId);
    const download = createDownloadObserver(page, cityId, "reason-source-search", testInfo.project.name);
    const sourceCell = await page.getByLabel("選択区間の確認リスト").locator("tbody td:nth-child(2) code").first().textContent();
    const sourceNeedle = sourceCell?.split("@")[0].slice(0, 10);
    expect(sourceNeedle, `${cityId} must expose a source for reason/source search`).toBeTruthy();
    await page.getByLabel("reason/source検索").fill(sourceNeedle);
    const filtered = await assertScreenMatchesExports(page, download);
    expect(filtered.payload.rows.length).toBeGreaterThan(0);
    expect(filtered.payload.rows.every((row) => row.hazards.length > 0 && row.hazards.every((hazard) => [hazard.reason, hazard.limitations, hazard.source_id].some((value) => String(value).toLocaleLowerCase("ja").includes(sourceNeedle.toLocaleLowerCase("ja")))))).toBe(true);
    for (const content of [filtered.csv, JSON.stringify(filtered.payload), filtered.html]) expect(content).toContain(sourceNeedle);
  });

  for (const sortBy of ["EDGE", "REVISION", "COVERAGE", "REASON", "OWNER"]) {
    test(`[ui_regression] ${cityId} exports sort-${sortBy.toLowerCase()}`, async ({ page }, testInfo) => {
      test.setTimeout(EXPORT_CASE_TIMEOUT_MS);
      await openExportPage(page, cityId);
      const download = createDownloadObserver(page, cityId, `sort-${sortBy.toLowerCase()}`, testInfo.project.name);
      await page.getByLabel("確認リストの並び順").selectOption(sortBy);
      const exported = await assertScreenMatchesExports(page, download);
      expect(exported.payload.sort_by).toBe(sortBy);
      assertSortOrder(exported.payload, sortBy);
    });
  }
}

for (const [cityId, disconnectedPath] of [
  ["kyoto_kiyomizu", "KK-OSM-N1697644482__KK-OSM-N3752885643"],
  ["kyoto_arashiyama", "kyoto-arashiyama:osm-node-000243776546__kyoto-arashiyama:osm-node-001212123705"],
]) {
  test(`[ui_regression] ${cityId} exports disconnected reason and empty row set`, async ({ page }, testInfo) => {
    test.setTimeout(EXPORT_CASE_TIMEOUT_MS);
    await openExportPage(page, cityId);
    const [startNode, endNode] = disconnectedPath.split("__");
    await page.getByLabel("出発node（candidate fixture）").selectOption(startNode);
    await page.getByLabel("目的node（candidate fixture）").selectOption(endNode);
    const download = createDownloadObserver(page, cityId, "disconnected", testInfo.project.name);
    const exported = await assertScreenMatchesExports(page, download);
    expect(exported.payload.path_key).toBe(disconnectedPath);
    expect(exported.payload.path_status).toBe("DISCONNECTED");
    expect(exported.payload.rows).toEqual([]);
    expect(exported.payload.candidate_distance).toBeNull();
    expect(exported.payload.path_reason).toBeTruthy();
    expect(exported.csv).toContain(exported.payload.path_reason);
    expect(exported.html).toContain(exported.payload.path_reason);
  });
}

test("[ui_regression] city state is reproducible and unconnected result selectors stay inactive", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "AblePath" })).toBeVisible();
  await expect(page.getByLabel("歩行profile（未計算）")).toBeDisabled();
  await expect(page.getByLabel("ハザード・固定シナリオ（未接続）")).toBeDisabled();
  await expect(page.getByLabel("Before/After比較（未接続）")).toBeDisabled();
  await expect(page.getByRole("radio", { name: "厳格" })).toBeDisabled();
  await expect(page.getByRole("radio", { name: "参考" })).toBeDisabled();
  const evidencePanel = page.locator(".evidence-panel");
  await expect(evidencePanel).toBeVisible();
  await expect(evidencePanel).toContainText("NOT_COMPUTED — M6未実装");

  await page.getByLabel("都市・回廊").selectOption("kyoto_arashiyama");
  await expect(page.getByRole("heading", { name: "嵐山・渡月橋" })).toBeVisible();
  await expect(page).toHaveURL(/city=kyoto_arashiyama/);
  await expect(page).not.toHaveURL(/scenario=/);
  await expect(page).not.toHaveURL(/evidence=/);
  await expect(page).not.toHaveURL(/phase=/);

  await page.reload();
  await expect(page.getByLabel("都市・回廊")).toHaveValue("kyoto_arashiyama");
  await expect(page.getByRole("radio", { name: "厳格" })).toBeChecked();
});

test("[ui_regression] changing city does not implicitly opt into a real-coordinate layer", async ({ page }) => {
  await page.goto("/?city=kyoto_arashiyama&layer=synthetic");

  await page.getByLabel("都市・回廊").selectOption("kyoto_kiyomizu");

  await expect(page.getByRole("button", { name: "SYNTHETIC_DEMO" })).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByRole("button", { name: "実座標 / CANDIDATE" })).toHaveAttribute("aria-pressed", "false");
  await expect(page).toHaveURL(/city=kyoto_kiyomizu.*layer=synthetic/);

  await page.getByRole("button", { name: "実座標 / CANDIDATE" }).click();
  await expect(page.getByText("REAL COORDINATES / CANDIDATE", { exact: true }).first()).toBeVisible();
  await expect(page).toHaveURL(/city=kyoto_kiyomizu.*layer=real/);
});

test("[ui_regression] KPI and evidence gaps remain visible and reasoned", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".kpi-card")).toHaveCount(5);
  await expect(page.locator(".kpi-card strong")).toHaveText(["—", "—", "—", "—", "—"]);
  await expect(page.locator(".kpi-card small").first()).not.toBeEmpty();
  await expect(page.getByText("official closure").locator(".." )).toContainText("UNKNOWN (null)");
  await expect(page.getByRole("heading", { name: "selected edge sources" })).toBeVisible();
  await expect(page.getByText("FIXTURE-KIYOMIZU-UI-001").first()).toBeVisible();
  await expect(page.getByText(/SYNTHETIC_DEMO \/ 2026-08-30 \/ UNKNOWN/).first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "source・facility・gap一覧" })).toBeVisible();
  await expect(page.getByText("kyoto_kiyomizu_gion_evacuation_plan", { exact: true })).toBeVisible();
  await expect(page.getByText("Verified facility entrance, capacity, and current operation records are unavailable.")).toBeVisible();
  const facilityReadiness = page.getByLabel("横スクロール可能なfacility readiness一覧");
  for (const readiness of ["facility", "entrance", "capacity", "operation", "demand", "origin", "profile (M6)"]) {
    await expect(facilityReadiness.getByRole("row", { name: new RegExp(`^${readiness.replace(/[()]/g, "\\$&")}`) })).toBeVisible();
  }
});

test("[source_conformance] Kyoto connects display evidence without promoting scientific or operational state", async ({ page }) => {
  await page.goto("/?city=kyoto_kiyomizu&layer=real");
  const official = page.locator(".official-evidence");
  // The approved continuation replaces the former not-sampled state with
  // source-bound native-cell samples. Keep the stronger provenance and
  // non-inference contract visible in the same regression.
  await expect(official).toContainText("NATIVE_CELL_SAMPLES_CONNECTED");
  await expect(official).toContainText("OFFICIAL_SPEC_AND_RAW_SHA_BOUND_NATIVE_CELL_SAMPLING");
  await expect(official).toContainText("DEM1A");
  await expect(official).toContainText("DEM5A");
  await expect(official).toContainText("no interpolation, product precedence, step, or cross-slope inference");
  await expect(official).toContainText("SOURCE_SIDE_EDGE_OVERLAP_CONNECTED");
  await expect(official).toContainText("612 edges / deep pilot 15 / ready 0 / computed 0");
  await expect(official.getByLabel("京都公式施設5カテゴリ接続状態")).toContainText("public_tourist_toilet");
  await expect(official.getByLabel("京都の公式座標施設一覧")).toContainText("SOURCE_PROVIDED_LONGITUDE_LATITUDE");
  await expect(official.getByLabel("京都M7 deep pilot reasoned null").getByRole("row")).toHaveCount(6);
  await expect(page.locator(".map-runtime-status")).toContainText("official hazard AVAILABLE (412)");
  await expect(page.locator(".map-runtime-status")).toContainText(/official facilities AVAILABLE/);
  await page.getByLabel("都市・回廊").selectOption("kyoto_arashiyama");
  await page.getByRole("button", { name: "実座標 / CANDIDATE" }).click();
  await expect(page.locator(".map-runtime-status")).not.toContainText("official hazard AVAILABLE (412)");
  await expect(page.locator(".map-runtime-status")).toContainText("official hazard AVAILABLE (159)");
  await expect(page.getByLabel("京都M7 deep pilot reasoned null").getByRole("row")).toHaveCount(6);
  await page.getByLabel("都市・回廊").selectOption("fujisawa_enoshima");
  await expect(page.getByText(/公式施設 0件/)).toBeVisible();
  await expect(page.locator(".official-evidence")).toContainText("NOT_CONNECTED_PUBLIC_GIT_LICENSE_REVIEW_REQUIRED");
  await expect(page.locator(".official-evidence tbody tr").filter({ hasText: "fujisawa-accessibility-" })).toHaveCount(0);
  await expect(page.locator(".official-evidence .map-marker, .official-evidence [data-marker]")).toHaveCount(0);
  const terrainInventory = page.getByLabel("terrain product inventory");
  await expect(terrainInventory).toContainText("DEM1A");
  await expect(terrainInventory).toContainText("DEM5A");
  await expect(terrainInventory).toContainText("records 46, unique locations 16, numeric 43, null records 3, null locations 1");
  const unresolvedTerrain = page.getByLabel("terrain unresolved native-cell records");
  await expect(unresolvedTerrain.getByRole("row")).toHaveCount(7);
  await expect(unresolvedTerrain).toContainText("SURFACE_VALUE_UNRESOLVED");
  await expect(unresolvedTerrain).toContainText("A -9999 value with a non-no-data surface label is not promoted to elevation.");
  const text = await page.locator("body").innerText();
  expect(text).not.toContain("安全な避難ルート");
  expect(text).not.toContain("CLOSEDを導出");
});

test("[ui_regression] map uses text marks and is keyboard operable", async ({ page }) => {
  await page.goto("/");
  const legend = page.getByLabel("状態凡例");
  await expect(legend).toContainText("P");
  await expect(legend).toContainText("C");
  await expect(legend).toContainText("F");
  await expect(legend).toContainText("?");
  const secondEdge = page.locator(".edge-hit[role=button]").nth(1);
  await secondEdge.focus();
  await secondEdge.press("Enter");
  await expect(page.getByText("KYS-DEMO-E002", { exact: true }).first()).toBeVisible();
});

test("[ui_regression] optional 3D failure is visible and 2D remains recoverable", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("都市・回廊").selectOption("kyoto_arashiyama");
  await page.getByRole("button", { name: "3D" }).click();
  await expect(page.getByRole("heading", { name: "この都市の3D layerは未設定です" })).toBeVisible();
  await expect(page.getByText("実在しないtilesetを補完せず、合成2Dへ戻せます。")).toBeVisible();
  await page.getByRole("button", { name: "2Dへ戻る" }).click();
  await expect(page.getByRole("group", { name: /シナリオ回廊図/ })).toBeVisible();
});

test("[ui_regression] skip link, page title, and pressed view state are explicit", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/清水・祇園.*AblePath/);
  const skipLink = page.getByRole("link", { name: /本文へ移動/ });
  await skipLink.focus();
  await expect(skipLink).toBeFocused();
  await skipLink.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
  const skipMap = page.getByRole("link", { name: /地図を飛ばしてedge一覧へ/ });
  await skipMap.focus();
  await skipMap.press("Enter");
  await expect(page.locator("#edge-table")).toBeFocused();
  await expect(page.getByRole("button", { name: "2D" })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "3D" }).click();
  await expect(page.getByRole("button", { name: "3D" })).toHaveAttribute("aria-pressed", "true");
});

test("[source_conformance] forbidden safety claims are absent", async ({ page }) => {
  for (const url of [
    "/?city=kyoto_kiyomizu&layer=synthetic",
    "/?city=kyoto_kiyomizu&layer=real",
    "/?city=kyoto_arashiyama&layer=synthetic",
    "/?city=fujisawa_enoshima&layer=synthetic",
  ]) {
    await page.goto(url);
    await expect(page.getByRole("heading", { name: "AblePath" })).toBeVisible();
    const text = await page.locator("body").innerText();
    expect(text).not.toContain("安全な避難ルート");
    expect(text).not.toContain("ほこナビ正式対応");
    expect(text).not.toContain("リアルタイム避難安全");
    expect(text).toContain("リアルタイムの安全保証");
    expect(text).toContain("静的スナップショット比較");
  }
});

test("[ui_regression] desktop captures all three city 2D states", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop-chromium", "one deterministic desktop screenshot per city");
  await page.goto("/");
  for (const cityId of ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"]) {
    await page.getByLabel("都市・回廊").selectOption(cityId);
    await expect(page.getByLabel("都市・回廊")).toHaveValue(cityId);
    await page.screenshot({ path: testInfo.outputPath(`${cityId}-2d.png`), fullPage: true });
  }
});

test("[ui_regression] desktop captures Kiyomizu real candidate mode", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop-chromium", "deterministic real-mode screenshot is a desktop artifact");
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
  await page.goto("/?city=kyoto_kiyomizu&layer=synthetic");
  await page.getByRole("button", { name: "実座標 / CANDIDATE" }).click();
  await expect(page.getByRole("heading", { name: "実座標候補graph" })).toBeVisible();
  await expect(page.getByText("REAL COORDINATES / CANDIDATE", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("CANDIDATE_REVIEW_REQUIRED", { exact: true }).first()).toBeVisible();
  await expect(page.locator(".map-runtime-status")).toContainText("candidate overlay AVAILABLE");
  await expect(page.locator(".map-runtime-status")).toContainText("background DEGRADED");
  await page.screenshot({
    path: testInfo.outputPath("kyoto_kiyomizu-real-candidate-2d.png"),
    fullPage: true,
    animations: "disabled",
    caret: "hide",
  });
});

test("[ui_regression] desktop captures the deterministic unverified-PLATEAU fallback", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop-chromium", "deterministic 3D-fallback screenshot is a desktop artifact");
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
  await page.route("https://assets.cms.plateau.reearth.io/**/tileset.json", (route) => route.abort("failed"));
  await page.goto("/?city=kyoto_kiyomizu&view=2d&layer=real");
  await expect(page.locator(".map-runtime-status")).toContainText("candidate overlay AVAILABLE");
  await expect(page.locator(".map-runtime-status")).toContainText("background DEGRADED");
  await page.getByRole("button", { name: "3D" }).click();
  await expect(page.getByText("NOT_CONNECTED", { exact: true }).first()).toBeVisible();
  await expect(page.getByText(/CORS・AOI・child tiles の検証 receipt が未完了/)).toBeVisible();
  await expect(page.getByText("SESSION_ROOT_TILESET_LOADED", { exact: true })).toHaveCount(0);
  await page.screenshot({
    path: testInfo.outputPath("kyoto_kiyomizu-3d-fallback.png"),
    fullPage: true,
    animations: "disabled",
    caret: "hide",
  });
});

test("[ui_regression] responsive layout avoids page-level horizontal overflow", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".app-shell")).toBeVisible();
  const dimensions = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.width + 1);
});

test("[ui_regression] 320 CSS-pixel reflow has no page-level horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto("/");
  await expect(page.locator(".app-shell")).toBeVisible();
  const dimensions = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }));
  const overflowSelectors = [".workspace-grid", ".map-column", ".map-shell", ".map-toolbar", ".evidence-panel"];
  for (const selector of overflowSelectors) {
    const element = page.locator(selector);
    await expect(element).toHaveCount(1);
    const bounds = await element.evaluate((node) => {
      const { left, right, width } = node.getBoundingClientRect();
      return { left, right, width, clientWidth: node.clientWidth, scrollWidth: node.scrollWidth };
    });
    const diagnostic = [
      `selector=${selector}`,
      `left=${bounds.left}`,
      `right=${bounds.right}`,
      `width=${bounds.width}`,
      `clientWidth=${bounds.clientWidth}`,
      `scrollWidth=${bounds.scrollWidth}`,
    ].join(", ");
    expect(bounds.right, diagnostic).toBeLessThanOrEqual(dimensions.width);
    expect(bounds.scrollWidth, diagnostic).toBeLessThanOrEqual(bounds.clientWidth + 1);
  }
  const skipLinkBounds = await page.locator(".skip-link").evaluateAll((links) => links.map((link) => {
    const { left, right } = link.getBoundingClientRect();
    return { left, right };
  }));
  expect(skipLinkBounds).toHaveLength(2);
  for (const bounds of skipLinkBounds) {
    expect(bounds.left).toBeGreaterThanOrEqual(0);
    expect(bounds.right).toBeLessThanOrEqual(dimensions.width);
  }
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.width + 1);
});

test("[ui_regression] Kiyomizu real coordinates use MapLibre and survive basemap failure", async ({ page }) => {
  let artifactRequests = 0;
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.endsWith("/data/maps/kyoto_kiyomizu.candidate_edges.geojson")) artifactRequests += 1;
  });
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
  await page.goto("/?city=kyoto_kiyomizu&layer=real");
  await expect(page.getByRole("heading", { name: "実座標候補graph" })).toBeVisible();
  await expect(page.getByText("REAL COORDINATES / CANDIDATE", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("CANDIDATE_REVIEW_REQUIRED", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("continuity NOT_ESTABLISHED", { exact: true })).toBeVisible();
  await expect(page.locator(".map-runtime-status")).toContainText("candidate overlay AVAILABLE");
  await expect(page.locator(".map-runtime-status")).toContainText("background DEGRADED");
  await expect(page.getByRole("link", { name: "© OpenStreetMap contributors" })).toHaveAttribute("href", "https://www.openstreetmap.org/copyright");
  await expect(page.getByRole("link", { name: "ODbL 1.0" })).toHaveAttribute("href", "https://opendatacommons.org/licenses/odbl/1-0/");
  await expect(page.getByRole("table", { name: /実座標候補edge/ }).getByRole("row")).toHaveCount(20);

  const selected = "KK-OSM-W1251544286-S01";
  await page.getByRole("row", { name: new RegExp(selected) }).getByRole("button", { name: "属性を表示" }).click();
  await expect(page).toHaveURL(new RegExp(`layer=real.*map_edge=${selected}`));
  await expect(page.getByLabel("選択した実座標候補edge")).toContainText(selected);
  const second = "KK-OSM-W1491152444-S01";
  await page.getByRole("row", { name: new RegExp(second) }).getByRole("button", { name: "属性を表示" }).click();
  await expect(page.getByLabel("選択した実座標候補edge")).toContainText(second);
  expect(artifactRequests).toBe(1);
  await expect(page.locator("#edge-table")).toBeAttached();
  const skipMap = page.getByRole("link", { name: /地図を飛ばしてedge一覧へ/ });
  await skipMap.focus();
  await skipMap.press("Enter");
  await expect(page.locator("#edge-table")).toBeFocused();
  await page.reload();
  await expect(page.getByRole("table", { name: /実座標候補edge/ }).getByRole("row", { name: new RegExp(second) })).toHaveClass(/active-row/);
});

test("[ui_regression] all three cities allow explicit real candidate mode", async ({ page }) => {
  await page.goto("/?city=kyoto_arashiyama&layer=real");
  await expect(page.getByRole("button", { name: "実座標 / CANDIDATE" })).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByRole("heading", { name: "実座標候補graph" })).toBeVisible();
  await expect(page.getByLabel("candidate path analysis")).toContainText("CONNECTED");
  await expect(page.getByLabel("candidate path analysis")).toContainText("coordinate_degree");
  await expect(page.getByLabel("candidate path analysis")).toContainText(/ordered edge IDs: (?!—)/);
});

// Acceptance map: the former multi-city test exhausted its shared 30 s budget
// on its seventh full-page screenshot in Hosted run 34690792994. Keep every
// assertion and all seven screenshot names, but give each independent city /
// path state its own standard test/context. No timeout, retry or export changes.
for (const cityId of ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"]) {
  test(`[ui_regression] precomputed candidate path controls: ${cityId} connected fixture`, async ({ page }, testInfo) => {
    await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
    await page.goto(`/?city=${cityId}&layer=real`);
    await expect(page.getByLabel("出発node（candidate fixture）")).toBeEnabled();
    await expect(page.getByLabel("目的node（candidate fixture）")).toBeEnabled();
    await expect(page.getByLabel("candidate path analysis")).toContainText("coordinate_degree");
    await expect(page.getByLabel("candidate path analysis")).toContainText("CONNECTED");
    await expect(page.getByLabel("candidate path analysis")).toContainText(/ordered edge IDs: (?!—)/);
    await expect(page.getByLabel("candidate path analysis")).toContainText("hazard: CONNECTED_PRECOMPUTED_PER_EDGE");
    await expect(page.getByLabel("candidate path analysis")).toContainText("M7 NOT_COMPUTED");
    if (testInfo.project.name === "desktop-chromium") await page.screenshot({ path: testInfo.outputPath({ kyoto_kiyomizu: "kiyomizu-real-analysis.png", kyoto_arashiyama: "arashiyama-real-analysis.png", fujisawa_enoshima: "fujisawa-real-analysis.png" }[cityId]), fullPage: true });
  });
}

test("[ui_regression] precomputed candidate path controls: Kiyomizu disconnected fixture", async ({ page }, testInfo) => {
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
  await page.goto("/?city=kyoto_kiyomizu&layer=real");
  const end = page.getByLabel("目的node（candidate fixture）");
  await expect(end).toBeEnabled();
  await expect(page.getByLabel("candidate path analysis")).toContainText("CONNECTED");
  if (testInfo.project.name === "desktop-chromium") await page.screenshot({ path: testInfo.outputPath("candidate-path-selected.png"), fullPage: true });
  await end.selectOption((await end.locator("option").nth(2).getAttribute("value")));
  await expect(page.getByLabel("candidate path analysis")).toContainText("DISCONNECTED");
  await expect(page.getByLabel("candidate path analysis")).toContainText("coordinate-degree distance: —");
  await expect(page.getByLabel("candidate path analysis")).toContainText("ordered edge IDs: —");
  if (testInfo.project.name === "desktop-chromium") { await page.screenshot({ path: testInfo.outputPath("disconnected-path.png"), fullPage: true }); await page.screenshot({ path: testInfo.outputPath("hazard-overlay-or-not-connected.png"), fullPage: true }); }
});

test("[ui_regression] precomputed candidate path controls: Arashiyama disconnected fixture at 320px", async ({ page }, testInfo) => {
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
  await page.goto("/?city=kyoto_arashiyama&layer=real");
  await expect(page.getByLabel("目的node（candidate fixture）")).toBeEnabled();
  await page.getByLabel("目的node（candidate fixture）").selectOption((await page.getByLabel("目的node（candidate fixture）").locator("option").nth(2).getAttribute("value")));
  await expect(page.getByLabel("candidate path analysis")).toContainText("DISCONNECTED");
  await page.setViewportSize({ width: 320, height: 900 });
  await expect(page.locator(".app-shell")).toBeVisible();
  if (testInfo.project.name === "desktop-chromium") await page.screenshot({ path: testInfo.outputPath("mobile-320-analysis.png"), fullPage: true });
});

test("[ui_regression] unverified PLATEAU metadata stays NOT_CONNECTED even when a tileset is mocked", async ({ page }) => {
  const requestedScripts = [];
  let tilesetRequests = 0;
  page.on("request", (request) => {
    if (/CesiumScene-.*\.js/.test(request.url())) requestedScripts.push(request.url());
  });
  await page.route("https://assets.cms.plateau.reearth.io/**/tileset.json", (route) => {
    tilesetRequests += 1;
    return route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({
      asset: { version: "1.1" },
      geometricError: 0,
      root: {
        boundingVolume: { region: [2.369, 0.610, 2.370, 0.611, 0, 30] },
        geometricError: 0,
        refine: "ADD",
      },
    }),
    });
  });
  await page.goto("/?city=kyoto_kiyomizu&layer=real");
  expect(requestedScripts).toHaveLength(0);
  await page.getByRole("button", { name: "3D" }).click();
  await expect(page.getByText("NOT_CONNECTED", { exact: true }).first()).toBeVisible();
  expect(requestedScripts).toHaveLength(0);
  await expect(page.getByText("OFFICIAL_METADATA_ONLY", { exact: true }).first()).toBeVisible();
  await expect(page.getByText(/CORS・AOI・child tiles の検証 receipt が未完了/)).toBeVisible();
  await page.waitForTimeout(500);
  expect(tilesetRequests).toBe(0);
});

test("[ui_regression] an unverified child-tile fixture never starts a Cesium request", async ({ page }) => {
  let childRequests = 0;
  await page.route("https://assets.cms.plateau.reearth.io/**/tileset.json", (route) => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({
      asset: { version: "1.1" },
      geometricError: 100,
      root: {
        boundingVolume: { region: [2.369, 0.610, 2.370, 0.611, 0, 30] },
        geometricError: 100,
        refine: "ADD",
        content: { uri: "child.b3dm" },
      },
    }),
  }));
  await page.route("**/child.b3dm", (route) => {
    childRequests += 1;
    return route.abort("failed");
  });
  await page.goto("/?city=kyoto_kiyomizu&layer=real");
  await page.getByRole("button", { name: "3D" }).click();
  await expect(page.getByText("NOT_CONNECTED", { exact: true }).first()).toBeVisible();
  expect(childRequests).toBe(0);
});

test("[ui_regression] missing CORS receipt preserves selected real-layer state without a request", async ({ page }) => {
  let requests = 0;
  await page.route("https://assets.cms.plateau.reearth.io/**/tileset.json", (route) => { requests += 1; return route.abort("failed"); });
  const selected = "KK-OSM-W1251544286-S01";
  await page.goto(`/?city=kyoto_kiyomizu&view=2d&layer=real&map_edge=${selected}`);
  await page.getByRole("button", { name: "3D" }).click();
  await expect(page.getByText("NOT_CONNECTED", { exact: true }).first()).toBeVisible();
  await expect(page).toHaveURL(new RegExp(`view=3d.*layer=real.*map_edge=${selected}`));
  expect(requests).toBe(0);
});

test("[ui_regression] a late mocked root response cannot promote metadata-only PLATEAU", async ({ page }) => {
  let requests = 0;
  await page.route("https://assets.cms.plateau.reearth.io/**/tileset.json", async (route) => {
    requests += 1;
    await new Promise((resolve) => setTimeout(resolve, 600));
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        asset: { version: "1.1" },
        geometricError: 0,
        root: {
          boundingVolume: { region: [2.369, 0.610, 2.370, 0.611, 0, 30] },
          geometricError: 0,
          refine: "ADD",
        },
      }),
    });
  });
  await page.goto("/?city=kyoto_kiyomizu&view=3d&layer=real");
  await expect(page.getByText("NOT_CONNECTED", { exact: true }).first()).toBeVisible();
  await page.waitForTimeout(100);
  expect(requests).toBe(0);
  await expect(page.getByText("SESSION_ROOT_TILESET_LOADED", { exact: true })).toHaveCount(0);
});

test("[ui_regression] real map remains within 320 360 375 and 400 CSS pixels", async ({ page }) => {
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
  for (const width of [320, 360, 375, 400]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/?city=kyoto_kiyomizu&layer=real");
    await expect(page.locator(".real-map-shell")).toBeVisible();
    const dimensions = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }));
    expect(dimensions.scrollWidth, `viewport ${width}`).toBeLessThanOrEqual(dimensions.width + 1);
    await expect(page.getByRole("link", { name: /OpenStreetMap contributors/ })).toBeVisible();
  }
});

test("[ui_regression] official evidence tables remain page-width responsive at 320 through 400 CSS pixels", async ({ page }) => {
  for (const width of [320, 360, 375, 400]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/?city=fujisawa_enoshima&layer=synthetic");
    await expect(page.getByText(/公式施設 0件/)).toBeVisible();
    await expect(page.locator(".official-evidence")).toContainText("NOT_CONNECTED_PUBLIC_GIT_LICENSE_REVIEW_REQUIRED");
    const dimensions = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }));
    expect(dimensions.scrollWidth, `official evidence viewport ${width}`).toBeLessThanOrEqual(dimensions.width + 1);
  }
});

test("[ui_regression] desktop captures the required V2 official-evidence artifact names", async ({ page }, testInfo) => {
  test.setTimeout(90_000);
  test.skip(testInfo.project.name !== "desktop-chromium", "V2 evidence screenshots are desktop review artifacts");
  const capture = async (name) => page.screenshot({ path: testInfo.outputPath(name), fullPage: true, animations: "disabled", caret: "hide" });
  await page.goto("/?city=kyoto_kiyomizu&layer=synthetic");
  for (const name of ["kiyomizu-gion-terrain-hazard.png", "kiyomizu-gion-official-facilities.png", "kiyomizu-gion-plateau-or-fallback.png", "kyoto-m7-evidence-not-computed-or-result.png", "kiyomizu-terrain-analysis.png", "m7-evidence-not-computed.png", "fallback.png"]) await capture(name);
  await page.getByLabel("都市・回廊").selectOption("kyoto_arashiyama");
  for (const name of ["arashiyama-terrain-flood.png", "arashiyama-official-facilities.png", "arashiyama-plateau-or-fallback.png", "arashiyama-terrain-analysis.png"]) await capture(name);
  await page.getByLabel("都市・回廊").selectOption("fujisawa_enoshima");
  for (const name of ["fujisawa-earthquake-scenario.png", "fujisawa-liquefaction-scenario.png", "fujisawa-accessibility-table.png"]) await capture(name);
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto("/?city=kyoto_kiyomizu&layer=synthetic");
  await capture("mobile-320-kyoto-official-data.png");
  await page.getByLabel("都市・回廊").selectOption("fujisawa_enoshima");
  await capture("mobile-320-official-data.png");
});

test("[ui_regression] desktop captures Kyoto parity overlays and reasoned-null evidence", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop-chromium", "Kyoto parity screenshots are desktop review artifacts");
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
  const capture = async (name) => page.screenshot({ path: testInfo.outputPath(name), fullPage: true, animations: "disabled", caret: "hide" });
  await page.goto("/?city=kyoto_kiyomizu&layer=real");
  await expect(page.locator(".map-runtime-status")).toContainText("official hazard AVAILABLE (412)");
  await expect(page.getByLabel("京都公式施設5カテゴリ接続状態")).toBeVisible();
  await expect(page.getByLabel("京都M7 deep pilot reasoned null")).toContainText("NOT_COMPUTED / null");
  await capture("kyoto-kiyomizu-gion-parity.png");
  await page.getByLabel("京都M7 deep pilot reasoned null").screenshot({ path: testInfo.outputPath("kyoto-m7-reasoned-null.png"), animations: "disabled", caret: "hide" });
  await page.getByLabel("都市・回廊").selectOption("kyoto_arashiyama");
  await page.getByRole("button", { name: "実座標 / CANDIDATE" }).click();
  await expect(page.locator(".map-runtime-status")).toContainText("official hazard AVAILABLE (159)");
  await expect(page.getByLabel("京都PLATEAU 2025 building evidence inventory")).toContainText("EXISTING_DETERMINISTIC_2D");
  await capture("kyoto-arashiyama-parity.png");
});
