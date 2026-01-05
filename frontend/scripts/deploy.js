#!/usr/bin/env node

/**
 * 部署脚本
 */

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

// 获取部署环境
const environment = process.argv[2] || 'staging'
const validEnvironments = ['staging', 'production']

if (!validEnvironments.includes(environment)) {
  console.error(`❌ 无效的部署环境: ${environment}`)
  console.error(`   可用环境: ${validEnvironments.join(', ')}`)
  process.exit(1)
}

console.log(`🚀 开始部署到 ${environment} 环境...\n`)

// 读取环境配置
const envFilePath = path.join(__dirname, '..', `.env.${environment}`)
if (!fs.existsSync(envFilePath)) {
  console.error(`❌ 环境配置文件不存在: ${envFilePath}`)
  console.error(`   请先创建 .env.${environment} 文件`)
  process.exit(1)
}

// 构建应用
console.log(`1. 构建应用 (${environment}环境)...`)
try {
  execSync(`npm run build:${environment}`, { stdio: 'inherit' })
  console.log('   ✅ 构建成功\n')
} catch (error) {
  console.error('   ❌ 构建失败')
  process.exit(1)
}

// 检查构建结果
console.log('2. 检查构建结果...')
const distPath = path.join(__dirname, '..', 'dist')
if (!fs.existsSync(distPath)) {
  console.error('   ❌ dist目录不存在')
  process.exit(1)
}

// 检查关键文件
const requiredFiles = ['index.html']
let missingFiles = []

// 检查 index.html
if (!fs.existsSync(path.join(distPath, 'index.html'))) {
  missingFiles.push('index.html')
}

// 检查 assets 目录
const assetsPath = path.join(distPath, 'assets')
if (!fs.existsSync(assetsPath)) {
  missingFiles.push('assets/')
}

if (missingFiles.length > 0) {
  console.error(`   ❌ 缺少关键文件: ${missingFiles.join(', ')}`)
  process.exit(1)
}

console.log('   ✅ 构建结果完整\n')

// 生成部署报告
console.log('3. 生成部署报告...')
const report = {
  environment,
  timestamp: new Date().toISOString(),
  buildSize: getDirectorySize(distPath),
  fileCount: countFiles(distPath)
}

const reportPath = path.join(distPath, 'deploy-report.json')
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2))

console.log(`   ✅ 部署报告已生成: ${reportPath}`)
console.log(`     环境: ${report.environment}`)
console.log(`     时间: ${report.timestamp}`)
console.log(`     构建大小: ${formatBytes(report.buildSize)}`)
console.log(`     文件数量: ${report.fileCount}\n`)

console.log('🎉 部署准备完成！')
console.log(`   构建目录: ${distPath}`)
console.log(`   下一步: 将dist目录内容部署到服务器`)

// 辅助函数
function getDirectorySize(dir) {
  let size = 0
  const files = fs.readdirSync(dir, { withFileTypes: true })

  files.forEach((file) => {
    const filePath = path.join(dir, file.name)
    if (file.isDirectory()) {
      size += getDirectorySize(filePath)
    } else {
      size += fs.statSync(filePath).size
    }
  })

  return size
}

function countFiles(dir) {
  let count = 0
  const files = fs.readdirSync(dir, { withFileTypes: true })

  files.forEach((file) => {
    const filePath = path.join(dir, file.name)
    if (file.isDirectory()) {
      count += countFiles(filePath)
    } else {
      count++
    }
  })

  return count
}

function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

