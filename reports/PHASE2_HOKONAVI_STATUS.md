# Phase 2 Hokonavi adapter status

`HOKONAVI_ADAPTER_PROTOTYPE=false`

`HOKONAVI_PRODUCTION_ADAPTER=false`

`HOKONAVI_OFFICIAL_CERTIFICATION=false`

The existing mapping contract and synthetic reference fixtures remain available,
but no new production adapter is integrated in this checkpoint. An isolated
prototype reached green fixture tests, then independent review found that it
could silently lose `maint_date` and some missing/code-99 distinctions, and that
its arbitrary sidecar mapping did not enforce the `SOURCE_FACT` /
`ABLEPATH_DESIGN` boundary.

The hard-deadline checkpoint therefore excludes that implementation rather than
weakening the mapping contract or shipping a false round-trip claim. A retry
requires exact internal and sidecar schemas, preservation or explicit rejection
of every bidirectional/source field, original-source round-trip mutation tests,
and a fresh independent review.

This is not official Hokonavi compatibility, certification, or administrative
validation. No real ministry network dataset was converted.
