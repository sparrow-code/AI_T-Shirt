import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

console.log("Using JavaScript conf");
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      "/api": "https://poodle-feasible-sadly.ngrok-free.app",
      "/images": "https://poodle-feasible-sadly.ngrok-free.app",
    },
  },
  preview: {
    port: 3000,
    host: true,
  },
  build: {
    outDir: "dist",
    assetsDir: "assets",
    sourcemap: false,
    minify: "terser",
    target: "es2015",
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
