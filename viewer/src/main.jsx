import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App.jsx";
import { initializeSentry } from "./observability/sentry.js";
import "./styles.css";

globalThis.CESIUM_BASE_URL = "./cesium/";

void initializeSentry().catch(() => {});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
