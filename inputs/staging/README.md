# inputs/staging/ — タスク別データ受け渡し契約

CodexはDropboxを見ない。人間（またはFable）がDropbox原本から**必要な分だけ**をタスク別フォルダへコピーして渡す。

```
inputs/staging/<TASK-ID>/
├─ <データファイル…>          # 小さな抜粋のみ（大容量原本は置かない）
├─ source_manifest.csv        # 由来行の抜粋: dataset_id,file_name,source_url,downloaded_at,sha256,license,crs,version,official_status,notes
└─ TASK_INPUT_README.md       # このタスクで使ってよい範囲・禁止事項
```

規則：manifestに無いファイルは使わない／manifestのsha256と一致しないファイルは使わない／ここに無いデータが必要なら実装せず「データ要求」として報告する。
