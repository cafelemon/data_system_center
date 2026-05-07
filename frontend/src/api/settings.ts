import { request, type ApiResponse } from './request'

export interface ArchiveTypeConfig {
  id: number
  name: string
  code: string
  enabled: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ArchiveTypeListResponse {
  items: ArchiveTypeConfig[]
}

export interface ArchiveTypePayload {
  name: string
  code: string
  enabled: boolean
  sort_order?: number
}

export interface RetentionPeriodConfig {
  id: number
  name: string
  years: number
  enabled: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface RetentionPeriodListResponse {
  items: RetentionPeriodConfig[]
}

export interface RetentionPeriodPayload {
  name: string
  years: number
  enabled: boolean
  sort_order?: number
}

export function getArchiveTypes() {
  return request.get<ArchiveTypeListResponse, ApiResponse<ArchiveTypeListResponse>>(
    '/api/settings/archive-types',
  )
}

export function createArchiveType(payload: ArchiveTypePayload) {
  return request.post<ArchiveTypeConfig, ApiResponse<ArchiveTypeConfig>>(
    '/api/settings/archive-types',
    payload,
  )
}

export function updateArchiveType(id: number, payload: ArchiveTypePayload) {
  return request.put<ArchiveTypeConfig, ApiResponse<ArchiveTypeConfig>>(
    `/api/settings/archive-types/${id}`,
    payload,
  )
}

export function updateArchiveTypeStatus(id: number, enabled: boolean) {
  return request.patch<ArchiveTypeConfig, ApiResponse<ArchiveTypeConfig>>(
    `/api/settings/archive-types/${id}/status`,
    { enabled },
  )
}

export function deleteArchiveType(id: number) {
  return request.delete<ArchiveTypeConfig, ApiResponse<ArchiveTypeConfig>>(
    `/api/settings/archive-types/${id}`,
  )
}

export function getRetentionPeriods() {
  return request.get<
    RetentionPeriodListResponse,
    ApiResponse<RetentionPeriodListResponse>
  >('/api/settings/retention-periods')
}

export function createRetentionPeriod(payload: RetentionPeriodPayload) {
  return request.post<RetentionPeriodConfig, ApiResponse<RetentionPeriodConfig>>(
    '/api/settings/retention-periods',
    payload,
  )
}

export function updateRetentionPeriod(id: number, payload: RetentionPeriodPayload) {
  return request.put<RetentionPeriodConfig, ApiResponse<RetentionPeriodConfig>>(
    `/api/settings/retention-periods/${id}`,
    payload,
  )
}

export function updateRetentionPeriodStatus(id: number, enabled: boolean) {
  return request.patch<RetentionPeriodConfig, ApiResponse<RetentionPeriodConfig>>(
    `/api/settings/retention-periods/${id}/status`,
    { enabled },
  )
}

export function deleteRetentionPeriod(id: number) {
  return request.delete<RetentionPeriodConfig, ApiResponse<RetentionPeriodConfig>>(
    `/api/settings/retention-periods/${id}`,
  )
}
