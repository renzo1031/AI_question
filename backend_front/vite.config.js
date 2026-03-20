import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 本地后端地址
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // 如果后端接口不包含 /api 前缀，请取消注释
      },
      '/ai-question': {
        target: 'http://localhost:9000', // MinIO 地址
        changeOrigin: true
      }
    }
  }
})
