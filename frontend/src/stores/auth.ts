import { defineStore } from 'pinia'

import { getCurrentUser, login, type LoginPayload } from '@/api/auth'
import {
  clearAuthToken,
  getAuthToken,
  setAuthToken,
} from '@/api/request'
import type { UserItem } from '@/api/users'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getAuthToken(),
    currentUser: null as UserItem | null,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    isAdmin: (state) => state.currentUser?.role.code === 'admin',
  },
  actions: {
    async login(payload: LoginPayload) {
      this.loading = true
      try {
        const response = await login(payload)
        this.token = response.data.access_token
        this.currentUser = response.data.user
        setAuthToken(response.data.access_token)
      } finally {
        this.loading = false
      }
    },
    async fetchCurrentUser() {
      if (!this.token) {
        return
      }
      const response = await getCurrentUser()
      this.currentUser = response.data
    },
    logout() {
      this.token = null
      this.currentUser = null
      clearAuthToken()
    },
  },
})
