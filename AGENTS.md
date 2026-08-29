# AGENTS.md — Codex運用規約（AblePath京都）

このリポジトリで作業するAI（Codex等）は、コードを書く前に本ファイルを読むこと。
プロジェクト＝**京都・清水の観光地で「誰が、なぜ通れないか」を証拠付きedgeで評価し、平時観光と地震・火災・大雨の避難計画成立性を同じ歩行グラフで検証する行政向けツール**。現在地＝**シナリオ計算エンジンv0.2**（合成データ・55テスト・120ラン決定論。まだ行政PoCではない）。

## 読む順序

1. `README.md`（30秒で動かす・安全契約・KPI4区分）
2. `docs/reference/DESIGN.md`（設計書v2.1＝要件・アーキテクチャ・論文マップの正本）
3. 担当タスクの`AI_TASKS/`ブリーフ1枚（ブリーフ外の変更・リファクタはしない）
4. 数値・式を触るときは`docs/reference/RESEARCH_LEDGER.md`の該当節（A1検証台帳）

## 凍結と安全境界（弱めるPRは拒否される）

- `src/allocate.py`は**凍結**（sha256=2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b）。変更が必要と思ったら実装せず提案として報告。
- 判定4状態の語彙（PASS/CONDITIONAL/FAIL/UNKNOWN）は凍結。**UNKNOWN→PASS/OPENへ落とす変換を書かない。**
- 安全契約（v0.2で実装済み）を維持：edge状態は密行列（欠落=停止）／fire_safe必須／複合一意制約／参照整合性／負値拒否／synthetic全数検査／`plaza_status_gating`／`--forbid-synthetic`。これらの検査を緩める・スキップする変更は不可。
- 決定論：乱数はシード固定。同一入力→`results/all_runs.json`のsha256一致。

## テスト規律

- 受け入れ条件は常に`python -m pytest tests/ -q`全通過（現行55本）。**先にテストを書く**（手計算フィクスチャの期待値と導出式をdocstringに明記）。
- テスト4分類のラベルをdocstring先頭に付ける：`[software_correctness]` `[source_conformance]` `[target_validation]` `[ui_regression]`。
- 意味論修正で既存期待値を更新する場合は、docstringに手計算根拠と更新理由を書く。黙って書き換えない。
- mutation確認（該当モジュールのみ）：片側瓦礫項の削除／m↔cm／≥↔>／UNKNOWN→OPEN／上り下り反転／mean+σ→mean−σ／(2/3)→23／容量超過割当——で必ず落ちることを完了報告に記録。

## 数値・定数の規律

- 数値定数は`data/constants_registry.yaml`から`tools/registry.py`の`get_constant(id, module=..., profile=...)`で引く。**直書き禁止**。
- 新しい外部数値（論文・法令・公式資料）が要るときは**実装せず「A1化要求」として報告**（人間またはFableが原本ページを確認してレジストリ登録するまで待つ）。翻訳DOCX・AI要約・Web検索結果から数値を採らない。
- チーム設定値はDESIGN_ASSUMPTIONとしてレジストリ＋README注記。テスト用合成値はFIXTURE_VALUE（レジストリ不要）。

## データの規律

- **Dropboxの絶対パスをコードに書かない。**外部データへのパスは`config/paths.local.toml`（Git管理外）から読む。雛形＝`config/paths.example.toml`。
- 外部データは`inputs/staging/<TASK-ID>/`に置かれたものだけを使う（各stagingフォルダの`TASK_INPUT_README.md`と`source_manifest.csv`が契約）。リポジトリ外・Dropbox全体を探索しない。
- 合成データのトークン（SYNTHETIC/PLACEHOLDER/ASSUMPTION_ONLY/UNVERIFIED_DEMO）を実データ風文字列に書き換えて検査を通さない。
- **京都市道路台帳平面図由来の数値・座標を一切取り込まない**（`data/ATTRIBUTION.md`）。

## 表現の規律（コード内文字列・README・出力に共通）

「安全な避難ルート」と言わない／時間断面・T+nフェーズは**静的スナップショットの分析**であり安全保証ではない／個別建物の倒壊・個別道路の冠水を予言しない／「救える人数」ではなく「追加で配分可能となる人数の上限」／4状態は本提案の統合であり既存標準準拠を名乗らない／海外閾値（ADAAG・香港・伊法）は参考レンジであり日本の適合基準ではない。

## ブランチ規約

`main`＝常にテストが通る安定版。作業はタスクブランチ：`task/m7-residual-width-tests`／`task/m7-residual-width-core`／`task/m2-topology-qa`／`task/kyoto-real-data-import`／`task/static-viewer`／`task/cesium-viewer`。1ブランチ=1ブリーフ。

## 完了報告テンプレ

変更ファイル一覧／実装判断（迷った点）／テスト内訳（新規・更新とその手計算根拠）／`pytest`結果／`all_runs.json`のsha256（2回実行）／mutation確認結果／A1化要求（あれば）。

## 直近タスクキュー（この順で）

1. **task/m7-residual-width-tests**：`AI_TASKS/03`のフィクスチャ3ケース（片側0.73m／両側0m／後退S=2→2.73m）＋mutation群を**テストだけ**書く（実装しない）。人間承認後に2へ。
2. **task/m7-residual-width-core**：残存幅ビルダー実装（物理層出力→派生4状態→profile判定層）。model/graph/runner/出力スキーマの変更可（allocate.pyのみ不可）。
3. **task/kyoto-real-data-import**：`AI_TASKS/01`。清水回廊の実データ変換（広場公式一覧・警戒区域の入手が先行条件＝人間側9/6期限）。
4. **task/m2-topology-qa**：QAコード8種（BLOCKER/REVIEW_REQUIRED/INFO・自動修正なし・わざと壊したフィクスチャ各1）。
5. **task/static-viewer**→**task/cesium-viewer**：`AI_TASKS/02`（runner出力を読むだけ。ビューア内で計算しない）。

## 人間確認ゲート

数式・単位・状態遷移・安全境界・配分目的関数・テスト期待値に触れるdiffは、マージ前に人間（またはFable）のレビューが必須。「テストが通った」はこのゲートを免除しない。
