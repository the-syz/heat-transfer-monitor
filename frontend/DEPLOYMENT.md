# 构建与部署说明

## 构建命令

### 开发环境
```bash
npm run dev
```
启动开发服务器，自动加载 `.env.development` 配置

### 测试环境构建
```bash
npm run build:staging
```
构建测试环境版本，使用 `.env.staging` 配置

### 生产环境构建
```bash
npm run build:production
```
构建生产环境版本，使用 `.env.production` 配置

## 部署流程

### 1. 部署前检查
```bash
npm run deploy:check
```
执行以下检查：
- Node 版本检查
- npm 版本检查
- 依赖安装检查
- 构建目录清理
- 代码规范检查

### 2. 部署到测试环境
```bash
npm run deploy:staging
```
1. 执行构建前检查
2. 构建测试环境版本
3. 验证构建结果
4. 生成部署报告

### 3. 部署到生产环境
```bash
npm run deploy:production
```
1. 执行构建前检查
2. 构建生产环境版本
3. 验证构建结果
4. 生成部署报告

## 构建优化

### 代码分割
- Vue 核心库（vue, vue-router, pinia）单独打包
- UI 组件库（element-plus）单独打包
- 第三方库（axios）单独打包

### 压缩优化
- 生产环境自动启用 Terser 压缩
- 自动移除 console 和 debugger
- CSS 代码分割启用

### 静态资源
- 图片资源：`assets/images/[name]-[hash].[ext]`
- 字体资源：`assets/fonts/[name]-[hash].[ext]`
- 其他资源：`assets/[ext]/[name]-[hash].[ext]`

## Nginx 配置

生产环境部署时，请参考 `nginx.conf` 文件配置 Nginx：

1. 复制配置文件到服务器
2. 修改 `server_name` 和 `root` 路径
3. 配置 API 代理地址
4. 重启 Nginx 服务

### 关键配置说明

- **Gzip 压缩**：启用 Gzip 压缩减少传输大小
- **静态资源缓存**：JS/CSS/图片缓存 1 年
- **HTML 不缓存**：确保用户获取最新版本
- **SPA 路由支持**：所有路由回退到 index.html
- **SSE 代理**：支持实时数据推送连接

## 环境变量

请参考 `ENV_SETUP.md` 文件创建环境变量配置文件。

## 部署报告

每次部署完成后，会在 `dist/deploy-report.json` 生成部署报告，包含：
- 部署环境
- 部署时间
- 构建大小
- 文件数量

## 注意事项

1. 确保服务器已安装 Node.js 16+ 和 npm
2. 生产环境部署前务必检查环境变量配置
3. 建议使用 HTTPS 协议部署
4. 定期检查构建产物大小，确保不超过 5MB
5. 部署后验证所有功能是否正常

