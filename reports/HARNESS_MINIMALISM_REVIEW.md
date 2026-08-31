# Harness minimalism review

Context sources: Phase 3 combined routing brief, explicit-routing addendum, `AGENTS.md`, and the repository viewer. Policy: `minimal-harness-v1`.

Accepted artifact: one short agent map, one detailed operations page, one Sentry production module, and one optional CodeGraph baseline script. Rejected as unnecessary: an agent framework, new provider/context/hook layers, custom telemetry backend, Sentry self-hosting, CodeGraph runtime/CI dependency, vendor/submodule, Docker requirement, and a persistent graph service.

Test budget: two Sentry tests cover the DSN-enabled strict allowlist/stack path and the disabled absent-DSN path. The governance test guards the short map plus retained safety anchors. Rollback point: discard `task/minimal-harness-observability-v1`. Human corrections/retries: a generated-map mutation was restored; parent review tightened the privacy contract and restored detailed repository rules. Human gate: review privacy scrubbing and any future source-map or MCP credential setup.
