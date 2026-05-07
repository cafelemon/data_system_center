<script setup lang="ts">
import {
  DataAnalysis,
  Document,
  Fold,
  Setting,
  SwitchButton,
  User,
} from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const menus = [
  { path: '/archives', label: '档案列表', icon: Document },
  { path: '/users', label: '用户管理', icon: User, requiresAdmin: true },
  { path: '/settings', label: '系统设置', icon: Setting },
  { path: '/statistics', label: '数据统计', icon: DataAnalysis },
]

const visibleMenus = computed(() =>
  menus.filter((item) => !item.requiresAdmin || authStore.isAdmin),
)

function handleSelect(path: string) {
  router.push(path)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="shell">
    <el-aside :width="appStore.sidebarCollapsed ? '72px' : '256px'" class="sidebar">
      <div class="brand" :class="{ collapsed: appStore.sidebarCollapsed }">
        <div class="brand-icon">
          <el-icon :size="22"><Document /></el-icon>
        </div>
        <div v-if="!appStore.sidebarCollapsed" class="brand-copy">
          <strong>档案管理系统</strong>
          <span>Archive System</span>
        </div>
      </div>

      <el-menu
        :collapse="appStore.sidebarCollapsed"
        :default-active="activeMenu"
        class="side-menu"
        router
        @select="handleSelect"
      >
        <el-menu-item v-for="item in visibleMenus" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.label }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <el-button
          class="collapse-button"
          :icon="Fold"
          text
          @click="appStore.toggleSidebar"
        />
        <span class="topbar-title">档案管理系统</span>
        <div class="topbar-spacer" />
        <div class="topbar-user" v-if="authStore.currentUser">
          <span>{{ authStore.currentUser.real_name }}</span>
          <el-tag size="small" effect="light">
            {{ authStore.currentUser.role.name }}
          </el-tag>
          <el-button :icon="SwitchButton" text @click="handleLogout">退出</el-button>
        </div>
      </el-header>

      <el-main class="content">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>
