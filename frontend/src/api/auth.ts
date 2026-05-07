import { request, type ApiResponse } from './request'
import type { UserItem } from './users'

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
  user: UserItem
}

export function login(payload: LoginPayload) {
  return request.post<LoginResponse, ApiResponse<LoginResponse>>(
    '/api/auth/login',
    payload,
  )
}

export function getCurrentUser() {
  return request.get<UserItem, ApiResponse<UserItem>>('/api/auth/me')
}
