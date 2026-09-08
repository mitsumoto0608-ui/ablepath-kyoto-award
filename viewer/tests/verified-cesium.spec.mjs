import { expect, test } from "@playwright/test";

const HARNESS = "http://127.0.0.1:4175/tests/fixtures/verified-cesium.html";
const TILESET = "https://assets.cms.plateau.reearth.io/test-fixture/tileset.json";


test("[ui_regression] verified Cesium fixture reaches root tileset runtime success", async ({ page }) => {
  await page.route(TILESET, (route) => route.fulfill({
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
  }));

  await page.goto(HARNESS);
  await expect(page.getByText("SESSION_ROOT_TILESET_LOADED", { exact: true })).toBeVisible({ timeout: 15_000 });
  await expect(page.getByLabel("runtime announcement")).toContainText("PLATEAU root tileset metadata");
  await expect(page.getByText("TEST FIXTURE — verified-connection control path only", { exact: true })).toBeVisible();
});


test("[ui_regression] verified Cesium timeout falls back to 2D and ignores the late root", async ({ page }) => {
  await page.addInitScript(() => { globalThis.__ABLEPATH_CESIUM_TIMEOUT_MS__ = 100; });
  await page.route(TILESET, async (route) => {
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

  await page.goto(HARNESS);
  await expect(page.getByRole("heading", { name: "2Dへfallback" })).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("status")).toContainText("タイムアウト");
  await page.waitForTimeout(700);
  await expect(page.getByText("SESSION_ROOT_TILESET_LOADED", { exact: true })).toHaveCount(0);
});
