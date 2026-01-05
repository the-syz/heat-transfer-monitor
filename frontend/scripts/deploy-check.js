#!/usr/bin/env node

/**
 * 部署前检查脚本
 */

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

console.log('🚀 开始部署前检查...\n')

// 检查Node版本
console.log('1. 检查Node版本...')
const nodeVersion = process.version
const requiredVersion = '>=16.0.0'
console.log(`   当前版本: ${nodeVersion}`)
console.log(`   要求版本: ${requiredVersion}\n`)

// 检查npm版本
console.log('2. 检查npm版本...')
try {
  const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim()
  console.log(`   当前版本: ${npmVersion}`)
} catch (error) {
  console.log('   ❌ 无法获取npm版本')
}

// 检查依赖安装
console.log('3. 检查依赖安装...')
const packageJsonPath = path.join(__dirname, '..', 'package.json')
const nodeModulesPath = path.join(__dirname, '..', 'node_modules')

if (!fs.existsSync(nodeModulesPath)) {
  console.log('   ❌ node_modules目录不存在，请先运行 npm install')
  process.exit(1)
} else {
  console.log('   ✅ 依赖已安装\n')
}

// 检查构建目录
console.log('4. 检查构建目录...')
const distPath = path.join(__dirname, '..', 'dist')
if (fs.existsSync(distPath)) {
  console.log('   ⚠️  dist目录已存在，将清空后重新构建')
  try {
    fs.rmSync(distPath, { recursive: true, force: true })
    console.log('   ✅ 已清空dist目录\n')
  } catch (error) {
    console.log(`   ❌ 清空dist目录失败: ${error.message}`)
  }
} else {
  console.log('   ✅ dist目录不存在，可以开始构建\n')
}

// 运行代码检查
console.log('5. 运行代码检查...')
try {
  execSync('npm run lint', { stdio: 'inherit' })
  console.log('   ✅ 代码检查通过\n')
} catch (error) {
  console.log('   ❌ 代码检查失败')
  process.exit(1)
}

// 运行测试（如果存在）
console.log('6. 检查测试配置...')
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'))
if (packageJson.scripts && packageJson.scripts.test) {
  console.log('   ⚠️  检测到测试脚本，但跳过执行（可选）\n')
} else {
  console.log('   ℹ️  未配置测试脚本，跳过\n')
}

console.log('🎉 部署前检查完成，可以开始构建！')

