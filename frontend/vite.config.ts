import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// T-016 (ASR-014): React + TypeScript + Vite.
// Build output lands in the package's static dir so `sdv-sim serve` can serve
// the SPA from a single process (ASR-019, T-020 packages it into the wheel).
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../sdv_sim/server/static",
    emptyOutDir: true,
  },
  server: {
    // `--dev` mode: the API server (127.0.0.1:8888 by default) proxies to this
    // Vite dev server. Port stays fixed for the known proxy target; the CLI
    // --port option configures the API server, not the Vite dev server.
    port: 5173,
    strictPort: true,
  },
});
