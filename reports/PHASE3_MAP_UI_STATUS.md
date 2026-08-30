# PHASE3 MAP UI lane status

```text
LANE_ID=MAP
LANE_STATUS=BLOCKED_CONTRACT
BASE_SHA=372ce8ec37dcc2a263bd6ae28e565f9c03ed9673
HEAD_SHA=bbd6fc989a4ab65e6694d449ad9da32c0416922a
HEAD_SHA_SCOPE=PRE_ADDENDUM_REPORT_COMMIT; REPORT_BEARING_HEAD_IS_BRANCH_REF
ALLOWED_PATHS_AUDIT=PASS
WORKING_TREE_CLEAN=PASS
CLEAN_VERIFICATION_HEAD=d910fb1966c40c7c7083e71501daf21beacd3151
FEATURE_BRANCH_PUSHED=false
HOSTED_CI=NOT_RUN
HOSTED_RUN_URL=null
INTEGRATION_RECOMMENDATION=REPORT_ONLY
PUSH_STATUS=BLOCKED_LOCAL_GUARD_NAMESPACE_DENIED
REMOTE_HEAD_SHA=null
HUMAN_GATES=["FEATURE_BRANCH_NAMESPACE_DECISION","OSM_TILE_AND_ODBL_RELEASE_POLICY","PLATEAU_PDL_AND_RUNTIME_TRUTH_SYNC","GLOBAL_TRUTH_SYNC","MAIN_MERGE_REVIEW"]
```

Git commitは自分自身のSHAをblob内へ保持できないため、`HEAD_SHA`はaddendum適用直前の
実装・監査済みcheckpointを示す。reportを含む最終headは
`refs/heads/codex/phase3-map-ui-v1`から解決する。

- branch: `codex/phase3-map-ui-v1`
- base: `372ce8ec37dcc2a263bd6ae28e565f9c03ed9673`
- lane: `MAP`
- date: `2026-08-31`

## Viewer-scoped truth

- `MAPLIBRE_RUNTIME_IMPLEMENTED=true`
- `KIYOMIZU_REAL_COORDINATE_VIEWER_CAPABILITY=true`
- `CESIUM_RUNTIME_IMPLEMENTED=true`
- `KIYOMIZU_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER=true`
- `ARASHIYAMA_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER=false`
- `FUJISAWA_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER=false`
- `PLATEAU_3D_CONNECTED=false`（citypackの静的truthを維持）
- `REAL_MAP_COMPLETE=false`（3都市全体・公式hazard・行政確認は未完了）

本laneはviewer能力を実装した。README、AGENTS.md、city statusに残る
`MAPLIBRE_CONNECTED=false`、`CESIUM_CONNECTED=false`、
`REAL_GEOMETRY_CONNECTED_TO_VIEWER=false`などのglobal truthは変更していない。
統合時にhuman reviewを経てtruth syncが必要であり、このlane単独でglobal CONNECTEDを主張しない。

## 実装

- MapLibre GL JS 6.6.0をexact pinし、清水のsource-traceableな実座標候補graph 19 edgeを表示する。
- 実座標layerは明示選択とし、`REAL / SOURCE_TRACEABLE_REAL / CANDIDATE / UNKNOWN`、
  `CANDIDATE_REVIEW_REQUIRED`、`NOT_ESTABLISHED`をUIとruntime validatorで維持する。
- OSM背景tileのCORS・通信失敗時も、same-originのローカル候補edge overlay、属性、全edge表を継続表示する。
- Cesium 1.144.0を3D選択時だけdynamic importし、token不要のPLATEAU LOD2 URLを読む。
  root、子tile、render、timeoutの失敗は理由を残して2Dへ戻し、layerとedgeのURL状態を保持する。
- PLATEAUのruntime root読込成功は`SESSION_ROOT_TILESET_LOADED`に限定し、静的接続truthへ昇格しない。
- 清水以外の2都市は、存在しない実geometry/3Dを補完せず`SYNTHETIC_DEMO`へfallbackする。
- 実データと合成データはlayer control、badge、provenance panel、source ID、licenseで区別する。
- OSM contributor copyrightとODbL licenseを別リンクで表示し、PLATEAU attributionを表示する。
- MapLibre/Cesium runtime assetはViteから同梱し、CDN runtime importとcommercial tokenを使わない。

## Provenance / deterministic artifact generation

viewer buildは、消費するcity入力をbyte-level SHA-256で固定し、不一致なら停止する。

| input | SHA-256 |
|---|---|
| candidate edges | `73e4f2d6965be2c8bb7a13229b4352fdef6886510219ebf9855d9581bbc3da7b` |
| corridor | `48b08553a9c2d7f8388bd893e83133287e01ad2efa9326116f5e8d3a31836dc7` |
| raw OSM source | `3d21ce674776c5c3e37c507c09a9458e062d2d31f5718b3e702313838ef7d2ec` |
| OSM query | `f32964329548d7d715c79cf05da6a28a7ac8230781acc4852f9174ba9f4dfb7b` |
| topology QA | `ea6a7b9257dd49147076af0bdec36a5ce189b87ce87ef1b763574d5b4ae9bb4e` |
| artifact manifest | `e83176c1396c3fd13001f3730f7017cd28bcfd2576c90104b971d401f83eb958` |
| PLATEAU metadata | `2a1e4c71370f58f0f40dc8b6eb9ae120b7f694b6caca1260a8a0efbbfeda78d3` |
| retained PLATEAU response | `ce58a92bb9da595d9251cd72b7b77af6da9a3748628a0e8370ffc6fbc6312242` |
| retained PLATEAU query | `eb9400f69b5ee88b802e972f426b4ff624ab759fe372776f67ecd83978221e40` |

生成copy SHAはsource candidate edges SHAと一致した。`cities/**`は変更していない。
凍結済み`src/allocate.py` SHAは
`2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`のままである。

## Tests

- clean dependency install: `npm ci --ignore-scripts` — pass、0 vulnerabilities
- targeted map/domain tests: pass
- viewer unit: `npm test` — 39 passed
- production build: `npm run build` — pass、1479 modules
- Playwright desktop/mobile: `npm run test:e2e` — 31 passed、1 intentional skip
- PLATEAU real URL non-gating smoke: HTTP 200、3D Tiles asset version 1.0
- full repository: `python -m pytest tests/ -q` — 499 passed、1 existing warning、136.89s
- runner pass 1: 120 runs、SHA-256 `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`
- runner pass 2: 120 runs、SHA-256 `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`

mutation checksは、artifact/copy/topology/manifest/PLATEAU hash変異、
`CANDIDATE_REVIEW_REQUIRED→VERIFIED`、`NOT_ESTABLISHED→ESTABLISHED`、
`PLATEAU_3D_CONNECTED false→true`、UNKNOWN以外のedge、座標軸swap、
dependency range/CDN import、子tile/render failure listener削除、2D fallback/URL保持削除で落ちる。

## Exact changed files

`BASE_SHA..HEAD_SHA`のMAP allowed-path差分は次の21ファイル。都市data、計算engine、
constants registry、README、DESIGN、main/tagは含まない。

```text
reports/PHASE3_MAP_UI_STATUS.md
tests/ui/dependencies.test.mjs
tests/ui/map_layers.test.mjs
viewer/DEPENDENCY_LICENSES.md
viewer/package-lock.json
viewer/package.json
viewer/public/data/maps/kyoto_kiyomizu.candidate_edges.geojson
viewer/public/data/maps/map-layers.json
viewer/scripts/build-map-artifacts.mjs
viewer/scripts/smoke-plateau-url.mjs
viewer/src/App.jsx
viewer/src/CesiumPanel.jsx
viewer/src/CesiumScene.jsx
viewer/src/MapLibreMap.jsx
viewer/src/domain.mjs
viewer/src/main.jsx
viewer/src/mapAsync.mjs
viewer/src/mapDomain.mjs
viewer/src/styles.css
viewer/tests/viewer.spec.mjs
viewer/vite.config.js
```

## Completion integrity audit

- `ALLOWED_PATHS_AUDIT=PASS`: 差分は上記21ファイルだけ。
- `WORKING_TREE_CLEAN=PASS`: detached verification worktree
  `C:/dev/ablepath-map-ui-completion`を`d910fb1966c40c7c7083e71501daf21beacd3151`で作成し、
  `git status --porcelain=v1`が空であることを確認。共有worktreeのscope外dirtyは変更していない。
- `SOURCE_CLASS_LICENSE_UNKNOWN_TRUTH=PASS`: OSMは`VGI / REAL geometry / ODbL 1.0`、
  PLATEAUは`OFFICIAL_METADATA_ONLY / PDL1.0`。candidate edgeのaccessibility・operationは全件`UNKNOWN`。
- `ALLOCATE_SHA256=2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`。
- `RUNNER_SHA256_PASS1=96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`。
- `RUNNER_SHA256_PASS2=96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`。
- `REFERENCE_983476E_UNCHANGED=PASS`: object `983476e323f1bd03005cc9ac6466e32d6f102aea`は解決可能。
  同commitが変更した`.gitattributes`に本laneの差分はない。指定baseのancestryには同commitを取り込んでいないため、
  cherry-pick・rewrite・内容変更をしていない。
- `MAIN_UNCHANGED=PASS`: local `main=112dbe9047d803528ee50dab284f6570de937583`。
- `TAG_UNCHANGED=PASS`: tag作成・更新・pushなし。
  observed `v0.2.0-baseline=0c3289b9174bf624c95faeaa3c1643664e31c2eb`。

## Independent review

- LUNA（contract/evidence）: 初回監査で、子tile/render fallback、OSM attribution、全入力hash、
  実layer source provenance、truth sync不足を指摘。viewer側で修正し、global truthは非昇格とした。
- TERA（test/invariant）: 初回監査で、fallback理由上書き、real table skip-link、
  edge選択時の再fetch、Cesium再初期化、timeout/unsafe wording test gapを指摘。修正と回帰testを追加した。
- agent間の意見対立はなかった。主agentは両監査のrelease blockerを採用した。
- 最終再監査: LUNA `Critical=0 / High=0`、TERA `Critical=0 / High=0`。

## Limited self-improvement log

共有memoryはread-onlyで参照し、このlane reportだけへlessonを記録した。

1. React mount失敗
   - OBSERVE: Playwrightはskip linkだけを検出し、最初のDOM待機でtimeout。
   - FINGERPRINT: early returnより後にhookが置かれたhook-order violation。
   - RETRIEVE: Windows Playwright終了stall lessonは別fingerprint。
   - DIAGNOSE: CODE。
   - ACT: `useCallback`をearly return前へ移動。
   - RESULT: targeted city test pass。
   - REFLECT: Windows上のCLI grep quotingを2回試したのは無駄。次回は`rg -g`で先に範囲を固定する。

2. basemap failure / 320px / safety text race
   - OBSERVE: local overlayがLOADING、320pxで339px、body text取得がmount前。
   - FINGERPRINT: remote rasterとlocal overlayの結合、flex min-content、待機不足。
   - DIAGNOSE: CODE + TEST。
   - ACT: local overlayを先に確立しrasterを非critical化、mobile min-width修正、heading待機。
   - RESULT: targetedとfull E2E pass。
   - REFLECT: remote failureを最初から独立状態として設計すべきだった。

3. Python test environment
   - OBSERVE: PATH Pythonにpytestなし、repo venv launcher exit 101、bundled Pythonにpytestなし。
   - FINGERPRINT: stale/incompatible Windows venv launcher。
   - RETRIEVE: `lesson-phase2-windows-test-environment-20260830`、
     `unique-external-pytest-basetemp-v1`。
   - DIAGNOSE: ENVIRONMENT。
   - ACT: OS temp配下にCI lock準拠の隔離venvと一意basetempを使用。
   - RESULT: full pytest pass。
   - REFLECT: 次回はrepo venvを再試行せず、lockfileから隔離venvを最初に作る。

4. map schema generator mismatch
   - OBSERVE: `unsupported viewer_map_schema_version: 1.0.0`、build/test exit 1。
   - FINGERPRINT: validator 1.1.0に対しgeneratorが1.0.0。
   - RETRIEVE: 同一lessonなし。
   - DIAGNOSE: CODE。
   - PLAN/ACT: generatorの宣言1行だけを1.1.0へ更新。fallbackなし。rollbackは同1行。
   - RESULT: build:dataとtargeted 9 tests pass。
   - REFLECT: schema field追加時はvalidator/generator/fixtureを同一checkpointで更新する。

5. child-tile fallback E2E通知競合
   - OBSERVE: 2D headingとURL復旧は成功、aria-liveだけがbasemap failure通知に上書き。
   - FINGERPRINT: transient announcement競合。
   - DIAGNOSE: TEST + UX。
   - ACT: persistent fallback bannerを追加し、child request＋2D state＋bannerを検証。
   - RESULT: desktop/mobile targeted pass。
   - REFLECT:状態遷移の証拠を単一の揮発live regionだけへ依存させない。

6. npm cache EPERM
   - OBSERVE: `npm ci`がuser npm-cacheの`EPERM stat`でexit 1。
   - FINGERPRINT: sandbox外cache参照拒否。
   - RETRIEVE: lane内に一致lessonなし。
   - DIAGNOSE: ENVIRONMENT。
   - ACT: 同一lockfile commandをsandbox外で1回だけ実行。
   - RESULT: 73 packages、0 vulnerabilities。
   - REFLECT: clean install gateはcache権限を先に確認する。

7. 存在しないE2E fixture edge ID
   - OBSERVE: 2件目row locatorが30秒timeout、desktop/mobile各1件。
   - FINGERPRINT: candidate artifactにない`...-S02`。
   - DIAGNOSE: TEST DATA。
   - ACT: artifactから実在する2件目IDを選択。
   - RESULT: targeted 2 pass、full E2E 31 pass / 1 skip。
   - REFLECT: fixture IDは推測せず生成artifactから取得する。

8. origin push authorization gate
   - OBSERVE: `git push -u origin codex/phase3-map-ui-v1`は、未確認originへの公開に対する明示承認不足として実行前に拒否。changed filesなし。
   - FINGERPRINT: unverified `origin` publication requires explicit destination approval。
   - RETRIEVE: 一致lessonなし。
   - DIAGNOSE: PLATFORM / authorization。
   - PLAN: primary fixは人間が`https://github.com/mitsumoto0608-ui/ablepath-kyoto-award.git`へのpushを明示承認すること。fallbackなし。allowed refは`codex/phase3-map-ui-v1`のみ、main/tagは対象外。
   - CHECKPOINT: 実装commit `c270c2d`はlocal branchに保存済み。
   - ACT: 同一pushは再試行せず停止。
   - REFLECT: remote destinationをpush前checkpointで提示し、明示承認を先に得る。

9. addendum適用後のexact payload push gate
   - OBSERVE: clean head `e7bf48dc3532f777bf5dca3de979f827f28e8752`から
     `git push -u origin codex/phase3-map-ui-v1`を要求したが、specific originへのexact payload公開承認が不足として実行前拒否。exit code/stdout/stderr/changed filesはprocess未生成のためなし。
   - FINGERPRINT: exact payload + specific destination publication approval required。
   - RETRIEVE: 直前lesson 8を確認。一般的なfeature push承認では不足する別のauthorization fingerprint。
   - DIAGNOSE: CONTRACT / PLATFORM authorization。
   - PLAN: primary fixは人間が
     `e7bf48dc3532f777bf5dca3de979f827f28e8752`を含む`codex/phase3-map-ui-v1`の全payloadを
     `https://github.com/mitsumoto0608-ui/ablepath-kyoto-award.git`へpushしてよいと明示承認すること。fallbackなし。
     allowed refは同feature branchのみ、rollbackはremote branch deletionを自動実行せず人間判断。
   - CHECKPOINT: local feature headは保存済み。clean detached verification worktreeあり。
   - ACT: 同一pushを再試行せず停止。
   - TARGETED/LANE/FULL TEST: code差分なし。直前の39 unit、build、31 E2E pass / 1 skip、499 pytest pass、runner二重SHAを維持。
   - REFLECT: addendumの一般push要件とspecific destination/payload公開承認を区別して開始時に取得する。

10. local push guard branch namespace denial
   - OBSERVE: 明示承認後、head `a84c7a4d77cb847643498dddd5c808ed23dc0c17`で
     `git push -u origin codex/phase3-map-ui-v1`を実行。exit 1。
     stderrは`LOCAL_GUARD_NAMESPACE_DENIED: only task/**, integration/**, and release/** branches may be pushed by an agent`。
     stdoutなし、changed filesなし、約5秒、Windows/PowerShell/local repository guard環境。
   - FINGERPRINT: agent push denied for `codex/**` namespace by local guard。
   - RETRIEVE: lane lessons 8・9を確認。authorization不足とは異なり、repository branch namespace contractによる拒否。
   - DIAGNOSE: GIT / CONTRACT。
   - PLAN: 新しい修復を開始しないというMASTER CONTROL移行指示に従い、primary fix・fallbackとも実行せず、
     branch namespace判断をorchestratorへ引き継ぐ。allowed pathは本lane reportのみ。rollback不要。
   - CHECKPOINT: local branchとclean detached verification worktreeに全成果を保存済み。
   - ACT: pushの再試行、branch rename、別ref pushを行わず停止。
   - TARGETED/LANE/FULL TEST: code差分なし。直前の全pass結果を維持。Hosted CIはbranch未pushのため`NOT_RUN`。
   - REFLECT: task開始時にlocal push guardの許可namespaceをbranch命名へ反映する必要がある。

同一fingerprintへ同一修正を反復しておらず、各failureは3attempt以内で解消した。

## Human review required

- ODbL attribution/share-alikeとpublic OSM tile利用方針。
- PLATEAU PDL1.0 attribution、runtime URL、viewer capabilityとstatic connection truthの区別。
- README、AGENTS.md、COMPLETION_LEVELS、city statusのglobal truth sync。
- 大きいCesium chunk（lazy-load済み）のperformance判断。
- mainへmergeする前の人間review。科学式、定数registry、UNKNOWN semantics、acceptance expected valuesは変更していない。

## A1化要求 / unresolved

- A1化要求: なし。新しい科学数値・法令閾値・公式data interpretationを追加していない。
- unresolved: 公式hazard geometry、M6/profile、実/CANDIDATE edgeへのM7接続、3都市全体の実geometry、現地・行政検証は別lane。
- out-of-scope dirty files `results/all_runs.json`、`results/summary.md`、`.workflow/**`は本commitへ含めない。
