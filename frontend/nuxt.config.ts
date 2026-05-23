// https://nuxt.com/docs/api/configuration/nuxt-config
import { resolve } from "path";
import type { NuxtPage } from "nuxt/schema";
import { isPublicRoute } from "./app/utils/routes";

function setMiddleware(nuxtPages: NuxtPage[]) {
  for (const page of nuxtPages) {
    page.meta ||= {};
    page.meta.middleware = [isPublicRoute(page.name) ? "public" : "private"];
    if (page.children) {
      setMiddleware(page.children);
    }
  }
}

export default defineNuxtConfig({
  modules: ["@nuxt/eslint", "@nuxt/ui", "@pinia/nuxt", "nuxt-qrcode"],

  devtools: {
    enabled: process.env.NODE_ENV === "development",
  },

  app: {
    head: {
      script: [
        {
          defer: true,
          src: "https://cloud.umami.is/script.js",
          "data-website-id": "f765ec70-c85e-499b-a75f-93744bdcabef",
        },
      ],
    },
  },

  css: ["~/assets/css/main.css"],

  ui: {
    theme: {
      colors: [
        "primary",
        "secondary",
        "info",
        "success",
        "warning",
        "neutral",
        "error",
        "orange",
        "amber",
      ],
    },
  },

  runtimeConfig: {
    public: {
      backendUrl: "",
      backendRootPath: "",
    },
  },

  routeRules: {
    "/login": { prerender: true },
    "/signup": { prerender: true },
    "/mfa": { prerender: true },
    "/reset-password": { prerender: true },
    "/**": { ssr: false },
  },

  compatibilityDate: "2025-01-15",

  vite: {
    build: {
      chunkSizeWarningLimit: 1200,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (
              id.includes("/node_modules/@unovis/") ||
              id.includes("/node_modules/d3/") ||
              id.includes("/node_modules/d3-")
            ) {
              return "vendor-charts";
            }
            if (
              id.includes("/node_modules/@tiptap/") ||
              id.includes("/node_modules/prosemirror-") ||
              id.includes("/node_modules/yjs/") ||
              id.includes("/node_modules/y-protocols/")
            ) {
              return "vendor-editor";
            }
          },
        },
      },
    },
    resolve: {
      alias: {
        shiki: resolve(__dirname, "app/lib/shiki-rekono.ts"),
      },
      dedupe: [
        "prosemirror-state",
        "prosemirror-tables",
        "prosemirror-model",
        "prosemirror-view",
        "prosemirror-transform",
      ],
    },
    server: {
      proxy:
        process.env.NODE_ENV === "development"
          ? {
              "^/api/(?!_nuxt_icon/).*": {
                target: "http://127.0.0.1:8000",
                changeOrigin: true,
              },
            }
          : {},
    },
    optimizeDeps: {
      exclude: ["tiptap-extension-code-block-shiki"],
      include: [
        "@nuxt/ui > prosemirror-state",
        "@nuxt/ui > prosemirror-tables",
        "@nuxt/ui > prosemirror-transform",
        "@nuxt/ui > prosemirror-model",
        "@nuxt/ui > prosemirror-view",
        "@nuxt/ui > prosemirror-gapcursor",
      ],
    },
  },

  hooks: {
    "pages:extend"(pages) {
      setMiddleware(pages);
    },
  },

  eslint: {
    config: {
      stylistic: {
        commaDangle: "never",
        braceStyle: "1tbs",
      },
    },
  },
});
