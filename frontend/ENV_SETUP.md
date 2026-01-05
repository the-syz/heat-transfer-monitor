# 环境变量配置说明

## 文件位置

请在项目根目录（frontend/）下创建以下环境变量文件：

### 1. .env.development（开发环境）

```env
# 开发环境配置
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=换热器监测系统(开发环境)
VITE_DEBUG=true
VITE_PUBLIC_PATH=/
VITE_BUILD_TIME=2026-01-04
```

### 2. .env.staging（测试环境）

```env
# 测试环境配置
VITE_API_BASE_URL=https://staging-api.heat-exchanger.com
VITE_APP_TITLE=换热器监测系统(测试环境)
VITE_DEBUG=true
VITE_PUBLIC_PATH=/
VITE_BUILD_TIME=2026-01-04
```

### 3. .env.production（生产环境）

```env
# 生产环境配置
VITE_API_BASE_URL=https://api.heat-exchanger.com
VITE_APP_TITLE=换热器性能监测系统
VITE_DEBUG=false
VITE_PUBLIC_PATH=/
VITE_BUILD_TIME=2026-01-04
VITE_CDN_URL=https://cdn.heat-exchanger.com
```

## 使用方法

1. 开发环境：直接运行 `npm run dev`，会自动加载 `.env.development`
2. 测试环境构建：运行 `npm run build:staging`，会加载 `.env.staging`
3. 生产环境构建：运行 `npm run build:production`，会加载 `.env.production`

## 注意事项

- 所有环境变量必须以 `VITE_` 开头才能在代码中访问
- 使用 `import.meta.env.VITE_API_BASE_URL` 访问环境变量
- `.env.*` 文件不应提交到版本控制系统（已在 .gitignore 中）
- 根据实际部署环境修改 API 地址和 CDN 地址

