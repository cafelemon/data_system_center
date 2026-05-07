<script setup lang="ts">
import { CircleCheckFilled, WarningFilled } from '@element-plus/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { getHealth, type HealthStatus } from '@/api/health'

const route = useRoute()
const loading = ref(false)
const errorMessage = ref('')
const health = ref<HealthStatus | null>(null)

const pageTitle = computed(() => String(route.meta.title ?? '档案管理系统'))
const pageSubtitle = computed(() => String(route.meta.subtitle ?? ''))
const isHealthy = computed(
  () => health.value?.status === 'ok' && health.value?.database === 'ok',
)

async function loadHealth() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await getHealth()
    health.value = response.data
  } catch (error) {
    health.value = null
    errorMessage.value = '后端服务暂不可用'
  } finally {
    loading.value = false
  }
}

onMounted(loadHealth)
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1>{{ pageTitle }}</h1>
        <p>{{ pageSubtitle }}</p>
      </div>
    </div>

    <el-card class="foundation-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>工程底座状态</span>
          <el-button size="small" :loading="loading" @click="loadHealth">刷新</el-button>
        </div>
      </template>

      <div v-if="health" class="health-grid">
        <div class="health-item">
          <span>接口服务</span>
          <strong>{{ health.service }}</strong>
        </div>
        <div class="health-item">
          <span>服务状态</span>
          <el-tag :type="isHealthy ? 'success' : 'warning'" effect="light">
            <el-icon><component :is="isHealthy ? CircleCheckFilled : WarningFilled" /></el-icon>
            {{ health.status }}
          </el-tag>
        </div>
        <div class="health-item">
          <span>数据库</span>
          <el-tag :type="health.database === 'ok' ? 'success' : 'danger'" effect="light">
            {{ health.database }}
          </el-tag>
        </div>
        <div class="health-item">
          <span>版本</span>
          <strong>{{ health.version }}</strong>
        </div>
      </div>

      <el-alert
        v-else-if="errorMessage"
        :title="errorMessage"
        type="warning"
        show-icon
        :closable="false"
      />

      <el-skeleton v-else :rows="3" animated />
    </el-card>
  </section>
</template>
