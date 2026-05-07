<script setup lang="ts">
import { Delete, Edit, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import {
  createArchiveType,
  createRetentionPeriod,
  deleteArchiveType,
  deleteRetentionPeriod,
  getArchiveTypes,
  getRetentionPeriods,
  updateArchiveType,
  updateArchiveTypeStatus,
  updateRetentionPeriod,
  updateRetentionPeriodStatus,
  type ArchiveTypeConfig,
  type RetentionPeriodConfig,
} from '@/api/settings'

type SettingTab = 'archive-types' | 'retention-periods'
type DialogMode = 'create' | 'edit'

interface ConfigFormState {
  name: string
  code: string
  years?: number
  enabled: boolean
}

const activeTab = ref<SettingTab>('archive-types')
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<DialogMode>('create')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const archiveTypes = ref<ArchiveTypeConfig[]>([])
const retentionPeriods = ref<RetentionPeriodConfig[]>([])

const form = reactive<ConfigFormState>({
  name: '',
  code: '',
  enabled: true,
})

const archiveTypeRules = {
  name: [{ required: true, message: '请输入类型名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编码值', trigger: 'blur' }],
}

const retentionPeriodRules = {
  name: [{ required: true, message: '请输入期限名称', trigger: 'blur' }],
  years: [{ required: true, message: '请输入年限值', trigger: 'change' }],
}

const currentRules = computed(() =>
  activeTab.value === 'archive-types' ? archiveTypeRules : retentionPeriodRules,
)

const dialogTitle = computed(() => {
  const prefix = dialogMode.value === 'create' ? '新增' : '编辑'
  return activeTab.value === 'archive-types'
    ? `${prefix}档案类型`
    : `${prefix}保管期限`
})

function getErrorMessage(error: unknown, fallback = '请求失败') {
  return error instanceof Error ? error.message : fallback
}

function resetForm() {
  Object.assign(form, {
    name: '',
    code: '',
    years: undefined,
    enabled: true,
  })
  formRef.value?.clearValidate()
}

function statusText(enabled: boolean) {
  return enabled ? '启用' : '禁用'
}

async function loadArchiveTypes() {
  const response = await getArchiveTypes()
  archiveTypes.value = response.data.items
}

async function loadRetentionPeriods() {
  const response = await getRetentionPeriods()
  retentionPeriods.value = response.data.items
}

async function loadCurrentTab() {
  loading.value = true
  try {
    if (activeTab.value === 'archive-types') {
      await loadArchiveTypes()
    } else {
      await loadRetentionPeriods()
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '配置加载失败'))
  } finally {
    loading.value = false
  }
}

function handleTabChange() {
  resetForm()
  loadCurrentTab()
}

function openCreateDialog() {
  dialogMode.value = 'create'
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openArchiveTypeEdit(item: ArchiveTypeConfig) {
  activeTab.value = 'archive-types'
  dialogMode.value = 'edit'
  editingId.value = item.id
  Object.assign(form, {
    name: item.name,
    code: item.code,
    years: undefined,
    enabled: item.enabled,
  })
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

function openRetentionPeriodEdit(item: RetentionPeriodConfig) {
  activeTab.value = 'retention-periods'
  dialogMode.value = 'edit'
  editingId.value = item.id
  Object.assign(form, {
    name: item.name,
    code: '',
    years: item.years,
    enabled: item.enabled,
  })
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

async function submitConfig() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }

  saving.value = true
  try {
    if (activeTab.value === 'archive-types') {
      const payload = {
        name: form.name.trim(),
        code: form.code.trim(),
        enabled: form.enabled,
      }
      if (dialogMode.value === 'create') {
        await createArchiveType(payload)
        ElMessage.success('档案类型已新增')
      } else if (editingId.value) {
        await updateArchiveType(editingId.value, payload)
        ElMessage.success('档案类型已更新')
      }
      await loadArchiveTypes()
    } else {
      const payload = {
        name: form.name.trim(),
        years: Number(form.years),
        enabled: form.enabled,
      }
      if (dialogMode.value === 'create') {
        await createRetentionPeriod(payload)
        ElMessage.success('保管期限已新增')
      } else if (editingId.value) {
        await updateRetentionPeriod(editingId.value, payload)
        ElMessage.success('保管期限已更新')
      }
      await loadRetentionPeriods()
    }
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function handleArchiveTypeStatus(item: ArchiveTypeConfig, enabled: boolean) {
  if (item.enabled === enabled) {
    return
  }
  try {
    await updateArchiveTypeStatus(item.id, enabled)
    ElMessage.success('状态已更新')
    await loadArchiveTypes()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '状态更新失败'))
  }
}

function handleArchiveTypeSwitch(item: ArchiveTypeConfig, value: string | number | boolean) {
  handleArchiveTypeStatus(item, Boolean(value))
}

async function handleRetentionPeriodStatus(
  item: RetentionPeriodConfig,
  enabled: boolean,
) {
  if (item.enabled === enabled) {
    return
  }
  try {
    await updateRetentionPeriodStatus(item.id, enabled)
    ElMessage.success('状态已更新')
    await loadRetentionPeriods()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '状态更新失败'))
  }
}

function handleRetentionPeriodSwitch(
  item: RetentionPeriodConfig,
  value: string | number | boolean,
) {
  handleRetentionPeriodStatus(item, Boolean(value))
}

async function handleArchiveTypeDelete(item: ArchiveTypeConfig) {
  try {
    await ElMessageBox.confirm(`确认删除“${item.name}”？`, '删除档案类型', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteArchiveType(item.id)
    ElMessage.success('档案类型已删除')
    await loadArchiveTypes()
  } catch (error) {
    if (error instanceof Error) {
      ElMessage.error(error.message)
    }
  }
}

async function handleRetentionPeriodDelete(item: RetentionPeriodConfig) {
  try {
    await ElMessageBox.confirm(`确认删除“${item.name}”？`, '删除保管期限', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteRetentionPeriod(item.id)
    ElMessage.success('保管期限已删除')
    await loadRetentionPeriods()
  } catch (error) {
    if (error instanceof Error) {
      ElMessage.error(error.message)
    }
  }
}

onMounted(loadCurrentTab)
</script>

<template>
  <section class="page settings-page">
    <div class="page-header">
      <div>
        <h1>系统设置</h1>
        <p>管理档案类型、保管期限等基础字典配置</p>
      </div>
    </div>

    <el-card class="settings-card" shadow="never">
      <div class="settings-toolbar">
        <el-tabs v-model="activeTab" class="settings-tabs" @tab-change="handleTabChange">
          <el-tab-pane label="档案类型配置" name="archive-types" />
          <el-tab-pane label="保管期限配置" name="retention-periods" />
        </el-tabs>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          新增配置
        </el-button>
      </div>

      <el-table
        v-if="activeTab === 'archive-types'"
        v-loading="loading"
        :data="archiveTypes"
        row-key="id"
      >
        <el-table-column prop="name" label="类型名称" min-width="220" />
        <el-table-column prop="code" label="编码值" min-width="180" />
        <el-table-column label="状态" min-width="160">
          <template #default="{ row }">
            <div class="status-switch-cell">
              <el-switch
                :model-value="row.enabled"
                @change="handleArchiveTypeSwitch(row, $event)"
              />
              <span>{{ statusText(row.enabled) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="编辑配置" placement="top">
                <el-button :icon="Edit" text @click="openArchiveTypeEdit(row)" />
              </el-tooltip>
              <el-tooltip content="删除配置" placement="top">
                <el-button
                  class="danger-action"
                  :icon="Delete"
                  text
                  @click="handleArchiveTypeDelete(row)"
                />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-table v-else v-loading="loading" :data="retentionPeriods" row-key="id">
        <el-table-column prop="name" label="期限名称" min-width="220" />
        <el-table-column prop="years" label="年限值" min-width="180" />
        <el-table-column label="状态" min-width="160">
          <template #default="{ row }">
            <div class="status-switch-cell">
              <el-switch
                :model-value="row.enabled"
                @change="handleRetentionPeriodSwitch(row, $event)"
              />
              <span>{{ statusText(row.enabled) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="编辑配置" placement="top">
                <el-button :icon="Edit" text @click="openRetentionPeriodEdit(row)" />
              </el-tooltip>
              <el-tooltip content="删除配置" placement="top">
                <el-button
                  class="danger-action"
                  :icon="Delete"
                  text
                  @click="handleRetentionPeriodDelete(row)"
                />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
      <el-form ref="formRef" :model="form" :rules="currentRules" label-width="92px">
        <el-form-item
          :label="activeTab === 'archive-types' ? '类型名称' : '期限名称'"
          prop="name"
        >
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item v-if="activeTab === 'archive-types'" label="编码值" prop="code">
          <el-input v-model="form.code" placeholder="请输入编码值" />
        </el-form-item>
        <el-form-item v-else label="年限值" prop="years">
          <el-input-number v-model="form.years" :min="-1" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.enabled" />
          <span class="form-switch-text">{{ statusText(form.enabled) }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitConfig">
          保存
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>
