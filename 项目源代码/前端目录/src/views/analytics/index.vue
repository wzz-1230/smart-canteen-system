<template>
  <div class="analytics-dashboard">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="summary-cards">
      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover" class="summary-card card-revenue">
          <div class="card-icon">💰</div>
          <div class="card-content">
            <div class="card-label">总收入</div>
            <div class="card-value">¥ {{ formatNumber(summary.totalRevenue) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover" class="summary-card card-cost">
          <div class="card-icon">📦</div>
          <div class="card-content">
            <div class="card-label">总支出</div>
            <div class="card-value">¥ {{ formatNumber(summary.totalCost) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover" class="summary-card card-profit">
          <div class="card-icon">📈</div>
          <div class="card-content">
            <div class="card-label">总利润</div>
            <div class="card-value profit-value">¥ {{ formatNumber(summary.totalProfit) }}</div>
            <div class="card-sublabel">利润率: {{ summary.profitRate }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover" class="summary-card card-order">
          <div class="card-icon">📋</div>
          <div class="card-content">
            <div class="card-label">订单总数</div>
            <div class="card-value">{{ formatNumber(summary.totalOrders) }}</div>
            <div class="card-sublabel">客单价: ¥ {{ formatNumber(summary.avgOrderAmount) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 库存周转分析 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📊 库存周转趋势</span>
              <el-tag size="small">实时数据</el-tag>
            </div>
          </template>
          <div ref="turnoverChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>🥘 物品类型分布</span>
              <el-tag size="small">类型统计</el-tag>
            </div>
          </template>
          <div ref="typeChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 收支趋势分析 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📈 收支趋势对比</span>
              <el-tag size="small" type="success">月度数据</el-tag>
            </div>
          </template>
          <div ref="revenueExpenseChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>💰 收入来源分布</span>
              <el-tag size="small" type="warning">分类</el-tag>
            </div>
          </template>
          <div ref="revenuePieChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 利润分析 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📊 利润趋势分析</span>
              <el-tag size="small" type="success">利润变化</el-tag>
            </div>
          </template>
          <div ref="profitChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📦 成本结构分布</span>
              <el-tag size="small" type="info">成本分析</el-tag>
            </div>
          </template>
          <div ref="costPieChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 库存详情表格 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24">
        <el-card shadow="hover" class="table-card">
          <template #header>
            <div class="card-header">
              <span>📋 库存记录详情</span>
              <el-tag size="small">实时更新</el-tag>
            </div>
          </template>
          <el-table :data="inventoryData" border stripe height="400" style="width: 100%">
            <el-table-column prop="itemName" label="物品名称" width="150" align="center" />
            <el-table-column prop="initialQuantity" label="初始数量" width="100" align="center" />
            <el-table-column prop="inQuantity" label="入库数量" width="100" align="center" />
            <el-table-column prop="outQuantity" label="出库数量" width="100" align="center" />
            <el-table-column prop="remainingQuantity" label="剩余数量" width="100" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.status === '0' ? 'success' : scope.row.status === '1' ? 'warning' : 'danger'" size="small">
                  {{ scope.row.remainingQuantity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="80" align="center" />
            <el-table-column prop="unitPrice" label="单价(¥)" width="100" align="center">
              <template #default="scope">{{ formatNumber(scope.row.unitPrice) }}</template>
            </el-table-column>
            <el-table-column prop="totalValue" label="库存价值(¥)" width="120" align="center">
              <template #default="scope">{{ formatNumber(scope.row.totalValue) }}</template>
            </el-table-column>
            <el-table-column prop="turnoverRate" label="周转率(%)" width="100" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.turnoverRate > 50 ? 'success' : scope.row.turnoverRate > 30 ? 'warning' : 'info'" size="small">
                  {{ scope.row.turnoverRate }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="recordDate" label="记录日期" width="180" align="center">
              <template #default="scope">{{ formatDate(scope.row.recordDate) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  getAnalyticsSummary,
  getInventoryTurnoverTrend,
  getInventoryTypeDistribution,
  getRevenueExpenseTrend,
  getRevenueCategoryDistribution,
  getExpenseCategoryDistribution,
  getProfitTrend,
  getCostStructureDistribution,
  listInventory
} from '@/api/analytics/analytics'

// 图表引用
const turnoverChartRef = ref(null)
const typeChartRef = ref(null)
const revenueExpenseChartRef = ref(null)
const revenuePieChartRef = ref(null)
const profitChartRef = ref(null)
const costPieChartRef = ref(null)

// 图表实例
let turnoverChart = null
let typeChart = null
let revenueExpenseChart = null
let revenuePieChart = null
let profitChart = null
let costPieChart = null

// 汇总数据
const summary = reactive({
  totalRevenue: 0,
  totalCost: 0,
  totalProfit: 0,
  profitRate: 0,
  totalOrders: 0,
  avgOrderAmount: 0
})

// 库存数据
const inventoryData = ref([])

// 工具函数
const formatNumber = (num) => {
  if (num == null || num === '') return '0'
  return Number(num).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (date) => {
  if (!date) return ''
  if (typeof date === 'string') {
    return date.replace('T', ' ').substring(0, 19)
  }
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const second = String(d.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`
}

// 加载数据
const loadData = async () => {
  try {
    // 并行加载所有数据
    const [summaryRes, turnoverRes, typeRes, revenueTrendRes, revenueDistRes, profitTrendRes, costDistRes, inventoryRes] = await Promise.all([
      getAnalyticsSummary(),
      getInventoryTurnoverTrend(),
      getInventoryTypeDistribution(),
      getRevenueExpenseTrend(),
      getRevenueCategoryDistribution(),
      getProfitTrend(),
      getCostStructureDistribution(),
      listInventory({ pageNum: 1, pageSize: 100 })
    ])

    // 更新汇总数据
    if (summaryRes && summaryRes.data) {
      Object.assign(summary, summaryRes.data)
    }

    // 更新库存数据
    if (inventoryRes && inventoryRes.rows) {
      inventoryData.value = inventoryRes.rows
    }

    // 更新图表
    nextTick(() => {
      updateTurnoverChart(turnoverRes?.data || turnoverRes || [])
      updateTypeChart(typeRes?.data || typeRes || [])
      updateRevenueExpenseChart(revenueTrendRes?.data || revenueTrendRes || [])
      updateRevenuePieChart(revenueDistRes?.data || revenueDistRes || [])
      updateProfitChart(profitTrendRes?.data || profitTrendRes || [])
      updateCostPieChart(costDistRes?.data || costDistRes || [])
    })
  } catch (error) {
    console.error('加载数据分析失败:', error)
    loadDemoData()
  }
}

// 加载演示数据
const loadDemoData = () => {
  summary.totalRevenue = 268500
  summary.totalCost = 189600
  summary.totalProfit = 78900
  summary.profitRate = 29.38
  summary.totalOrders = 5820
  summary.avgOrderAmount = 46.13

  const demoInventory = [
    { itemName: '猪肉', initialQuantity: 500, inQuantity: 150, outQuantity: 320, remainingQuantity: 330, unit: '公斤', unitPrice: 35, totalValue: 11550, turnoverRate: 64.0, status: '0', recordDate: '2026-06-15 10:30:00' },
    { itemName: '鸡肉', initialQuantity: 400, inQuantity: 120, outQuantity: 280, remainingQuantity: 240, unit: '公斤', unitPrice: 22, totalValue: 5280, turnoverRate: 70.0, status: '0', recordDate: '2026-06-15 10:30:00' },
    { itemName: '牛肉', initialQuantity: 200, inQuantity: 80, outQuantity: 180, remainingQuantity: 100, unit: '公斤', unitPrice: 68, totalValue: 6800, turnoverRate: 90.0, status: '1', recordDate: '2026-06-15 10:30:00' },
    { itemName: '鱼肉', initialQuantity: 150, inQuantity: 60, outQuantity: 130, remainingQuantity: 80, unit: '公斤', unitPrice: 45, totalValue: 3600, turnoverRate: 86.67, status: '1', recordDate: '2026-06-15 10:30:00' },
    { itemName: '蔬菜', initialQuantity: 800, inQuantity: 300, outQuantity: 600, remainingQuantity: 500, unit: '公斤', unitPrice: 8, totalValue: 4000, turnoverRate: 75.0, status: '0', recordDate: '2026-06-15 10:30:00' },
    { itemName: '鸡蛋', initialQuantity: 3000, inQuantity: 800, outQuantity: 2200, remainingQuantity: 1600, unit: '个', unitPrice: 0.8, totalValue: 1280, turnoverRate: 73.33, status: '0', recordDate: '2026-06-15 10:30:00' },
    { itemName: '食用油', initialQuantity: 300, inQuantity: 100, outQuantity: 220, remainingQuantity: 180, unit: '升', unitPrice: 15, totalValue: 2700, turnoverRate: 73.33, status: '0', recordDate: '2026-06-15 10:30:00' },
    { itemName: '酱油', initialQuantity: 150, inQuantity: 40, outQuantity: 90, remainingQuantity: 100, unit: '瓶', unitPrice: 12, totalValue: 1200, turnoverRate: 60.0, status: '0', recordDate: '2026-06-15 10:30:00' },
    { itemName: '米饭餐具', initialQuantity: 600, inQuantity: 100, outQuantity: 150, remainingQuantity: 550, unit: '套', unitPrice: 3.5, totalValue: 1925, turnoverRate: 25.0, status: '0', recordDate: '2026-06-15 10:30:00' },
    { itemName: '饮料', initialQuantity: 500, inQuantity: 150, outQuantity: 380, remainingQuantity: 270, unit: '瓶', unitPrice: 4, totalValue: 1080, turnoverRate: 76.0, status: '0', recordDate: '2026-06-15 10:30:00' },
    { itemName: '啤酒', initialQuantity: 200, inQuantity: 60, outQuantity: 150, remainingQuantity: 110, unit: '瓶', unitPrice: 8, totalValue: 880, turnoverRate: 75.0, status: '0', recordDate: '2026-06-15 10:30:00' },
    { itemName: '食盐', initialQuantity: 120, inQuantity: 40, outQuantity: 80, remainingQuantity: 80, unit: '包', unitPrice: 5, totalValue: 400, turnoverRate: 66.67, status: '2', recordDate: '2026-06-15 10:30:00' }
  ]
  inventoryData.value = demoInventory

  nextTick(() => {
    updateTurnoverChart([
      { itemName: '猪肉', turnoverRate: 64.0, totalValue: 11550 },
      { itemName: '鸡肉', turnoverRate: 70.0, totalValue: 5280 },
      { itemName: '牛肉', turnoverRate: 90.0, totalValue: 6800 },
      { itemName: '鱼肉', turnoverRate: 86.67, totalValue: 3600 },
      { itemName: '蔬菜', turnoverRate: 75.0, totalValue: 4000 },
      { itemName: '鸡蛋', turnoverRate: 73.33, totalValue: 1280 }
    ])
    updateTypeChart([
      { name: '食材', value: 385 },
      { name: '调料', value: 85 },
      { name: '餐具', value: 100 },
      { name: '饮品', value: 65 }
    ])
    updateRevenueExpenseChart([
      { periodName: '1月', totalRevenue: 15000, totalCost: 12000, totalProfit: 3000 },
      { periodName: '2月', totalRevenue: 18500, totalCost: 14800, totalProfit: 3700 },
      { periodName: '3月', totalRevenue: 22000, totalCost: 17600, totalProfit: 4400 },
      { periodName: '4月', totalRevenue: 19800, totalCost: 16200, totalProfit: 3600 },
      { periodName: '5月', totalRevenue: 24500, totalCost: 19200, totalProfit: 5300 },
      { periodName: '6月', totalRevenue: 28600, totalCost: 22000, totalProfit: 6600 }
    ])
    updateRevenuePieChart([
      { name: '堂食销售', value: 45000 },
      { name: '外卖订单', value: 28000 },
      { name: '套餐收入', value: 18500 },
      { name: '饮品收入', value: 9600 },
      { name: '其他收入', value: 3400 }
    ])
    updateProfitChart([
      { periodName: '1月', profit: 3000, profitRate: 20.0 },
      { periodName: '2月', profit: 3700, profitRate: 20.0 },
      { periodName: '3月', profit: 4400, profitRate: 20.0 },
      { periodName: '4月', profit: 3600, profitRate: 18.18 },
      { periodName: '5月', profit: 5300, profitRate: 21.63 },
      { periodName: '6月', profit: 6600, profitRate: 23.08 }
    ])
    updateCostPieChart([
      { name: '食材采购', value: 96400 },
      { name: '人工成本', value: 65000 },
      { name: '水电费用', value: 15200 },
      { name: '设备维护', value: 8000 },
      { name: '其他支出', value: 5000 }
    ])
  })
}

// 库存周转趋势图
const updateTurnoverChart = (data) => {
  if (!turnoverChart) return
  const names = data.map(item => item.itemName || item.name)
  const rates = data.map(item => item.turnoverRate || 0)
  const values = data.map(item => item.totalValue || 0)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        let result = params[0].name + '<br/>'
        params.forEach(item => {
          result += item.marker + item.seriesName + ': ' + (item.seriesName.includes('率') ? item.value + '%' : '¥' + Number(item.value).toLocaleString()) + '<br/>'
        })
        return result
      }
    },
    legend: { data: ['周转率(%)', '库存价值(¥)'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30 } },
    yAxis: [
      { type: 'value', name: '周转率(%)', position: 'left' },
      { type: 'value', name: '库存价值(¥)', position: 'right' }
    ],
    series: [
      {
        name: '周转率(%)',
        type: 'bar',
        data: rates,
        itemStyle: { color: '#409EFF' },
        barWidth: '35%'
      },
      {
        name: '库存价值(¥)',
        type: 'line',
        yAxisIndex: 1,
        data: values,
        itemStyle: { color: '#E6A23C' },
        smooth: true
      }
    ]
  }
  turnoverChart.setOption(option)
}

// 物品类型分布图
const updateTypeChart = (data) => {
  if (!typeChart) return

  const option = {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', x: 'left' },
    series: [
      {
        name: '物品类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: {
          label: { show: true, fontSize: 16, fontWeight: 'bold' }
        },
        labelLine: { show: false },
        data: data.map((item, idx) => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'][idx % 5] }
        }))
      }
    ]
  }
  typeChart.setOption(option)
}

// 收支趋势图
const updateRevenueExpenseChart = (data) => {
  if (!revenueExpenseChart) return
  const periods = data.map(item => item.periodName || item.name)
  const revenues = data.map(item => item.totalRevenue || item.revenue || 0)
  const costs = data.map(item => item.totalCost || item.cost || 0)
  const profits = data.map(item => item.totalProfit || item.profit || 0)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        let result = params[0].name + '<br/>'
        params.forEach(item => {
          result += item.marker + item.seriesName + ': ¥' + Number(item.value).toLocaleString() + '<br/>'
        })
        return result
      }
    },
    legend: { data: ['收入', '支出', '利润'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: periods },
    yAxis: { type: 'value', axisLabel: { formatter: '¥{value}' } },
    series: [
      { name: '收入', type: 'bar', data: revenues, itemStyle: { color: '#67C23A' }, barWidth: '20%' },
      { name: '支出', type: 'bar', data: costs, itemStyle: { color: '#F56C6C' }, barWidth: '20%' },
      { name: '利润', type: 'line', data: profits, itemStyle: { color: '#409EFF' }, smooth: true, lineStyle: { width: 3 } }
    ]
  }
  revenueExpenseChart.setOption(option)
}

// 收入分类饼图
const updateRevenuePieChart = (data) => {
  if (!revenuePieChart) return

  const option = {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: ¥{c} ({d}%)' },
    legend: { orient: 'vertical', x: 'left' },
    series: [
      {
        name: '收入来源',
        type: 'pie',
        radius: '65%',
        data: data.map((item, idx) => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: ['#67C23A', '#409EFF', '#E6A23C', '#F56C6C', '#909399'][idx % 5] }
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  revenuePieChart.setOption(option)
}

// 利润趋势图
const updateProfitChart = (data) => {
  if (!profitChart) return
  const periods = data.map(item => item.periodName || item.name)
  const profits = data.map(item => item.profit || item.totalProfit || 0)
  const profitRates = data.map(item => item.profitRate || 0)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let result = params[0].name + '<br/>'
        params.forEach(item => {
          result += item.marker + item.seriesName + ': ' + (item.seriesName.includes('率') ? item.value + '%' : '¥' + Number(item.value).toLocaleString()) + '<br/>'
        })
        return result
      }
    },
    legend: { data: ['利润额', '利润率(%)'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: periods },
    yAxis: [
      { type: 'value', name: '利润(¥)', position: 'left' },
      { type: 'value', name: '利润率(%)', position: 'right' }
    ],
    series: [
      {
        name: '利润额',
        type: 'line',
        smooth: true,
        data: profits,
        itemStyle: { color: '#409EFF' },
        lineStyle: { width: 3 },
        areaStyle: { color: 'rgba(64, 158, 255, 0.2)' }
      },
      {
        name: '利润率(%)',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        data: profitRates,
        itemStyle: { color: '#E6A23C' },
        lineStyle: { width: 3, type: 'dashed' }
      }
    ]
  }
  profitChart.setOption(option)
}

// 成本结构图
const updateCostPieChart = (data) => {
  if (!costPieChart) return

  const option = {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: ¥{c} ({d}%)' },
    legend: { orient: 'vertical', x: 'left' },
    series: [
      {
        name: '成本分布',
        type: 'pie',
        roseType: 'radius',
        radius: [20, 120],
        center: ['50%', '50%'],
        data: data.map((item, idx) => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A', '#909399'][idx % 5] }
        })),
        animationType: 'scale',
        animationEasing: 'exponentialInOut',
        animationDelay: () => Math.random() * 100
      }
    ]
  }
  costPieChart.setOption(option)
}

// 窗口大小变化时重置图表
const handleResize = () => {
  turnoverChart?.resize()
  typeChart?.resize()
  revenueExpenseChart?.resize()
  revenuePieChart?.resize()
  profitChart?.resize()
  costPieChart?.resize()
}

// 初始化图表
const initCharts = () => {
  if (turnoverChartRef.value) turnoverChart = echarts.init(turnoverChartRef.value)
  if (typeChartRef.value) typeChart = echarts.init(typeChartRef.value)
  if (revenueExpenseChartRef.value) revenueExpenseChart = echarts.init(revenueExpenseChartRef.value)
  if (revenuePieChartRef.value) revenuePieChart = echarts.init(revenuePieChartRef.value)
  if (profitChartRef.value) profitChart = echarts.init(profitChartRef.value)
  if (costPieChartRef.value) costPieChart = echarts.init(costPieChartRef.value)
}

onMounted(() => {
  nextTick(() => {
    initCharts()
    loadData()
    window.addEventListener('resize', handleResize)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  turnoverChart?.dispose()
  typeChart?.dispose()
  revenueExpenseChart?.dispose()
  revenuePieChart?.dispose()
  profitChart?.dispose()
  costPieChart?.dispose()
})
</script>

<style scoped>
.analytics-dashboard {
  padding: 20px;
  background: #f0f2f5;
  min-height: calc(100vh - 84px);
}

.summary-cards {
  margin-bottom: 20px;
}

.summary-card {
  border-radius: 12px;
  border: none;
  overflow: hidden;
}

.summary-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  padding: 24px 20px;
}

.card-icon {
  font-size: 48px;
  margin-right: 16px;
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.profit-value {
  color: #67C23A;
}

.card-sublabel {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.card-revenue :deep(.el-card__body) { background: linear-gradient(135deg, #f0fdf0 0%, #dcfce7 100%); }
.card-cost :deep(.el-card__body) { background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); }
.card-profit :deep(.el-card__body) { background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); }
.card-order :deep(.el-card__body) { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); }

.chart-section {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
  border: none;
  height: 100%;
}

.table-card {
  border-radius: 12px;
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart {
  width: 100%;
  height: 380px;
}

@media (max-width: 768px) {
  .summary-card :deep(.el-card__body) {
    padding: 16px;
    flex-direction: column;
    text-align: center;
  }

  .card-icon {
    font-size: 32px;
    margin-right: 0;
    margin-bottom: 8px;
  }

  .chart {
    height: 280px;
  }
}
</style>
