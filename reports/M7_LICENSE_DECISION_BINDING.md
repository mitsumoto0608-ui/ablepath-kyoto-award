# License decision binding（scope 別 machine truth）

**Historical record only.** This pre-decision receipt remains unchanged in meaning and is not runtime authority. The current authority is `reports/F1_F6_DECISION_BINDING.json` with scope in `reports/LICENSE_FINAL_SCOPE_DECISION.json`; see `reports/DELIVERY_DECISION_BINDING_AUTHORITY.json`. `NOT_YET_MACHINE_BOUND` below is preserved as the historical state and must not override the current decision.

- `LICENSE_REVIEW_PROCESS_COMPLETE=true`（根拠: human direction 2026-09-03 (task pack CODEX_M7_AUTONOMOUS_RESEARCH_CONTRACT_CLOSURE_V2 §0): 「license最終確認は完了済み」）
- `LICENSE_DECISION_ARTIFACT_BINDING=NOT_YET_MACHINE_BOUND`（repo・ローカル root を探索したが、scope 別の最終 decision artifact は未発見。既存 `reports/LICENSE_DECISION.md` は 8/30 の選択肢提示で PUBLIC_DISTRIBUTION_AUTHORIZED=false のまま）
- `PUBLIC_REDISTRIBUTION_ALLOWED=false`（人間の一文から推測しない）

| scope | status | basis |
|---|---|---|
| private_internal_analysis | CONTINUE | human statement: review process complete; internal development continues |
| private_git_repository | CONTINUE | same; branch stays in private repo mitsumoto0608-ui/ablepath-kyoto-award |
| internal_rc | CONTINUE_INTERNAL_ONLY | deterministic internal RC allowed; not a public archive |
| public_git | NOT_AUTHORIZED | no explicit scope decision artifact; PUBLIC_DISTRIBUTION_AUTHORIZED=false remains |
| public_rc | NOT_AUTHORIZED | same |
| public_demo | NOT_AUTHORIZED | same |

最終 decision の置き場: `reports/LICENSE_FINAL_SCOPE_DECISION.json`（配置後に自動で MACHINE_BOUND へ）。一般論の license review は再開しない。法的結論は出していない。
