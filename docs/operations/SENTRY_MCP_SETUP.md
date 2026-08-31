# Sentry MCP: documentation-only pilot

No Sentry MCP connection or configuration is emitted by this branch. Codex supports `enabled_tools` and per-tool approval, but the exact Sentry read-only tool names and scopes were not independently verified. A connection may be proposed only after that verification and an active Codex configuration prove a tool-level allowlist for selected read-only inspection operations. Candidate reads are issue/event/release inspection only. Issue close, assignment, triage, deletion, and any write operation remain a human gate.

Before any future setup, a human must approve OAuth/token scope and confirm rollback (disconnect/revoke token). Store credentials outside Git. If the platform cannot enforce selected read tools, do not connect MCP; use the normal Sentry UI with human-controlled access instead. Re-check the current Codex and official Sentry MCP syntax at the time of setup.

References: [Codex MCP documentation](https://developers.openai.com/codex/mcp) and [official Sentry MCP documentation](https://docs.sentry.io/product/sentry-mcp/).
