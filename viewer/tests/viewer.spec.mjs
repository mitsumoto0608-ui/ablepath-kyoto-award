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
  for (const readiness of ["facility", "entrance", "capacity", "operation", "demand", "origin", "profile (M6)"]) {
    await expect(page.getByRole("row", { name: new RegExp(`^${readiness.replace(/[()]/g, "\\$&")}`) })).toBeVisible();
  }
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
  await expect(page.getByRole("heading", { name: "清水・祇園 実座標候補graph" })).toBeVisible();
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

test("[ui_regression] cities without a reviewed real artifact normalize to synthetic fallback", async ({ page }) => {
  await page.goto("/?city=kyoto_arashiyama&layer=real");
  await expect(page.getByRole("button", { name: "実座標 / CANDIDATE" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "SYNTHETIC_DEMO" })).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByRole("group", { name: /シナリオ回廊図/ })).toBeVisible();
  await expect(page).toHaveURL(/layer=synthetic/);
});

test("[ui_regression] Cesium is lazy-loaded and a mocked local tileset gates runtime success", async ({ page }) => {
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
  await expect(page.getByText("SESSION_ROOT_TILESET_LOADED", { exact: true })).toBeVisible();
  expect(requestedScripts.length).toBeGreaterThan(0);
  await expect(page.getByText("OFFICIAL_METADATA_ONLY", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("PLATEAU_3D_CONNECTED=false", { exact: false })).toBeVisible();
  await page.waitForTimeout(500);
  expect(tilesetRequests).toBe(1);
});

test("[ui_regression] Cesium child-tile failure after root load returns to 2D", async ({ page }) => {
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
  await expect(page.getByRole("heading", { name: "清水・祇園 実座標候補graph" })).toBeVisible({ timeout: 15_000 });
  await expect(page).toHaveURL(/view=2d.*layer=real/);
  expect(childRequests).toBeGreaterThan(0);
  await expect(page.getByText("3Dから2Dへfallback", { exact: true })).toBeVisible();
});

test("[ui_regression] Cesium CORS failure returns to 2D and preserves real-layer URL state", async ({ page }) => {
  await page.addInitScript(() => { globalThis.__ABLEPATH_CESIUM_TIMEOUT_MS__ = 100; });
  await page.route("https://assets.cms.plateau.reearth.io/**/tileset.json", (route) => route.abort("failed"));
  const selected = "KK-OSM-W1251544286-S01";
  await page.goto(`/?city=kyoto_kiyomizu&view=2d&layer=real&map_edge=${selected}`);
  await page.getByRole("button", { name: "3D" }).click();
  await expect(page.getByRole("heading", { name: "清水・祇園 実座標候補graph" })).toBeVisible();
  await expect(page).toHaveURL(new RegExp(`view=2d.*layer=real.*map_edge=${selected}`));
  await expect(page.getByText("3Dから2Dへfallback", { exact: true })).toBeVisible();
});

test("[ui_regression] Cesium timeout returns to 2D and ignores a late root response", async ({ page }) => {
  await page.addInitScript(() => { globalThis.__ABLEPATH_CESIUM_TIMEOUT_MS__ = 100; });
  await page.route("https://assets.cms.plateau.reearth.io/**/tileset.json", async (route) => {
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
  await expect(page.getByRole("heading", { name: "清水・祇園 実座標候補graph" })).toBeVisible({ timeout: 15_000 });
  await expect(page).toHaveURL(/view=2d.*layer=real/);
  await expect(page.getByText("3Dから2Dへfallback", { exact: true })).toBeVisible();
  await page.waitForTimeout(750);
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
