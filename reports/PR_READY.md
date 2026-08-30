# Draft PR and hosted gate handoff

- Draft PR: https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/pull/1
- Base/head: `main` <- `integration/overnight-multicity-20260830`
- Hosted pull-request run: https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/actions/runs/33296386535
- Hosted-verified product HEAD: `96b78af91af3d0b8ab693caf15f1908dd4a82d56`
- Jobs: Python 3.12 / Linux `SUCCESS`; Python 3.12 / Windows newline smoke `SUCCESS`; Static viewer / Node 22 `SUCCESS`.
- `MAIN_MERGED=false`; the PR remains draft, auto-merge is disabled, and it has not been made ready for review.

The Hosted Ubuntu runs exposed a Linux-only 320 CSS-pixel reflow failure: `scrollWidth=322` with `clientWidth=320`. Trace evidence ruled out the skip links (`right=132` and `right=252`) and identified the responsive CSS Grid track and horizontal map toolbar retaining min-content width. Three bounded automatic repair attempts did not remove the fingerprint. One additional human-authorized repair changed the single-column track to `minmax(0, 1fr)`, allowed the grid items to shrink, and stacked/wrapped the mobile toolbar. The final 320px local diagnostic was `document clientWidth=320, scrollWidth=320`; the workspace, map column, map shell, toolbar, and evidence panel all remained within `right<=304` with no internal overflow. The assertions, labels, focus behavior, keyboard targets, and safety/data contracts were not weakened.

The report-only commit containing this handoff must itself pass the same pull-request Hosted Actions workflow. PR target remains `main`; do not merge until the human gates in `reports/KNOWN_GAPS.md` are explicitly approved. Do not move `v0.2.0-baseline`.
