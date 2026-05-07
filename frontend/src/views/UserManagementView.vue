<script setup lang="ts">
import { Edit, Plus, Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import {
  createUser,
  getUserOptions,
  getUsers,
  updateUser,
  updateUserStatus,
  type UserItem,
  type UserListParams,
  type UserOptionsResponse,
  type UserPayload,
  type UserStatus,
} from '@/api/users'
import { useAuthStore } from '@/stores/auth'

type DialogMode = 'create' | 'edit'

interface UserFilters {
  keyword: string
  role_id?: number
  status: UserStatus | ''
  department_id?: number
  page: number
  page_size: number
}

interface UserFormState {
  username: string
  real_name: string
  email: string
  role_id?: number
  department_id?: number
  status: UserStatus
  password: string
}

const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<DialogMode>('create')
const editingUserId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const users = ref<UserItem[]>([])
const total = ref(0)
const options = ref<UserOptionsResponse>({
  roles: [],
  departments: [],
  statuses: [
    { label: '启用', value: 'enabled' },
    { label: '禁用', value: 'disabled' },
  ],
})

const filters = reactive<UserFilters>({
  keyword: '',
  status: '',
  page: 1,
  page_size: 10,
})

const form = reactive<UserFormState>({
  username: '',
  real_name: '',
  email: '',
  status: 'enabled',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }],
  department_id: [{ required: true, message: '请选择部门', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

const dialogTitle = computed(() =>
  dialogMode.value === 'create' ? '新增用户' : '编辑用户',
)

function getErrorMessage(error: unknown, fallback = '请求失败') {
  return error instanceof Error ? error.message : fallback
}

function formatDate(value: string) {
  return value.slice(0, 10)
}

function userInitials(user: UserItem) {
  return user.real_name.slice(0, 1).toUpperCase()
}

function buildParams(): UserListParams {
  return {
    keyword: filters.keyword.trim() || undefined,
    role_id: filters.role_id,
    status: (filters.status || undefined) as UserStatus | undefined,
    department_id: filters.department_id,
    page: filters.page,
    page_size: filters.page_size,
  }
}

async function loadOptions() {
  const response = await getUserOptions()
  options.value = response.data
}

async function loadUsers() {
  loading.value = true
  try {
    const response = await getUsers(buildParams())
    users.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '用户列表加载失败'))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  filters.page = 1
  loadUsers()
}

function handleReset() {
  filters.keyword = ''
  filters.role_id = undefined
  filters.status = ''
  filters.department_id = undefined
  filters.page = 1
  loadUsers()
}

function handleSizeChange() {
  filters.page = 1
  loadUsers()
}

function resetForm() {
  Object.assign(form, {
    username: '',
    real_name: '',
    email: '',
    role_id: options.value.roles[0]?.id,
    department_id: options.value.departments[0]?.id,
    status: 'enabled',
    password: '',
  })
  formRef.value?.clearValidate()
}

function openCreateDialog() {
  dialogMode.value = 'create'
  editingUserId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(user: UserItem) {
  dialogMode.value = 'edit'
  editingUserId.value = user.id
  Object.assign(form, {
    username: user.username,
    real_name: user.real_name,
    email: user.email,
    role_id: user.role.id,
    department_id: user.department.id,
    status: user.status,
    password: '',
  })
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

function buildUserPayload() {
  const payload: UserPayload = {
    real_name: form.real_name.trim(),
    email: form.email.trim(),
    role_id: Number(form.role_id),
    department_id: Number(form.department_id),
    status: form.status,
  }
  if (dialogMode.value === 'create') {
    payload.username = form.username.trim()
  }
  if (form.password.trim()) {
    payload.password = form.password
  }
  return payload
}

async function submitUser() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }

  saving.value = true
  try {
    if (dialogMode.value === 'create') {
      await createUser(buildUserPayload())
      ElMessage.success('用户已新增')
    } else if (editingUserId.value) {
      await updateUser(editingUserId.value, buildUserPayload())
      ElMessage.success('用户已更新')
    }
    dialogVisible.value = false
    await loadUsers()
    if (editingUserId.value === authStore.currentUser?.id) {
      await authStore.fetchCurrentUser()
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function handleStatusChange(user: UserItem, enabled: boolean) {
  const nextStatus: UserStatus = enabled ? 'enabled' : 'disabled'
  if (user.status === nextStatus) {
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认${enabled ? '启用' : '禁用'}用户“${user.real_name}”？`,
      '调整用户状态',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: enabled ? 'info' : 'warning',
      },
    )
    await updateUserStatus(user.id, nextStatus)
    ElMessage.success('用户状态已更新')
    await loadUsers()
  } catch (error) {
    if (error instanceof Error) {
      ElMessage.error(error.message)
    }
  }
}

function handleSwitchChange(user: UserItem, value: string | number | boolean) {
  handleStatusChange(user, Boolean(value))
}

onMounted(async () => {
  try {
    await loadOptions()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '筛选选项加载失败'))
  }
  await loadUsers()
})
</script>

<template>
  <section class="page user-page">
    <div class="page-header">
      <div>
        <h1>用户管理</h1>
        <p>管理系统用户账号与权限配置</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">
        新增用户
      </el-button>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16">
        <el-col :xs="24" :md="9">
          <el-input
            v-model="filters.keyword"
            :prefix-icon="Search"
            clearable
            placeholder="搜索用户名、邮箱或部门..."
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :md="5">
          <el-select
            v-model="filters.role_id"
            clearable
            placeholder="全部角色"
            @change="handleSearch"
          >
            <el-option
              v-for="role in options.roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-col>
        <el-col :xs="24" :md="5">
          <el-select
            v-model="filters.status"
            clearable
            placeholder="全部状态"
            @change="handleSearch"
          >
            <el-option
              v-for="status in options.statuses"
              :key="status.value"
              :label="status.label"
              :value="status.value"
            />
          </el-select>
        </el-col>
        <el-col :xs="24" :md="5">
          <el-select
            v-model="filters.department_id"
            clearable
            placeholder="全部部门"
            @change="handleSearch"
          >
            <el-option
              v-for="department in options.departments"
              :key="department.id"
              :label="department.name"
              :value="department.id"
            />
          </el-select>
        </el-col>
      </el-row>
      <div class="filter-actions">
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
      </div>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="users" row-key="id">
        <el-table-column label="用户名" min-width="180">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="32">{{ userInitials(row) }}</el-avatar>
              <div>
                <strong>{{ row.real_name }}</strong>
                <span>{{ row.username }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="角色" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.role.code === 'admin' ? 'primary' : 'info'" effect="light">
              {{ row.role.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="部门" prop="department.name" min-width="150" />
        <el-table-column label="邮箱" prop="email" min-width="220" />
        <el-table-column label="状态" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'enabled' ? 'success' : 'danger'" effect="light">
              {{ row.status === 'enabled' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="140">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="编辑用户" placement="top">
                <el-button :icon="Edit" text @click="openEditDialog(row)" />
              </el-tooltip>
              <el-tooltip
                :content="row.id === authStore.currentUser?.id ? '不能禁用当前账号' : '启用/禁用'"
                placement="top"
              >
                <el-switch
                  :model-value="row.status === 'enabled'"
                  :disabled="row.id === authStore.currentUser?.id"
                  @change="handleSwitchChange(row, $event)"
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
          @current-change="loadUsers"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px">
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            :disabled="dialogMode === 'edit'"
            placeholder="请输入用户名"
          />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="form.role_id" placeholder="请选择角色">
            <el-option
              v-for="role in options.roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="部门" prop="department_id">
          <el-select v-model="form.department_id" placeholder="请选择部门">
            <el-option
              v-for="department in options.departments"
              :key="department.id"
              :label="department.name"
              :value="department.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio-button label="enabled">启用</el-radio-button>
            <el-radio-button label="disabled">禁用</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            placeholder="留空则使用默认密码或保持原密码"
            show-password
            type="password"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitUser">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>
