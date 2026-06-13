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
      link: [{ rel: "icon", href: "/favicon-light.png", type: "image/png" }],
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
        process.env.NODE_ENV === "development" &&
        !process.env.NUXT_PUBLIC_BACKEND_URL
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
        "@internationalized/date",
        "@nuxt/ui > prosemirror-gapcursor",
        "@nuxt/ui > prosemirror-model",
        "@nuxt/ui > prosemirror-state",
        "@nuxt/ui > prosemirror-tables",
        "@nuxt/ui > prosemirror-transform",
        "@nuxt/ui > prosemirror-view",
        "@shikijs/core",
        "@shikijs/engine-javascript",
        "@shikijs/langs/bash",
        "@shikijs/langs/batch",
        "@shikijs/langs/c",
        "@shikijs/langs/cmd",
        "@shikijs/langs/cpp",
        "@shikijs/langs/csharp",
        "@shikijs/langs/css",
        "@shikijs/langs/dart",
        "@shikijs/langs/diff",
        "@shikijs/langs/dockerfile",
        "@shikijs/langs/erlang",
        "@shikijs/langs/go",
        "@shikijs/langs/graphql",
        "@shikijs/langs/groovy",
        "@shikijs/langs/html",
        "@shikijs/langs/http",
        "@shikijs/langs/java",
        "@shikijs/langs/javascript",
        "@shikijs/langs/json",
        "@shikijs/langs/jsx",
        "@shikijs/langs/kotlin",
        "@shikijs/langs/lua",
        "@shikijs/langs/makefile",
        "@shikijs/langs/markdown",
        "@shikijs/langs/mermaid",
        "@shikijs/langs/nginx",
        "@shikijs/langs/perl",
        "@shikijs/langs/php",
        "@shikijs/langs/powershell",
        "@shikijs/langs/python",
        "@shikijs/langs/r",
        "@shikijs/langs/ruby",
        "@shikijs/langs/rust",
        "@shikijs/langs/scala",
        "@shikijs/langs/shellscript",
        "@shikijs/langs/sql",
        "@shikijs/langs/swift",
        "@shikijs/langs/toml",
        "@shikijs/langs/tsx",
        "@shikijs/langs/typescript",
        "@shikijs/langs/xml",
        "@shikijs/langs/yaml",
        "@shikijs/langs/zsh",
        "@shikijs/themes/github-dark",
        "@shikijs/themes/github-light",
        "@tiptap/core",
        "@tiptap/extension-emoji",
        "@tiptap/extension-list/task-item",
        "@tiptap/extension-list/task-list",
        "@tiptap/extension-table",
        "@tiptap/pm/tables",
        "@tiptap/vue-3",
        "@unovis/ts",
        "@unovis/ts/maps",
        "@unovis/vue",
        "@vue/devtools-core",
        "@vue/devtools-kit",
        "@vueuse/core",
        "jwt-decode",
        "vue-qrcode-reader",
        "zod",
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
