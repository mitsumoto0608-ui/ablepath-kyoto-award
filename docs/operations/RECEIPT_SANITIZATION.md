# receipt 無害化手順（署名付きURLの除去）

生ダウンロードの receipt（`ablepath-raw/.../receipts/receipt-<dataset_id>.json`）には、
S3 の presigned クエリ（`X-Amz-Signature` 等）が残ることがある。これは一時的とはいえ
credential であり、共有・同梱・push の前に必ず落とす。

## 実行

```
python -m tools.sanitize_receipt <path>/receipt-<dataset_id>.json
```

- 既定の出力は同じディレクトリの `receipt-<dataset_id>.sanitized.json`。
- 出力先を変えるなら `--out <path>`。既存ファイルの上書きは `--force` が必要。
- 入力と同じパスを `--out` に渡した場合は非ゼロ終了で拒否する。

## ポリシー

- 原本 receipt は絶対に書き換えない。ツールも読み取りしかしない。
- 共有・バンドル・push してよいのは `.sanitized.json` のみ。原本は raw 領域に留める。
- クレデンシャル的クエリを含む URL はクエリとフラグメントを丸ごと削除する（部分削除はしない）。
  scheme/host/path は残るので、CKAN の resource UUID やファイル名は追跡できる。
- `Authorization` / `Cookie` / `Set-Cookie` / `X-Amz-Security-Token` ヘッダは値を `REDACTED` にする。
- 削除したのはキー名のみ記録し、値はどこにも残さない。

## 検証

派生 receipt の `sha256` / `byte_size` / `integrity` は原本と同一であること（ダウンロード物の
同一性はここで担保される）。加えて `sanitization.source_receipt_sha256` が原本ファイル
そのもののハッシュと一致することを確認する:

```
shasum -a 256 <path>/receipt-<dataset_id>.json
```
