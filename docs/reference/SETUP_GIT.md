# 初回セットアップ（このzipを受け取った人向け）

このリポジトリは**Git初期化・baseline commit・タグ付与済み**の状態で納品されている。

## 1. 展開場所

```
<LOCAL_WORKTREE>
```

**Dropboxの中に展開しない**（`.git`の同期競合を避ける）。

## 2. 動作確認（PowerShell）

```powershell
cd <LOCAL_WORKTREE>
pip install pandas scipy networkx pytest pyyaml
python -m pytest tests -q        # 55 passed を確認
python -m src.runner data/       # 120ラン
git log --oneline -3             # baseline commit と v0.2.0-baseline タグを確認
```

## 3. GitHubへpush（https://github.com/myablepathway-svg 配下に非公開リポジトリを作成してから）

GitHub上で `myablepathway-svg/ablepath-kyoto-award` を **Private** で新規作成（README等は追加しない・空のまま）。その後：

```powershell
cd <LOCAL_WORKTREE>
git config user.name  "mitsumoto"                 # 必要なら自分の名義に
git config user.email "mitsumoto0608@gmail.com"
git remote add origin https://github.com/myablepathway-svg/ablepath-kyoto-award.git
git push -u origin main
git push origin --tags
```

## 4. 最初のブランチ（AGENTS.mdのタスクキュー1）

```powershell
git switch -c task/m7-residual-width-tests
```

Codexにはこのリポジトリ（<LOCAL_WORKTREE>）だけを開かせ、AGENTS.mdを読ませてから作業させる。

## 5. Dropboxとの分担

- Git＝コード・テスト・設定・設計書（docs/reference/）・A1台帳・小さな合成データ・レジストリ・manifest
- Dropbox＝論文PDF・PLATEAU/OSM原本・現地写真・LiDAR・提出ZIP（`05_RELEASES/`）
- 受け渡しは`inputs/staging/<TASK-ID>/`へ必要分だけコピー（`inputs/staging/README.md`が契約）
- リリース時のみ：テストが通った版にタグ→zip＋RELEASE_MANIFEST.jsonを`05_RELEASES/vX.Y.Z-…/`へ

## 6. 注意

- `config/paths.example.toml`を`config/paths.local.toml`にコピーして自分のDropboxパスを設定（local側はGit管理外）
- レイアウト注：現行は`data/`＝合成デモデータ。推奨構成の`data/demo_synthetic/`への改名は`task/repo-layout`として別途行う（baselineでは動作安定を優先し未実施）
