/**
 * 主题管理工具
 */

// 主题配置
export const themes = {
  light: {
    name: 'light',
    colors: {
      primary: '#1a237e',
      secondary: '#00bcd4',
      background: '#ffffff',
      surface: '#f5f5f5',
      text: '#212121',
      textSecondary: '#757575',
      border: '#e0e0e0',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336'
    }
  },
  dark: {
    name: 'dark',
    colors: {
      primary: '#534bae',
      secondary: '#62efff',
      background: '#121212',
      surface: '#1e1e1e',
      text: '#ffffff',
      textSecondary: '#b0b0b0',
      border: '#424242',
      success: '#66bb6a',
      warning: '#ffb74d',
      error: '#ef5350'
    }
  },
  blue: {
    name: 'blue',
    colors: {
      primary: '#1565c0',
      secondary: '#29b6f6',
      background: '#f5f7fa',
      surface: '#ffffff',
      text: '#263238',
      textSecondary: '#607d8b',
      border: '#cfd8dc',
      success: '#43a047',
      warning: '#ffa726',
      error: '#e53935'
    }
  }
}

// 当前主题
let currentTheme = 'light'

/**
 * 获取当前主题
 */
export function getCurrentTheme() {
  return themes[currentTheme]
}

/**
 * 设置主题
 * @param {string} themeName - 主题名称
 */
export function setTheme(themeName) {
  if (!themes[themeName]) {
    console.warn(`主题 ${themeName} 不存在，使用默认主题`)
    themeName = 'light'
  }
  
  currentTheme = themeName
  const theme = themes[themeName]
  
  // 更新CSS变量
  Object.entries(theme.colors).forEach(([key, value]) => {
    document.documentElement.style.setProperty(`--color-${key}`, value)
  })
  
  // 保存到localStorage
  localStorage.setItem('theme', themeName)
  
  // 触发主题变更事件
  window.dispatchEvent(new CustomEvent('theme-change', { detail: theme }))
  
  return theme
}

/**
 * 初始化主题
 */
export function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light'
  return setTheme(savedTheme)
}

/**
 * 切换主题
 */
export function toggleTheme() {
  const themesList = Object.keys(themes)
  const currentIndex = themesList.indexOf(currentTheme)
  const nextIndex = (currentIndex + 1) % themesList.length
  return setTheme(themesList[nextIndex])
}

