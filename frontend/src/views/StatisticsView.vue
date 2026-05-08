<script setup lang="ts">
import {
  Clock,
  Files,
  OfficeBuilding,
  Refresh,
  TrendCharts,
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'

import {
  getDepartmentRanking,
  getMonthlyTrend,
  getStatisticsOverview,
  getStatusDistribution,
  getTypeDistribution,
  type DepartmentRankingItem,
  type DistributionItem,
  type MonthlyTrendItem,
  type StatisticsOverviewResponse,
  type StatisticsArchiveMedium,
} from '@/api/statistics'

const loading = ref(false)
const errorMessage = ref('')
const archiveMedium = ref<StatisticsArchiveMedium>('all')
const overview = ref<StatisticsOverviewResponse | null>(null)
const statusItems = ref<DistributionItem[]>([])
const typeItems = ref<DistributionItem[]>([])
const departmentItems = ref<DepartmentRankingItem[]>([])
const monthlyTrendItems = ref<MonthlyTrendItem[]>([])

const typeChartRef = ref<HTMLDivElement | null>(null)
const departmentChartRef = ref<HTMLDivElement | null>(null)
const trendChartRef = ref<HTMLDivElement | null>(null)

let typeChart: ReturnType<typeof echarts.init> | null = null
let departmentChart: ReturnType<typeof echarts.init> | null = null
let trendChart: ReturnType<typeof echarts.init> | null = null

const chartColors = [
  '#3b82f6',
  '#10b981',
  '#f59e0b',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
  '#84cc16',
  '#f97316',
  '#64748b',
]

const statusColors: Record<string, string> = {
  在库: '#22c55e',
  借出: '#3b82f6',
  待归档: '#f59e0b',
  待审核: '#94a3b8',
  已归档: '#64748b',
  已销毁: '#ef4444',
}

const metricCards = computed(() => [
  {
    label: '档案总数',
    value: overview.value?.total_archives ?? 0,
    note: '累计入库档案',
    icon: Files,
    tone: 'blue',
  },
  {
    label: '本月新增',
    value: overview.value?.monthly_new ?? 0,
    note: '当前自然月新增',
    icon: TrendCharts,
    tone: 'green',
  },
  {
    label: '即将到期',
    value: overview.value?.expiring_soon ?? 0,
    note: '未来90天需关注',
    icon: Clock,
    tone: 'orange',
  },
  {
    label: '涉及部门',
    value: overview.value?.department_count ?? 0,
    note: '有档案分布部门数',
    icon: OfficeBuilding,
    tone: 'purple',
  },
])

const mediumTabs: Array<{ label: string; value: StatisticsArchiveMedium }> = [
  { label: '全部', value: 'all' },
  { label: '纸质', value: 'paper' },
  { label: '电子', value: 'electronic' },
]

function formatNumber(value: number) {
  return new Intl.NumberFormat('zh-CN').format(value)
}

function formatPercentage(value: number) {
  return `${value.toFixed(1)}%`
}

function getStatusColor(item: DistributionItem, index: number) {
  return statusColors[item.name] ?? chartColors[index % chartColors.length]
}

function getTypeChart() {
  if (!typeChart && typeChartRef.value) {
    typeChart = echarts.init(typeChartRef.value)
  }
  return typeChart
}

function getDepartmentChart() {
  if (!departmentChart && departmentChartRef.value) {
    departmentChart = echarts.init(departmentChartRef.value)
  }
  return departmentChart
}

function getTrendChart() {
  if (!trendChart && trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
  }
  return trendChart
}

function renderTypeChart() {
  const chart = getTypeChart()
  if (!chart) {
    return
  }

  const data = typeItems.value
    .filter((item) => item.count > 0)
    .map((item) => ({
      name: item.name,
      value: item.count,
    }))

  chart.setOption({
    color: chartColors,
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br/>数量：{c}<br/>占比：{d}%',
    },
    legend: {
      bottom: 0,
      left: 'center',
      type: 'scroll',
      icon: 'roundRect',
      itemWidth: 14,
      itemHeight: 8,
      textStyle: {
        color: '#526071',
      },
    },
    title: data.length
      ? undefined
      : {
          text: '暂无数据',
          left: 'center',
          top: 'middle',
          textStyle: {
            color: '#94a3b8',
            fontSize: 14,
            fontWeight: 500,
          },
        },
    series: [
      {
        name: '档案类型',
        type: 'pie',
        radius: ['48%', '72%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: true,
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            formatter: '{b}\n{d}%',
            fontSize: 13,
            fontWeight: 600,
          },
        },
        data,
      },
    ],
  })
}

function renderDepartmentChart() {
  const chart = getDepartmentChart()
  if (!chart) {
    return
  }

  chart.setOption({
    color: ['#3b82f6'],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    grid: {
      top: 28,
      right: 18,
      bottom: 58,
      left: 52,
    },
    xAxis: {
      type: 'category',
      data: departmentItems.value.map((item) => item.name),
      axisTick: {
        show: false,
      },
      axisLabel: {
        interval: 0,
        rotate: 35,
        color: '#526071',
      },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: {
        color: '#526071',
      },
      splitLine: {
        lineStyle: {
          color: '#e5e7eb',
        },
      },
    },
    series: [
      {
        name: '档案数量',
        type: 'bar',
        data: departmentItems.value.map((item) => item.count),
        barMaxWidth: 36,
        itemStyle: {
          borderRadius: [5, 5, 0, 0],
        },
      },
    ],
  })
}

function renderTrendChart() {
  const chart = getTrendChart()
  if (!chart) {
    return
  }

  chart.setOption({
    color: ['#10b981'],
    tooltip: {
      trigger: 'axis',
    },
    grid: {
      top: 28,
      right: 18,
      bottom: 42,
      left: 52,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: monthlyTrendItems.value.map((item) => item.month),
      axisTick: {
        show: false,
      },
      axisLabel: {
        color: '#526071',
      },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: {
        color: '#526071',
      },
      splitLine: {
        lineStyle: {
          color: '#e5e7eb',
        },
      },
    },
    series: [
      {
        name: '入库数量',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        data: monthlyTrendItems.value.map((item) => item.count),
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(16, 185, 129, 0.22)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.02)' },
            ],
          },
        },
      },
    ],
  })
}

function renderCharts() {
  renderTypeChart()
  renderDepartmentChart()
  renderTrendChart()
}

function resizeCharts() {
  typeChart?.resize()
  departmentChart?.resize()
  trendChart?.resize()
}

async function loadStatistics() {
  loading.value = true
  errorMessage.value = ''

  try {
    const params = {
      archive_medium: archiveMedium.value,
    }
    const [overviewResponse, statusResponse, typeResponse, departmentResponse, trendResponse] =
      await Promise.all([
        getStatisticsOverview(params),
        getStatusDistribution(params),
        getTypeDistribution(params),
        getDepartmentRanking(8, params),
        getMonthlyTrend(12, params),
      ])

    overview.value = overviewResponse.data
    statusItems.value = statusResponse.data.items
    typeItems.value = typeResponse.data.items
    departmentItems.value = departmentResponse.data.items
    monthlyTrendItems.value = trendResponse.data.items
    await nextTick()
    renderCharts()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '数据统计加载失败'
  } finally {
    loading.value = false
  }
}

function handleMediumChange() {
  loadStatistics()
}

onMounted(() => {
  window.addEventListener('resize', resizeCharts)
  loadStatistics()
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  typeChart?.dispose()
  departmentChart?.dispose()
  trendChart?.dispose()
})
</script>

<template>
  <section class="page statistics-page">
    <div class="page-header">
      <div>
        <h1>数据统计</h1>
        <p>档案资产概况与分布趋势分析</p>
      </div>
      <div class="page-actions">
        <el-segmented
          v-model="archiveMedium"
          class="statistics-medium-switch"
          :options="mediumTabs"
          :disabled="loading"
          @change="handleMediumChange"
        />
        <el-button :icon="Refresh" :loading="loading" @click="loadStatistics">
          刷新
        </el-button>
      </div>
    </div>

    <el-alert
      v-if="errorMessage"
      class="statistics-alert"
      :title="errorMessage"
      type="warning"
      show-icon
      :closable="false"
    />

    <div v-loading="loading" class="metric-grid">
      <article
        v-for="item in metricCards"
        :key="item.label"
        class="metric-card"
        :class="`metric-card-${item.tone}`"
      >
        <div>
          <span>{{ item.label }}</span>
          <strong>{{ formatNumber(item.value) }}</strong>
          <small>{{ item.note }}</small>
        </div>
        <div class="metric-icon">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
      </article>
    </div>

    <section v-loading="loading" class="statistics-panel status-panel">
      <div class="panel-header">
        <h2>档案状态分布</h2>
      </div>
      <div class="status-grid">
        <article
          v-for="(item, index) in statusItems"
          :key="item.id"
          class="status-item"
        >
          <span
            class="status-dot"
            :style="{ backgroundColor: getStatusColor(item, index) }"
          />
          <strong>{{ formatNumber(item.count) }}</strong>
          <span>{{ item.name }}</span>
          <small>{{ formatPercentage(item.percentage) }}</small>
        </article>
      </div>
    </section>

    <div class="chart-grid">
      <section v-loading="loading" class="statistics-panel chart-panel">
        <div class="panel-header">
          <h2>档案类型分布</h2>
        </div>
        <div ref="typeChartRef" class="chart-surface" />
      </section>

      <section v-loading="loading" class="statistics-panel chart-panel">
        <div class="panel-header">
          <h2>部门档案数量</h2>
        </div>
        <div ref="departmentChartRef" class="chart-surface" />
      </section>

      <section v-loading="loading" class="statistics-panel chart-panel trend-panel">
        <div class="panel-header">
          <div>
            <h2>月度入库趋势</h2>
            <p>最近12个月档案入库数量变化趋势</p>
          </div>
        </div>
        <div ref="trendChartRef" class="chart-surface chart-surface-wide" />
      </section>
    </div>
  </section>
</template>
