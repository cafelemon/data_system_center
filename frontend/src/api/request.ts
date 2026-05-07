import axios, { type AxiosError } from 'axios'

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export const AUTH_TOKEN_KEY = 'archive-system-token'

export function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY)
}

export function setAuthToken(token: string) {
  localStorage.setItem(AUTH_TOKEN_KEY, token)
}

export function clearAuthToken() {
  localStorage.removeItem(AUTH_TOKEN_KEY)
}

export const request = axios.create({
  baseURL: '/',
  timeout: 10000,
})

request.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError<ApiResponse<unknown>>) => {
    const statusCode = error.response?.status
    const message = error.response?.data?.message || error.message || '请求失败'

    if (statusCode === 401) {
      clearAuthToken()
      if (window.location.pathname !== '/login') {
        const currentPath = `${window.location.pathname}${window.location.search}`
        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`
      }
    }

    return Promise.reject(new Error(message))
  },
)
