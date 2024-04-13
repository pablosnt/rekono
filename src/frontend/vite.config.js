import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    headers: {
      'Cache-Control': 'no-store',
      // 'Content-Security-Policy': "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; connect-src 'self'; img-src 'self' data: www.kali.org raw.githubusercontent.com camo.githubusercontent.com fullhunt.io gitleaks.io nuclei.projectdiscovery.io www.lunasec.io; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'",
      'Referrer-Policy': 'no-referrer',
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-Powered-By': '',
    },
    proxy: {
      '/api/': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
    }
  }
})
