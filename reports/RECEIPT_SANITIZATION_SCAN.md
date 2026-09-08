# Receipt sanitization scan（2026-09-03）

結果: **CLEAN**

- Git 追跡ファイル 528 件を走査（パターン: X-Amz-Credential / X-Amz-Security-Token / X-Amz-Signature / X-Amz-Algorithm / X-Amz-Date / X-Amz-Expires / X-Amz-SignedHeaders / response-content-disposition / signature= / access_token= / ASIA…）。allowlist 外のヒット: 0 件（`tests/realdata/test_plateau_building_evidence.py:108` は既存 guard テストの正規表現リテラルで、資格情報ではない）。allowlist（フェイク値のみを含む）: docs/operations/RECEIPT_SANITIZATION.md, tests/tools/test_sanitize_receipt.py, tools/sanitize_receipt.py。
- ブランチ b64b5d0..HEAD の全 blob を走査: allowlist 外ヒット 0 件 → bundle にも含まれない。
- handoff 出力（`claude-takeover-audit-20260903/` のコンテナ側コピー）: ヒット 0 件。
- 元 receipt `receipt-mlit_walkspace_kyoto_h23.json`（Git 外）は **未変更**（SHA-256 6fe66de1…、sanitizer 実行前後で同一）。派生 `receipt-mlit_walkspace_kyoto_h23.sanitized.json` を生成済み: presigned query 8 キーを除去、トークン文字列なし、`sha256`／`byte_size`／`integrity` は保持。
- PLATEAU の 2 receipt（京都・藤沢 CityGML）には presigned query は含まれていなかった。
- 共有ポリシー: staging／bundle／push／report に添付できるのは `*.sanitized.json` のみ（`docs/operations/RECEIPT_SANITIZATION.md`）。
