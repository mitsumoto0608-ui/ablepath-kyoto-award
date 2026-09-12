import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";

// Profiling a rapid city switch found ~5 s in Playwright's injected full-DOM
// accessible-name snapshot for the 4,721-row table, not in the application.
// Keep trace actions, screenshots and sources, but omit DOM/ARIA snapshots for
// this spec only. Real interactions, all-row assertions and timeouts are intact.
test.use({ trace: { mode: "retain-on-failure", snapshots: false, screenshots: true, sources: true } });

// One normal path per city plus one fatal integrity path; provenance/security
// justify the three payloads and both corrupt-data variants. No user study claim.
const cities = ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"];
for (const city of cities) {
  test(`[ui_regression] admin checklist ${city}: static rows, whole CSV and print`, async ({ page }, testInfo) => {
    const report = JSON.parse(await readFile(new URL(`../../reports/ADMIN_CHECKLIST_${city}.json`, import.meta.url), "utf8"));
    await page.goto(`/?city=${cities.find((other) => other !== city)}`);
    await page.getByLabel("都市・回廊").selectOption(city);
    const panel = page.locator("section.admin-checklist");
    await expect(panel.locator(".admin-counts b")).toHaveText(String(report.items.length));
    await expect(panel.locator("tbody tr")).toHaveCount(report.items.length);
    // The generic table-button rule is white-on-dark; this transparent button
    // must use the existing dark ink token on the paper background instead.
    await expect(panel.locator(".admin-row-button").first()).toHaveCSS("color", "rgb(16, 42, 50)");
    const first = report.items.find((item) => item.object_type === "edge" && item.status === "UNKNOWN" && item.verification_method === "FIELD_MEASUREMENT");
    expect(first).toBeTruthy();
    for (const [group, value] of [["object_type", first.object_type], ["status", first.status], ["verification_method", first.verification_method]]) {
      await panel.getByRole("group", { name: group, exact: true }).getByLabel(value, { exact: true }).check();
    }
    const filtered = report.items.filter((row) => row.object_type === first.object_type && row.status === first.status && row.verification_method === first.verification_method);
    await expect(panel.locator(".admin-counts b")).toHaveText(String(filtered.length));
    await expect(panel.locator("tbody tr")).toHaveCount(filtered.length);
    await panel.getByRole("button", { name: `${first.item_id} の詳細`, exact: true }).click();
    for (const value of [first.item_id, first.unknown_reason, first.verification_target.label, first.priority_rule, first.source_sha256 ?? "null"]) {
      await expect(panel.locator(".admin-checklist-detail")).toContainText(value);
    }
    const downloadEvent = page.waitForEvent("download");
    await panel.getByRole("button", { name: `CSVを保存（全${report.items.length}行）`, exact: true }).click();
    const download = await downloadEvent;
    expect(await download.failure()).toBeNull();
    expect(await readFile(await download.path())).toEqual(await readFile(new URL(`../../reports/ADMIN_CHECKLIST_${city}.csv`, import.meta.url)));
    await expect(panel.getByRole("link", { name: "JSON manifest（生成済みファイル）", exact: true })).toHaveAttribute("href", `./data/admin/${city}.checklist.json`);
    if (city === "fujisawa_enoshima") expect(report.items.filter((row) => row.object_type === "facility")).toHaveLength(0);
    await page.screenshot({ path: `../reports/UI_SCREENSHOTS/admin-${city}-${testInfo.project.name}.png`, fullPage: false });
    // Browser print CSS is verified on actual rendered DOM. This does not stand
    // in for HUMAN_GATE 5 (a previously unbriefed human reader).
    await page.emulateMedia({ media: "print" });
    await expect(panel.locator(".admin-print-header")).toBeVisible();
    for (const hash of Object.values(report.generated_from)) await expect(panel.locator(".admin-print-header")).toContainText(hash);
    await expect(panel.locator(".admin-print-header")).toContainText("M6: NOT_COMPUTED / M7: NOT_COMPUTED");
    await expect(panel.locator(".admin-actions")).toBeHidden();
    await expect(panel.locator(".admin-filters")).toBeHidden();
    for (const element of await page.locator("main > *:not(.admin-checklist)").all()) await expect(element).toBeHidden();
    expect(await panel.locator(".admin-checklist-table").evaluate((node) => getComputedStyle(node).overflow)).toBe("visible");
  });
}

test("[ui_regression] admin integrity failure never renders or exports partial rows", async ({ page }) => {
  const city = "fujisawa_enoshima";
  const manifestUrl = new URL(`../public/data/admin/${city}.checklist.json`, import.meta.url);
  const manifest = JSON.parse(await readFile(manifestUrl, "utf8"));
  const shardPath = manifest.shards[0].path.slice(1);
  for (const mode of ["shard_corrupt", "manifest_rewrite"]) {
    let injected = false;
    await page.route("**/data/admin/**", async (route) => {
      const url = new URL(route.request().url());
      if (mode === "shard_corrupt" && url.pathname === shardPath) { injected = true; return route.fulfill({ status: 200, contentType: "application/json", body: "[]\n" }); }
      if (mode === "manifest_rewrite" && url.pathname.endsWith(`${city}.checklist.json`)) { injected = true; return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ...manifest, shards: [], counts: { ...manifest.counts, items: 0 } }) }); }
      return route.continue();
    });
    await page.goto(`/?city=${city}`);
    const panel = page.locator("section.admin-checklist");
    await expect(panel).toContainText("行政確認ワークフローの確認票を読み込めませんでした:");
    await expect(panel).toContainText(mode === "shard_corrupt" ? "byte count does not match" : "reviewed application binding");
    expect(injected).toBe(true);
    await expect(panel.locator("tbody tr")).toHaveCount(0);
    await expect(panel.getByRole("button")).toHaveCount(0);
    await page.unrouteAll({ behavior: "wait" });
  }
});
