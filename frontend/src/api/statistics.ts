import { request, type ApiResponse } from './request'

export type StatisticsArchiveMedium = 'all' | 'paper' | 'electronic'

export interface StatisticsParams {
  archive_medium?: StatisticsArchiveMedium
}

export interface StatisticsOverviewResponse {
  total_archives: number
  monthly_new: number
  expiring_soon: number
  department_count: number
}

export interface DistributionItem {
  id: number
  name: string
  code: string
  count: number
  percentage: number
}

export interface DistributionResponse {
  items: DistributionItem[]
  total: number
}

export interface DepartmentRankingItem {
  id: number
  name: string
  code: string
  count: number
}

export interface DepartmentRankingResponse {
  items: DepartmentRankingItem[]
}

export interface MonthlyTrendItem {
  month: string
  count: number
}

export interface MonthlyTrendResponse {
  items: MonthlyTrendItem[]
}

export function getStatisticsOverview(params?: StatisticsParams) {
  return request.get<
    StatisticsOverviewResponse,
    ApiResponse<StatisticsOverviewResponse>
  >('/api/statistics/overview', { params })
}

export function getStatusDistribution(params?: StatisticsParams) {
  return request.get<DistributionResponse, ApiResponse<DistributionResponse>>(
    '/api/statistics/status-distribution',
    { params },
  )
}

export function getTypeDistribution(params?: StatisticsParams) {
  return request.get<DistributionResponse, ApiResponse<DistributionResponse>>(
    '/api/statistics/type-distribution',
    { params },
  )
}

export function getDepartmentRanking(limit = 8, params?: StatisticsParams) {
  return request.get<
    DepartmentRankingResponse,
    ApiResponse<DepartmentRankingResponse>
  >('/api/statistics/department-ranking', {
    params: {
      ...params,
      limit,
    },
  })
}

export function getMonthlyTrend(months = 12, params?: StatisticsParams) {
  return request.get<MonthlyTrendResponse, ApiResponse<MonthlyTrendResponse>>(
    '/api/statistics/monthly-trend',
    {
      params: {
        ...params,
        months,
      },
    },
  )
}
