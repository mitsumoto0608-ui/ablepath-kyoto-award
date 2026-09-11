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
| `viewer/public/data/admin/<city_id>.checklist.json` | 画面が読む正本（公開ビルド。`internal_use_only` 行を含まない） |
| `reports/ADMIN_CHECKLIST_<city_id>.json` | 上と同一 bytes |
| `reports/ADMIN_CHECKLIST_<city_id>.csv` | 同一 serializer（`toChecklistCsv`）由来の CSV |

再生成は `cd viewer && npm run build:data`。決定論的であり、再ビルドは byte 一致しなければならない。

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
5. CSV が必要なら「CSVを保存」。JSON は生成済み静的ファイルへのリンクから取得する。

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
- **照会先が receipt に無い行がある** — その行は `verification_target.label = "NO_TARGET_IN_RECEIPTS"`、
  `export_ready = false` となる。行を落とさず、原因を `unknown_reason` に残す。
