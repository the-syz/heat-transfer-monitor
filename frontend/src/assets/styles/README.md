# 样式系统使用说明

## 文件结构

```
styles/
├── variables.scss  # 设计变量（颜色、字体、间距等）
├── mixins.scss     # 样式混合和函数
├── reset.scss      # 样式重置
├── global.scss     # 全局样式和工具类
└── index.scss      # 入口文件
```

## 使用方法

### 1. 在组件中使用设计变量

```vue
<style lang="scss" scoped>
.my-component {
  // 使用颜色
  color: color(primary);
  background-color: color(gray-100);
  
  // 使用间距
  padding: spacing(4);
  margin: spacing(2);
  
  // 使用字体大小
  font-size: font-size('lg');
}
</style>
```

### 2. 使用 Mixins

```vue
<style lang="scss" scoped>
.card {
  @include flex-center;
  @include respond-to('md') {
    @include flex-between;
  }
}
</style>
```

### 3. 使用工具类

```vue
<template>
  <div class="flex-center text-truncate">
    <span>内容</span>
  </div>
</template>
```

### 4. 使用主题系统

```javascript
import { setTheme, toggleTheme, getCurrentTheme } from '@/utils/theme'

// 设置主题
setTheme('dark')

// 切换主题
toggleTheme()

// 获取当前主题
const theme = getCurrentTheme()
```

## 设计变量说明

### 颜色系统
- `primary`: 主色调（深蓝色 #1a237e）
- `secondary`: 辅助色（青色 #00bcd4）
- `success`: 成功状态（绿色 #4caf50）
- `warning`: 警告状态（橙色 #ff9800）
- `error`: 错误状态（红色 #f44336）
- `gray-*`: 中性色系列（50-900）

### 间距系统
- `spacing(0-10)`: 4px 的倍数间距

### 响应式断点
- `xs`: 0px
- `sm`: 576px
- `md`: 768px
- `lg`: 992px
- `xl`: 1200px
- `xxl`: 1400px

## 注意事项

1. 所有 SCSS 文件会自动导入 `variables.scss` 和 `mixins.scss`（通过 vite.config.js 配置）
2. 使用 `color()` 函数获取颜色，而不是直接使用 map-get
3. 响应式设计使用 `@include respond-to()` mixin
4. 主题切换会自动更新 CSS 变量，组件可以通过 CSS 变量使用主题颜色

