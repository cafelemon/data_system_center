import { request, type ApiResponse } from './request'

export interface HealthStatus {
  service: string
  status: string
  database: string
  version: string
  timestamp: string
}

export function getHealth() {
  return request.get<HealthStatus, ApiResponse<HealthStatus>>('/api/health')
}
