import { defineConfig } from "vite";

export default defineConfig({
  root: "site-static",
  base: "/quotecourt-genlayer/",
  build: { outDir: "../pages-dist", emptyOutDir: true },
});
