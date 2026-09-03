# -*- coding: utf-8 -*-
"""[software_correctness] receipt 無害化ツールの契約。

署名付きURLが1本でも残ると、共有した瞬間に一時credentialが外に出る。
「クエリ全落とし」「原本不変」「冪等」の3点を固定する。
"""
import json
import subprocess
import sys
from pathlib import Path

from tools.sanitize_receipt import sanitize_receipt, sanitize_url

REPO_ROOT = Path(__file__).resolve().parents[2]

FAKE_PRESIGNED = (
    "https://ckan-storage.s3.amazonaws.com/ckan/resources/"
    "51247b97-0000-4000-8000-000000000000/08.zip"
    "?response-content-disposition=attachment%3B%20filename%3D08.zip"
    "&X-Amz-Algorithm=AWS4-HMAC-SHA256"
    "&X-Amz-Credential=ASIAEXAMPLEKEY%2F20260831%2Fus-east-1%2Fs3%2Faws4_request"
    "&X-Amz-Date=20260831T185243Z&X-Amz-Expires=3600"
    "&X-Amz-SignedHeaders=host"
    "&X-Amz-Security-Token=EXAMPLETOKEN"
    "&X-Amz-Signature=EXAMPLESIGNATURE#frag"
)
CLEAN_PRESIGNED = (
    "https://ckan-storage.s3.amazonaws.com/ckan/resources/"
    "51247b97-0000-4000-8000-000000000000/08.zip"
)
LANDING = (
    "https://www.geospatial.jp/ckan/dataset/12fed482-0000-4000-8000-000000000000"
    "/resource/51247b97-0000-4000-8000-000000000000/download/08.zip"
)
FIXED_AT = "2026-09-03T00:00:00Z"


def _receipt():
    return {
        "receipt_schema_version": "1.0.0",
        "raw_receipt_id": "receipt-mlit_walkspace_kyoto_h23",
        "dataset_id": "mlit_walkspace_kyoto_h23",
        "status": "DOWNLOADED",
        "requested_url": LANDING,
        "final_url_sanitized": FAKE_PRESIGNED,
        "redirect_chain": [LANDING, FAKE_PRESIGNED],
        "http_status": 200,
        "headers": {
            "Location": FAKE_PRESIGNED,
            "ETag": '"abc123"',
            "Authorization": "AWS4-HMAC-SHA256 Credential=ASIAEXAMPLEKEY",
            "Cookie": "session=EXAMPLETOKEN",
        },
        "accessed_at": "2026-08-31T18:52:42Z",
        "original_filename": "08.zip",
        "byte_size": 62079,
        "sha256": "7140bf6d" + "0" * 56,
        "integrity": {"algorithm": "sha256", "verified": True},
    }


def test_presigned_query_and_fragment_are_removed():
    """[software_correctness] 署名付きURLはクエリとフラグメントごと落ちる。"""
    cleaned, removed = sanitize_url(FAKE_PRESIGNED)
    assert cleaned == CLEAN_PRESIGNED
    assert "?" not in cleaned and "#" not in cleaned
    assert "51247b97-0000-4000-8000-000000000000" in cleaned
    assert cleaned.endswith("/08.zip")
    assert "X-Amz-Signature" in removed
    assert "X-Amz-Security-Token" in removed
    assert "X-Amz-Credential" in removed


def test_harmless_query_is_untouched():
    """[software_correctness] 無害なクエリは保持する。"""
    url = "https://example.jp/list?page=2&sort=name"
    cleaned, removed = sanitize_url(url)
    assert cleaned == url
    assert removed == []


def test_nested_urls_and_headers_are_sanitized():
    """[software_correctness] headers/redirect_chain も再帰的に処理される。"""
    out = sanitize_receipt(_receipt(), sanitized_at=FIXED_AT)
    assert out["final_url_sanitized"] == CLEAN_PRESIGNED
    assert out["requested_url"] == LANDING
    assert out["redirect_chain"] == [LANDING, CLEAN_PRESIGNED]
    assert out["headers"]["Location"] == CLEAN_PRESIGNED
    assert out["headers"]["Authorization"] == "REDACTED"
    assert out["headers"]["Cookie"] == "REDACTED"
    assert out["headers"]["ETag"] == '"abc123"'
    assert out["sanitization"]["redacted_header_keys"] == ["Authorization", "Cookie"]
    assert out["sanitization"]["derived_from_receipt_id"] == (
        "receipt-mlit_walkspace_kyoto_h23"
    )


def test_non_url_fields_are_identical():
    """[software_correctness] 完全性フィールドは一切変更しない。"""
    src = _receipt()
    out = sanitize_receipt(src, sanitized_at=FIXED_AT)
    for field in ("sha256", "byte_size", "integrity", "accessed_at",
                  "original_filename", "http_status", "dataset_id"):
        assert out[field] == src[field]


def test_idempotent():
    """[software_correctness] 無害化済みを再処理しても変化しない。"""
    once = sanitize_receipt(_receipt(), source_sha256="deadbeef", sanitized_at=FIXED_AT)
    twice = sanitize_receipt(once, sanitized_at=FIXED_AT)
    assert twice == once


def _run_cli(*args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "tools.sanitize_receipt", *args],
        cwd=str(cwd), capture_output=True, text=True,
    )


def test_cli_refuses_to_overwrite_input_or_existing_output(tmp_path):
    """[software_correctness] 原本上書きと既存出力の無断上書きを拒む。"""
    src = tmp_path / "receipt-x.json"
    src.write_text(json.dumps(_receipt()), encoding="utf-8")
    before = src.read_bytes()

    same = _run_cli(str(src), "--out", str(src), cwd=REPO_ROOT)
    assert same.returncode != 0
    assert src.read_bytes() == before

    ok = _run_cli(str(src), cwd=REPO_ROOT)
    assert ok.returncode == 0
    out = tmp_path / "receipt-x.sanitized.json"
    assert out.is_file()
    assert src.read_bytes() == before

    again = _run_cli(str(src), cwd=REPO_ROOT)
    assert again.returncode != 0
    forced = _run_cli(str(src), "--force", cwd=REPO_ROOT)
    assert forced.returncode == 0


def test_no_credential_substrings_in_output(tmp_path):
    """[software_correctness] 出力テキストに署名系キー名/値が残らない。"""
    src = tmp_path / "receipt-y.json"
    src.write_text(json.dumps(_receipt()), encoding="utf-8")
    proc = _run_cli(str(src), cwd=REPO_ROOT)
    assert proc.returncode == 0
    text = (tmp_path / "receipt-y.sanitized.json").read_text(encoding="utf-8")
    body = json.loads(text)
    body.pop("sanitization")
    body_text = json.dumps(body, ensure_ascii=False)
    for needle in ("X-Amz-Security-Token", "X-Amz-Signature", "X-Amz-Credential",
                   "EXAMPLETOKEN", "EXAMPLESIGNATURE", "ASIAEXAMPLEKEY"):
        assert needle not in body_text
    assert text.endswith("\n")
    assert "\r" not in text
