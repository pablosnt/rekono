module.exports = {
  devServer: {
    headers: {
      'Content-Security-Policy': "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; connect-src 'self'; img-src 'self' data: www.kali.org raw.githubusercontent.com camo.githubusercontent.com; script-src 'self' 'unsafe-eval'; style-src 'self' 'sha256-lkDe8os/5Aap/ouRMWJeJNQBiCkjAVo1JXVGUhtOnvw=' 'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=' 'sha256-z/EWESw3l34tjlyen03tMJHfJbLpsAp0UzDARjA+mIY=' 'sha256-vAmFo+rw61CpbXd9BPwoKmgwd8L9JK0yGNlclapoQVk=' 'sha256-i0JTwIrMztDmTtnJjmsISIe8mpVTJE6YBQyLG7WgL98=' 'sha256-BIpa5d7e8YSkEusAsfy39n8KgXUfaPL4FYbPbMK0XK8=' 'sha256-CMcBozO2BZ4hVVbYLDgFiXaEeXnPAdXawRwM20KqO/k=' 'sha256-zD01CfgfngvkCk+eseQsdFyQBrGInbuWAbIS42nXVn8=' 'sha256-XAZO3UnvvqixprBpLGOYEuFYtHXv532qAXJsQEcW4hc=' 'sha256-kwpt3lQZ21rs4cld7/uEm9qI5yAbjYzx+9FGm/XmwNU='",
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'no-referrer',
      'X-Powered-By': ''
    },
    proxy: {
      '/api/': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
    }
  },
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'Rekono'
    }
  }
}