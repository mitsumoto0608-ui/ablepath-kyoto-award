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
  await page.getByRole("button", { name: "3D" }).click();
  await expect(page.getByRole("heading", { name: "3Dは未接続です" })).toBeVisible();
  await expect(page.getByText("2D表示と証拠情報は引き続き利用できます")).toBeVisible();
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
  await page.goto("/");
  const text = await page.locator("body").innerText();
  expect(text).not.toContain("安全な避難ルート");
  expect(text).not.toContain("ほこナビ正式対応");
  expect(text).not.toContain("リアルタイム避難安全");
  expect(text).toContain("リアルタイムの安全保証");
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
  const dimensions = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.width + 1);
});

test("[ui_regression] 320 CSS-pixel reflow has no page-level horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto("/");
  const dimensions = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.width + 1);
});
