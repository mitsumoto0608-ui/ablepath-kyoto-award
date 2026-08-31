# Sentry pilot status

Status: `IMPLEMENTED_OPT_IN_NOT_CONFIGURED`.

Tools used: official `@sentry/react` `10.72.0` SDK and local unit tests. With no `VITE_SENTRY_DSN`, the SDK is not imported and no telemetry is initialized. With a DSN, `beforeSend` produces only format-constrained metadata and numeric stack structure; exception/mechanism strings, filename/module/function, message/logentry/user/request/contexts/extra/tags/breadcrumbs, and arbitrary event fields are dropped. PII defaults, breadcrumbs, tracing, `profileSessionSampleRate`, both replay sample rates, logs, metrics, client reports, and current data-collection categories (`userInfo`, `cookies`, `httpHeaders`, `httpBodies`, `urlQueryParams`, `graphQL.document/variables`, `databaseQueryData`, `genAI.inputs/outputs`, stack-frame variables, context lines) are disabled; secret-like keys/values, all path/query variants, and coordinates do not survive.

Source-map upload, Sentry MCP credentials, organization/project selection, and adding controlled domain tags are human gates. Accepted artifact is reversible by removing this feature branch. No DSN/token/API key is tracked. Retries/human corrections: a prebuild-generated map artifact mutation was restored; parent review required the strict allowlist and restored repository-policy detail.
