# Draft PR and hosted gate handoff

- Draft PR: https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/pull/1
- Base/head: `main` <- `integration/overnight-multicity-20260830`
- Hosted pull-request run: https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/actions/runs/33293555725
- Hosted-verified product HEAD: `f421693c3a5b931e48617b15287f6d1ca90ef2f7`
- Jobs: Python 3.12 / Linux `SUCCESS`; Python 3.12 / Windows newline smoke `SUCCESS`; Static viewer / Node 22 `SUCCESS`.
- `MAIN_MERGED=false`; the PR remains draft, auto-merge is disabled, and it has not been made ready for review.

The initial hosted runs at `4abb477cc44655f2b780fb794d506d90b3abe15c` exposed a Linux-only 320 CSS-pixel reflow failure: `scrollWidth=322` with `clientWidth=320`. The failure fingerprint is `PLAYWRIGHT_UBUNTU_320_REFLOW_SKIP_MAP_LINK_MIN_CONTENT_2PX_OVERFLOW`, classified as platform-triggered UI code. The targeted repair places the second skip link at the existing mobile inset without weakening the test, label, keyboard navigation, focus treatment, or safety/data contracts.

The report-only commit containing this handoff must itself pass the same pull-request Hosted Actions workflow. PR target remains `main`; do not merge until the human gates in `reports/KNOWN_GAPS.md` are explicitly approved. Do not move `v0.2.0-baseline`.
