# AGENTS.md — Codex運用規約（AblePath京都）

このリポジトリで作業するAI（Codex等）は、コードを書く前に本ファイルを読むこと。
プロジェクト＝**京都・清水、京都・嵐山、藤沢・江の島の観光地で「誰が、なぜ通れないか」を証拠付きedgeで評価し、平時観光と地震・火災・大雨の避難計画成立性を同じ歩行グラフで検証する行政向けツール**。現在地＝**シナリオ計算エンジンv0.2＋M7残存幅コア＋multi-city engineering UI shell**。3都市の表示geometryは`SYNTHETIC_DEMO`、graphは`CANDIDATE`であり、実地図、MapLibre、Cesium、M6/profile統合、行政PoCは未完成。清水には別laneとしてsource-traceableな実VGI artifactとcandidate graphがあるが、viewer/modelには未接続。KPIの根拠不足は0ではなく`null`＋reason、M6は`NOT_COMPUTED`として扱う。

Current truth flags: `OVERALL_STATUS=PARTIAL_COMPLETE`、`ENGINEERING_UI_SHELL_COMPLETE=true`、`TWO_D_IMPLEMENTATION=SYNTHETIC_SVG_SCHEMATIC`、`KIYOMIZU_REAL_ARTIFACT_CAPABILITY=true`、`REAL_GEOMETRY_ARTIFACTS_AVAILABLE=PARTIAL`、`REAL_GEOMETRY_CONNECTED=false`、`REAL_GEOMETRY_CONNECTED_SCOPE=VIEWER_OR_MODEL_PIPELINE`、`MODEL_CONNECTED=false`、`MAPLIBRE_CONNECTED=false`、`CESIUM_CONNECTED=false`、`ADMIN_VALIDATED=false`。Hosted CIはLinux Python、Windows Python、static viewer/Nodeを検証する。M7 coreは実装済みだが、3都市の実/CANDIDATE edgeには未接続。

### Execution Efficiency Rule

利用可能なsub-agent機能は積極的に使うこと。

独立可能な調査・テスト設計・監査を直列に処理せず、
安全に分割可能なら並列実行する。

標準構成:
- MAIN = coordinator / implementer
- LUNA = design / evidence / contract auditor
- TERA = tests / invariants / mutation / regression auditor

ただし同一ファイルへの並列書き込みは禁止。
速度より安全契約を優先する。

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

- 受け入れ条件は常に`python -m pytest tests/ -q`全通過。固定テスト本数を正本にせず、対象commitのHosted CI結果とローカル実行結果を報告する。**先にテストを書く**（手計算フィクスチャの期待値と導出式をdocstringに明記）。
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

`main`＝常にテストが通る安定版。作業はタスクブランチまたは人間が指定したintegrationブランチで行い、1ブランチ=1ブリーフを原則とする。人間ゲートなしに`main`へmergeしない。

## 完了報告テンプレ

変更ファイル一覧／実装判断（迷った点）／テスト内訳（新規・更新とその手計算根拠）／`pytest`結果／`all_runs.json`のsha256（2回実行）／mutation確認結果／A1化要求（あれば）。

## 直近タスクキュー（この順で）

1. 3都市のsource-traceableな実geometryを取得・検証・接続する。
2. MapLibreを用いた実地図2D表示へ接続する。
3. 公式hazard geometryを取得し、edgeとの重なりを検証する。
4. 実/CANDIDATE edgeへM7残存幅コアを接続する。
5. M6/profile判定を実装し、`NOT_COMPUTED`を解消する。
6. Cesium/PLATEAU 3D表示を実装する。
7. ほこナビadapterとround-trip・情報損失検証を実装する。
8. 現地確認と行政レビューで妥当性を検証する。

## Multi-Agent / Sub-Agent Orchestration

本プロジェクトでは、作業時間短縮と品質向上のため、利用可能な場合は
sub-agent / parallel agent を積極的に使用する。

ただし「並列化そのもの」を目的にしてはならない。
最優先は、安全契約・再現性・人間レビュー可能性である。

### 基本方針

主エージェントは coordinator / integrator とする。

主エージェントの責任:
- タスク全体の理解
- 変更範囲の固定
- sub-agentへの仕事分割
- 重複作業の防止
- 最終diff統合
- pytest / runner / SHA確認
- 安全契約確認
- 人間レビュー項目の明示

利用可能なsub-agentがある場合、
独立して並列実行できる仕事は原則としてsub-agentへ委譲する。

例:
- コードベース探索
- 関連仕様の確認
- テストケース列挙
- mutation候補作成
- 数式の独立再計算
- provenance確認
- ドキュメント矛盾検出
- Git diff監査
- schema監査
- regression risk確認

### LUNA

LUNAが利用可能な場合、主に次を担当させる。

- 設計書・AGENTS.md・AI_TASKS・README間の契約照合
- 論文根拠と実装仕様の対応確認
- A0/A1/A2・TRANSFER_STATUSの確認
- 単位、数式、定数ID、provenanceの独立監査
- unsafe wording / overclaimの検出
- 未決事項の抽出
- 実装前レビュー
- 実装後のdiffレビュー

原則としてLUNAは、
主エージェントと独立に結論を出し、
主エージェントの判断を追認するだけの役割にしない。

### TERA

TERAが利用可能な場合、主に次を担当させる。

- pytest / fixture / invariant / mutation設計
- boundary caseの列挙
- negative testの設計
- UNKNOWN / FAIL / CONDITIONAL / PASSの状態遷移監査
- deterministic output確認
- SHA-256再現性確認
- Git差分・生成物差分確認
- regression risk確認
- failure injection
- acceptance gate監査

TERAは可能な限り、
実装者とは独立してテスト期待値を計算する。

### 並列化ルール

以下は並列化してよい。

- read-only調査
- 数式の独立再計算
- test case設計
- mutation候補作成
- docs監査
- provenance監査
- schema監査
- Git diff監査
- regression risk分析

以下は原則として同時編集禁止。

- 同一Pythonファイル
- 同一schema
- constants_registry.yaml
- src/allocate.py
- 同一テストファイル
- 同一生成物
- Git index
- branch / commit / merge操作

複数agentが同じファイルを編集する必要がある場合、
主エージェントが順番を決める。

### Writer Ownership

1タスクにつき、各ファイルのwriterは原則1agentだけとする。

例:

MAIN:
- src/residual_width.py

TERA:
- tests/test_residual_width.py の設計案のみ
  （実際の書き込み権限が与えられた場合を除く）

LUNA:
- docs/review/* の監査
- 設計との矛盾報告

同じファイルへの同時書き込みは禁止。

### 最短経路の原則

主エージェントは開始時に、
タスクを以下に分解する。

A. blocker
B. parallelizable
C. sequential
D. human gate

blockerを最初に解消する。

parallelizableはsub-agentへ同時委譲する。

sequentialは依存順に実行する。

human gateが必要な箇所では自動で先へ進まない。

### Sub-Agent Budget

単純な作業ではsub-agentを乱立させない。

原則:
- 小タスク: 0〜1 sub-agent
- 中タスク: 2〜3 sub-agent
- 大タスク: 3〜5 sub-agent

同じ質問を複数agentへ投げる場合は、
独立検証が目的であることを明示する。

### Mandatory Independent Review

以下は最低1つの独立sub-agentレビューを推奨し、
利用可能なら必ず実施する。

- 数式追加・変更
- 単位変換
- safety boundary変更
- UNKNOWN処理変更
- profile判定変更
- scenario状態変更
- constants registry追加
- official data interpretation
- public-facing numerical claim
- deterministic output変更

特に高リスク変更では、

Implementer
→ TERA test/audit
→ LUNA contract/evidence audit
→ Main integration

の順を基本とする。

### No Hallucinated Delegation

存在しないagentを「実行した」と報告してはいけない。

LUNA / TERA / sub-agent機能が利用できない環境では、
主エージェント自身が同じチェックリストを実行し、

"sub-agent unavailable; performed serial self-audit"

と明記する。

### Reporting

終了報告には以下を含める。

- 使用したsub-agent
- 各agentへ渡した仕事
- 各agentの結論
- agent間で意見が割れた点
- 主エージェントが採用した判断
- 変更ファイル
- tests
- runner
- SHA-256
- unresolved issues
- human review required

## 人間確認ゲート

数式・単位・状態遷移・安全境界・配分目的関数・テスト期待値に触れるdiffは、マージ前に人間（またはFable）のレビューが必須。「テストが通った」はこのゲートを免除しない。
