module.exports = {
  devServer: {
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