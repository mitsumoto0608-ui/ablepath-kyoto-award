import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { cpSync, existsSync, readFileSync, statSync } from "node:fs";
import { extname, resolve, sep } from "node:path";

const CESIUM_BUILD_ROOT = resolve("node_modules/cesium/Build/Cesium");
const CESIUM_RUNTIME_DIRS = ["Assets", "ThirdParty", "Widgets", "Workers"];

function contentType(path) {
  return ({
    ".css": "text/css; charset=utf-8",
    ".gif": "image/gif",
    ".glsl": "text/plain; charset=utf-8",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".wasm": "application/wasm",
    ".webp": "image/webp",
    ".xml": "application/xml; charset=utf-8",
  })[extname(path).toLowerCase()] ?? "application/octet-stream";
}

function cesiumRuntimeAssets() {
  return {
    name: "ablepath-cesium-runtime-assets",
    configureServer(server) {
      server.middlewares.use("/cesium", (request, response, next) => {
        const relative = decodeURIComponent((request.url ?? "/").split("?")[0]).replace(/^\/+/, "");
        const requested = resolve(CESIUM_BUILD_ROOT, relative);
        if (!requested.startsWith(`${CESIUM_BUILD_ROOT}${sep}`) || !existsSync(requested) || !statSync(requested).isFile()) {
          next();
          return;
        }
        response.statusCode = 200;
        response.setHeader("Content-Type", contentType(requested));
        response.end(readFileSync(requested));
      });
    },
    closeBundle() {
      const outputRoot = resolve("dist/cesium");
      for (const directory of CESIUM_RUNTIME_DIRS) {
        cpSync(resolve(CESIUM_BUILD_ROOT, directory), resolve(outputRoot, directory), { recursive: true });
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), cesiumRuntimeAssets()],
  base: "./",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: true,
  },
});
