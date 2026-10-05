import { isTauri } from "@tauri-apps/api/core";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./App.css";

function blockBrowserAccess(): void {
  document.head.innerHTML = "<title>404 Not Found</title>";
  document.body.innerHTML = "";
  document.documentElement.style.background = "#fff";
  const root = document.getElementById("root");
  if (root) root.innerHTML = "";
}

function disableNativeBrowserMenus(): void {
  document.addEventListener("contextmenu", (e) => e.preventDefault(), true);
  document.addEventListener(
    "keydown",
    (e) => {
      const key = e.key.toLowerCase();
      if (key === "f12") e.preventDefault();
      if (e.ctrlKey && e.shiftKey && (key === "i" || key === "j" || key === "c")) {
        e.preventDefault();
      }
    },
    true,
  );
}

export async function bootstrap(): Promise<void> {
  let allowed = false;

  try {
    allowed = await isTauri();
  } catch {
    allowed = false;
  }

  if (!allowed) {
    blockBrowserAccess();
    return;
  }

  disableNativeBrowserMenus();

  ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}
