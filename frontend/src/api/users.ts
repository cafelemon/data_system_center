import { request, type ApiResponse } from './request'

export type UserStatus = 'enabled' | 'disabled'

export interface RoleInfo {
  id: number
  name: string
  code: string
  enabled: boolean
}

export interface DepartmentInfo {
  id: number
  name: string
  code: string
  enabled: boolean
}

export interface UserItem {
  id: number
  username: string
  real_name: string
  email: string
  status: UserStatus
  role: RoleInfo
  department: DepartmentInfo
  created_at: string
  updated_at: string
}

export interface UserListParams {
  keyword?: string
  role_id?: number
  status?: UserStatus
  department_id?: number
  page: number
  page_size: number
}

export interface UserListResponse {
  items: UserItem[]
  total: number
  page: number
  page_size: number
}

export interface SelectOption {
  id: number
  name: string
  code: string
}

export interface StatusOption {
  label: string
  value: UserStatus
}

export interface UserOptionsResponse {
  roles: SelectOption[]
  departments: SelectOption[]
  statuses: StatusOption[]
}

export interface UserPayload {
  username?: string
  real_name: string
  email: string
  role_id: number
  department_id: number
  status: UserStatus
  password?: string
}

export function getUsers(params: UserListParams) {
  return request.get<UserListResponse, ApiResponse<UserListResponse>>('/api/users', {
    params,
  })
}

export function getUserOptions() {
  return request.get<UserOptionsResponse, ApiResponse<UserOptionsResponse>>(
    '/api/users/options',
  )
}

export function createUser(payload: UserPayload) {
  return request.post<UserItem, ApiResponse<UserItem>>('/api/users', payload)
}

export function updateUser(userId: number, payload: UserPayload) {
  return request.put<UserItem, ApiResponse<UserItem>>(`/api/users/${userId}`, payload)
}

export function updateUserStatus(userId: number, status: UserStatus) {
  return request.patch<UserItem, ApiResponse<UserItem>>(`/api/users/${userId}/status`, {
    status,
  })
}
