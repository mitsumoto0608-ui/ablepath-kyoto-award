# G5–G8 Literature Index Status

統合タスクID: ABLEPATH-LITERATURE-INDEX-INTEGRATION-AND-EVIDENCE-CLOSURE-V1
原researchタスクID: ABLEPATH-G5-G8-LITERATURE-INDEX-READONLY-V1
実施日: 2026-09-01
役割: research-only integration / evidence contract audit

## Outcome

Gate 5–8で起きるP01–P17を分類したstandalone indexを、real AblePath repositoryのisolated worktreeへ統合した。`AGENTS.md`、`README.md`、`DESIGN.md`、`RESEARCH_LEDGER.md`、`MINIMAL_SUFFICIENT_ENGINEERING.md`、M6/Hokonavi freeze packets、PR #6 head `027d57b29f107717f4a57dc85c580632befd40a4`のcurrent G5–G8 reportsと照合済み。製品コード、schema、数値定数、M6/M7、UI、city data、`main`は変更していない。

統合監査で、A1/A2語彙、CSA/PROWAGの現行M6 evidence status、M7既存frozen contractとの境界、Ohtsu標本数、Moya部分標本の記述、PLATEAU 5.1文書とFY2025/v5 city packageの区別をresearch側だけで修正した。

作成物:

- docs/research/G5_G8_MASTER_BIBLIOGRAPHY.csv
- docs/research/G5_G8_PROBLEM_SOURCE_MAP.csv
- docs/research/G5_G8_GATE_SOURCE_MAP.md
- docs/research/G5_G8_SOURCE_CARDS.md
- docs/research/G5_G8_RESEARCH_GAPS.md
- docs/research/problem_packets/P01.md–P17.md
- reports/G5_G8_LITERATURE_INDEX_STATUS.md

## Inventory / deduplication

SOURCE_WORKSPACE_REPORTED_TOTAL_LOCAL_FILES_SCANNED=812
SOURCE_WORKSPACE_REPORTED_PRIMARY_LIBRARY_FILES_HASHED=121
SOURCE_WORKSPACE_REPORTED_PRIMARY_LIBRARY_UNIQUE_SHA256=116
TOTAL_UNIQUE_SOURCES=38
ORIGINAL_VERIFIED=33
DISCOVERY_ONLY=5
SOURCE_WORKSPACE_REPORTED_DUPLICATES_REMOVED=5
PROBLEM_PACKETS_READY=17
PROBLEMS_WITH_EVIDENCE_GAPS=17

統合監査で直接再現できたのは38 unique sources、33 ORIGINAL_VERIFIED、5 DISCOVERY_ONLY、17 packets、17 gap packets。812 / 121 / 116 / 5はitemized inventory/hash manifestがIMPORT ONLYに含まれないため、source workspaceの履歴reported countとしてのみ保持し、独立再現済みとはしない。private DB/raw research dataは読込・転記していない。

## Gate collections

Gate 5 sources: S001, S002, S005–S008, S015–S019, S023
Gate 6 sources: S002, S005, S015–S022, S031
Gate 7 sources: S006, S008–S013, S016, S020, S022–S025, S029, S032, S034
Gate 8 sources: S001–S005, S007, S010, S014, S021, S023–S030, S033–S034

## Top 10 most important sources

1. S005 — PLATEAU 3D都市モデル標準製品仕様書 第5.1版
2. S006 — 国土数値情報 洪水浸水想定区域データ（2025年度版）
3. S009 — PROWAG 2023 final rule
4. S003 — OGC CityGML 3.0 Conceptual Model
5. S015 — Moya et al. 2020, earthquake debris extent in Japan
6. S020 — Coppola & Marshall 2021, effective clear width
7. S022 — Treccani et al. 2022, historic-city point-cloud accessible path
8. S023 — Askari et al. 2025, Project Sidewalk vs government field data
9. S017 — 横屋ほか2024, 熊本地震road blockage validation
10. S032 — Ohtsu et al. 2020, assisted evacuation by device/slope

## Important findings

- PLATEAUの現行参照文書は5.1 (2026-03-19)。現行G8候補はFY2025 / product specification v5 city packagesであり、packageの実class・CRS・AOI・license・integrityは未検証。CityGML 3.0移行資料はFY2028予定の案で、現在のcity dataset実装を証明しない。
- PROWAG final rule is 2023. Older papers that use an ADA/PROWAG 3-ft value must not be presented as the current final R302.2 criterion.
- Hazard polygons carry scenario/source/year limitations; overlap is not closure or wheelchair passability.
- Moya’s Mashiki wood-frame debris equations and Yu/Gardoni’s Haiti C3 model have different calibration populations. Coefficients must not be averaged or transferred silently.
- Translation, AI synthesis, and deep-research reports remain DISCOVERY_ONLY even when their candidate citation is plausible.

## Human action required

HUMAN_ACTION_REQUIRED=

1. EN 17210本文を取得できない間はDISCOVERY_ONLY / REJECTを維持し、数値・条項を推測しない。
2. PLATEAU city package、CORS/root-child trace、official facility operation record、local M7 edge evidenceはEvidence Closure Queueのゲートに従い、欠落時は未接続 / `NOT_COMPUTED`を維持する。
3. 日本の法的適用、数値閾値、profile state、closure precedence、damage/debris rule、safety/accessibility claimはHUMAN FREEZE前にproductionへ昇格しない。

## Git status

Integration branch: `task/g5-g8-literature-index-integration-v1` from `origin/main@515955000d3df28b5b20e468a6312a006f7f95ea`. Commit/push/draft PR receipt is added by this task after verification. `main` merge, tag, and release are not attempted.
