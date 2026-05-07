<script setup lang="ts">
import { Document, Lock, User } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()

const form = reactive({
  username: 'admin',
  password: 'Admin@123456',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : '登录失败'
}

async function handleLogin() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }

  try {
    await authStore.login({
      username: form.username.trim(),
      password: form.password,
    })
    ElMessage.success('登录成功')
    router.replace(String(route.query.redirect || '/archives'))
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-panel">
      <div class="login-brand">
        <div class="brand-icon">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div>
          <h1>档案管理系统</h1>
          <p>Archive System</p>
        </div>
      </div>

      <el-card class="login-card" shadow="never">
        <template #header>
          <div class="login-card-header">
            <strong>账号登录</strong>
            <span>纸质档案目录管理后台</span>
          </div>
        </template>

        <el-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent>
          <el-form-item prop="username">
            <el-input v-model="form.username" :prefix-icon="User" placeholder="用户名" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              :prefix-icon="Lock"
              placeholder="密码"
              show-password
              type="password"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-button
            class="login-submit"
            type="primary"
            size="large"
            :loading="authStore.loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form>

        <div class="login-hint">
          <span>演示账号</span>
          <strong>admin / Admin@123456</strong>
        </div>
      </el-card>
    </section>
  </main>
</template>
