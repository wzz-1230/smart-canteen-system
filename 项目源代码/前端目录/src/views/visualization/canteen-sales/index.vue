<template>
  <div class="canteen-sales">
    <!-- 顶部整体分析按钮 -->
    <el-row :gutter="20" class="row-overall">
      <el-col :span="24">
        <el-card shadow="hover" class="overall-card">
          <div class="overall-inner">
            <div class="overall-left">
              <el-icon :size="32" color="#409EFF"><MagicStick /></el-icon>
              <div class="overall-info">
                <div class="overall-title">食堂销售数据智能分析</div>
                <div class="overall-sub">整合销售趋势、菜品排行和时段分布，一键生成全面的数据分析报告</div>
              </div>
            </div>
            <el-button
              type="primary"
              size="large"
              :loading="analyzing.overall"
              @click="analyzeOverall"
              class="overall-btn">
              <el-icon><MagicStick /></el-icon>
              <span>&nbsp;一键 AI 整体分析</span>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第一行：4 个统计卡片 -->
    <el-row :gutter="20" class="row-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-blue">
              <el-icon :size="28"><Wallet /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">总销售额</div>
              <div class="text-value">¥ {{ formatNumber(summary.total_amount) }}</div>
              <div class="text-sub">累计销售 ¥ {{ formatNumber(summary.total_amount) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-green">
              <el-icon :size="28"><Document /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">总订单数</div>
              <div class="text-value">{{ formatNumber(summary.total_orders) }}</div>
              <div class="text-sub">累计订单 {{ formatNumber(summary.total_orders) }} 单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-orange">
              <el-icon :size="28"><TrendCharts /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">客单价</div>
              <div class="text-value">¥ {{ toFixed2(summary.avg_amount) }}</div>
              <div class="text-sub">订单平均金额 ¥ {{ toFixed2(summary.avg_amount) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="card-inner">
            <div class="icon-box icon-red">
              <el-icon :size="28"><UserFilled /></el-icon>
            </div>
            <div class="text-box">
              <div class="text-label">热销菜品数</div>
              <div class="text-value">{{ formatNumber(hotDishCount) }}</div>
              <div class="text-sub">TOP 热门菜品统计</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：趋势图 + 菜品排行 -->
    <el-row :gutter="20" class="row-charts">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><DataAnalysis /></el-icon>
                <span>&nbsp;每日销售趋势（近30天）</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeTrend" :loading="analyzing.trend">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="dailyChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Rank /></el-icon>
                <span>&nbsp;菜品销售排行 TOP 10</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeDishes" :loading="analyzing.dishes">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="dishChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行：销售时段分布 -->
    <el-row :gutter="20" class="row-charts">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><DataBoard /></el-icon>
                <span>&nbsp;销售时段分布（24 小时）</span>
              </div>
              <el-button size="small" type="primary" @click="analyzeHourly" :loading="analyzing.hourly">
                <el-icon><MagicStick /></el-icon>
                <span>&nbsp;AI 分析</span>
              </el-button>
            </div>
          </template>
          <div ref="hourlyChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI 分析结果弹窗（增强版） -->
    <el-dialog
      v-model="aiDialog.visible"
      :title="aiDialog.title"
      width="780px"
      top="5vh"
      :close-on-click-modal="false">
      <div class="ai-content">
        <div class="ai-header">
          <el-icon :size="36" color="#409EFF"><MagicStick /></el-icon>
          <div class="ai-header-text">
            <div class="ai-title">AI 智能分析报告</div>
            <div class="ai-subtitle">基于实时数据分析 · {{ currentTimeStr }}</div>
          </div>
          <div class="ai-header-tag">
            <el-tag :type="aiDialog.dataType === 'overall' ? 'danger' : 'primary'" size="small">
              {{ aiDialog.dataType === 'overall' ? '整体分析' : '单项分析' }}
            </el-tag>
          </div>
        </div>

        <div class="ai-toolbar" v-if="aiDialog.content && !aiLoading">
          <el-button size="small" @click="copyAnalysis">
            <el-icon><DocumentCopy /></el-icon>
            <span>&nbsp;复制内容</span>
          </el-button>
          <el-button size="small" type="success" @click="exportAsMarkdown">
            <el-icon><Download /></el-icon>
            <span>&nbsp;导出 Markdown</span>
          </el-button>
          <el-button size="small" type="warning" @click="exportAsText">
            <el-icon><Document /></el-icon>
            <span>&nbsp;导出 TXT</span>
          </el-button>
          <el-button size="small" type="info" @click="printAnalysis">
            <el-icon><Printer /></el-icon>
            <span>&nbsp;打印报告</span>
          </el-button>
        </div>

        <div class="ai-body" :class="{ 'ai-loading': aiLoading }" v-loading="aiLoading">
          <div v-if="aiDialog.content" class="ai-markdown-content" v-html="renderedMarkdown"></div>
          <el-empty v-else-if="!aiLoading" description="暂无分析结果，请点击 AI 分析按钮生成报告" />
        </div>
      </div>
      <template #footer>
        <el-button @click="aiDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import {
  Wallet, Document, TrendCharts, UserFilled, DataAnalysis, Rank,
  MagicStick, DataBoard, DocumentCopy, Download, Printer
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getCanteenSalesSummary,
  getCanteenDailyTrend,
  getDishRanking,
  getCanteenHourlyDistribution
} from '@/api/visualization'
import { aiAnalyze } from '@/api/ai'

const loading = ref(false)
const aiLoading = ref(false)

const summary = ref({
  total_amount: 0,
  total_orders: 0,
  avg_amount: 0
})
const hotDishCount = ref(0)

const dailyData = ref([])
const dishData = ref([])
const hourlyData = ref([])

const dailyChartRef = ref(null)
const dishChartRef = ref(null)
const hourlyChartRef = ref(null)

let dailyChart = null
let dishChart = null
let hourlyChart = null

const analyzing = reactive({
  trend: false,
  dishes: false,
  hourly: false,
  overall: false
})

const aiDialog = reactive({
  visible: false,
  title: 'AI 智能分析',
  content: '',
  dataType: ''
})

const currentTimeStr = computed(() => {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`
})

const renderedMarkdown = computed(() => {
  if (!aiDialog.content) return ''
  return renderMarkdown(aiDialog.content)
})

// 轻量级 Markdown 渲染函数
function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  html = html.replace(/^######\s+(.+)$/gm, '<h6 class="md-h6">$1</h6>')
  html = html.replace(/^#####\s+(.+)$/gm, '<h5 class="md-h5">$1</h5>')
  html = html.replace(/^####\s+(.+)$/gm, '<h4 class="md-h4">$1</h4>')
  html = html.replace(/^###\s+(.+)$/gm, '<h3 class="md-h3">$1</h3>')
  html = html.replace(/^##\s+(.+)$/gm, '<h2 class="md-h2">$1</h2>')
  html = html.replace(/^#\s+(.+)$/gm, '<h1 class="md-h1">$1</h1>')

  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/`([^`]+)`/g, '<code class="md-code">$1</code>')

  html = html.replace(/^[-*+]\s+(.+)$/gm, '<li class="md-li">$1</li>')
  html = html.replace(/^(\d+)\.\s+(.+)$/gm, '<li class="md-li md-li-num"><span class="md-num">$1.</span> $2</li>')
  html = html.replace(/(<li[^>]*>.*<\/li>\n?)+/g, (match) => {
    return `<ul class="md-ul">${match}</ul>`
  })

  html = html.replace(/^>\s+(.+)$/gm, '<blockquote class="md-quote">$1</blockquote>')
  html = html.replace(/^---\s*$/gm, '<hr class="md-hr" />')
  html = html.replace(/\n{2,}/g, '</p><p class="md-p">')
  html = html.replace(/\n/g, '<br/>')

  if (!html.startsWith('<h') && !html.startsWith('<ul') && !html.startsWith('<blockquote') && !html.startsWith('<p')) {
    html = '<p class="md-p">' + html + '</p>'
  }

  return html
}

const formatNumber = (num) => {
  if (num === null || num === undefined || num === '') return '0'
  const n = Number(num)
  if (Number.isNaN(n)) return '0'
  return String(Math.round(n * 100) / 100).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const toFixed2 = (num) => {
  if (num === null || num === undefined || num === '') return '0.00'
  const n = Number(num)
  if (Number.isNaN(n)) return '0.00'
  return n.toFixed(2)
}

const loadSummary = async () => {
  try {
    const res = await getCanteenSalesSummary()
    const data = res && res.data
    if (data) {
      summary.value = {
        total_amount: data.total_amount ?? 0,
        total_orders: data.total_orders ?? 0,
        avg_amount: data.avg_amount ?? 0
      }
    }
  } catch (e) {
    console.error('加载销售汇总失败:', e)
  }
}

const loadDailyTrend = async () => {
  try {
    const res = await getCanteenDailyTrend()
    const data = res && res.data
    if (Array.isArray(data)) {
      dailyData.value = data
    }
    renderDailyChart()
  } catch (e) {
    console.error('加载每日销售趋势失败:', e)
  }
}

const loadDishRanking = async () => {
  try {
    const res = await getDishRanking()
    const data = res && res.data
    if (Array.isArray(data)) {
      dishData.value = data
      hotDishCount.value = data.length
    }
    renderDishChart()
  } catch (e) {
    console.error('加载菜品排行失败:', e)
  }
}

const loadHourlyDistribution = async () => {
  try {
    const res = await getCanteenHourlyDistribution()
    const data = res && res.data
    if (Array.isArray(data)) {
      hourlyData.value = data
    }
    renderHourlyChart()
  } catch (e) {
    console.error('加载销售时段分布失败:', e)
  }
}

const quantityColors = ['#F56C6C', '#E6A23C', '#F7BA2A', '#67C23A', '#48D1CC', '#409EFF', '#79BBFF', '#8e7cc3', '#909399', '#C0C4CC']

function formatAmountAxis(val) {
  if (val >= 1000) {
    return (val / 1000).toFixed(1) + 'k'
  }
  return val
}

function getDishColor(params) {
  return quantityColors[params.dataIndex % quantityColors.length]
}

const renderDailyChart = () => {
  if (!dailyChart) return
  const data = dailyData.value || []
  const dates = data.map(d => d.date)
  const amounts = data.map(d => Number(d.amount || 0))
  const orders = data.map(d => Number(d.order_count || 0))

  dailyChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['销售额', '订单数'],
      top: 0
    },
    grid: {
      top: 50,
      left: 70,
      right: 70,
      bottom: 50
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45 }
    },
    yAxis: [
      {
        type: 'value',
        name: '金额',
        axisLabel: { formatter: formatAmountAxis }
      },
      {
        type: 'value',
        name: '订单数',
        axisLabel: { formatter: '{value}' }
      }
    ],
    series: [
      {
        name: '销售额',
        type: 'bar',
        data: amounts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#79BBFF' }
          ])
        },
        barWidth: '50%'
      },
      {
        name: '订单数',
        type: 'line',
        yAxisIndex: 1,
        data: orders,
        smooth: true,
        itemStyle: { color: '#67C23A' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103,194,58,0.3)' },
            { offset: 1, color: 'rgba(103,194,58,0.05)' }
          ])
        }
      }
    ]
  })
}

const renderDishChart = () => {
  if (!dishChart) return
  const data = (dishData.value || []).slice(0, 10)
  const names = data.map(d => d.menu_name).reverse()
  const amounts = data.map(d => Number(d.total_amount || 0)).reverse()

  dishChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      top: 20,
      left: 110,
      right: 70,
      bottom: 30
    },
    xAxis: {
      type: 'value',
      axisLabel: { formatter: formatAmountAxis }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: { fontSize: 12 }
    },
    series: [
      {
        type: 'bar',
        data: amounts,
        barWidth: '60%',
        itemStyle: {
          color: getDishColor,
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: '¥{c}'
        }
      }
    ]
  })
}

const renderHourlyChart = () => {
  if (!hourlyChart) return
  const raw = hourlyData.value || []
  const map = {}
  raw.forEach(d => {
    const h = Number(d.hour)
    if (!Number.isNaN(h) && h >= 0 && h < 24) {
      map[h] = {
        amount: Number(d.amount || 0),
        count: Number(d.count || 0)
      }
    }
  })
  const hours = []
  const amounts = []
  const counts = []
  for (let h = 0; h < 24; h++) {
    hours.push(String(h).padStart(2, '0') + ':00')
    amounts.push(map[h] ? map[h].amount : 0)
    counts.push(map[h] ? map[h].count : 0)
  }

  hourlyChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['销售额', '订单数'],
      top: 0
    },
    grid: {
      top: 50,
      left: 70,
      right: 70,
      bottom: 50
    },
    xAxis: {
      type: 'category',
      data: hours,
      axisLabel: { fontSize: 12 }
    },
    yAxis: [
      {
        type: 'value',
        name: '金额',
        axisLabel: { formatter: formatAmountAxis }
      },
      {
        type: 'value',
        name: '订单数',
        axisLabel: { formatter: '{value}' }
      }
    ],
    series: [
      {
        name: '销售额',
        type: 'bar',
        data: amounts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#FFB300' },
            { offset: 1, color: '#FFE082' }
          ])
        },
        barWidth: '55%'
      },
      {
        name: '订单数',
        type: 'line',
        yAxisIndex: 1,
        data: counts,
        smooth: true,
        itemStyle: { color: '#F56C6C' },
        lineStyle: { width: 2 }
      }
    ]
  })
}

const initCharts = () => {
  if (dailyChartRef.value) dailyChart = echarts.init(dailyChartRef.value)
  if (dishChartRef.value) dishChart = echarts.init(dishChartRef.value)
  if (hourlyChartRef.value) hourlyChart = echarts.init(hourlyChartRef.value)
}

const handleResize = () => {
  dailyChart && dailyChart.resize()
  dishChart && dishChart.resize()
  hourlyChart && hourlyChart.resize()
}

const openAiDialog = (title, dataType = '') => {
  aiDialog.visible = true
  aiDialog.title = title
  aiDialog.content = ''
  aiDialog.dataType = dataType
  aiLoading.value = true
}

const extractAnalysisContent = (res) => {
  if (!res) return '分析完成'
  if (typeof res === 'string') return res
  if (res.data) {
    if (typeof res.data === 'string') return res.data
    if (res.data.analysis) return res.data.analysis
    if (res.data.message) return res.data.message
    if (res.data.content) return res.data.content
    if (res.data.result) return res.data.result
  }
  if (res.analysis) return res.analysis
  if (res.message) return res.message
  if (res.content) return res.content
  return 'AI 分析完成'
}

// ============ 单项分析函数 ============

const analyzeTrend = async () => {
  analyzing.trend = true
  openAiDialog('销售趋势 AI 分析报告', 'trend')
  try {
    const trendForAI = dailyData.value.map(d => ({
      日期: d.date,
      销售额: d.amount,
      订单数: d.order_count
    }))

    const res = await aiAnalyze({
      dataType: 'canteen-sales-trend',
      dataSummary: {
        总销售额: summary.value.total_amount,
        总订单数: summary.value.total_orders,
        客单价: summary.value.avg_amount,
        近30天趋势: trendForAI
      },
      userQuestion: `请作为专业的数据分析师，基于以下食堂销售数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **数据概览**：总销售额、总订单数、客单价等关键指标
2. **趋势分析**：销售趋势变化、峰值低谷日期、可能的影响因素
3. **关键发现**：从数据中挖掘出的重要洞察
4. **优化建议**：基于分析给出具体可行的运营建议

## 输出要求
- 使用 Markdown 格式输出
- 标题、列表、粗体强调关键数据
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('分析趋势失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.trend = false
    aiLoading.value = false
  }
}

const analyzeDishes = async () => {
  analyzing.dishes = true
  openAiDialog('菜品销售 AI 分析报告', 'dishes')
  try {
    const dishForAI = (dishData.value || []).slice(0, 10).map(d => ({
      菜品名称: d.menu_name,
      销量: d.total_quantity,
      销售额: d.total_amount
    }))

    const res = await aiAnalyze({
      dataType: 'canteen-dish-ranking',
      dataSummary: dishForAI,
      userQuestion: `请作为专业的餐饮运营分析师，基于以下菜品销售数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **热门菜品分析**：销量和销售额最高的菜品、成功原因分析
2. **菜品结构分析**：菜品结构是否合理、是否存在过度依赖风险
3. **优化建议**：菜单调整、定价策略、促销建议等

## 输出要求
- 使用 Markdown 格式输出
- 可使用表格展示 TOP 10 菜品数据
- 用 **粗体** 强调关键菜品和数据
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('分析菜品失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.dishes = false
    aiLoading.value = false
  }
}

const analyzeHourly = async () => {
  analyzing.hourly = true
  openAiDialog('销售时段分布 AI 分析报告', 'hourly')
  try {
    const hourlyForAI = hourlyData.value.map(d => ({
      时段: d.hour,
      销售额: d.amount,
      订单数: d.count
    }))

    const res = await aiAnalyze({
      dataType: 'canteen-hourly-distribution',
      dataSummary: {
        总销售额: summary.value.total_amount,
        总订单数: summary.value.total_orders,
        '近24小时分布': hourlyForAI
      },
      userQuestion: `请作为专业的餐饮运营分析师，基于以下24小时销售时段分布数据，生成一份结构化的分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **用餐高峰识别**：主要用餐高峰时段、销售额和订单占比
2. **冷清时段分析**：销量最低的时段、可能的原因
3. **时段特征分析**：不同时段的客单价差异、订单特点
4. **优化建议**：人员排班、时段营销策略等

## 输出要求
- 使用 Markdown 格式输出
- 用 **粗体** 强调关键时段和数据
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('分析时段分布失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.hourly = false
    aiLoading.value = false
  }
}

// ============ 整体分析函数 ============

const analyzeOverall = async () => {
  analyzing.overall = true
  openAiDialog('食堂销售数据 AI 整体分析报告', 'overall')
  try {
    const trendForAI = dailyData.value.map(d => ({
      日期: d.date, 销售额: d.amount, 订单数: d.order_count
    }))

    const dishForAI = (dishData.value || []).slice(0, 10).map(d => ({
      菜品名称: d.menu_name, 销量: d.total_quantity, 销售额: d.total_amount
    }))

    const hourlyForAI = hourlyData.value.map(d => ({
      时段: d.hour, 销售额: d.amount, 订单数: d.count
    }))

    const res = await aiAnalyze({
      dataType: 'canteen-sales-overall',
      dataSummary: {
        总体指标: {
          总销售额: summary.value.total_amount,
          总订单数: summary.value.total_orders,
          客单价: summary.value.avg_amount,
          热销菜品数: hotDishCount.value
        },
        '近30天销售趋势': trendForAI,
        '菜品销售排行TOP10': dishForAI,
        '24小时时段分布': hourlyForAI
      },
      userQuestion: `请作为专业的数据分析师和餐饮运营顾问，基于以下食堂的完整销售数据，生成一份全面深入的数据分析报告：

## 分析方向（仅供参考，请根据实际数据灵活调整）
1. **执行摘要**：食堂整体经营状况总结、关键数据指标
2. **销售趋势分析**：销售峰值低谷、波动规律、增长或下降趋势
3. **菜品销售分析**：热门菜品分析、菜品结构合理性
4. **时段分布分析**：用餐高峰识别、冷清时段分析、优化建议
5. **关键发现**：从数据中提炼的重要洞察和业务风险
6. **综合建议**：具体可执行的优化建议

## 输出要求
- 使用 Markdown 格式输出
- 用 **粗体** 强调关键发现和数据
- 可用表格呈现数据对比
- 建议内容要有可操作性
- 请根据实际数据情况，自由调整分析维度和内容结构`
    })

    aiDialog.content = extractAnalysisContent(res)
  } catch (e) {
    console.error('整体分析失败:', e)
    aiDialog.content = `**分析失败**

错误信息：${e.message || e.toString()}

请检查后端服务是否正常运行，或稍后重试。`
  } finally {
    analyzing.overall = false
    aiLoading.value = false
  }
}

// ============ 导出与辅助函数 ============

const copyAnalysis = async () => {
  if (!aiDialog.content) return
  try {
    await navigator.clipboard.writeText(aiDialog.content)
    ElMessage.success('内容已复制到剪贴板')
  } catch (e) {
    const textarea = document.createElement('textarea')
    textarea.value = aiDialog.content
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('内容已复制到剪贴板')
    } catch (err) {
      ElMessage.error('复制失败，请手动复制')
    }
    document.body.removeChild(textarea)
  }
}

const exportAsMarkdown = () => {
  if (!aiDialog.content) return
  const content = `# ${aiDialog.title}

> 生成时间：${currentTimeStr.value}
> 数据来源：食堂销售看板实时数据

---

${aiDialog.content}

---

*本报告由 AI 智能分析系统自动生成*`

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const fileName = `食堂销售分析报告_${Date.now()}.md`
  triggerDownload(blob, fileName)
  ElMessage.success('Markdown 文件已下载')
}

const exportAsText = () => {
  if (!aiDialog.content) return
  const textContent = aiDialog.content
    .replace(/[#*`>]/g, '')
    .replace(/---/g, '========================================')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]+>/g, '')

  const content = `${'='.repeat(60)}
${aiDialog.title}
${'='.repeat(60)}

生成时间：${currentTimeStr.value}
数据来源：食堂销售看板实时数据

${'-'.repeat(60)}

${textContent}

${'-'.repeat(60)}
本报告由 AI 智能分析系统自动生成
${'='.repeat(60)}`

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const fileName = `食堂销售分析报告_${Date.now()}.txt`
  triggerDownload(blob, fileName)
  ElMessage.success('TXT 文件已下载')
}

const printAnalysis = () => {
  if (!aiDialog.content) return
  const printWindow = window.open('', '_blank', 'width=900,height=700')
  if (!printWindow) {
    ElMessage.warning('无法打开打印窗口，请检查浏览器设置')
    return
  }
  printWindow.document.write(`
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <title>${aiDialog.title}</title>
      <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; padding: 30px; line-height: 1.8; color: #303133; }
        h1 { color: #409EFF; border-bottom: 3px solid #409EFF; padding-bottom: 10px; }
        h2 { color: #67C23A; border-left: 4px solid #67C23A; padding-left: 12px; margin-top: 25px; }
        h3 { color: #E6A23C; margin-top: 20px; }
        strong { color: #F56C6C; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ebeef5; padding: 8px 12px; text-align: left; }
        th { background: #f5f7fa; font-weight: bold; }
        ul, ol { padding-left: 25px; }
        li { margin: 6px 0; }
        blockquote { border-left: 4px solid #909399; padding-left: 15px; color: #606266; margin: 15px 0; }
        code { background: #f5f7fa; padding: 2px 6px; border-radius: 3px; color: #F56C6C; font-family: monospace; }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%); border-radius: 8px; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ebeef5; color: #909399; font-size: 12px; }
        @media print { body { padding: 15px; } }
      </style>
    </head>
    <body>
      <div class="header">
        <h1 style="border:none; margin:0;">${aiDialog.title}</h1>
        <p style="margin: 10px 0 0 0; color: #606266;">生成时间：${currentTimeStr.value}</p>
      </div>
      <div style="padding: 10px 20px;">${renderedMarkdown.value}</div>
      <div class="footer">本报告由 AI 智能分析系统自动生成</div>
      <script>window.onload = function() { setTimeout(function() { window.print(); }, 500); }<\/script>
    </body>
    </html>
  `)
  printWindow.document.close()
}

const triggerDownload = (blob, fileName) => {
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  setTimeout(() => URL.revokeObjectURL(url), 100)
}

onMounted(() => {
  initCharts()
  loading.value = true
  Promise.all([
    loadSummary(),
    loadDailyTrend(),
    loadDishRanking(),
    loadHourlyDistribution()
  ]).finally(() => {
    loading.value = false
  })
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  dailyChart && dailyChart.dispose()
  dishChart && dishChart.dispose()
  hourlyChart && hourlyChart.dispose()
})
</script>

<style scoped>
.canteen-sales {
  padding: 20px;
}

/* 整体分析卡片 */
.row-overall {
  margin-bottom: 20px;
}

.overall-card {
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 50%, #e1f3d8 100%);
  border: none;
}

.overall-card :deep(.el-card__body) {
  padding: 20px 25px;
}

.overall-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.overall-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.overall-info {
  display: flex;
  flex-direction: column;
}

.overall-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.overall-sub {
  font-size: 13px;
  color: #606266;
}

.overall-btn {
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  padding: 0 28px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.35);
}

.overall-btn:hover {
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.5);
}

/* 统计卡片行 */
.row-cards {
  margin-bottom: 24px;
}

.row-charts {
  margin-bottom: 24px;
}

.stat-card {
  height: 140px;
  padding: 12px;
  box-sizing: border-box;
}

.stat-card :deep(.el-card__body) {
  height: 100%;
  padding: 12px;
}

.card-inner {
  display: flex;
  align-items: center;
  height: 100%;
}

.icon-box {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
  color: #ffffff;
}

.icon-blue {
  background: linear-gradient(135deg, #409EFF 0%, #1860B0 100%);
}

.icon-green {
  background: linear-gradient(135deg, #67C23A 0%, #2F8B2A 100%);
}

.icon-orange {
  background: linear-gradient(135deg, #E6A23C 0%, #B97E1A 100%);
}

.icon-red {
  background: linear-gradient(135deg, #F56C6C 0%, #B93A3A 100%);
}

.text-box {
  flex: 1;
  min-width: 0;
}

.text-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 6px;
  font-weight: 500;
}

.text-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1.25;
  white-space: nowrap;
}

.text-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chart-container {
  width: 100%;
  height: 380px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

/* AI 分析对话框 */
.ai-content {
  padding: 5px 0;
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.ai-header-text {
  flex: 1;
}

.ai-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 3px;
}

.ai-subtitle {
  font-size: 12px;
  color: #909399;
}

/* 工具栏 */
.ai-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

/* AI 内容区 */
.ai-body {
  min-height: 400px;
  max-height: 560px;
  overflow-y: auto;
  padding: 24px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.ai-body.ai-loading {
  min-height: 300px;
}

/* Markdown 内容样式 */
.ai-markdown-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.9;
}

.ai-markdown-content :deep(.md-h1) {
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
  text-align: center;
  padding: 20px 0;
  margin: 0 0 25px 0;
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
  border-radius: 8px;
}

.ai-markdown-content :deep(.md-h2) {
  font-size: 18px;
  font-weight: 700;
  color: #67C23A;
  padding-left: 14px;
  border-left: 4px solid #67C23A;
  margin: 30px 0 15px 0;
}

.ai-markdown-content :deep(.md-h3) {
  font-size: 15px;
  font-weight: 700;
  color: #E6A23C;
  margin: 20px 0 10px 0;
}

.ai-markdown-content :deep(.md-h4),
.ai-markdown-content :deep(.md-h5),
.ai-markdown-content :deep(.md-h6) {
  font-size: 14px;
  font-weight: 600;
  color: #909399;
  margin: 15px 0 8px 0;
}

.ai-markdown-content :deep(.md-p) {
  margin: 12px 0;
  text-align: justify;
}

.ai-markdown-content :deep(strong) {
  color: #F56C6C;
  font-weight: 700;
  background: #fef0f0;
  padding: 2px 6px;
  border-radius: 3px;
}

.ai-markdown-content :deep(em) {
  font-style: italic;
  color: #606266;
}

.ai-markdown-content :deep(.md-code) {
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #F56C6C;
  border: 1px solid #e4e7ed;
}

.ai-markdown-content :deep(.md-ul) {
  padding-left: 24px;
  margin: 12px 0;
}

.ai-markdown-content :deep(.md-li) {
  margin: 8px 0;
  line-height: 1.8;
  list-style-type: disc;
}

.ai-markdown-content :deep(.md-li.md-li-num) {
  list-style-type: none;
}

.ai-markdown-content :deep(.md-num) {
  display: inline-block;
  min-width: 25px;
  font-weight: 700;
  color: #409EFF;
}

.ai-markdown-content :deep(.md-quote) {
  padding: 12px 18px;
  margin: 15px 0;
  background: #f5f7fa;
  border-left: 4px solid #909399;
  border-radius: 4px;
  color: #606266;
}

.ai-markdown-content :deep(.md-hr) {
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent, #dcdfe6, transparent);
  margin: 25px 0;
}

/* 滚动条样式 */
.ai-body::-webkit-scrollbar {
  width: 8px;
}

.ai-body::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 4px;
}

.ai-body::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

.ai-body::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>
