import { readFileSync } from "node:fs";

const catalog = JSON.parse(readFileSync(new URL("../public/data/maps/map-layers.json", import.meta.url), "utf8"));
const kiyomizu = catalog.cities.find((city) => city.city_id === "kyoto_kiyomizu");
const url = kiyomizu?.cesium?.tileset_url;

if (!url) {
  process.stdout.write("PLATEAU_REAL_URL_SMOKE=NON_GATING_FAILED reason=missing_reviewed_metadata\n");
  process.exitCode = 0;
} else {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10_000);
  try {
    const response = await fetch(url, { signal: controller.signal, headers: { Accept: "application/json" } });
    const body = response.ok ? await response.json() : null;
    if (!response.ok || body?.asset?.version === undefined || body?.root === undefined) {
      throw new Error(`HTTP_${response.status}_OR_INVALID_TILESET`);
    }
    process.stdout.write(`PLATEAU_REAL_URL_SMOKE=NON_GATING_PASS http=${response.status} asset=${body.asset.version}\n`);
  } catch (error) {
    const reason = error?.name === "AbortError" ? "timeout" : String(error?.message ?? "unknown").replace(/\s+/g, "_").slice(0, 160);
    process.stdout.write(`PLATEAU_REAL_URL_SMOKE=NON_GATING_FAILED reason=${reason}\n`);
  } finally {
    clearTimeout(timer);
    process.exitCode = 0;
  }
}
