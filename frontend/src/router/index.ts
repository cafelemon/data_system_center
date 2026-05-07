import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import ArchiveListView from '@/views/ArchiveListView.vue'
import MainLayout from '@/layouts/MainLayout.vue'
import FoundationView from '@/views/FoundationView.vue'
import LoginView from '@/views/LoginView.vue'
import SystemSettingsView from '@/views/SystemSettingsView.vue'
import UserManagementView from '@/views/UserManagementView.vue'
import { useAuthStore } from '@/stores/auth'

export const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      public: true,
    },
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/archives',
    children: [
      {
        path: 'archives',
        name: 'archives',
        component: ArchiveListView,
        meta: {
          title: '档案列表',
          subtitle: '管理系统中的所有档案记录，支持检索、筛选与导出',
        },
      },
      {
        path: 'users',
        name: 'users',
        component: UserManagementView,
        meta: {
          title: '用户管理',
          subtitle: '管理系统用户账号与权限配置',
          requiresAdmin: true,
        },
      },
      {
        path: 'settings',
        name: 'settings',
        component: SystemSettingsView,
        meta: {
          title: '系统设置',
          subtitle: '管理档案类型、保管期限等基础字典配置',
          requiresAdmin: true,
        },
      },
      {
        path: 'statistics',
        name: 'statistics',
        component: FoundationView,
        meta: {
          title: '数据统计',
          subtitle: '档案资产概况与分布趋势分析',
        },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (to.meta.public) {
    if (to.path === '/login' && authStore.token) {
      if (!authStore.currentUser) {
        try {
          await authStore.fetchCurrentUser()
        } catch {
          authStore.logout()
          return true
        }
      }
      return String(to.query.redirect || '/archives')
    }
    return true
  }

  if (!authStore.token) {
    return {
      path: '/login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (!authStore.currentUser) {
    try {
      await authStore.fetchCurrentUser()
    } catch {
      authStore.logout()
      return {
        path: '/login',
        query: {
          redirect: to.fullPath,
        },
      }
    }
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return '/archives'
  }

  return true
})

export default router
