import { defineConfig } from "vite";

export default defineConfig({
  root: "site-static",
  base: "/deliverycourt-genlayer/",
  build: { outDir: "../pages-dist", emptyOutDir: true },
});
