# Security and trust-boundary report

Status: **PASS with external-write degradation** (`GITHUB_PUSH_BLOCKED`).

## Boundary applied

- Web pages, PDFs, source comments, GitHub content, OSM tags, filenames, manifests, and API errors were treated as untrusted data.
- No instruction embedded in external content was executed or allowed to override repository contracts.
- No `curl | sh`, `iex`, unsigned installer, downloaded executable, or elevated OS-package installation was used.
- No external repository was cloned and no external source code was copied into the product.
- Official and VGI records were retained as metadata-only. No downloaded geometry was promoted to `REAL`.
- Runtime state and logs exclude credentials. The repository-external Python environment is not a release input.

## Scans

- `scripts/overnight/verify_repository.py --root .`: PASS after resolving one scanner self-fixture collision.
- The collision was in `tests/cities/test_fujisawa_pack.py`, whose prohibited-token fixture contained the same local-path tokens the lexical scanner detects. The two tokens are now assembled at test runtime; the values, search scope, and assertion are unchanged. LUNA and TERA independently rated the fix Critical 0 / High 0 / Medium 0.
- Tracked large/raw extension check: PASS.
- Credential-pattern check: PASS.
- Local absolute-path check: PASS.
- Viewer unsafe-claim checks: PASS in unit and E2E tests.

## External writes

GitHub CLI was present but not authenticated, and push was blocked by the execution safety review. No retry, credential request, or bypass was attempted. The local branch and review packet are complete; see `reports/PR_READY.md`.

## Downloads and archives

City manifests contain metadata records only (`download_status=METADATA_ONLY`). No external ZIP/PDF/GeoJSON payload was committed or extracted. The UTF-8-safe release builder and its path/checksum/extraction guards are reviewed. The final release ZIP is built and extraction-tested only after the final local commit; its outcome and SHA-256 belong to the human handoff, not this pre-build report snapshot.
