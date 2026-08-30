# Security and trust-boundary report

Status: **PASS for the pre-governance-sync source commit**. GitHub authentication/push is available; draft PR #1 is open, auto-merge is disabled, and `main` is unchanged.

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

Current state: GitHub CLI is authenticated as `mitsumoto0608-ui`, branch updates are pushed, and draft PR #1 targets `main`. Hosted run `33296626023` succeeded for pre-governance-sync commit `aa957e3a024561022e939b4b00579251c9062a42` across Linux Python, Windows Python, and static viewer/Node jobs. The governance-sync commit must receive its own successful Hosted run before handoff. Auto-merge is off and no merge to `main` has occurred.

Historical state: an earlier report snapshot recorded `GITHUB_PUSH_BLOCKED` while GitHub CLI was unauthenticated. That was accurate for the earlier snapshot but is no longer the active condition. No token is stored or printed by these reports.

## Downloads and archives

City manifests contain metadata records only (`download_status=METADATA_ONLY`). No external ZIP/PDF/GeoJSON payload was committed or extracted. The UTF-8-safe release builder uses Git `HEAD` blobs for tracked files and rejects dirty or ambiguous Git state.

In a Git checkout, RC tests also obtain their seed bytes from the resolved `HEAD` commit. In an extracted non-Git RC, tests require `RELEASE_MANIFEST.json` and `SHA256SUMS.txt`, verify payload membership, duplicate/path safety, the checksum file's special-member hash, and each required local payload's byte count and SHA-256 before using it. Missing or inconsistent metadata fails closed. These archive-internal records provide integrity consistency, not authenticity against coordinated tampering; the externally reported final ZIP SHA-256 is the trust anchor. The final archive outcome and SHA-256 are recorded in the human handoff after the final commit and Hosted gate.
