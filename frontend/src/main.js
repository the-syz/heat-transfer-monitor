import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './assets/styles/index.scss'
import { initTheme } from './utils/theme'

// 创建应用
const app = createApp(App)

// 使用Pinia状态管理
const pinia = createPinia()
app.use(pinia)

// 使用Element Plus UI框架
app.use(ElementPlus, {
  // 全局配置
  size: 'default',
  zIndex: 2000,
})

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用路由
app.use(router)

// 初始化主题系统
initTheme()

// 测试环境变量加载
console.log('=== 环境变量测试 ===')
console.log('API Base URL:', import.meta.env.VITE_API_BASE_URL)
console.log('App Title:', import.meta.env.VITE_APP_TITLE)
console.log('Debug Mode:', import.meta.env.VITE_DEBUG)
console.log('Build Time:', import.meta.env.VITE_BUILD_TIME)
console.log('===================')

// 挂载应用
app.mount('#app')