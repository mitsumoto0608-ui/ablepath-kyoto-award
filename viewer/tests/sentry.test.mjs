import test from "node:test";
import assert from "node:assert/strict";

import { initializeSentry, scrubSentryBreadcrumb } from "../src/observability/sentry.js";

test("[software_correctness] enabled Sentry keeps only allowlisted metadata and a sanitized stack", async () => {
  let options;
  const started = await initializeSentry({
    dsn: "https://public@example.ingest.sentry.io/1",
    loadSdk: async () => ({ globalHandlersIntegration: () => ({}), init: (value) => { options = value; } }),
  });
  const sanitized = options.beforeSend({
    event_id: "0123456789abcdef0123456789abcdef", release: "viewer-1", environment: "pilot", level: "error",
    message: "unstructured prose must never leave the browser", extra: { token: "supersecret", note: "confidential note" },
    user: { email: "person@example.com" }, breadcrumbs: [{ message: "confidential click text" }],
    exception: { values: [{ type: "MedicalRecord-12345", value: "confidential error message", mechanism: { type: "render?search=alice", handled: false }, stacktrace: { frames: [
      { filename: "C:\\Users\\name\\Dropbox\\app.js?token=supersecret", module: "/srv/private/customer-12345", function: "render?search=alice", lineno: 12, colno: 4, in_app: true },
      { filename: "34.9990_135.7815.js", lineno: 21, colno: 9, in_app: false },
    ] } }] },
  });
  const serialized = JSON.stringify(sanitized);

  assert.equal(started, true);
  assert.equal(options.sendDefaultPii, false);
  assert.equal(options.maxBreadcrumbs, 0);
  assert.equal(options.enableMetrics, false);
  assert.equal(options.profileSessionSampleRate, 0);
  assert.equal(options.replaysSessionSampleRate, 0);
  assert.equal(options.replaysOnErrorSampleRate, 0);
  assert.deepEqual(options.dataCollection, {
    userInfo: false,
    cookies: false,
    httpHeaders: { request: false, response: false },
    httpBodies: [],
    urlQueryParams: false,
    graphQL: { document: false, variables: false },
    databaseQueryData: false,
    genAI: { inputs: false, outputs: false },
    stackFrameVariables: false,
    frameContextLines: 0,
  });
  assert.equal(serialized.includes("supersecret"), false);
  assert.equal(serialized.includes("confidential"), false);
  assert.equal(serialized.includes("person@example.com"), false);
  for (const forbidden of ["MedicalRecord-12345", "/srv/private/customer-12345", "render?search=alice", "34.9990_135.7815.js"]) assert.equal(serialized.includes(forbidden), false);
  assert.deepEqual(sanitized.exception.values[0].stacktrace.frames[0], { lineno: 12, colno: 4, in_app: true });
  assert.equal(options.beforeBreadcrumb({ message: "anything" }), null);
  assert.equal(scrubSentryBreadcrumb(), null);
});

test("[software_correctness] a missing DSN leaves the Sentry SDK disabled and unloaded", async () => {
  let loaded = false;
  const started = await initializeSentry({ dsn: "", loadSdk: async () => { loaded = true; throw new Error("must not load"); } });
  assert.equal(started, false);
  assert.equal(loaded, false);
});
