# AblePath multi-city engineering kit — 観光×地震・火災・大雨 検証ツール

**現在地＝PARTIAL_COMPLETE**：安全契約・データ検査・KPI4区分・論文定数管理・再現性を備えたシナリオ計算エンジンv0.2、M7残存幅コア、清水・嵐山・藤沢（江の島）の3都市engineering UI shellを実装済みです。3都市のデフォルト表示は`SYNTHETIC_DEMO`模式図で、各都市とも明示操作時だけsource-traceable VGIの実座標`CANDIDATE` graphへ切り替えられ、MapLibre runtimeが候補edgeを表示します。全都市でroute continuityは`NOT_ESTABLISHED`であり、通行可能性・accessibility・安全性・運用状態を意味しません。Cesium runtimeは実装済みですが、実PLATEAU tilesetは未検証・未接続です。M6/profile、実edgeへのM7、KPI/model、行政PoCとpublic releaseは未完成です。公式hazardのglobal/operational接続は未完成ですが、`ABLEPATH-KYOTO-FUJISAWA-DELIVERY-SPRINT-V1`ではprivate/internal scopeに限り、京都A31b・京都土砂・藤沢A40のsource-side edge overlapをscenario別の証拠として接続しました。これはCLOSED/FAIL・damage・debris・通行可能性・安全性を生成しません。task-scoped current truthは`reports/DELIVERY_SPRINT_STATUS.json`、従来のPhase 4 gateはこの追加接続以前のhistorical snapshotです。

中心説明：**観光地で、誰が、なぜ通れないかを証拠付きedgeで評価し、平時のアクセシブル観光と地震・地震火災・大雨の静的scenarioを同じ歩行グラフで検証するためのengineering kit。** 現段階は行政判断や安全を保証する製品ではありません。

現在の3都市pack:

- 京都・清水：デフォルトは模式回廊`SYNTHETIC_DEMO`。明示切替時だけ、OSM historical snapshot `2026-08-30T00:00:00Z`、retained raw 17 ways / 142 nodes、normalized `SOURCE_TRACEABLE_REAL` / `VGI`、candidate graph 21 nodes / 19 edges / 2 components、route continuity `NOT_ESTABLISHED`の実座標候補layerをMapLibreで表示
- 京都・嵐山：デフォルトは`SYNTHETIC_DEMO`。明示切替時だけ、source-traceable VGIの530 nodes / 578 edges / 9 componentsの`CANDIDATE` layerを表示。route continuity `NOT_ESTABLISHED`
- 藤沢・江の島：デフォルトは`SYNTHETIC_DEMO`。明示切替時だけ、source-traceable VGIの16 nodes / 15 edges / 1 componentの`CANDIDATE` layerを表示。route continuity `NOT_ESTABLISHED`

`M6`未実装のためprofile結果は`NOT_COMPUTED`で、selectorは無効です。需要・現在容量・検証済み入口・運用状態の根拠が不足するKPIは、0と推定せず`null`＋reasonを返します。

```text
OVERALL_STATUS=PARTIAL_COMPLETE
CURRENT_MACHINE_TRUTH_AUTHORITY=reports/PHASE4_ANALYSIS_UI_GATE.json
ENGINEERING_UI_SHELL_COMPLETE=true
TWO_D_IMPLEMENTATION=HYBRID_SYNTHETIC_DEFAULT_WITH_THREE_CITY_REAL_CANDIDATE_OPT_IN
REAL_GEOMETRY_CONNECTED=true
REAL_GEOMETRY_CONNECTED_SCOPE=ALL_THREE_CITIES_EXPLICIT_OPT_IN_VGI_CANDIDATE_VIEWER_ONLY_NOT_MODEL_PIPELINE
KIYOMIZU_REAL_ARTIFACT_CAPABILITY=true
KIYOMIZU_CANDIDATE_GRAPH_AVAILABLE=true
ALL_THREE_CITIES_SOURCE_TRACEABLE_VGI_CANDIDATE_GEOMETRY=true
REAL_GEOMETRY_ARTIFACTS_AVAILABLE=ALL_THREE_CITIES_SOURCE_TRACEABLE_VGI_CANDIDATE
ALL_THREE_CITIES_REAL_GEOMETRY=false
REAL_GEOMETRY_CONNECTED_TO_VIEWER=true
REAL_GEOMETRY_CONNECTED_TO_VIEWER_SCOPE=ALL_THREE_CITIES_EXPLICIT_OPT_IN_VGI_CANDIDATE_ONLY
REAL_MAP_COMPLETE=false
MODEL_CONNECTED=false
M7_CONNECTED_TO_REAL_EDGES=false
M6_CONNECTED=false
KPI_CONNECTED=false
ADMIN_VALIDATED=false
MAPLIBRE_RUNTIME_IMPLEMENTED=true
MAPLIBRE_CONNECTED=true
MAPLIBRE_CONNECTED_SCOPE=ALL_THREE_CITIES_EXPLICIT_OPT_IN_VGI_CANDIDATE_ONLY
ALL_THREE_CITIES_MAPLIBRE_CONNECTED=true
KIYOMIZU_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER=true
ARASHIYAMA_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER=true
FUJISAWA_REAL_2D_ARTIFACT_CONNECTED_IN_VIEWER=true
CESIUM_RUNTIME_IMPLEMENTED=true
CESIUM_CONNECTED=false
PLATEAU_3D_CONNECTED=false
THREE_D_IMPLEMENTATION=RUNTIME_IMPLEMENTED_MOCKED_GATE_REAL_TILESET_NOT_VALIDATED
DEMO_COMPLETE=false
PUBLIC_RELEASE_READY=false
```

現在のmachine-readableな全体正本は`reports/PHASE4_ANALYSIS_UI_GATE.json`です。`reports/COMPLETION_LEVELS.json`はそのcompatibility mirrorです。3都市のhash-bound artifactとprovenanceは各city packのmanifest/receiptが正本で、清水のv1 source catalogueは`cities/kyoto_kiyomizu/sources/source_manifest.csv`、artifact authorityは`cities/kyoto_kiyomizu/realdata/artifact_manifest.v2.json`です。実座標edgeであることは通行可能性や安全性を意味しません。幅・勾配・段差・access・operationは`UNKNOWN`または`null + reason`で、M6/M7・KPI・modelへ未接続です。公式hazard analysisは0都市で、清水のpreviewもquarantineのままです。

## 30秒で動かす

Python full suiteの基本前提はGitとPythonです。local-main-guardのcore static/Git guard tests always runし、PowerShell 7（`pwsh`）がないminimal Linuxではonly the installer/status integration tests skipします。完全なinstaller/status evidenceは`pwsh`を備えたHosted Windows/Linux jobで確認します。UI unit/build/E2Eを行う場合はNode、npm、Playwrightも必要です。

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r scripts/overnight/requirements-ci.lock
python -m pip install --no-deps -e .
python -m pytest tests/ -q
python -m src.runner data/               # legacy synthetic baseline: 120 runs
```

Viewerのunit/build/E2E:

```bash
cd viewer
npm ci --ignore-scripts
npm test
npm run build
npm run dev
```

Viewer E2E（開発serverとは別のshellで実行）:

```bash
cd viewer
npx playwright install chromium
npm run test:e2e
```

Git cloneではGit blobを正本としてrelease archiveを作成し、trackedな未commit差分があればfail closedします。一方、RC ZIPを展開した非Gitディレクトリでは、同梱`RELEASE_MANIFEST.json`と`SHA256SUMS.txt`を検証してからテストfixtureの基準bytesを取得します。RC内checksumは整合性検査であり署名ではないため、配布時に別経路で共有されたZIP SHA-256をtrust anchorとして照合してください。

## 藤沢キットとの関係

配分エンジン（`src/allocate.py`：最近接・辞書式3段LP・η混合）は**藤沢CITYHACK_MASTERから無改変で再利用**。差し替えたのはハザード層だけ：

| 藤沢（期限型） | 京都（閉塞型・本キット） |
|---|---|
| T_tsunami(zone)の期限内判定 | 期限なし。時間断面5/10/15/30分の到達累積 |
| 津波避難ビル＋垂直移動 | 観光客緊急避難広場（第一段階のみ。二段階はAWARD期） |
| 浸水域による経路制約 | **scenario別edge状態 OPEN/NARROWED/CLOSED/UNKNOWN** |
| —— | **大雨**：警戒区域・浸水域の閉塞＋wet×石畳のprofile別減速 |
| —— | **地震火災**：時間フェーズ（T+10/30/60分）で閉塞集合が拡大。目的地はfire_safe広場（広域避難場所想定）に限定 |
| 施設UNKNOWN厳格/楽観 | **edge UNKNOWN厳格/楽観**（差＝道路状況確認の価値） |

## 実装済み（対象commitのテスト結果で確認）

地震3段階（弱/中/強の固定閉塞scenario——個別建物の倒壊予測はしない）。地震火災3フェーズ（T+10/30/60分——延焼を予測せず、被害想定・既往延焼シミュレーション成果〔PLATEAU UC23-26系〕を固定フェーズとして比較。火面拡大の単調性をテストで保証）。大雨3段階（L3=雨天路面のみ／L4=土砂警戒区域閉塞＋白川増水／L5=浸水拡大＋冠水UNKNOWN）。wet×stone のprofile別減速（雨の石畳。車いすは徐行0.6倍）。土地不案内＝判断遅延60秒＋迷い係数1.2（設計仮定・AWARD期にturn属性で置換。平時観光の所要時間にも同じ式を適用）。閉塞単調性・保存則・flow≦nearest・断面累積単調・厳格⊆楽観をテストが保証。

**KPIは4区分**：到達可能（physically_reachable）／収容（accommodated＝旧arrived）／滞留（overflow_waiting＝到達はできるが満員で待つ）／到達不能（unreachable）。「未収容」を容量不足と到達不能に分けないと、ハザードが強いときに**需要が容量不足から到達不能へ移った**のを「改善」と読み違える。

**安全契約（データが無いことを「大丈夫」に化けさせない）**：edge状態は(scenario×edge)の密行列でOPENも明示（行の欠落＝停止）／`plazas.fire_safe`は必須列（既定Trueで補完しない）／複合一意制約・参照整合性・負値の拒否／`plaza_status_gating=true`のとき厳格ランは`OFFICIAL_VERIFIED`の広場だけを配分対象にする（同梱デモはfalse＝従来出力のまま。`--forbid-synthetic`はtrueを要求）／SYNTHETIC・PLACEHOLDER・ASSUMPTION_ONLY・UNVERIFIED_DEMOの全数検査（全DataFrameの全文字列列＋settings）。

## legacy synthetic baselineの代表ラン（自動生成）

<!-- METRICS:BEGIN -->
<!-- tools/generate_readme_metrics.py が results/all_runs.json（全120ラン）から生成。手で編集しない -->

| 代表ラン | 需要 | 到達可能 | 収容 | 滞留（容量不足） | 到達不能 |
|---|---:|---:|---:|---:|---:|
| 平日・平常時・誘導配分 | 3,260 | 3,260 | 3,260 | 0 | 0 |
| 平日・大雨L4・最近接 | 3,260 | 3,260 | 2,620 | 640 | 0 |
| 平日・大雨L4・誘導配分 | 3,260 | 3,260 | 3,260 | 0 | 0 |
| 平日・地震火災 T+10状態 | 3,260 | 3,260 | 3,000 | 260 | 0 |
| 平日・地震火災 T+60状態 | 3,260 | 1,730 | 1,730 | 0 | 1,530 |
| 紅葉期ピーク・平常時・誘導配分 | 8,150 | 8,150 | 4,500 | 3,650 | 0 |
| ピーク・地震（閉塞強） | 8,150 | 6,625 | 4,500 | 2,125 | 1,525 |
| ピーク・大雨L5・厳格（E011のUNKNOWNを使わない） | 8,150 | 2,800 | 2,800 | 0 | 5,350 |
| ピーク・大雨L5・楽観（E011を使えると仮定） | 8,150 | 6,625 | 4,500 | 2,125 | 1,525 |
| ピーク・地震火災 T+10状態 | 8,150 | 8,150 | 3,000 | 5,150 | 0 |
| ピーク・地震火災 T+60状態 | 8,150 | 4,325 | 3,000 | 1,325 | 3,825 |

到達可能＝利用可能広場への経路がある需要／収容＝容量内に収まった需要／滞留＝到達はできるが満員で待つ需要／到達不能＝経路が無い需要。需要＝収容＋滞留＋到達不能（保存則をテストで固定）。
<!-- METRICS:END -->

## legacy synthetic baselineが示す仮説的構図（実都市の根拠ではない）

- **地震火災**：T+10分想定の道路状態スナップショットでは車いす含め清水門前から円山公園への経路があり、T+60状態では孤立する（OFFPEAKで到達不能1,530人）。PEAKでは広域避難場所一極集中でT+10状態から滞留5,150人——**フェーズによって律速が容量↔到達性で入れ替わる**。「T+10状態のスナップショットではまだ経路がある」＝早期避難・情報伝達の価値を火災が最も鋭く出す（各フェーズは独立した静的スナップショットであり、避難中の閉塞進行を解いているのではない）。

- **RAIN_L5**：五条坂（E011）の冠水状況がUNKNOWN。UNKNOWN道路を利用可能と仮定すると到達不能が5,350→1,525人へ減るが、広場容量不足2,125人が新たに顕在化する（PEAK・誘導配分。厳格＝収容2,800／到達不能5,350、楽観＝収容4,500／滞留2,125／到達不能1,525）。**この帯＝「道路1本の状況確認の価値」**であり、大雨版のUNKNOWNパネルの主役。確認できても全員が入れるわけではない、というのが4区分で初めて見える。
- OFFPEAK×RAIN_L4：最近接だと滞留640人→誘導配分で0人。大雨でも配分の価値が出る。
- PEAK（紅葉期想定）：**平常時**は誘導配分でも滞留3,650人が残る＝**広場容量の構造的不足マップ**（一時滞在施設・二段階の必然性への導線）。ハザードが強いscenarioでは需要が容量不足から到達不能へ移るため、滞留の数字はscenarioごとに違う（上の代表ラン表を参照）。
- 車いすprofileのsynthetic fixtureでは、二年坂・産寧坂を階段として不通にし、RAIN_L4固定scenarioでも東大路側の合成edgeが残るという静的計算結果になる。これは実道路の通行可能性・accessibility・hazard下の安全性を示さず、実世界の経路成立は`NOT_ESTABLISHED`である。

## 実データ差し替えの確認先（公式）

将来の差し替え候補は、土砂災害警戒区域＝京都府「土砂災害警戒区域等指定箇所情報」＋京都市Web版ハザードマップ／浸水想定＝京都市防災ポータル／緊急避難広場・一時滞在施設＝京都市の公式一覧（**円山公園が広場かは未確認・要確認**）／PLATEAU京都2025（建物・道路LOD3.4・橋梁・洪水・土砂LOD1）／歩行グラフ＝OSM＋QGIS＋現地実測（ほこナビ旧京都データは宇治のため使用不可・仕様参考のみ）。これらの公式hazard・施設・PLATEAUは現時点でproduction pipelineへ未接続。**京都市道路台帳平面図は複製・加工・派生作成・営利利用が禁止のためデータソースにしない**（詳細は`data/ATTRIBUTION.md`）。

## 数値と根拠の規律

- コード定数・発表数値にしてよいのは`査読論文A1検証台帳_2026-08-28.md`（Dropbox同梱）で**原本ページ確認済み（A1）**の値のみ。又聞き（A0）は`ASSUMPTION_`扱い。
- 判定4状態（PASS/CONDITIONAL/FAIL/UNKNOWN）は**既存研究の3状態系＋UNKNOWN悲観原則の統合（本提案）**であり、既存標準の実装ではない——準拠を名乗らない。
- 観測の重み（実測1.0/写真0.9/申告0.5）と48時間失効は**evidence_policy_v0＝本製品の設計仮定**。論文・標準由来ではなく、行政運用者が調整できるパラメータとして公開する。
- M7残存幅コアは実装済みだが、3都市の実/CANDIDATE edgeへは未接続。**scenarioを作る補助計算であり、被害を予言する道具ではない**（横屋2024：益城町を対象にした当該検証では最良設定で道路延長ベース最大78.8%の一致。不一致が残るため、個別道路の被害を断定しない）。
- `data/profiles.csv` の速度パラメータ（`flat_speed_mps` / `stair_speed_mps` / `slope_speed_factor_per_pct` / `wet_stone_speed_factor`）は現時点では全て **DESIGN_ASSUMPTION**（論文値ではないチーム設定値）。**M6でOhtsu表（`OHTSU_SPEED_TABLE_MS`：介助前提・神戸・理想化条件）へ置換予定**であり、置換までは京都未較正の暫定値として扱う（今回のPATCHでは値を変更していない＝結果不変）。
- 定数は`tools/registry.py`経由で引く：`get_constant("MOYA_DEBRIS_SLOPE", module="M7")`。`allowed_modules`外・`PRESENTATION_ONLY`の計算利用・`allowed_profiles`外の転用は`ValueError`で止まる（`tests/test_registry.py`が固定）。原本PDFの同一性は`python tools/verify_manifest.py <PDFのディレクトリ>`でSHA-256照合する（未発見はWARNINGでスキップ、不一致はエラー）。

## 次にやること（優先順）

1. 3都市のVGI `CANDIDATE` geometryを現地・管理者証拠で検証する
2. 公式hazard geometryを取得し、edgeとの重なりを検証する
3. 実/CANDIDATE edgeへM7のreviewed inputsを接続する
4. M6/profile判定を実装し、`NOT_COMPUTED`を解消する
5. 検証済み実PLATEAU tilesetをCesium runtimeへ接続する
6. ほこナビadapterとround-trip・情報損失検証を実装する
7. 施設・入口・容量・運用・需要を検証しKPI/modelへ接続する
8. 現地確認と行政レビューで妥当性を検証する

安全表現：「安全な避難ルート」と言わない。時間断面は分析用であり安全基準ではない。個別建物の倒壊・個別道路の冠水を予言しない（固定scenarioの比較）。UNKNOWNをPASSに落とさない。
