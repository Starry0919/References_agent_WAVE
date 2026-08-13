import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Frontend is built into ./dist and served by FastAPI as a same-origin SPA
// (see harness/server.py) so production never needs CORS. In dev, the
// backend has no CORS middleware either -> proxy /api and /ws so the Vite
// dev server on :5173 still talks same-origin to the real API on :8642.
const BACKEND_ORIGIN = process.env.VITE_BACKEND_ORIGIN ?? "http://127.0.0.1:8642";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": { target: BACKEND_ORIGIN, changeOrigin: true },
      "/ws": { target: BACKEND_ORIGIN, ws: true, changeOrigin: true },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: false,
  },
});
