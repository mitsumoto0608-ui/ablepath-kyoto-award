# 行政確認ワークフロー運用手順（T-A / admin-check checklist v1）

## 1. これは何か

`viewer/public/data/admin/<city_id>.checklist.json` は、既存 receipt を機械変換しただけの確認票である。
新しい事実・判定・推定を一切含まない。1 行が「1 オブジェクト × 1 属性」の確認単位であり、
「いま receipt にどう書いてあるか」「なぜ埋まっていないか」「次に誰へ何を照会するか」だけを持つ。

免責節（生成物・印刷 HTML・本 docs で同一の固定文を使う。`viewer/src/adminChecklistCsv.mjs` の
`ADMIN_CHECKLIST_GUARD_TEXTS` が唯一の定義であり、ここはその逐語引用である）:

- この表は行政による検証結果ではありません。通行可否・安全性・アクセシビリティの判定を含みません。
- 露出は被害ではない。
- UNKNOWNは通行不可でも可でもない。
- priority_rank は並び順の機械規則であり、危険度・重要度ではありません。
- 露出は被害ではない。damage_state・debris_present・official_closure・通行可否を導出しない。

`safety_claim` / `accessibility_claim` / `admin_validated` は全 city で `false`、`m6_status` / `m7_status` は
`NOT_COMPUTED` のままである。HUMAN_GATE 1（PoC counterpart の確定）が済むまで internal PoC 用として扱う。

## 2. 生成物

| path | 内容 |
| --- | --- |
| `viewer/public/data/admin/<city_id>.checklist.json` | 画面が読む **manifest**（header・counts・`shards[]`。行そのものは持たない） |
| `viewer/public/data/admin/<city_id>/<section>.partNN.rows.json` | 行 shard（compact JSON）。1 ファイル 2 MiB 以下 |
| `reports/ADMIN_CHECKLIST_<city_id>.json` | 行を含む完全版（pretty） |
| `reports/ADMIN_CHECKLIST_<city_id>.csv` | 同一 serializer（`toChecklistCsv`）由来の CSV |

再生成は `cd viewer && npm run build:data`。決定論的であり、再ビルドは byte 一致しなければならない。

### 2.1 shard 分割（2 MiB ポータビリティ上限）

ブラウザが取得するファイルは 1 本あたり **2 MiB 以下**でなければならない。行を間引いたり要約したりして縮めることは
してはならないので、代わりに**分割**する。

- 行は決定論的な並び順（`priority_rank` → `object_type` → `object_id` → `attribute`）のまま、
  section（`object_type`）が変わる位置と、次の行を足すと上限を超える位置で切る。
  したがって **manifest の順に shard を連結すると、分割前とまったく同じ並びの全行が得られる**。
- 行 shard は compact `JSON.stringify`（pretty 出力をやめるのは**書式の選択**であって内容の変更ではない）。
  manifest と `reports/` の完全版は従来どおり pretty のままである。
- manifest の各 shard には `path` / `section` / `part` / `row_count` / `sha256` / `bytes` が入る。
- 画面の loader は **全 shard の SHA-256 と `row_count`、および合計行数を検証してから**描画する。
  1 本でも欠落・不一致があれば fail-closed で停止し、部分描画は行わない。
- **これは spec からの逸脱である。** spec WANT#2 は「`reports/ADMIN_CHECKLIST_<city_id>.json` は viewer 配下と同一 bytes」
  と定めているが、shard 化により viewer 側は manifest（行なし）となり、両者は同一 bytes ではなくなった。
  行の内容・並び・件数は完全に同一で、`reports/` 側が全行の正本である。
  また `viewer/public/data/admin/<city_id>/*.rows.json` は spec の ALLOWED_PATHS（`viewer/public/data/admin/<city_id>.checklist.json`）
  に列挙されていないパスであり、これも逸脱である。いずれも §8 に記載する。
- `reports/` は画面が取得しないため 2 MiB 上限の対象外である（repo 側の上限は公開派生物の 10 MiB）。
  `reports/ADMIN_CHECKLIST_kyoto_arashiyama.json` は約 6.4 MiB の完全版であり、これが全行の正本である。

## 3. 誰が何を埋めるか

**埋めてよい欄は `human_fields` の 4 つだけ**である。生成物では常に `null` であり、UI も保存しない。
印刷した紙、または内部運用の別台帳に人が書く。

| 欄 | 誰が | 内容 |
| --- | --- | --- |
| `human_fields.assignee` | 行政担当 | 照会・計測の担当者名 |
| `human_fields.due` | 行政担当 | 期限 |
| `human_fields.result` | 行政担当 | 照会結果・計測結果の記録先（受領した一次資料の所在） |
| `human_fields.note` | 行政担当 | 備考 |

**埋めてはいけない欄**（人が書き換えると receipt との対応が壊れる。変更したい場合は receipt 側を直して再生成する）:

- `status` — receipt の状態語から機械変換した値。`UNKNOWN` を `CONFIRMED` に手で書き換えない。
- `unknown_reason` — receipt に実在する状態語の逐語コピー。新しい理由語を作らない。
- `priority_rank` / `priority_rule` — 並び順の機械規則。priority_rank は並び順の機械規則であり、危険度・重要度ではありません。感覚で並べ替えない。
- `source_id` / `source_revision` / `source_sha256` — `CONFIRMED` 行にのみ入る。手入力しない。
- `verification_target` — receipt からの逐語コピー。要約・言い換えをしない。
- `exposure_flags` — 露出の集計のみ。ここから被害・閉塞・通行の状態を作らない。

`UNKNOWN` は既定値で埋めない。「概ね確認済み」等の丸めをしない。`UNKNOWN` のまま残すことが正しい状態である。

## 4. 状態語の読み方

| status | 意味 |
| --- | --- |
| `CONFIRMED` | 出所つきの値が receipt にある（`source_id` / `source_revision` / `source_sha256` が揃う） |
| `UNKNOWN` | receipt が「わからない」と記録している。理由語は `unknown_reason` |
| `NOT_CONNECTED` | データ自体が接続されていない（列挙されていない・パッケージに候補が無い） |
| `PERMISSION_REQUIRED` | 出所の許諾審査が未了で、値を公開表示できない |

`verification_method` は次の作業種別を示す: `FIELD_MEASUREMENT`（現地計測）/ `OFFICIAL_QUERY`（照会）/
`DOCUMENT_REVIEW`（資料確認）/ `NOT_APPLICABLE`（`CONFIRMED` 行）。

## 5. 使い方（推奨手順）

1. viewer の「行政確認ワークフロー」セクションで city を選ぶ。
2. `object_type` / `status` / `verification_method` で絞り込む。件数は常に「絞り込み後 / 全体」で表示される。
3. 行を選んで詳細（出所・SHA-256・照会先・露出集計・priority_rule）を確認する。
4. 「印刷」で紙に出し、`human_fields` の 4 欄を手で埋める。
5. CSV が必要なら「CSVを保存」（画面が連結した全行を同一 serializer に通すため、`reports/` の CSV と byte 一致する）。JSON manifest は生成済み静的ファイルへのリンクから取得する。全行入りの JSON は `reports/ADMIN_CHECKLIST_<city_id>.json`。

## 6. 人間ゲート（Codex / 自動処理では閉じない）

1. **PoC counterpart の確定** — この票を実際に使う行政側の部署・役割が決まるまで internal PoC。`admin_validated: false` を維持する。
2. **藤沢施設行の内部利用判断** — `fujisawa_webgis_toilets_accessibility` は `LICENSE_REVIEW_REQUIRED`。
   既定ビルドは `includeInternalUseOnly: false` であり、藤沢の施設行は公開ビルドに 1 件も含まれない。
   内部 PoC で扱うかどうか、`includeInternalUseOnly: true` のビルドを回すかどうかは人間の決定である。
3. **照会文面の送付** — `verification_target` は照会先の候補列挙にすぎない。実際の照会・メール送付・現地計測は人が行う。
4. **京都市道路台帳平面図** — `EXCLUDED_PROHIBITED` のまま。照会先候補にも入れない（生成器は当該 candidate を `dataset_ids` から除外する）。
5. **fresh-context acceptance** — 事前知識ゼロの読み手に `kyoto_kiyomizu` の印刷 HTML だけを渡し、
   (a) 確認済みの項目とその出典、(b) UNKNOWN の項目とその理由語、(c) 次に誰へ何を照会するか、
   (d) この表が判定ではないこと、の 4 点を口頭で言えるかを人間が確認する。
   言えない項目があれば**文言のみ**を直す（データを足さない）。

### fresh-context acceptance 記録欄

| 実施日 | 読み手 | (a) 出典 | (b) 理由語 | (c) 照会先 | (d) 判定ではないこと | 直した文言 |
| --- | --- | --- | --- | --- | --- | --- |
| （未実施） | | | | | | |

## 7. 既知の制約（データを足して解消しないこと）

- **edge に subarea が無い** — subarea を割り当てる receipt が存在しないため、全 edge 行の `subarea_id` は
  `SUBAREA_NOT_ASSIGNED_IN_RECEIPTS` である。幾何から推定して埋めない。
- **藤沢施設の行データが公開 tip に無い** — `cities/fujisawa_enoshima/facilities/official/FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json`
  は `public_git_current_tip_status = METADATA_ONLY_ROW_DERIVATIVES_EXCLUDED` により現在の公開 Git tip に存在しない。
  生成器は receipt の件数（57）から行を捏造せず、0 行を出し、`fujisawa_facility_row_source_status` にその状態語を残す。
  行データが内部で復元された場合のみ `includeInternalUseOnly: true` のビルドで 57 record 分が現れる。
- **住所から座標を作らない** — 藤沢施設の `geometry_status` は `ADDRESS_ONLY` のまま `NOT_CONNECTED` である。
- **shard に scenario 次元は無い** — checklist の行に hazard scenario を割り当てる receipt が存在しないため、
  shard の分割軸は section（`object_type`）と決定論的な part 番号だけである。scenario 別の分割は行わない
  （無い次元を作らない）。
- **R7 に「照会先」列は無い** — `reports/PHASE4_DATA_ACQUISITION_MATRIX.csv` は city × subarea × category ごとの
  未取得作業を並べた表であり、部署名・担当者・連絡先の列を持たない。したがって施設・plaza 行の
  `verification_target.label` は receipt の `notes` を逐語コピーした**制約の説明**であって、照会先そのものではない。
  誰に照会するかは HUMAN_GATE 3 で人間が決める。該当行が複数ある場合は、行順に依存しないよう
  distinct な `notes` をコードポイント順に並べて ` / ` で連結する（先頭行を採らない）。
- **照会先が receipt に無い行がある** — その行は `verification_target.label = "NO_TARGET_IN_RECEIPTS"`、
  `export_ready = false` となる。行を落とさず、原因を `unknown_reason` に残す。

## 8. spec からの逸脱一覧

| # | 逸脱 | 理由 | 影響 |
| --- | --- | --- | --- |
| 1 | R5 の行データ（`FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json`）が repo に無い | `public_git_current_tip_status = METADATA_ONLY_ROW_DERIVATIVES_EXCLUDED` | 藤沢施設行 0 件。件数から行を捏造しない。状態語を header に記録（§7） |
| 2 | WANT#2「reports JSON == viewer JSON bytes」を満たさない | 2 MiB ポータビリティ上限を、行を落とさずに満たすため shard 化した | viewer 側は manifest、`reports/` 側が全行の正本。行の内容・並び・件数は同一（§2.1） |
| 3 | `viewer/public/data/admin/<city_id>/*.rows.json` は spec の ALLOWED_PATHS に無い | 同上（shard の置き場） | 生成物のみ。生成器・画面・テスト以外のコードには触れていない |
| 4 | shard の分割軸に scenario を使わない | checklist の行に hazard scenario を割り当てる receipt が存在しない | 分割軸は section（`object_type`）＋決定論的 part 番号のみ（§7） |
| 5 | 生成物の並び順に `localeCompare` を使わない | ICU データ依存で生成 bytes が機械依存になるため、コードポイント比較に統一 | 並び順の実測差分はゼロ |
| 6 | SHA-256 は LF 正規化後のバイトに対して計算する | 既存の `canonicalTextHash` 流儀に合わせたため | Git blobの入力はLFで生バイトSHAと一致。WindowsのCRLF checkoutは正規化が必要。配信shardは正規化せず生バイト検証 |
| 7 | `viewer` に Blob / `window.print` が無いという spec の前提が現状と不一致 | 既に `ReviewChecklistPanel` が `downloadText`（Blob）を使っている | 新機構を発明せず既存流儀に揃えた |

### 2026-09-12 Codex takeover 限定補遺

| 既存の逸脱番号 | 今回の扱い |
| --- | --- |
| 2・3 | 所有者指定takeover masterにより限定承認。reports全行が正本、manifest/shardは配信表現 |
| 1・4 | 入力データの制約。行・scenarioを補わず保持 |
| 5・6・7 | 既存の決定論・LF・export実装契約との整合として保持 |

manifest順のshard連結はreportsの全行・順序・件数と一致する。
各manifestのSHAをreview済みアプリに固定し、全shardの生バイトSHA・bytes・件数、
city・item ID・pathの一意性、内部行の除外を表示前に検証する。
manifest自己申告だけを真正性証明とはしない。アプリ全体の差し替えを防ぐ署名ではない。
画面では全行をスクロール表示し、印刷時には高さ制限を解除する。
CSVはfilter中も全行、JSONリンクはmanifestであり全行JSONではない。
機械E2EはHUMAN_GATE 5の初見利用者確認を代替しない。HUMAN_GATE 1–5は未完了。
新しい確認票E2Eに限り、大量行の記録処理による遅延を避けるためtraceのDOM/ARIA snapshotを省く。
実DOMの全行・filter・詳細・実CSV保存・印刷・破損拒否の検査、既存timeout、画面記録は維持する。
既存の地域・区間export試験の記録方法は変更しない。

T-Bの現行CRS・利用条件は
`reports/FUJISAWA_INTENSITY_CRS_CLOSURE_RECEIPT.json`を参照。
独立receiptの対応表はreportsへ置き、既存citypackのartifact集合・manifestは変更しない。
県の01_震度8scenarioのbindingは藤沢市施設の許諾や過去の公開履歴へ適用しない。
