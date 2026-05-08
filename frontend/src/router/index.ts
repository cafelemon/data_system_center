import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import ArchiveListView from '@/views/ArchiveListView.vue'
import MainLayout from '@/layouts/MainLayout.vue'
import LoginView from '@/views/LoginView.vue'
import OperationLogsView from '@/views/OperationLogsView.vue'
import StatisticsView from '@/views/StatisticsView.vue'
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
    redirect: '/paper-archives',
    children: [
      {
        path: 'archives',
        redirect: '/paper-archives',
      },
      {
        path: 'paper-archives',
        name: 'paper-archives',
        component: ArchiveListView,
        meta: {
          title: '纸质档案管理',
          subtitle: '管理纸质档案目录、纸质份数、归档部门与存放位置',
          archiveMedium: 'paper',
        },
      },
      {
        path: 'electronic-archives',
        name: 'electronic-archives',
        component: ArchiveListView,
        meta: {
          title: '电子档案管理',
          subtitle: '管理电子档案目录、归档部门与电子存储路径',
          archiveMedium: 'electronic',
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
        component: StatisticsView,
        meta: {
          title: '数据统计',
          subtitle: '档案资产概况与分布趋势分析',
        },
      },
      {
        path: 'operation-logs',
        name: 'operation-logs',
        component: OperationLogsView,
        meta: {
          title: '操作日志',
          subtitle: '查看系统关键操作、登录、导出和配置修改记录',
          requiresAdmin: true,
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
      return String(to.query.redirect || '/paper-archives')
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
    return '/paper-archives'
  }

  return true
})

export default router
