const SAFE_METADATA = {
  event_id: /^[a-f0-9]{32}$/i,
  timestamp: /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/,
  platform: /^(?:javascript|node|python)$/,
  level: /^(?:fatal|error|warning|info|debug)$/,
  release: /^[A-Za-z0-9._-]{1,100}$/,
  environment: /^[A-Za-z0-9._-]{1,64}$/,
};

function safeNumber(value) {
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

function sanitizeFrame(frame) {
  const cleaned = {};
  const lineno = safeNumber(frame?.lineno);
  const colno = safeNumber(frame?.colno);
  if (lineno !== undefined) cleaned.lineno = lineno;
  if (colno !== undefined) cleaned.colno = colno;
  if (typeof frame?.in_app === "boolean") cleaned.in_app = frame.in_app;
  return cleaned;
}

function sanitizeException(value) {
  const frames = Array.isArray(value?.stacktrace?.frames)
    ? value.stacktrace.frames.map(sanitizeFrame).filter((frame) => Object.keys(frame).length)
    : [];
  return frames.length ? { stacktrace: { frames } } : {};
}

export function scrubSentryBreadcrumb() {
  return null;
}

export function scrubSentryEvent(event) {
  const cleaned = {};
  for (const [field, pattern] of Object.entries(SAFE_METADATA)) {
    const value = event?.[field];
    if (typeof value === "string" && pattern.test(value)) cleaned[field] = value;
  }
  const values = Array.isArray(event?.exception?.values)
    ? event.exception.values.map(sanitizeException).filter((value) => Object.keys(value).length)
    : [];
  if (values.length) cleaned.exception = { values };
  return cleaned;
}

export async function initializeSentry({ dsn = import.meta.env.VITE_SENTRY_DSN, loadSdk = () => import("@sentry/react") } = {}) {
  if (!dsn) return false;
  const Sentry = await loadSdk();
  Sentry.init({
    dsn,
    sendDefaultPii: false,
    defaultIntegrations: false,
    integrations: [Sentry.globalHandlersIntegration()],
    maxBreadcrumbs: 0,
    tracesSampleRate: 0,
    profilesSampleRate: 0,
    profileSessionSampleRate: 0,
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate: 0,
    enableLogs: false,
    enableMetrics: false,
    sendClientReports: false,
    dataCollection: {
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
    },
    beforeSend: scrubSentryEvent,
    beforeBreadcrumb: scrubSentryBreadcrumb,
  });
  return true;
}
