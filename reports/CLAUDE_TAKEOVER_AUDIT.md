# CLAUDE_TAKEOVER_AUDIT — Codex→Claude Code 移管監査（第1run・無変更）

> **解決状況（task/claude-post-pr10-evidence-closure-v1 での更新）**: TK-01・TK-03・TK-04・TK-05・TK-06(申告訂正)・TK-11 は本ブランチで解決済み（`git log b64b5d0..HEAD`）。TK-02（viewer計算のsrc側移管）・TK-06のPNG削除・TK-07・TK-08・TK-09・TK-10・TK-12は未解決（人間裁定または後続タスク）。TK-13はNEEのまま。§7の「無変更」は第1run時点の記述。

実施: 2026-09-03／方式: read-only。primary worktree（C:\dev\ablepath-kyoto-award）は無変更（`GIT_OPTIONAL_LOCKS=0`で参照のみ）。監査はbundle `official-data-to-m7-evidence-v1.bundle` をコンテナへ複製し、PR #10 head `b64b5d0` の**detached isolated worktree**で実施。独立サブ監査2班（Opus: D/ABC班＝M7・データ、E/F班＝UI・生成バイト）＋統合者。GitHub API/Webへの照会は行っていない（PR状態・CI runは**pack申告のまま＝未独立確認**）。

## 1. TAKEOVER_PRE-FLIGHT（照合結果）

| 項目 | pack期待値 | 実測 | 判定 |
|---|---|---|---|
| remote | mitsumoto0608-ui/ablepath-kyoto-award | origin URL一致 | OK |
| origin/main | 5159550 | 5159550（tree 252a1c0） | OK |
| baseline tag | 0c3289b | 0c3289b | OK |
| PR #6 head | fdd780f | origin/integration/g5-g8-v1 = fdd780f | OK（※local `integration/g5-g8-v1` は旧027d57b） |
| PR #7 head | 7380e02 | origin/task/g5-g8-literature-index-integration-v1 = 7380e02 | OK（※local同名branchは旧48fb8dc） |
| PR #8 head | 1cb145f | local/origin一致 | OK |
| PR #9 head | c5dcdd0 | local/origin一致 | OK |
| composition head/tree | d029f33 / 48f835d | d029f33 / 48f835d | OK |
| PR #10 head/tree | b64b5d0 / 10daa14 | b64b5d0 / 10daa14（local・origin・bundle三者一致） | OK |
| PR #6〜#9 ⊂ composition | — | 4 head全てd029f33の祖先、mainはcompositionの祖先 | OK |
| PR #10 changed files | 91 | 91（`16_PR10_CHANGED_FILES.txt`と完全一致） | OK |
| PR #10 state OPEN/DRAFT/MERGEABLE, CI run 33593170231 | 申告 | **未照会（NEE）** | NEE |
| runner SHA ×2 | 96ea1404… | 96ea1404…（2回一致） | OK |
| allocate.py SHA | 2e5c6f7f… | 2e5c6f7f…（worktree実ファイル＋git show） | OK |
| pytest | 568 passed（Windows申告） | Linux: **564 passed / 4 skipped**（skip=PowerShell guard、旧SEC-02のfail→skip化を確認） | OK（環境差のみ） |
| viewer unit | 60 passed | 60/60 pass（node --test、node_modules不要） | OK |
| E2E viewer.spec.mjs | Hosted CI PASS申告 | NOT_RUN（Playwright未導入） | NEE |
| final RC A/B | 270542…／907 files each | 両方270542…、907 members、`cmp`でbyte一致 | OK |
| bundle | ed53bfd2… | ed53bfd2…（device側・コンテナ側とも）、`git bundle verify`=complete history、heads=b64b5d0/d029f33 | OK |
| CORRECTED_V2 zip | 297F6AA0…/17 | pack同梱コピーで**未照合**（C:\dev直下は未接続）→ 後続 | NEE |
| pack自身 SHA256SUMS | 28件 | 28/28一致 | OK |

## 2. Phase 1 独立再検証（申告値の再計数）

- Kyoto A31b: kiyomizu_gion **366** / arashiyama **136**（staging・viewer配信ともbyte同一）。
- Kyoto施設: **58 / 19 = 77**（staging・viewer配信byte同一）。座標はsource提供、silent_geocoding=false。
- 藤沢施設: 339行（★119）／江の島・片瀬57行（★17）。★=`ostomate_detail_available=true`のみ。他5属性は57件全て`UNKNOWN`。lat/lonは`UNKNOWN_NO_SILENT_GEOCODING`、geometry_status=ADDRESS_ONLY、map_ready=false（57/57）。
- PLATEAU AOI inventory: **5**（kiyomizu/gion/connector/arashiyama/enoshima_katase）。
- M7: readiness CSV **612行**、deep_pilot true=**15**（各都市5）、callable/ready/computed=**0/0/0**（612行全てfalse）、implicit_defaults_used=false（612）、damage_or_debris_derived_from_hazard=false（612）。clear_width/left/right/variant/hazard_status全612 MISSING。
- M6: NOT_COMPUTED（全status JSON）。safe_route/accessibility/admin_validated/public_release_ready=false。
- raw原本（zip/gml/pdf/xlsx/tif等）の追跡: **0件**。5MB超ファイル: 0件。
- 絶対パス: データ結合ファイル内に無し。ヒットは`.gitignore`/雛形/テストの禁止パターン/過去レポート文言のみ。
- hazard overlap→CLOSED/FAIL/damage/debris のコード経路: **不在**（src/scripts/viewer/cities全走査）。MapLibreMap.jsxはhazard artifactに`official_closure/damage_state/debris_present/setback_m`があれば実行時throw（fail-closed）。
- 凍結API `calculate_residual_width` の新規呼び出し: 本diffに無し（唯一の呼出`src/analysis/m7_pilot.py:87`はevidence_readyゲート下＝到達不能）。
- 禁止表現: 全ヒットが否定文脈のみ。

## 3. 相違点・所見（重大度順）

| ID | 重大度 | 所見 | 証拠 |
|---|---|---|---|
| TK-01 | HIGH | 配信`viewer/public/data/analysis/*.json`の`official_evidence.source_hashes`のうち6系統が現行repo bytesと不一致（kyoto_status 991ca56c→実3d9b3590、terrain_inventory 3都市、fujisawa facility_receipt 90b0a7b1→実60c63dc0）。レポート更新後に再生成せず同梱。UIの「source hash binding」表に**古いハッシュがそのまま表示**される。他のmaps/official/map-layers.jsonは再ビルドでbyte一致。 | `viewer/scripts/build-map-artifacts.mjs:85-91`, `App.jsx:364-365`; commit c2b8c4b/864c72a |
| TK-02 | HIGH | DES-14未解消：`viewer/scripts/build-map-artifacts.mjs:104-134`がDijkstra・連結成分・path_matrix・M7集計をviewer配下で計算。ランタイムは表示のみだが「ビューア内で計算しない」境界は未達。 | 同上 |
| TK-03 | MEDIUM→運用HIGH | `reports/OVERNIGHT_NEW_WORK_COMMIT_MANIFEST.json`は**10 commit**、実レンジd029f33..b64b5d0は**12**。欠落=`7cb7c50`（docs: Kyoto parity replay status）と`b64b5d0`（自己除外ポリシー記載あり）。7cb7c50の欠落は未説明。retarget不成立時のreplayでreceiptが黙って落ちる。 | manifest:6-18 |
| TK-04 | MEDIUM | official層の`copied_sha256`がsourceパスのハッシュ（=artifact_sha256と同値）で、配信先byteを読み直していない。maps層（`:171`,`:155-163`）と非対称。今回一致したが検証として機能せず（SEC-10根本原因の残存）。 | `build-map-artifacts.mjs:68,95` |
| TK-05 | MEDIUM | `tests/ui/official_data_layers.test.mjs:13-51`はtempへ再ビルドするがコミット済み配信byteと比較しない→TK-01を検出不能。 | 同上 |
| TK-06 | MEDIUM | `screenshot_binary_committed:false`（`reports/OFFICIAL_DATA_TO_M7_FINAL_STATUS.json:46`ほか）に反し`reports/UI_SCREENSHOTS/*-2d.png` 3枚（計1,939,205 bytes）がgit追跡下（本diff外で追加、本diffが偽申告を再表明）。 | git ls-files |
| TK-07 | MEDIUM | `reports/M7_ALL_EDGE_EVIDENCE_READINESS.json`の生成スクリプトが未追跡（`scripts/`は消費側のみ）。テストは`assess_m7_readiness`で全辺再計算し照合するため**検証可能**だが再生成不能。 | `tests/analysis/test_m7_real_edge_evidence.py:73-93` |
| TK-08 | MEDIUM | 受領書欠落: KYOTO-OFFICIAL-PARITY-V1/source_receipts.json の避難所2件にlicense無し・4件全てCRS無し；OFFICIAL-LOCAL-ARTIFACT-PROMOTION-V2/source_bindings.json 6 family license無し・5件source_url null（license_crs_matrix.csvに`LICENSE_REVIEW_REQUIRED`として別記録、connected:false）。 | 各ファイル |
| TK-09 | MEDIUM | exact-count固定テスト多数（612/15/17/12/9/9/339/119/57/17/5/2/77/58/19/…）。正当な追加で破綻（旧MERGE-01型）。0件系（computed==0等）はfail-closed契約として保持が正しい。 | D班F14一覧 |
| TK-10 | LOW | `build_kyoto_official_parity.py:414` `evidence_ready_count: 0`リテラル固定（pilot_status側は集計由来）；`:220` 元ID空行に連番で`facility_record_id`合成。 | 同上 |
| TK-11 | LOW | `viewer/public/data/analysis/*.json`・`maps/map-layers.json`が`.gitattributes` LF allowlist未登録（変更91ファイルはCRLF 0件）。 | .gitattributes |
| TK-12 | LOW | ローカルrepo衛生: local `main`=112dbe9（origin/main 5159550と乖離、前回FLOW-03のまま）、local `integration/g5-g8-v1`/`task/g5-g8-literature-index-integration-v1`はorigin側headより古い、HEADは`codex/phase3-map-ui-v1`（9e3411b）、worktree 70件がprunable、`.git/_to_delete_index.lock.stale`残置。監査には影響なし。 | device `git for-each-ref`/`worktree list` |
| TK-13 | NEE | GitHub側状態（PR OPEN/DRAFT/MERGEABLE、CI run 3 job SUCCESS、screenshot artifact）、E2E、CORRECTED_V2 zip SHA、raw Dropbox `新しいの` の原本SHA照合は未実施。 | — |

前回監査（9/1）からの進捗確認: SEC-10（copied_sha256虚偽）は**配信byte一致に修復**（ただしTK-04の構造は残存）／SEC-02（guard fail→skip）**修復**／FLOW-01/02はPR #9で対応（composition上でmap_truth 60/60 pass）／MERGE-01は composition で解消（564 pass）。

## 4. 総合判定

**TAKEOVER_AUDIT = GREEN_WITH_NOTES**
移管の前提（ref/tree/bundle/RC/SHA/test/申告件数）は全て実測で一致し、安全契約違反（hazard→closure、暗黙default、M6計算、禁止表現、raw追跡、絶対パス）は不検出。ただしTK-01〜03は**次のchild branchで最初に閉じるべき実欠陥**であり、PR #10自体は「現状のままhuman review可、main retarget前にTK-01/03修理推奨」。

## 5. 現在地

- 技術正本: PR #10 head b64b5d0（tree 10daa14）= composition d029f33 + 12 commits。PR #6〜#9は未merge（人間操作待ち）。
- 実データ接続: Kyoto A31b内部表示・施設77件・DEM AOI検証・PLATEAU inventory・藤沢施設ADDRESS_ONLY。M7 real edge = 0/0/0（入力証拠不足の正しい結果）。M6 NOT_COMPUTED。Hokonavi無効。
- 監査ワークスペース: `/tmp/takeover/repo.git`（bundle複製）、`/tmp/takeover/wt-pr10`（detached b64b5d0、clean）。primary無変更、GitHub無書込、branch/tag無変更。

## 6. 次の安全な1手（人間承認後）

1. ユーザーのローカルで（primaryは触らず）:
   `git -C C:\dev\ablepath-kyoto-award worktree add --detach C:\dev\ablepath-claude-takeover-pr10 b64b5d0c07ee7cc109adb0f5cf5f1f4193ff5800`
   → その中で `git switch -c task/claude-post-pr10-evidence-closure-v1`（PR #10 headから、push前に人間確認）。
2. 同branchの最初のcommit（順に）: (a) `reports/CLAUDE_TAKEOVER_AUDIT.{md,json}` 追加、(b) TK-01: analysis JSON再生成＋TK-05の「再ビルド=コミット済みbyte」テスト追加、(c) TK-03: commit manifestを`git log d029f33..HEAD`から導出、(d) TK-04: official層copied_sha256を配信先byteで再計算、(e) TK-06: screenshot申告の訂正。TK-02（viewer計算のsrc側移管）は設計判断を要するため人間裁定後。
3. その後 08_M7_TAKEOVER_PLAN §「具体的な次作業」1〜8（H23幅の結合可否→PLATEAU stable ID照合→setback freeze有無→missing維持→field coverage matrix→現地調査票）。値の捏造なし、computed=0維持。

## 7. Rollback

- 本runは何も変更していない → rollback対象なし。コンテナ側は `rm -rf /tmp/takeover/repo.git /tmp/takeover/wt-pr10` で消去可。
- 次runで作るworktree/branchは `git worktree remove C:\dev\ablepath-claude-takeover-pr10` と `git branch -D task/claude-post-pr10-evidence-closure-v1`（**未push・自分で作った場合のみ**、人間が実行）で完全復元。PR #10・composition・main・tagは一切触らないため復元不要。

## 8. 境界確認

primary repository: 無変更／GitHub: 無書込・無照会／branch・tag・PR: 無変更／M6・Hokonavi: 未freeze／M7入力の推測: なし／safe・accessibility・admin_validated claim: なし。
