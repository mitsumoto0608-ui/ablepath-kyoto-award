# ほこナビ2024仕様参照マッピング契約

## 位置づけ

本書は、AblePath内部データと国土交通省「歩行空間ネットワークデータ整備仕様（2024年7月）」の間を結ぶ、**ほこナビ2024仕様を参照した対応契約**である。`src/hokonavi/`にはこの契約を固定する`SYNTHETIC` fixture限定prototypeがあるが、実データの変換や仕様適合の認証を意味しない。機械可読なmapping正本は `schemas/hokonavi_2024_mapping.yaml`、AblePath独自情報のexact sidecar正本は`schemas/hokonavi_2024_sidecar.schema.json`とする。

`adapter_implemented=false`はfull/real-data adapterが未実装であることを表し、限定prototypeは`adapter_prototype_implemented=true`、`adapter_implementation_scope=SYNTHETIC_FIXTURE_ONLY`として別に表す。

- 公式仕様: https://www.mlit.go.jp/sogoseisaku/soukou/content/001757259.pdf
- 公式掲載ページ: https://www.mlit.go.jp/sogoseisaku/soukou/sogoseisaku_soukou_tk_000056.html
- 発行主体: 国土交通省 政策統括官付
- 版: 2024年7月、49ページ
- 確認日: 2026-08-30
- 新版確認: `newer_revision_found=false`。2026-08-30に上記公式掲載ページを確認した範囲では、2024年7月版より新しい歩行空間ネットワークデータ整備仕様へのリンクは掲載されていなかった。公式サイト全体・将来時点での不存在は主張しない。将来新版を発見しても、この契約は自動で切り替えない。

## 原典の固定点

`文書頁`は本文フッターのページ番号、`PDF頁`は表紙を1とするPDFファイル上のページ番号である。両者を混ぜない。

| 対象 | 原典（文書頁 / PDF頁） |
|---|---|
| データ構造（リンク・ノード） | §1.3, 文書p.2 / PDF p.4 |
| JGD2011 | §2.2, 文書p.4 / PDF p.6 |
| リンク配置・起終点 | §3.2.2の起終点規則, 文書p.5 / PDF p.7、および配置詳細 文書pp.6–8 / PDF pp.8–10 |
| リンク54項目 | §3.3.1 表3.2, 文書pp.13–15 / PDF pp.15–17 |
| リンク取得方法 | §3.3.2, 文書pp.16–20 / PDF pp.18–22 |
| 幅・勾配・段差ランク | 表3.3, 文書p.21 / PDF p.23 |
| 幅・勾配・段差の詳細 | 文書pp.27–29 / PDF pp.29–31 |
| ノード7項目 | §3.3.3 表3.8, 文書p.33 / PDF p.35 |
| 階層 | §3.3.4, 文書pp.34–36 / PDF pp.36–38 |
| CSV/Shapefile/GeoJSON/GML | §3.4, 文書p.37 / PDF p.39 |

## statusの意味

| status | 意味 |
|---|---|
| `FULL` | 値・単位・意味を失わず対応できる |
| `PARTIAL` | コード体系、精度、意味範囲の差を明示して対応する |
| `SIDECAR_REQUIRED` | AblePath coreまたはほこナビ側だけでは保持できずsidecarが必須 |
| `UNMAPPED` | 直接対応がない。黙ってdropせず、拒否または外部sidecar保持 |
| `NOT_APPLICABLE` | 2024年版ネットワーク仕様の適用範囲外 |

## node/link/connector

- nodeは`node_id`、緯度、経度、`floor`、`in_out`、`link1_id`から`link99_id`までの接続リンクIDを扱う（表3.8）。adapterは存在する番号付き列を順に収集する。stable IDは文字列として保存し、adapterが採番し直さない。場所情報コードは推奨であり必須ID体系ではない（§3.3.4）。
- linkは`link_id`、`start_id`、`end_id`を分離し、参照整合性を検査する（表3.2）。起点・終点は幾何の並びと一致させるが、任意に方向を反転してIDを変えない。
- geometryはGeoJSON `Point` / `LineString`で保持する。公式仕様はGeoJSONを許容し、表3.2/3.8のフィールド名をproperty名に用いる（§3.4）。
- directionは`1=両方向, 2=起点→終点, 3=終点→起点, 99=不明`。`99`を両方向へ変換しない。
- connectorは階段、スロープ、エレベーター、エスカレーターを`route_type`と関連項目の整合した組として扱う。`stairs=false`だけから段数0を作らない。
- `route_type`は`1=対応属性なし, 2=動く歩道, 3=踏切, 4=エレベーター, 5=エスカレーター, 6=階段, 7=スロープ, 99=不明`である。`elevator=1`は「エレベーターなし」であり、対応ありを意味しない。
- levelは`floor`を基にする。屋外地上0、歩道橋等1、地下-1、中間階を小数で表す原典規則と、AblePathのlevel domainを照合する。
- `in_out`は`1=施設外(OUTDOOR), 2=施設内外の境界(BOUNDARY), 3=施設内(INDOOR)`のexact codebookとして扱い、raw codeも保持する。

## route/path・幅・勾配・段差

- `rt_struct`（経路の構造）は`route_structure`、`route_type`（経路の種別）は`route_type`へ別々に対応させ、共通の`edge_type`へ畳み込まない。少なくとも`rt_struct=2`は「車道と歩道の物理的な分離なし」、`3`は「横断歩道」、`4`は「横断歩道の路面標示の無い道路の横断部」である。
- `width`はカテゴリ、`w_min`はリンク内最小幅のm値である。カテゴリから中点を捏造しない。
- `vtcl_slope`は方向を含むカテゴリ、`vSlope_max`は整数%の最大値である。AblePath `slope_estimate`へ変換するときは符号・精度のlossを明記する。
- `lev_diff`は段差カテゴリ、`levDif_max`はcm単位の最大値である。0、欠落、99を同一視しない。
- `rank`は幅・縦断勾配・段差の3文字ランクであり、AblePathのprofile別4状態ではない。
- `r_method`は幅・勾配・段差の順に`1=現地調査, 2=走行軌跡`を並べた3文字である（表3.2 no.6、§3.3.2 no.6、文書p.22 / PDF p.24）。adapterは3属性へ分解し、同時にraw文字列をsidecarへ保持する。`121`は幅=現地調査、勾配=走行軌跡、段差=現地調査であり、AblePathのobservation/evidence全体を表現しない。

## static widthとM7 residual width

両者は物理的・時間的な意味が異なるため、同一fieldにしない。

| 層 | field | 例 | 意味 |
|---|---|---:|---|
| static network | `clear_width_static_m` | 4.00 | 平常の静的な最小有効幅の入力 |
| scenario result | `remaining_clear_width_m` | 0.73 | M7が特定scenario入力から計算した残存幅 |

`remaining_clear_width_m`で`clear_width_static_m`を上書きすること、および逆方向の上書きを禁止する。M7値はsidecarに置き、variant・hazard metadata・provenanceと一緒に保持する。

## UNKNOWNとAblePath独自情報

各fieldの原典コード`99`または欠損由来のUNKNOWNは、`0`、`false`、`OPEN`、`PASS`、`safe`へ変換しない。`code_99`という疑似fieldは作らない。原典で空欄が「制限なし」を意味する項目と、`99=不明`、属性欠落を`SOURCE_CODE_99` / `SEMANTIC_BLANK` / `MISSING_ATTRIBUTE`として区別する。`start_time`はこの区別を検証するpolicy-only fixture例であり、40件のfield mappingには数えない。

observation、evidence、validity、profile判定、scenario、provenance、Before/After、operation statusは、2024年版ネットワーク仕様だけでは完全に表せない。`schemas/hokonavi_2024_mapping.yaml`の指示に従いsidecarへ保持し、表現不能な項目を黙ってdropしない。詳細は `HOKONAVI_2024_INFORMATION_LOSS.md` に固定する。

## exact sidecar prototype v1

`schemas/hokonavi_2024_sidecar.schema.json`はversion `1.0.0`を固定し、unknown propertyを拒否する。edgeごとに複数のM7 variant、observation、evidence、profile×scenario、scenario状態、Before/After、operation statusを配列で保持し、edge参照とID重複を検査する。`provenance`は`source_role=ABLEPATH_DESIGN`、source ID、CRS、method、適用constant IDを別欄で保持する。

- profileの4状態とscenarioの`OPEN/NARROWED/CLOSED/UNKNOWN`は別field・別enumであり、相互変換しない。
- `NOT_COMPUTED`は状態値ではなく`computation_status`として保持し、対応するstateは`null`にする。
- hazard/operation dataが`UNKNOWN`なら、残存幅とclosureを0/falseにせず`null`にする。
- M7 recordの`remaining_clear_width_m`はsidecarだけに置き、static networkの`clear_width_static_m`を上書きしない。
- sidecarを許容しないexportでは、AblePath独自情報が存在すれば停止する。

## SOURCE_FACTとABLEPATH_DESIGN

- `SOURCE_FACT`は国土交通省仕様が定義するfield、code、単位、頁参照だけに用いる。
- `ABLEPATH_DESIGN`はM7、profile、scenario、Before/After、operation status、provenance等のAblePath独自設計に用い、`docs/reference/DESIGN.md`またはM7契約を正本として引用する。
- AblePath独自項目のmappingには、国土交通省仕様の§1.2等を根拠として付けない。国土交通省側の記録は、その項目が仕様範囲外であることを示す`scope_exclusion`としてのみ分離記録する。

## adapter停止条件

adapter実装は以下で停止する。

- ID重複、dangling start/end、node/link混在
- CRS未宣言またはJGD2011への変換根拠なし
- 未知コードを既知値へ丸める要求
- static widthとscenario widthの上書き
- `PARTIAL`/`SIDECAR_REQUIRED`/`UNMAPPED`項目のloss記録欠落
- source/method、provenance、operation statusを捨てる要求
