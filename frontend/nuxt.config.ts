// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ["@nuxt/eslint", "@nuxt/ui", "@pinia/nuxt"],

  devtools: {
    enabled: true,
  },

  css: ["~/assets/css/main.css"],

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
