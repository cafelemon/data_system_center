import { request, type ApiResponse } from './request'

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

export function getStatisticsOverview() {
  return request.get<
    StatisticsOverviewResponse,
    ApiResponse<StatisticsOverviewResponse>
  >('/api/statistics/overview')
}

export function getStatusDistribution() {
  return request.get<DistributionResponse, ApiResponse<DistributionResponse>>(
    '/api/statistics/status-distribution',
  )
}

export function getTypeDistribution() {
  return request.get<DistributionResponse, ApiResponse<DistributionResponse>>(
    '/api/statistics/type-distribution',
  )
}

export function getDepartmentRanking(limit = 8) {
  return request.get<
    DepartmentRankingResponse,
    ApiResponse<DepartmentRankingResponse>
  >('/api/statistics/department-ranking', {
    params: {
      limit,
    },
  })
}

export function getMonthlyTrend(months = 12) {
  return request.get<MonthlyTrendResponse, ApiResponse<MonthlyTrendResponse>>(
    '/api/statistics/monthly-trend',
    {
      params: {
        months,
      },
    },
  )
}
