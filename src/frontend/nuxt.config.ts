import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  devtools: { enabled: true },
  build: {
    transpile: ['vuetify'],
  },
  runtimeConfig: {
    backendUrl: process.env.BACKEND_URL,
    backendRootPath: process.env.BACKEND_ROOT_PATH,
  },
  vite: {
    vue: {
      template: {
        transformAssetUrls,
      },
    },
    server: {
      headers: {
        'Cache-Control': 'no-store',
        // 'Content-Security-Policy': "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; connect-src 'self'; img-src 'self' data: www.kali.org raw.githubusercontent.com camo.githubusercontent.com fullhunt.io gitleaks.io nuclei.projectdiscovery.io www.lunasec.io; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'no-referrer',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-Powered-By': ''
      },
      proxy: {
        '/api/': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true
        }
      }
    }
  },
  modules: [
    (_options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', (config) => {
        // @ts-expect-error
        config.plugins.push(vuetify({ autoImport: true }))
      })
    },
    '@pinia/nuxt',
    '@nuxt/image',
    '@nuxt/eslint'
  ]
})
