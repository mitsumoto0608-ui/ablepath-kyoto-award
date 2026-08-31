# Opt-in Sentry error-context pilot

This is an errors-only browser pilot using the official `@sentry/react` `10.72.0` SDK. It is not a Sentry server, telemetry backend, replay service, tracing deployment, or source-map upload implementation.

`viewer/src/observability/sentry.js` dynamically imports the SDK only when `VITE_SENTRY_DSN` is non-empty. With no DSN it returns without loading the SDK, sending a request, or affecting application startup. `.env.example` intentionally contains an empty value; no DSN, token, organization, or project belongs in Git.

With a DSN, default integrations are disabled and the global error handler is the only integration. `sendDefaultPii=false`, breadcrumbs are disabled/dropped, tracing/profile/replay sample rates are zero, and logs, metrics, and client reports are disabled. The explicit current data-collection settings (`userInfo`, `cookies`, `httpHeaders`, `httpBodies`, `urlQueryParams`, `graphQL.document/variables`, `databaseQueryData`, `genAI.inputs/outputs`, `stackFrameVariables`, and `frameContextLines`) are all off. `beforeSend` is a strict allowlist: only format-constrained controlled event metadata and numeric stack-frame line/column plus `in_app` can remain; all exception, mechanism, filename, module, function, message/logentry/user/request/contexts/extra/tags/breadcrumbs, and arbitrary fields are dropped. Thus no query, absolute/Dropbox path, coordinate variant, secret-like value, PII, or free text can survive a frame.

The only intended debugging context is release/environment and a sanitized stack trace. City, renderer, dataset/revision, and scenario identifiers may be added only after a human confirms each value is a non-PII controlled identifier. Source-map upload needs a separate human gate with organization, project, and `SENTRY_AUTH_TOKEN`; this pilot does not implement it.

Official references: [Sentry JavaScript configuration](https://docs.sentry.io/platforms/javascript/configuration/options/) and [React installation](https://docs.sentry.io/platforms/javascript/guides/react/).
