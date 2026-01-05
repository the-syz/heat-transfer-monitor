<template>
  <div class="home">
    <el-container>
      <el-header>
        <h1>换热器性能监测系统</h1>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>欢迎使用换热器性能监测系统</span>
                </div>
              </template>
              <p>系统正在初始化中...</p>
              <el-button
                type="primary"
                @click="goToLogin"
              >
                前往登录
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.el-header {
  background-color: #1a237e;
  color: white;
  text-align: center;
  line-height: 60px;
}

.el-main {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
