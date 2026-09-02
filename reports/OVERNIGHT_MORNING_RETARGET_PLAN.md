# Overnight premerge composition — morning retarget plan

`PREMERGE_COMPOSITION_MODE=true` で作成した夜間成果を、human-only main protectionを維持したまま再接続する手順です。

1. 人間がPR #6 → #7 → #8 → #9を通常merge commitでprivate `main`へ順番に取り込み、branchを保持する。
2. `origin/main`をfetchし、4 PRの内容が入り、baseline tagが不変であることを確認する。
3. merge後mainのtreeが、事前合成tree `48f835d5805df29b070339a1f7dad3a8530ffdfa`と同等であることを確認する。異なる場合は自動retargetせず差分監査する。
4. 更新済みmainからisolated worktreeを作り、`reports/OVERNIGHT_NEW_WORK_COMMIT_MANIFEST.json`のcommitを記載順にclean replayする。競合時はmain保護を迂回せず停止する。
5. full Python、runner 120×2、all_runs/allocate SHA、viewer unit/build/E2E、npm audit、trust/secret/large-file scan、RC A/Bを再確認する。
6. stacked draft PRのbaseを`main`へretargetするか、clean replay branchから新しいdraft PRを作る。先頭の`DO_NOT_MERGE_TO_MAIN=true`は人間が最終diffとHosted CIを確認するまで維持する。

禁止事項は継続します: force push、`--no-verify`、branch削除、tag、release、M6/Hokonavi freeze、main protection変更。

現在の追加実装pre-receipt headは `93c7b901d713b1e85301f440407e5f43a26c92cd`。sourceとhash一致のactive pre-push guardを確認し、composition/headとも通常push済み。stacked draft PRは[#10](https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/pull/10)。morning replayではmanifest末尾のKyoto parityおよびCI screenshot timeout commitまで順に取り込み、清水・祇園・接続回廊のcombined AOIと嵐山AOIを混同しないこと、A31bはinternal displayのみ、M7は10 edgeすべてreasoned-nullのままであることを再確認する。
