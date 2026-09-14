import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";

// One main user journey plus its fatal 3D failure, independently per city and
// browser. Official live render proof is separate; this fixture never claims it.
for (const city of ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"]) {
  test(`[ui_regression] shared workspace and fail-closed 3D preserve real exports: ${city}`, async ({ page }, testInfo) => {
    test.setTimeout(60_000);
    await page.route("https://tile.openstreetmap.org/**", (route) => route.abort("failed"));
    let rootRequests = 0;
    await page.route("https://assets.cms.plateau.reearth.io/**/tileset.json", (route) => {
      rootRequests += 1;
      return route.fulfill({ contentType: "application/json", body: "{}" });
    });
    await page.goto(`/?city=${city}&layer=real`);
    await expect(page.getByRole("heading", { name: "地域・区間の確認リスト" })).toBeVisible();
    await expect(page.locator('.map-runtime-status[data-visible-candidate-fragments]:not([data-visible-candidate-fragments="0"])')).toBeVisible();
    await expect(page.locator(".map-runtime-status")).toContainText("candidate overlay AVAILABLE");
    await expect(page.locator(".map-runtime-status")).toContainText("official hazard AVAILABLE");
    const toggle = page.getByRole("button", { name: "地域・登録地点を選ぶ", exact: true });
    if (await toggle.isVisible()) await toggle.click();
    const origin = page.getByLabel("出発node（candidate fixture）");
    const destination = page.getByLabel("目的node（candidate fixture）");
    // Inspect the native option itself: the generic enabled-state matcher can
    // retarget an option to its enabled select. Same-point choices stay disabled.
    await expect(origin.locator(`option[value="${await destination.inputValue()}"]`)).toHaveJSProperty("disabled", true);
    await expect(destination.locator(`option[value="${await origin.inputValue()}"]`)).toHaveJSProperty("disabled", true);
    await page.getByLabel("地図・詳細のDEM資料").selectOption("DEM5A");
    const scenarioSelect = page.getByLabel("地図・詳細のsource scenario");
    const scenario = await scenarioSelect.locator("option").nth(1).getAttribute("value");
    await scenarioSelect.selectOption(scenario);
    await expect(page.getByLabel("確認リスト・exportのsource scenario")).toHaveValue(scenario);
    if (await toggle.isVisible()) await toggle.click();
    const detailToggle = page.getByRole("button", { name: "選択区間の詳細を開く · UNKNOWN", exact: true });
    if (await detailToggle.isVisible()) await detailToggle.click();
    const inspector = page.locator(".segment-inspector");
    await inspector.getByText("DEMセル標高 · DEM5A（原典値）", { exact: true }).click();
    await expect(inspector.getByLabel("選択区間のDEM標高")).toContainText("DEM5A");
    await expect(inspector.getByLabel("選択区間のDEM標高")).not.toContainText("DEM1A");
    await inspector.getByRole("button", { name: "次の区間", exact: true }).click();
    const selected = await inspector.locator(".segment-id").innerText();
    const selectionBefore = new URL(page.url()).searchParams;
    await expect(inspector).toContainText("UNKNOWN");
    await expect(inspector).toContainText("M7: NOT_COMPUTED / result null");
    await expect(inspector).toContainText("JGD2024_VERTICAL_JAPAN_DATUM_2024");
    expect(rootRequests).toBe(0);
    // Wait for the actual intercepted root request, not an arbitrary delay
    // from clicking while Cesium's lazy module and WebGL are still starting.
    const rootResponse = page.waitForResponse((response) => response.url().endsWith("/tileset.json"));
    await inspector.getByRole("button", { name: "同じ区間を3Dで確認", exact: true }).click();
    expect(await (await rootResponse).text()).toBe("{}");
    await expect(page.locator(".map-fallback-notice")).toContainText("root changed since reviewed receipt");
    await expect(page.locator(".real-map-shell")).toBeVisible();
    expect(rootRequests).toBeGreaterThan(0);
    expect(await page.locator(".cesium-canvas").count()).toBe(0);
    const selectionAfter = new URL(page.url()).searchParams;
    for (const key of ["city", "map_edge", "from", "to", "terrainProduct", "scenario"]) expect(selectionAfter.get(key)).toBe(selectionBefore.get(key));
    expect(selectionAfter.get("map_edge")).toBe(selected);
    await page.getByRole("navigation", { name: "アプリ内メニュー" }).getByRole("link", { name: "行政確認", exact: true }).click();
    await expect(page.locator(".shared-selection")).toContainText(selected);
    await expect(page.locator(".shared-source-conditions")).toContainText(`DEM DEM5A / scenario ${scenario}`);
    await page.getByRole("navigation", { name: "アプリ内メニュー" }).getByRole("link", { name: "書き出す", exact: true }).click();
    const saved = {};
    for (const [format, name] of [["json", "JSONを保存"], ["csv", "CSVを保存"], ["html", "印刷用HTMLを保存"]]) {
      const pending = page.waitForEvent("download");
      await page.getByRole("button", { name, exact: true }).click();
      const download = await pending;
      expect(await download.failure()).toBeNull();
      saved[format] = await readFile(await download.path(), "utf8");
    }
    const payload = JSON.parse(saved.json);
    expect(payload.city_id).toBe(city);
    const screenEdges = await page.getByLabel("選択区間の確認リスト").locator("tbody th code").allTextContents();
    expect(payload.rows.map((row) => row.edge_id)).toEqual(screenEdges);
    for (const edge of screenEdges) { expect(saved.csv).toContain(edge); expect(saved.html).toContain(edge); }
    for (const row of payload.rows) {
      for (const sample of row.terrain_samples ?? []) expect(sample.product).toBe("DEM5A");
      for (const hazard of row.hazards) expect(hazard.scenario_id).toBe(scenario);
    }
    // Export schema carries named unknowns rather than a global uppercase
    // status token. Verify the actual semantic fields, including Fujisawa.
    expect(payload.rows.length).toBeGreaterThan(0);
    for (const row of payload.rows) expect(row.unknowns).toEqual(expect.arrayContaining(["accessibility", "passability", "M6", "M7"]));
    await page.getByRole("navigation", { name: "アプリ内メニュー" }).getByRole("link", { name: "地図", exact: true }).click();
    if (await detailToggle.isVisible()) await detailToggle.click();
    await page.screenshot({ path: testInfo.outputPath(`${city}-astra-workspace.png`), fullPage: false });
  });
}
