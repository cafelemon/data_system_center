import { request, type ApiResponse } from './request'

export type ArchiveMedium = 'paper' | 'electronic'

export interface LookupItem {
  id: number
  name: string
  code: string
  enabled: boolean
}

export interface RetentionPeriodItem {
  id: number
  name: string
  years: number
  enabled: boolean
}

export interface ArchiveItem {
  id: number
  archive_no: string
  title: string
  archive_type: LookupItem
  status: LookupItem
  retention_period: RetentionPeriodItem
  department: LookupItem
  archive_medium: ArchiveMedium
  internal_archive_type: string
  paper_copies: number
  archive_date: string | null
  paper_storage_location: string | null
  electronic_storage_path: string | null
  archiver_name: string | null
  owner_name: string | null
  archive_year: number | null
  security_level: string | null
  importance_level: string | null
  project_name: string | null
  related_party: string | null
  contract_no: string | null
  keywords: string | null
  remarks: string | null
  created_at: string
  updated_at: string
}

export interface ArchiveListParams {
  keyword?: string
  archive_medium: ArchiveMedium
  internal_archive_type?: string
  archive_type_id?: number
  department_id?: number
  status_id?: number
  page: number
  page_size: number
}

export type ArchiveExportParams = Omit<ArchiveListParams, 'page' | 'page_size'>

export interface ArchiveListResponse {
  items: ArchiveItem[]
  total: number
  page: number
  page_size: number
}

export interface ArchiveOptionsResponse {
  archive_types: LookupItem[]
  statuses: LookupItem[]
  departments: LookupItem[]
  retention_periods: RetentionPeriodItem[]
}

export interface ArchivePayload {
  archive_no: string
  title: string
  archive_medium: ArchiveMedium
  archive_type_id: number
  internal_archive_type: string
  status_id: number
  retention_period_id: number
  department_id: number
  paper_copies: number
  archive_date: string | null
  paper_storage_location: string | null
  electronic_storage_path: string | null
  archiver_name: string | null
  owner_name: string | null
  archive_year: number | null
  security_level: string | null
  importance_level: string | null
  project_name: string | null
  related_party: string | null
  contract_no: string | null
  keywords: string | null
  remarks: string | null
}

export function getArchives(params: ArchiveListParams) {
  return request.get<ArchiveListResponse, ApiResponse<ArchiveListResponse>>(
    '/api/archives',
    {
      params,
    },
  )
}

export function exportArchives(params: ArchiveExportParams) {
  return request.get<Blob, Blob>('/api/archives/export', {
    params,
    responseType: 'blob',
  })
}

export function getArchiveOptions() {
  return request.get<ArchiveOptionsResponse, ApiResponse<ArchiveOptionsResponse>>(
    '/api/archives/options',
  )
}

export function getArchive(archiveId: number) {
  return request.get<ArchiveItem, ApiResponse<ArchiveItem>>(
    `/api/archives/${archiveId}`,
  )
}

export function createArchive(payload: ArchivePayload) {
  return request.post<ArchiveItem, ApiResponse<ArchiveItem>>('/api/archives', payload)
}

export function updateArchive(archiveId: number, payload: ArchivePayload) {
  return request.put<ArchiveItem, ApiResponse<ArchiveItem>>(
    `/api/archives/${archiveId}`,
    payload,
  )
}

export function deleteArchive(archiveId: number) {
  return request.delete<ArchiveItem, ApiResponse<ArchiveItem>>(
    `/api/archives/${archiveId}`,
  )
}

export function batchDeleteArchives(archiveIds: number[]) {
  return request.delete<ArchiveListResponse, ApiResponse<ArchiveListResponse>>(
    '/api/archives/batch',
    {
      data: {
        archive_ids: archiveIds,
      },
    },
  )
}
