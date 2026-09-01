import { expect, test } from "@playwright/test";

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

test("[source_conformance] official evidence keeps Kyoto disconnected and Fujisawa facilities table-only", async ({ page }) => {
  await page.goto("/?city=kyoto_kiyomizu&layer=synthetic");
  const official = page.locator(".official-evidence");
  await expect(official).toContainText("CRS/AOI/vertical datum review remains unresolved");
  await expect(official).toContainText("No closure is derived");
  await expect(official).toContainText("612 edges / deep pilot 15 / ready 0 / computed 0");
  await expect(official).toContainText("Kiyomizu/Gion/connector");
  await page.getByLabel("都市・回廊").selectOption("fujisawa_enoshima");
  await expect(page.getByText(/公式施設 57件/)).toBeVisible();
  await expect(page.locator(".official-evidence tbody tr").filter({ hasText: "fujisawa-accessibility-" })).toHaveCount(57);
  await expect(page.locator(".official-evidence").getByText(/ADDRESS_ONLY、地図markerなし/)).toBeVisible();
  await expect(page.locator(".official-evidence").getByText("UNKNOWN / UNKNOWN / UNKNOWN")).toHaveCount(57);
  await expect(page.locator(".official-evidence .map-marker, .official-evidence [data-marker]")).toHaveCount(0);
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
  await expect(page.locator(".map-runtime-status")).toContainText("local overlay AVAILABLE");
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
  await expect(page.locator(".map-runtime-status")).toContainText("local overlay AVAILABLE");
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
  await expect(page.locator(".map-runtime-status")).toContainText("local overlay AVAILABLE");
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
  await expect(page.getByRole("row", { name: new RegExp(second) })).toHaveClass(/active-row/);
});

test("[ui_regression] all three cities allow explicit real candidate mode", async ({ page }) => {
  await page.goto("/?city=kyoto_arashiyama&layer=real");
  await expect(page.getByRole("button", { name: "実座標 / CANDIDATE" })).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByRole("heading", { name: "実座標候補graph" })).toBeVisible();
  await expect(page.getByLabel("candidate path analysis")).toContainText("CONNECTED");
  await expect(page.getByLabel("candidate path analysis")).toContainText("coordinate_degree");
  await expect(page.getByLabel("candidate path analysis")).toContainText(/ordered edge IDs: (?!—)/);
});

test("[ui_regression] precomputed candidate path controls change fixtures without runtime graph calculation", async ({ page }, testInfo) => {
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
  for (const cityId of ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"]) {
    await page.goto(`/?city=${cityId}&layer=real`);
    await expect(page.getByLabel("出発node（candidate fixture）")).toBeEnabled();
    await expect(page.getByLabel("目的node（candidate fixture）")).toBeEnabled();
    await expect(page.getByLabel("candidate path analysis")).toContainText("coordinate_degree");
    await expect(page.getByLabel("candidate path analysis")).toContainText("CONNECTED");
    await expect(page.getByLabel("candidate path analysis")).toContainText(/ordered edge IDs: (?!—)/);
    await expect(page.getByLabel("candidate path analysis")).toContainText("hazard: NOT_CONNECTED");
    await expect(page.getByLabel("candidate path analysis")).toContainText("M7 NOT_COMPUTED");
    if (testInfo.project.name === "desktop-chromium") await page.screenshot({ path: testInfo.outputPath({ kyoto_kiyomizu: "kiyomizu-real-analysis.png", kyoto_arashiyama: "arashiyama-real-analysis.png", fujisawa_enoshima: "fujisawa-real-analysis.png" }[cityId]), fullPage: true });
  }
  await page.goto("/?city=kyoto_kiyomizu&layer=real");
  const start = page.getByLabel("出発node（candidate fixture）");
  const end = page.getByLabel("目的node（candidate fixture）");
  if (testInfo.project.name === "desktop-chromium") await page.screenshot({ path: testInfo.outputPath("candidate-path-selected.png"), fullPage: true });
  await end.selectOption((await end.locator("option").nth(2).getAttribute("value")));
  await expect(page.getByLabel("candidate path analysis")).toContainText("DISCONNECTED");
  await expect(page.getByLabel("candidate path analysis")).toContainText("coordinate-degree distance: —");
  await expect(page.getByLabel("candidate path analysis")).toContainText("ordered edge IDs: —");
  if (testInfo.project.name === "desktop-chromium") { await page.screenshot({ path: testInfo.outputPath("disconnected-path.png"), fullPage: true }); await page.screenshot({ path: testInfo.outputPath("hazard-overlay-or-not-connected.png"), fullPage: true }); }
  await page.goto("/?city=kyoto_arashiyama&layer=real");
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
    await expect(page.getByText(/公式施設 57件/)).toBeVisible();
    const dimensions = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }));
    expect(dimensions.scrollWidth, `official evidence viewport ${width}`).toBeLessThanOrEqual(dimensions.width + 1);
  }
});

test("[ui_regression] desktop captures the required V2 official-evidence artifact names", async ({ page }, testInfo) => {
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
