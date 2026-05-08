<script setup lang="ts">
import {
  Delete,
  Download,
  Edit,
  Plus,
  Refresh,
  Search,
  View,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import {
  batchDeleteArchives,
  createArchive,
  deleteArchive,
  exportArchives,
  getArchive,
  getArchiveOptions,
  getArchives,
  updateArchive,
  type ArchiveItem,
  type ArchiveListParams,
  type ArchiveMedium,
  type ArchiveOptionsResponse,
  type ArchivePayload,
} from '@/api/archives'
import { useAuthStore } from '@/stores/auth'

type DialogMode = 'create' | 'edit'

interface ArchiveFilters {
  keyword: string
  internal_archive_type: string
  department_id?: number
  status_id?: number
  page: number
  page_size: number
}

interface ArchiveFormState {
  archive_no: string
  title: string
  archive_type_id?: number
  internal_archive_type: string
  status_id?: number
  retention_period_id?: number
  department_id?: number
  paper_copies: number
  archive_date: string | null
  paper_storage_location: string
  electronic_storage_path: string
  archiver_name: string
  owner_name: string
  archive_year?: number
  security_level: string
  importance_level: string
  project_name: string
  related_party: string
  contract_no: string
  keywords: string
  remarks: string
}

const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const detailLoading = ref(false)
const exporting = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const dialogMode = ref<DialogMode>('create')
const editingArchiveId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const archives = ref<ArchiveItem[]>([])
const selectedArchives = ref<ArchiveItem[]>([])
const currentArchive = ref<ArchiveItem | null>(null)
const total = ref(0)
const options = ref<ArchiveOptionsResponse>({
  archive_types: [],
  statuses: [],
  departments: [],
  retention_periods: [],
})

const filters = reactive<ArchiveFilters>({
  keyword: '',
  internal_archive_type: '',
  page: 1,
  page_size: 10,
})

const form = reactive<ArchiveFormState>({
  archive_no: '',
  title: '',
  internal_archive_type: '',
  paper_copies: 1,
  archive_date: null,
  paper_storage_location: '',
  electronic_storage_path: '',
  archiver_name: '',
  owner_name: '',
  security_level: '内部',
  importance_level: '普通',
  project_name: '',
  related_party: '',
  contract_no: '',
  keywords: '',
  remarks: '',
})

const rules = {
  archive_no: [{ required: true, message: '请输入档案编号', trigger: 'blur' }],
  title: [{ required: true, message: '请输入档案名称', trigger: 'blur' }],
  archive_type_id: [{ required: true, message: '请选择档案类型', trigger: 'change' }],
  internal_archive_type: [
    { required: true, message: '请输入内部档案类型', trigger: 'blur' },
  ],
  status_id: [{ required: true, message: '请选择状态', trigger: 'change' }],
  retention_period_id: [
    { required: true, message: '请选择保管期限', trigger: 'change' },
  ],
  department_id: [{ required: true, message: '请选择归档部门', trigger: 'change' }],
  paper_copies: [{ required: true, message: '请输入纸质份数', trigger: 'blur' }],
}

const archiveMedium = computed<ArchiveMedium>(() =>
  route.meta.archiveMedium === 'electronic' ? 'electronic' : 'paper',
)
const isPaperArchive = computed(() => archiveMedium.value === 'paper')
const pageTitle = computed(() =>
  isPaperArchive.value ? '纸质档案管理' : '电子档案管理',
)
const pageSubtitle = computed(() =>
  isPaperArchive.value
    ? '管理纸质档案目录、纸质份数、归档部门与存放位置'
    : '管理电子档案目录、归档部门与电子存储路径',
)
const dialogTitle = computed(() =>
  dialogMode.value === 'create' ? '新建档案' : '编辑档案',
)
const selectedArchiveIds = computed(() => selectedArchives.value.map((item) => item.id))
const selectableArchiveTypes = computed(() =>
  options.value.archive_types.filter(
    (item) => item.enabled || item.id === form.archive_type_id,
  ),
)
const selectableRetentionPeriods = computed(() =>
  options.value.retention_periods.filter(
    (item) => item.enabled || item.id === form.retention_period_id,
  ),
)
const selectableDepartments = computed(() =>
  options.value.departments.filter(
    (item) => item.enabled || item.id === form.department_id,
  ),
)

function getErrorMessage(error: unknown, fallback = '请求失败') {
  return error instanceof Error ? error.message : fallback
}

function formatDate(value: string | null) {
  return value || '-'
}

function optionLabel(name: string, enabled: boolean) {
  return enabled ? name : `${name}（停用）`
}

function emptyToNull(value: string) {
  const trimmed = value.trim()
  return trimmed || null
}

function buildParams(): ArchiveListParams {
  return {
    keyword: filters.keyword.trim() || undefined,
    archive_medium: archiveMedium.value,
    internal_archive_type: filters.internal_archive_type.trim() || undefined,
    department_id: filters.department_id,
    status_id: filters.status_id,
    page: filters.page,
    page_size: filters.page_size,
  }
}

function buildExportParams() {
  return {
    keyword: filters.keyword.trim() || undefined,
    archive_medium: archiveMedium.value,
    internal_archive_type: filters.internal_archive_type.trim() || undefined,
    department_id: filters.department_id,
    status_id: filters.status_id,
  }
}

function statusTagType(statusName: string) {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    在库: 'primary',
    借出: 'success',
    待归档: 'warning',
    待审核: 'info',
    已归档: 'info',
    已销毁: 'danger',
  }
  return map[statusName] || 'info'
}

async function loadOptions() {
  const response = await getArchiveOptions()
  options.value = response.data
}

async function loadArchives() {
  loading.value = true
  try {
    const response = await getArchives(buildParams())
    archives.value = response.data.items
    total.value = response.data.total
    selectedArchives.value = []
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '档案列表加载失败'))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  filters.page = 1
  loadArchives()
}

function handleReset() {
  filters.keyword = ''
  filters.internal_archive_type = ''
  filters.department_id = undefined
  filters.status_id = undefined
  filters.page = 1
  loadArchives()
}

function handleSizeChange() {
  filters.page = 1
  loadArchives()
}

function handleSelectionChange(selection: ArchiveItem[]) {
  selectedArchives.value = selection
}

function resetForm() {
  const enabledArchiveTypes = options.value.archive_types.filter((item) => item.enabled)
  const enabledRetentionPeriods = options.value.retention_periods.filter(
    (item) => item.enabled,
  )
  const enabledDepartments = options.value.departments.filter((item) => item.enabled)
  Object.assign(form, {
    archive_no: '',
    title: '',
    archive_type_id: enabledArchiveTypes[0]?.id,
    internal_archive_type: '',
    status_id: options.value.statuses[0]?.id,
    retention_period_id: enabledRetentionPeriods[0]?.id,
    department_id: enabledDepartments[0]?.id,
    paper_copies: 1,
    archive_date: null,
    paper_storage_location: '',
    electronic_storage_path: '',
    archiver_name: '',
    owner_name: '',
    archive_year: undefined,
    security_level: '内部',
    importance_level: '普通',
    project_name: '',
    related_party: '',
    contract_no: '',
    keywords: '',
    remarks: '',
  })
  formRef.value?.clearValidate()
}

function fillForm(archive: ArchiveItem) {
  Object.assign(form, {
    archive_no: archive.archive_no,
    title: archive.title,
    archive_type_id: archive.archive_type.id,
    internal_archive_type: archive.internal_archive_type,
    status_id: archive.status.id,
    retention_period_id: archive.retention_period.id,
    department_id: archive.department.id,
    paper_copies: archive.paper_copies,
    archive_date: archive.archive_date,
    paper_storage_location: archive.paper_storage_location || '',
    electronic_storage_path: archive.electronic_storage_path || '',
    archiver_name: archive.archiver_name || '',
    owner_name: archive.owner_name || '',
    archive_year: archive.archive_year || undefined,
    security_level: archive.security_level || '',
    importance_level: archive.importance_level || '',
    project_name: archive.project_name || '',
    related_party: archive.related_party || '',
    contract_no: archive.contract_no || '',
    keywords: archive.keywords || '',
    remarks: archive.remarks || '',
  })
  formRef.value?.clearValidate()
}

function openCreateDialog() {
  dialogMode.value = 'create'
  editingArchiveId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(archive: ArchiveItem) {
  dialogMode.value = 'edit'
  editingArchiveId.value = archive.id
  fillForm(archive)
  dialogVisible.value = true
}

function buildArchivePayload(): ArchivePayload {
  return {
    archive_no: form.archive_no.trim(),
    title: form.title.trim(),
    archive_medium: archiveMedium.value,
    archive_type_id: Number(form.archive_type_id),
    internal_archive_type: form.internal_archive_type.trim(),
    status_id: Number(form.status_id),
    retention_period_id: Number(form.retention_period_id),
    department_id: Number(form.department_id),
    paper_copies: isPaperArchive.value ? Number(form.paper_copies) : 0,
    archive_date: form.archive_date,
    paper_storage_location: isPaperArchive.value
      ? emptyToNull(form.paper_storage_location)
      : null,
    electronic_storage_path: isPaperArchive.value
      ? null
      : emptyToNull(form.electronic_storage_path),
    archiver_name: emptyToNull(form.archiver_name),
    owner_name: emptyToNull(form.owner_name),
    archive_year: form.archive_year || null,
    security_level: emptyToNull(form.security_level),
    importance_level: emptyToNull(form.importance_level),
    project_name: emptyToNull(form.project_name),
    related_party: emptyToNull(form.related_party),
    contract_no: emptyToNull(form.contract_no),
    keywords: emptyToNull(form.keywords),
    remarks: emptyToNull(form.remarks),
  }
}

async function submitArchive() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }

  saving.value = true
  try {
    if (dialogMode.value === 'create') {
      await createArchive(buildArchivePayload())
      ElMessage.success('档案已新建')
    } else if (editingArchiveId.value) {
      await updateArchive(editingArchiveId.value, buildArchivePayload())
      ElMessage.success('档案已更新')
    }
    dialogVisible.value = false
    await loadArchives()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function openDetailDialog(archive: ArchiveItem) {
  detailVisible.value = true
  detailLoading.value = true
  currentArchive.value = null
  try {
    const response = await getArchive(archive.id)
    currentArchive.value = response.data
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '档案详情加载失败'))
    detailVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

async function handleDeleteArchive(archive: ArchiveItem) {
  try {
    await ElMessageBox.confirm(
      `确认删除档案「${archive.title}」？删除后将不再出现在列表中。`,
      '删除档案',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  deleting.value = true
  try {
    await deleteArchive(archive.id)
    ElMessage.success('档案已删除')
    await loadArchives()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '删除失败'))
  } finally {
    deleting.value = false
  }
}

async function handleBatchDelete() {
  if (!selectedArchiveIds.value.length) {
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认删除当前已选的 ${selectedArchiveIds.value.length} 条档案？`,
      '批量删除档案',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  deleting.value = true
  try {
    await batchDeleteArchives(selectedArchiveIds.value)
    ElMessage.success('已批量删除')
    await loadArchives()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '批量删除失败'))
  } finally {
    deleting.value = false
  }
}

function exportFilename() {
  const timestamp = new Date()
    .toISOString()
    .replace(/[-:]/g, '')
    .replace('T', '_')
    .slice(0, 15)
  const prefix = isPaperArchive.value ? '纸质档案目录' : '电子档案目录'
  return `${prefix}_${timestamp}.xlsx`
}

async function handleExport() {
  exporting.value = true
  try {
    const blob = await exportArchives(buildExportParams())
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = exportFilename()
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出文件已生成')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '导出失败'))
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  try {
    await loadOptions()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '筛选选项加载失败'))
  }
  await loadArchives()
})

watch(archiveMedium, async () => {
  handleReset()
  resetForm()
})
</script>

<template>
  <section class="page archive-page">
    <div class="page-header">
      <div>
        <h1>{{ pageTitle }}</h1>
        <p>{{ pageSubtitle }}</p>
      </div>
      <div class="page-actions">
        <el-button
          v-if="authStore.isAdmin"
          :icon="Delete"
          :loading="deleting"
          :disabled="!selectedArchiveIds.length"
          type="danger"
          plain
          @click="handleBatchDelete"
        >
          批量删除
        </el-button>
        <el-button :icon="Download" :loading="exporting" @click="handleExport">
          导出Excel
        </el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          新建档案
        </el-button>
      </div>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16">
        <el-col :xs="24" :md="10">
          <label class="filter-label">关键词搜索</label>
          <el-input
            v-model="filters.keyword"
            :prefix-icon="Search"
            clearable
            placeholder="输入档案名称或编号..."
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :md="4">
          <label class="filter-label">内部档案类型</label>
          <el-input
            v-model="filters.internal_archive_type"
            :prefix-icon="Search"
            clearable
            placeholder="输入内部类型"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :md="4">
          <label class="filter-label">归档部门</label>
          <el-select
            v-model="filters.department_id"
            clearable
            placeholder="全部归档部门"
            @change="handleSearch"
          >
            <el-option
              v-for="item in options.departments"
              :key="item.id"
              :label="optionLabel(item.name, item.enabled)"
              :value="item.id"
            />
          </el-select>
        </el-col>
        <el-col :xs="24" :md="4">
          <label class="filter-label">状态</label>
          <el-select
            v-model="filters.status_id"
            clearable
            placeholder="全部状态"
            @change="handleSearch"
          >
            <el-option
              v-for="item in options.statuses"
              :key="item.id"
              :label="optionLabel(item.name, item.enabled)"
              :value="item.id"
            />
          </el-select>
        </el-col>
        <el-col :xs="24" :md="2" class="filter-reset-col">
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="archives"
        row-key="id"
        @selection-change="handleSelectionChange"
      >
        <el-table-column v-if="authStore.isAdmin" type="selection" width="48" />
        <el-table-column prop="archive_no" label="档案编号" min-width="150" />
        <el-table-column prop="title" label="档案名称" min-width="220" />
        <el-table-column
          v-if="isPaperArchive"
          prop="paper_copies"
          label="纸质份数"
          min-width="100"
        />
        <el-table-column label="档案类型" min-width="120">
          <template #default="{ row }">
            {{ row.archive_type.name }}
          </template>
        </el-table-column>
        <el-table-column
          prop="internal_archive_type"
          label="内部档案类型"
          min-width="150"
        />
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status.name)" effect="dark">
              {{ row.status.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="保管期限" min-width="110">
          <template #default="{ row }">
            {{ row.retention_period.name }}
          </template>
        </el-table-column>
        <el-table-column label="归档部门" min-width="160">
          <template #default="{ row }">
            {{ row.department.name }}
          </template>
        </el-table-column>
        <el-table-column label="归档人" min-width="110">
          <template #default="{ row }">
            {{ row.archiver_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="归档日期" min-width="120">
          <template #default="{ row }">
            {{ formatDate(row.archive_date) }}
          </template>
        </el-table-column>
        <el-table-column
          v-if="isPaperArchive"
          prop="paper_storage_location"
          label="存放位置"
          min-width="140"
        />
        <el-table-column
          v-else
          prop="electronic_storage_path"
          label="存放路径"
          min-width="220"
        />
        <el-table-column prop="owner_name" label="责任人" min-width="100" />
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="查看详情" placement="top">
                <el-button :icon="View" text @click="openDetailDialog(row)" />
              </el-tooltip>
              <el-tooltip content="编辑档案" placement="top">
                <el-button :icon="Edit" text @click="openEditDialog(row)" />
              </el-tooltip>
              <el-tooltip v-if="authStore.isAdmin" content="删除档案" placement="top">
                <el-button
                  :icon="Delete"
                  text
                  type="danger"
                  @click="handleDeleteArchive(row)"
                />
              </el-tooltip>
            </div>
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
          @current-change="loadArchives"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="760px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item label="档案编号" prop="archive_no">
              <el-input v-model="form.archive_no" placeholder="如 DA-2020-0001" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="档案名称" prop="title">
              <el-input v-model="form.title" placeholder="请输入档案名称" />
            </el-form-item>
          </el-col>
          <el-col v-if="isPaperArchive" :xs="24" :md="12">
            <el-form-item label="纸质份数" prop="paper_copies">
              <el-input-number v-model="form.paper_copies" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="档案类型" prop="archive_type_id">
              <el-select v-model="form.archive_type_id" placeholder="请选择档案类型">
                <el-option
                  v-for="item in selectableArchiveTypes"
                  :key="item.id"
                  :label="optionLabel(item.name, item.enabled)"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="内部档案类型" prop="internal_archive_type">
              <el-input
                v-model="form.internal_archive_type"
                placeholder="请输入内部档案类型"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="状态" prop="status_id">
              <el-select v-model="form.status_id" placeholder="请选择状态">
                <el-option
                  v-for="item in options.statuses"
                  :key="item.id"
                  :label="optionLabel(item.name, item.enabled)"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="保管期限" prop="retention_period_id">
              <el-select v-model="form.retention_period_id" placeholder="请选择保管期限">
                <el-option
                  v-for="item in selectableRetentionPeriods"
                  :key="item.id"
                  :label="optionLabel(item.name, item.enabled)"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="归档部门" prop="department_id">
              <el-select v-model="form.department_id" placeholder="请选择归档部门">
                <el-option
                  v-for="item in selectableDepartments"
                  :key="item.id"
                  :label="optionLabel(item.name, item.enabled)"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="归档人">
              <el-input v-model="form.archiver_name" placeholder="请输入归档人" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="归档日期">
              <el-date-picker
                v-model="form.archive_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item v-if="isPaperArchive" label="存放位置">
              <el-input
                v-model="form.paper_storage_location"
                placeholder="如 A区-01柜"
              />
            </el-form-item>
            <el-form-item v-else label="存放路径">
              <el-input
                v-model="form.electronic_storage_path"
                placeholder="如 /archives/2026/..."
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="责任人">
              <el-input v-model="form.owner_name" placeholder="请输入责任人" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="档案年度">
              <el-input-number v-model="form.archive_year" :min="1900" :max="2100" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="密级">
              <el-input v-model="form.security_level" placeholder="如 内部" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="重要程度">
              <el-input v-model="form.importance_level" placeholder="如 普通" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="项目">
              <el-input v-model="form.project_name" placeholder="请输入项目名称" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="关联单位">
              <el-input v-model="form.related_party" placeholder="请输入关联单位" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="合同编号">
              <el-input v-model="form.contract_no" placeholder="请输入合同编号" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="关键词">
              <el-input v-model="form.keywords" placeholder="请输入关键词" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input
                v-model="form.remarks"
                type="textarea"
                :rows="3"
                placeholder="请输入备注"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitArchive">
          保存
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="档案详情" width="760px">
      <el-skeleton v-if="detailLoading" :rows="6" animated />
      <el-descriptions
        v-else-if="currentArchive"
        class="archive-descriptions"
        :column="2"
        border
      >
        <el-descriptions-item label="档案编号">
          {{ currentArchive.archive_no }}
        </el-descriptions-item>
        <el-descriptions-item label="档案名称">
          {{ currentArchive.title }}
        </el-descriptions-item>
        <el-descriptions-item v-if="isPaperArchive" label="纸质份数">
          {{ currentArchive.paper_copies }}
        </el-descriptions-item>
        <el-descriptions-item label="档案类型">
          {{ currentArchive.archive_type.name }}
        </el-descriptions-item>
        <el-descriptions-item label="内部档案类型">
          {{ currentArchive.internal_archive_type }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTagType(currentArchive.status.name)" effect="dark">
            {{ currentArchive.status.name }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="保管期限">
          {{ currentArchive.retention_period.name }}
        </el-descriptions-item>
        <el-descriptions-item label="归档部门">
          {{ currentArchive.department.name }}
        </el-descriptions-item>
        <el-descriptions-item label="归档人">
          {{ currentArchive.archiver_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="归档日期">
          {{ formatDate(currentArchive.archive_date) }}
        </el-descriptions-item>
        <el-descriptions-item v-if="isPaperArchive" label="存放位置">
          {{ currentArchive.paper_storage_location || '-' }}
        </el-descriptions-item>
        <el-descriptions-item v-else label="存放路径">
          {{ currentArchive.electronic_storage_path || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="责任人">
          {{ currentArchive.owner_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="档案年度">
          {{ currentArchive.archive_year || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="密级">
          {{ currentArchive.security_level || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="重要程度">
          {{ currentArchive.importance_level || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="项目">
          {{ currentArchive.project_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="关联单位">
          {{ currentArchive.related_party || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="合同编号">
          {{ currentArchive.contract_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="关键词">
          {{ currentArchive.keywords || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentArchive.remarks || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </section>
</template>
