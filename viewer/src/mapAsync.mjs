export function withTimeout(promise, timeoutMs, message = "operation timed out") {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(message)), timeoutMs);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

function failureMessage(args, fallback) {
  for (const value of [...args].reverse()) {
    if (value instanceof Error && value.message) return value.message;
    if (typeof value?.message === "string" && value.message) return value.message;
    if (typeof value?.url === "string" && value.url) return `${fallback}: ${value.url}`;
  }
  return fallback;
}

export function installCesiumFailureListeners({ tileset, scene, onFailure }) {
  let failed = false;
  const failOnce = (...args) => {
    if (failed) return;
    failed = true;
    onFailure(failureMessage(args, "PLATEAU tile/renderの読込に失敗しました"));
  };
  const tileFailure = (...args) => failOnce(...args);
  const renderFailure = (...args) => failOnce(...args);
  tileset?.tileFailed?.addEventListener(tileFailure);
  scene?.renderError?.addEventListener(renderFailure);
  return {
    hasFailed: () => failed,
    remove: () => {
      tileset?.tileFailed?.removeEventListener(tileFailure);
      scene?.renderError?.removeEventListener(renderFailure);
    },
  };
}
