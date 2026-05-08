<script setup lang="ts">
import { Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'

import {
  getOperationLogs,
  type OperationLogItem,
  type OperationLogListParams,
} from '@/api/operationLogs'

interface OperationLogFilters {
  keyword: string
  module: string
  operation_type: string
  page: number
  page_size: number
}

const loading = ref(false)
const logs = ref<OperationLogItem[]>([])
const total = ref(0)
const dateRange = ref<[string, string] | []>([])

const filters = reactive<OperationLogFilters>({
  keyword: '',
  module: '',
  operation_type: '',
  page: 1,
  page_size: 10,
})

function getErrorMessage(error: unknown, fallback = '请求失败') {
  return error instanceof Error ? error.message : fallback
}

function buildParams(): OperationLogListParams {
  return {
    keyword: filters.keyword.trim() || undefined,
    module: filters.module.trim() || undefined,
    operation_type: filters.operation_type.trim() || undefined,
    date_from: dateRange.value[0],
    date_to: dateRange.value[1],
    page: filters.page,
    page_size: filters.page_size,
  }
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString('zh-CN', {
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function operatorName(row: OperationLogItem) {
  if (!row.user) {
    return '系统'
  }
  return `${row.user.real_name}（${row.user.username}）`
}

async function loadLogs() {
  loading.value = true
  try {
    const response = await getOperationLogs(buildParams())
    logs.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '操作日志加载失败'))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  filters.page = 1
  loadLogs()
}

function handleReset() {
  filters.keyword = ''
  filters.module = ''
  filters.operation_type = ''
  dateRange.value = []
  filters.page = 1
  loadLogs()
}

function handleSizeChange() {
  filters.page = 1
  loadLogs()
}

onMounted(loadLogs)
</script>

<template>
  <section class="page operation-log-page">
    <div class="page-header">
      <div>
        <h1>操作日志</h1>
        <p>查看系统关键操作、登录、导出和配置修改记录</p>
      </div>
      <div class="page-actions">
        <el-button :icon="Refresh" :loading="loading" @click="loadLogs">刷新</el-button>
      </div>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16">
        <el-col :xs="24" :md="7">
          <label class="filter-label">关键词搜索</label>
          <el-input
            v-model="filters.keyword"
            :prefix-icon="Search"
            clearable
            placeholder="用户、目标、详情或IP"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :md="4">
          <label class="filter-label">模块</label>
          <el-input
            v-model="filters.module"
            clearable
            placeholder="全部模块"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :md="4">
          <label class="filter-label">操作类型</label>
          <el-input
            v-model="filters.operation_type"
            clearable
            placeholder="全部操作"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :md="6">
          <label class="filter-label">操作日期</label>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :md="3" class="filter-reset-col">
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="logs" row-key="id">
        <el-table-column label="操作时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作人" min-width="170">
          <template #default="{ row }">
            {{ operatorName(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" min-width="120" />
        <el-table-column prop="operation_type" label="操作类型" min-width="130" />
        <el-table-column label="目标" min-width="180">
          <template #default="{ row }">
            {{ row.target_name || row.target_id || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作详情" min-width="260">
          <template #default="{ row }">
            <span class="log-detail-cell">{{ row.operation_detail || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="IP地址" min-width="130">
          <template #default="{ row }">
            {{ row.ip_address || '-' }}
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-bar">
        <span>共 {{ total }} 条记录</span>
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="prev, pager, next, sizes"
          @current-change="loadLogs"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
  </section>
</template>
