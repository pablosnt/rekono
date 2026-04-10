// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ["@nuxt/eslint", "@nuxt/ui", "@pinia/nuxt", "nuxt-qrcode"],

  devtools: {
    enabled: process.env.NODE_ENV === "development",
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
        "error",
        "orange",
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
    "/": { prerender: true },
  },

  compatibilityDate: "2025-01-15",

  vite: {
    resolve: {
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

  eslint: {
    config: {
      stylistic: {
        commaDangle: "never",
        braceStyle: "1tbs",
      },
    },
  },
});
