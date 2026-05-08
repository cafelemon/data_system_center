import { request, type ApiResponse } from './request'

export interface OperationLogUser {
  id: number
  username: string
  real_name: string
}

export interface OperationLogItem {
  id: number
  user: OperationLogUser | null
  module: string
  operation_type: string
  target_id: string | null
  target_name: string | null
  operation_detail: string | null
  ip_address: string | null
  created_at: string
}

export interface OperationLogListParams {
  keyword?: string
  module?: string
  operation_type?: string
  date_from?: string
  date_to?: string
  page: number
  page_size: number
}

export interface OperationLogListResponse {
  items: OperationLogItem[]
  total: number
  page: number
  page_size: number
}

export function getOperationLogs(params: OperationLogListParams) {
  return request.get<
    OperationLogListResponse,
    ApiResponse<OperationLogListResponse>
  >('/api/operation-logs', {
    params,
  })
}
