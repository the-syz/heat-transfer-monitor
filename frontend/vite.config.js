import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())

  return {
    // 基础路径
    base: env.VITE_PUBLIC_PATH || '/',

    // 插件配置
    plugins: [vue()],

    // 解析配置
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@views': resolve(__dirname, 'src/views'),
        '@stores': resolve(__dirname, 'src/stores'),
        '@utils': resolve(__dirname, 'src/utils'),
        '@api': resolve(__dirname, 'src/api'),
        '@assets': resolve(__dirname, 'src/assets'),
        '@layouts': resolve(__dirname, 'src/layouts'),
        '@composables': resolve(__dirname, 'src/composables')
      }
    },

    // 开发服务器配置
    server: {
      port: 3000,
      host: true,
      open: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          secure: false
        },
        '/realtime-stream': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        }
      },
      cors: true
    },

    // 构建配置
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      minify: mode === 'production' ? 'terser' : false,
      terserOptions:
        mode === 'production'
          ? {
              compress: {
                drop_console: true,
                drop_debugger: true
              }
            }
          : {},
      rollupOptions: {
        output: {
          // 代码分割策略
          manualChunks: {
            vue: ['vue', 'vue-router', 'pinia'],
            ui: ['element-plus'],
            vendor: ['axios']
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.')
            const ext = info[info.length - 1]
            if (/\.(png|jpe?g|gif|svg|webp|avif)$/.test(assetInfo.name)) {
              return `assets/images/[name]-[hash].[ext]`
            }
            if (/\.(woff2?|eot|ttf|otf)$/.test(assetInfo.name)) {
              return `assets/fonts/[name]-[hash].[ext]`
            }
            return `assets/[ext]/[name]-[hash].[ext]`
          }
        }
      },
      // 构建大小限制警告
      chunkSizeWarningLimit: 1000,
      // 启用CSS代码分割
      cssCodeSplit: true
    },

    // 预构建配置
    optimizeDeps: {
      include: ['vue', 'vue-router', 'pinia', 'axios', 'element-plus'],
      exclude: []
    },

    // CSS配置
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @use "@assets/styles/variables.scss" as *;
            @use "@assets/styles/mixins.scss" as *;
          `
        }
      }
    }
  }
})

