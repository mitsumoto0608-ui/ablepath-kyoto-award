# Delivery sprint viewer quickstart

1. Run `cd viewer`, `npm ci`, then `npm run dev`.
2. Open the local URL shown by Vite.
3. Choose **都市・回廊**:
   - `京都・清水〜祇園`
   - `京都・嵐山`
   - `藤沢・江の島`
4. Select **実座標 / CANDIDATE**. This explicit opt-in leaves the default synthetic schematic unchanged.
5. In **candidate path fixture**, choose the precomputed origin and destination. Arbitrary routing is not computed in the browser.
6. In **地域・区間の確認リスト**, filter by source scenario/revision, coverage, missing field, reason/source text, or owner-candidate type; choose an explicit sort order. The table and all three downloads use the same filtered rows.
7. Save **CSV**, **JSON**, or **印刷用HTML**. Each contains candidate edges, source IDs/revisions/SHA-256, terrain status, official facility rows and attributes, and explicit unknowns.
8. Inspect **公式データの接続状態** for DEM blockers, disconnected Fujisawa earthquake/liquefaction inventories, Kyoto facility categories, PLATEAU fallback, and M7 reasoned-null evidence.

The screen is a candidate evidence review tool. It does not assert safety, accessibility, passability, current facility availability, or administrative validation.
